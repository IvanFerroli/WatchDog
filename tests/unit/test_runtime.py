from __future__ import annotations

from datetime import UTC, datetime, timedelta

from watchdog.adapters.composite import SourceFailure
from watchdog.adapters.slack_ui import AdapterErrorCode, SlackAdapterError
from watchdog.application import MonitorRuntime
from watchdog.classification import EventClassifier, NotificationRules
from watchdog.core.deduplication import DeduplicationService
from watchdog.core.models import HealthState, ObservedEvent
from watchdog.core.normalizer import EventNormalizer
from watchdog.persistence import SQLiteEventStore


class FakeClock:
    def __init__(self) -> None:
        self.value = datetime(2026, 7, 22, 12, tzinfo=UTC)

    def now(self) -> datetime:
        self.value += timedelta(milliseconds=1)
        return self.value


class FakeAdapter:
    adapter_version = "fake-v1"

    def __init__(self, events: list[ObservedEvent]) -> None:
        self.events = events
        self.error: SlackAdapterError | None = None
        self.last_failures: tuple[SourceFailure, ...] = ()

    def observe(self) -> list[ObservedEvent]:
        if self.error:
            raise self.error
        return self.events


class RecordingNotifier:
    def __init__(self) -> None:
        self.events: list[object] = []

    def notify(self, event: object) -> None:
        self.events.append(event)


class FailOnceNotifier(RecordingNotifier):
    def notify(self, event: object) -> None:
        if not self.events:
            self.events.append("failed")
            raise RuntimeError("synthetic notification failure")
        self.events.append(event)


def _runtime(
    adapter: FakeAdapter, store: SQLiteEventStore, notifier: RecordingNotifier
) -> MonitorRuntime:
    return MonitorRuntime(
        adapter=adapter,
        normalizer=EventNormalizer(),
        classifier=EventClassifier(
            direct_mention_labels=("direta",),
            group_mention_labels=("grupo",),
        ),
        deduplication=DeduplicationService(store),
        rules=NotificationRules(),
        store=store,
        notifier=notifier,
        clock=FakeClock(),
        poll_interval_seconds=0.01,
    )


def test_runtime_alerts_direct_once_and_ignores_group() -> None:
    observed_at = datetime(2026, 7, 22, tzinfo=UTC)
    adapter = FakeAdapter(
        [
            ObservedEvent("slack", observed_at, external_key="1", raw_type="direta"),
            ObservedEvent("slack", observed_at, external_key="2", raw_type="grupo"),
        ]
    )
    notifier = RecordingNotifier()
    store = SQLiteEventStore(":memory:")
    runtime = _runtime(adapter, store, notifier)

    first = runtime.run_once()
    second = runtime.run_once()

    assert first.state is HealthState.MONITORING
    assert first.new_items_last_scan == 2
    assert second.new_items_last_scan == 0
    assert len(notifier.events) == 1
    assert len(store.list_events()) == 2
    store.close()


def test_runtime_transitions_from_absent_to_monitoring_and_pause() -> None:
    adapter = FakeAdapter([])
    notifier = RecordingNotifier()
    store = SQLiteEventStore(":memory:")
    runtime = _runtime(adapter, store, notifier)
    adapter.error = SlackAdapterError(AdapterErrorCode.SLACK_NOT_RUNNING, "not found")

    failed = runtime.run_once()
    adapter.error = None
    recovered = runtime.run_once()
    runtime.pause()
    paused = runtime.run_once()
    runtime.resume()

    assert failed.state is HealthState.SLACK_NOT_RUNNING
    assert failed.last_error_code == "SLACK_NOT_RUNNING"
    assert recovered.state is HealthState.MONITORING
    assert paused.state is HealthState.PAUSED
    assert runtime.health.snapshot().state is HealthState.STARTING
    store.close()


def test_runtime_retries_reserved_but_unalerted_direct_event() -> None:
    adapter = FakeAdapter(
        [
            ObservedEvent(
                "slack",
                datetime(2026, 7, 22, tzinfo=UTC),
                external_key="retry-1",
                raw_type="direta",
            )
        ]
    )
    notifier = FailOnceNotifier()
    store = SQLiteEventStore(":memory:")
    runtime = _runtime(adapter, store, notifier)

    assert runtime.run_once().state is HealthState.DEGRADED
    assert runtime.run_once().state is HealthState.MONITORING
    assert len(notifier.events) == 2
    assert store.is_alerted(runtime.deduplication.generate_key(adapter.events[0]))
    store.close()


def test_runtime_processes_dm_and_reports_partial_source_failure() -> None:
    adapter = FakeAdapter(
        [
            ObservedEvent(
                "windows.user_notification_listener.slack",
                datetime(2026, 7, 22, tzinfo=UTC),
                external_key="windows-toast:1",
                raw_type="MD",
            )
        ]
    )
    adapter.last_failures = (SourceFailure("slack_uia", "ACTIVITY_NOT_FOUND"),)
    notifier = RecordingNotifier()
    store = SQLiteEventStore(":memory:")
    runtime = _runtime(adapter, store, notifier)

    snapshot = runtime.run_once()

    assert snapshot.state is HealthState.DEGRADED
    assert snapshot.last_error_code == "SOURCE_PARTIAL_FAILURE"
    assert snapshot.new_items_last_scan == 1
    assert len(notifier.events) == 1
    store.close()
