from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from watchdog.core.models import EventCategory, EventPriority, OperationalEvent
from watchdog.notifications import NotificationError, NullNotifier, WindowsNotifier
from watchdog.notifications.windows import (
    DEFAULT_SLACK_DESTINATION,
    notification_destination,
)


class FakeToast:
    shown = 0
    last_values: dict[str, str] = {}
    last_action: tuple[str, str] | None = None

    def __init__(self, **values: str) -> None:
        self.values = values
        FakeToast.last_values = values

    def show(self) -> None:
        FakeToast.shown += 1

    def add_actions(self, label: str, launch: str) -> None:
        FakeToast.last_action = (label, launch)


def _event(category: EventCategory = EventCategory.DIRECT_MENTION) -> OperationalEvent:
    return OperationalEvent(
        id="1",
        source="slack",
        category=category,
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
    FakeToast.last_action = None
    notifier = WindowsNotifier(
        toast_factory=FakeToast,
        sound_player=sounds.append,
        sound_enabled=True,
    )

    notifier.notify(_event())

    assert FakeToast.shown == 1
    assert sounds == [None]
    assert FakeToast.last_values["duration"] == "long"
    assert FakeToast.last_values["launch"] == DEFAULT_SLACK_DESTINATION
    assert FakeToast.last_action == ("Abrir no Slack", DEFAULT_SLACK_DESTINATION)


def test_null_notifier_and_disabled_sound() -> None:
    event = _event()
    NullNotifier().notify(event)
    FakeToast.shown = 0
    WindowsNotifier(toast_factory=FakeToast, sound_enabled=False).notify(event)
    assert FakeToast.shown == 1


def test_notifier_rejects_non_positive_preview_length() -> None:
    with pytest.raises(ValueError, match="preview_length"):
        WindowsNotifier(preview_length=0)


def test_preview_can_be_hidden() -> None:
    WindowsNotifier(
        toast_factory=FakeToast,
        sound_enabled=False,
        show_preview=False,
    ).notify(_event())
    assert FakeToast.last_values["msg"] == "Nova menção direta"


def test_direct_message_uses_distinct_title_and_hidden_preview() -> None:
    WindowsNotifier(
        toast_factory=FakeToast,
        sound_enabled=False,
        show_preview=False,
    ).notify(_event(EventCategory.DIRECT_MESSAGE))

    assert FakeToast.last_values["title"] == "Nova mensagem privada no Slack"
    assert FakeToast.last_values["msg"] == "Nova mensagem privada"


def test_toast_uses_existing_brand_icon(tmp_path: Path) -> None:
    icon = tmp_path / "alwaystrack.png"
    icon.write_bytes(b"synthetic icon")

    WindowsNotifier(
        toast_factory=FakeToast,
        sound_enabled=False,
        icon_path=icon,
    ).notify(_event())

    assert FakeToast.last_values["icon"] == str(icon.resolve())


def test_remote_preview_is_inert_in_winotify_powershell_and_xml() -> None:
    base = _event()
    event = OperationalEvent(
        id=base.id,
        source=base.source,
        category=base.category,
        priority=base.priority,
        observed_at=base.observed_at,
        deduplication_key=base.deduplication_key,
        classifier_version=base.classifier_version,
        body='linha 1\n$($env:USERNAME) `cmd` ]]> "@',
    )

    WindowsNotifier(toast_factory=FakeToast, sound_enabled=False).notify(event)

    message = FakeToast.last_values["msg"]
    assert "\n" not in message
    assert "`$(" in message
    assert "``cmd``" in message
    assert "]]]]><![CDATA[>" in message


@pytest.mark.skipif(sys.platform == "win32", reason="non-Windows fail-closed behavior")
def test_native_backend_fails_closed_outside_windows() -> None:
    with pytest.raises(NotificationError, match="unavailable"):
        WindowsNotifier().notify(_event())


def test_backend_exception_is_wrapped() -> None:
    def broken_factory(**_: str) -> object:
        raise RuntimeError("synthetic")

    with pytest.raises(NotificationError, match="notification failed"):
        WindowsNotifier(toast_factory=broken_factory).notify(_event())


@pytest.mark.parametrize(
    "destination",
    [
        "slack://channel?team=T123&id=C123",
        "https://acme.slack.com/archives/C123/p1784760246639139",
        "https://slack.com/app_redirect?channel=C123",
    ],
)
def test_toast_click_uses_safe_captured_slack_destination(destination: str) -> None:
    base = _event()
    event = OperationalEvent(
        id=base.id,
        source=base.source,
        category=base.category,
        priority=base.priority,
        observed_at=base.observed_at,
        deduplication_key=base.deduplication_key,
        classifier_version=base.classifier_version,
        metadata={"slack_destination": destination},
    )

    WindowsNotifier(toast_factory=FakeToast, sound_enabled=False).notify(event)

    assert FakeToast.last_values["launch"] == destination.replace("&", "&amp;")


@pytest.mark.parametrize(
    "destination",
    [
        "file:///C:/Windows/System32/calc.exe",
        "https://evil.example/redirect",
        "https://[slack.com",
        "slack://open\r\nfile:///unsafe",
        "slack://open?$($env:USERNAME)",
        "slack://open?value=`calc`",
        "",
    ],
)
def test_invalid_destination_falls_back_to_opening_slack(destination: str) -> None:
    base = _event()
    event = OperationalEvent(
        id=base.id,
        source=base.source,
        category=base.category,
        priority=base.priority,
        observed_at=base.observed_at,
        deduplication_key=base.deduplication_key,
        classifier_version=base.classifier_version,
        metadata={"slack_destination": destination},
    )

    assert notification_destination(event) == DEFAULT_SLACK_DESTINATION
