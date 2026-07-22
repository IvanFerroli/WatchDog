from __future__ import annotations

import sys
from datetime import UTC, datetime

import pytest

from watchdog.core.models import EventCategory, EventPriority, OperationalEvent
from watchdog.notifications import NotificationError, NullNotifier, WindowsNotifier


class FakeToast:
    shown = 0
    last_values: dict[str, str] = {}

    def __init__(self, **values: str) -> None:
        self.values = values
        FakeToast.last_values = values

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


def test_null_notifier_and_disabled_sound() -> None:
    event = _event()
    NullNotifier().notify(event)
    FakeToast.shown = 0
    WindowsNotifier(toast_factory=FakeToast, sound_enabled=False).notify(event)
    assert FakeToast.shown == 1


def test_preview_can_be_hidden() -> None:
    WindowsNotifier(
        toast_factory=FakeToast,
        sound_enabled=False,
        show_preview=False,
    ).notify(_event())
    assert FakeToast.last_values["msg"] == "Nova menção direta"


@pytest.mark.skipif(sys.platform == "win32", reason="non-Windows fail-closed behavior")
def test_native_backend_fails_closed_outside_windows() -> None:
    with pytest.raises(NotificationError, match="unavailable"):
        WindowsNotifier().notify(_event())


def test_backend_exception_is_wrapped() -> None:
    def broken_factory(**_: str) -> object:
        raise RuntimeError("synthetic")

    with pytest.raises(NotificationError, match="notification failed"):
        WindowsNotifier(toast_factory=broken_factory).notify(_event())
