from __future__ import annotations

from datetime import UTC, datetime

from watchdog.core.models import EventCategory, EventPriority, OperationalEvent
from watchdog.notifications import WindowsNotifier


class FakeToast:
    shown = 0

    def __init__(self, **values: str) -> None:
        self.values = values

    def show(self) -> None:
        FakeToast.shown += 1


def _event() -> OperationalEvent:
    return OperationalEvent(
        id="1",
        source="slack",
        category=EventCategory.DIRECT_MENTION,
        priority=EventPriority.HIGH,
        observed_at=datetime(2026, 7, 22, tzinfo=UTC),
        deduplication_key="dedup:1",
        classifier_version="test",
        actor=None,
        location=None,
        body=None,
    )


def test_notifier_supports_missing_fields_and_injected_windows_backends() -> None:
    sounds: list[str | None] = []
    FakeToast.shown = 0
    notifier = WindowsNotifier(
        toast_factory=FakeToast,
        sound_player=sounds.append,
        sound_enabled=True,
    )

    notifier.notify(_event())

    assert FakeToast.shown == 1
    assert sounds == [None]
