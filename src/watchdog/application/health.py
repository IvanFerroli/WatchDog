"""Thread-safe, observable monitor health state."""

from __future__ import annotations

import threading
from dataclasses import dataclass, replace
from datetime import datetime

from watchdog.core.models import HealthState


@dataclass(frozen=True, slots=True)
class HealthSnapshot:
    state: HealthState = HealthState.STARTING
    last_transition_at: datetime | None = None
    last_successful_scan_at: datetime | None = None
    last_error_at: datetime | None = None
    last_error_code: str | None = None
    items_read_last_scan: int = 0
    new_items_last_scan: int = 0
    direct_mentions_today: int = 0
    consecutive_failures: int = 0


class HealthMonitor:
    def __init__(self) -> None:
        self._snapshot = HealthSnapshot()
        self._lock = threading.RLock()

    def snapshot(self) -> HealthSnapshot:
        with self._lock:
            return self._snapshot

    def transition(
        self,
        state: HealthState,
        at: datetime,
        *,
        error_code: str | None = None,
    ) -> HealthSnapshot:
        with self._lock:
            failures = self._snapshot.consecutive_failures
            if error_code:
                failures += 1
            elif state is HealthState.MONITORING:
                failures = 0
            self._snapshot = replace(
                self._snapshot,
                state=state,
                last_transition_at=at,
                last_error_at=at if error_code else self._snapshot.last_error_at,
                last_error_code=error_code if error_code else self._snapshot.last_error_code,
                consecutive_failures=failures,
            )
            return self._snapshot

    def record_scan(
        self,
        at: datetime,
        *,
        items_read: int,
        new_items: int,
        direct_alerts: int,
    ) -> HealthSnapshot:
        with self._lock:
            self._snapshot = replace(
                self._snapshot,
                state=HealthState.MONITORING,
                last_transition_at=at,
                last_successful_scan_at=at,
                items_read_last_scan=items_read,
                new_items_last_scan=new_items,
                direct_mentions_today=self._snapshot.direct_mentions_today + direct_alerts,
                consecutive_failures=0,
            )
            return self._snapshot
