"""Cancelable monitor loop that wires contracted core ports."""

from __future__ import annotations

import logging
import threading
from datetime import UTC, datetime

from watchdog.adapters.slack_ui.errors import AdapterErrorCode, SlackAdapterError
from watchdog.classification.classifier import EventClassifier
from watchdog.classification.rules import NotificationRules
from watchdog.core.deduplication import DeduplicationService
from watchdog.core.models import HealthState, ObservedEvent, OperationalState
from watchdog.core.normalizer import EventNormalizer
from watchdog.core.ports import EventAdapter, EventStore, Notifier

from .health import HealthMonitor, HealthSnapshot


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class MonitorRuntime:
    """Run one serialized scan loop; failures become health transitions."""

    def __init__(
        self,
        *,
        adapter: EventAdapter,
        normalizer: EventNormalizer,
        classifier: EventClassifier,
        deduplication: DeduplicationService,
        rules: NotificationRules,
        store: EventStore,
        notifier: Notifier,
        clock: SystemClock,
        poll_interval_seconds: float,
        health: HealthMonitor | None = None,
    ) -> None:
        if poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be positive")
        self.adapter = adapter
        self.normalizer = normalizer
        self.classifier = classifier
        self.deduplication = deduplication
        self.rules = rules
        self.store = store
        self.notifier = notifier
        self.clock = clock
        self.poll_interval_seconds = poll_interval_seconds
        self.health = health or HealthMonitor()
        self._cancelled = threading.Event()
        self._paused = threading.Event()
        self._scan_lock = threading.Lock()
        self._logger = logging.getLogger("watchdog.runtime")
        self.health.transition(HealthState.STARTING, self.clock.now())

    @property
    def cancelled(self) -> bool:
        return self._cancelled.is_set()

    @property
    def paused(self) -> bool:
        return self._paused.is_set()

    def pause(self) -> None:
        self._paused.set()
        self.health.transition(HealthState.PAUSED, self.clock.now())
        self._log("monitor.paused")

    def resume(self) -> None:
        self._paused.clear()
        self.health.transition(HealthState.STARTING, self.clock.now())
        self._log("monitor.resumed")

    def stop(self) -> None:
        self._cancelled.set()
        self._log("monitor.stopping")

    def run_forever(self) -> HealthSnapshot:
        while not self.cancelled:
            if not self.paused:
                self.run_once()
            self._cancelled.wait(self.poll_interval_seconds)
        return self.health.snapshot()

    def run_once(self) -> HealthSnapshot:
        if self.cancelled or self.paused:
            return self.health.snapshot()
        if not self._scan_lock.acquire(blocking=False):
            return self.health.snapshot()
        try:
            return self._run_scan()
        finally:
            self._scan_lock.release()

    def _run_scan(self) -> HealthSnapshot:
        try:
            observed = list(self.adapter.observe())
        except SlackAdapterError as exc:
            return self._adapter_failure(exc)
        except Exception:
            return self._failure(HealthState.ERROR, "UNEXPECTED_ADAPTER_ERROR")

        new_items = 0
        direct_alerts = 0
        had_notification_failure = False
        for raw in observed:
            try:
                is_new, alerted = self._process(raw)
                new_items += int(is_new)
                direct_alerts += int(alerted)
            except Exception:
                had_notification_failure = True
                self._failure(HealthState.DEGRADED, "EVENT_PROCESSING_FAILED")

        now = self.clock.now()
        snapshot = self.health.record_scan(
            now,
            items_read=len(observed),
            new_items=new_items,
            direct_alerts=direct_alerts,
        )
        if had_notification_failure:
            snapshot = self.health.transition(
                HealthState.DEGRADED,
                now,
                error_code="EVENT_PROCESSING_FAILED",
            )
        self._persist_state(snapshot)
        self._log(
            "scan.completed",
            items_read=len(observed),
            new_items=new_items,
            alerts=direct_alerts,
            degraded=had_notification_failure,
        )
        return snapshot

    def _process(self, raw: ObservedEvent) -> tuple[bool, bool]:
        normalized = self.normalizer.normalize(raw)
        classification = self.classifier.classify(normalized)
        result = self.deduplication.claim(normalized, classification)
        # A failed notifier leaves the event reserved but not alerted. The next
        # observation must retry it instead of silently turning it into a duplicate.
        pending_alert = not result.is_new and not self.store.is_alerted(
            result.event.deduplication_key
        )
        decision = self.rules.decide(result.event, is_new=result.is_new or pending_alert)
        if not decision.alert:
            self._log(
                "event.not_alerted",
                category=result.event.category.value,
                reason=decision.reason,
                is_new=result.is_new,
            )
            return result.is_new, False
        self.notifier.notify(result.event)
        alerted_at = self.clock.now()
        self.store.mark_alerted(result.event.deduplication_key, alerted_at)
        self._log("event.alerted", category=result.event.category.value)
        return True, True

    def _adapter_failure(self, exc: SlackAdapterError) -> HealthSnapshot:
        mapping = {
            AdapterErrorCode.SLACK_NOT_RUNNING: HealthState.SLACK_NOT_RUNNING,
            AdapterErrorCode.SLACK_NOT_ACCESSIBLE: HealthState.SLACK_NOT_ACCESSIBLE,
            AdapterErrorCode.WINDOW_LOST: HealthState.SLACK_NOT_ACCESSIBLE,
            AdapterErrorCode.ACTIVITY_NOT_FOUND: HealthState.ACTIVITY_NOT_FOUND,
            AdapterErrorCode.STRUCTURE_CHANGED: HealthState.DEGRADED,
            AdapterErrorCode.READ_FAILED: HealthState.DEGRADED,
            AdapterErrorCode.STRATEGY_NOT_CONFIGURED: HealthState.DEGRADED,
            AdapterErrorCode.UNSUPPORTED_PLATFORM: HealthState.ERROR,
        }
        return self._failure(mapping[exc.code], exc.code.value)

    def _failure(self, state: HealthState, code: str) -> HealthSnapshot:
        now = self.clock.now()
        snapshot = self.health.transition(state, now, error_code=code)
        record_failure = getattr(self.store, "record_failure", None)
        if callable(record_failure):
            try:
                record_failure(code, now)
            except Exception:
                self._logger.exception("store.failure_record_failed")
        self._persist_state(snapshot)
        self._log("monitor.failure", code=code, state=state.value)
        return snapshot

    def _persist_state(self, snapshot: HealthSnapshot) -> None:
        try:
            self.store.save_state(
                OperationalState(
                    last_successful_scan_at=snapshot.last_successful_scan_at,
                    last_error_at=snapshot.last_error_at,
                    last_error_code=snapshot.last_error_code,
                    adapter_version=getattr(self.adapter, "adapter_version", None),
                )
            )
        except Exception:
            self._logger.exception("store.state_save_failed")

    def _log(self, event: str, **context: object) -> None:
        self._logger.info(event, extra={"context": context})
