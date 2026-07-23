from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from watchdog.adapters.windows_notifications import (
    SlackDirectMessagePolicy,
    UserNotificationListenerSource,
    WindowsNotificationError,
    WindowsNotificationErrorCode,
    WindowsNotificationRecord,
    WinRTUserNotificationBackend,
    _record_from_winrt,
)

NOW = datetime(2026, 7, 22, 12, tzinfo=UTC)


class FakeBackend:
    def __init__(self, records: list[WindowsNotificationRecord] | None = None) -> None:
        self.records = records or []

    def list_toasts(self) -> list[WindowsNotificationRecord]:
        return list(self.records)


def _record(
    notification_id: int,
    *texts: str,
    created_at: datetime = NOW,
    display: str = "Slack",
    app_id: str = "com.squirrel.slack.slack",
    package: str = "com.tinyspeck.slackdesktop",
) -> WindowsNotificationRecord:
    return WindowsNotificationRecord(
        notification_id=notification_id,
        creation_time=created_at,
        app_display_name=display,
        app_user_model_id=app_id,
        package_family_name=package,
        text_elements=tuple(texts),
    )


def test_source_establishes_baseline_then_emits_each_new_dm_once() -> None:
    old = _record(10, "Pessoa antiga", "mensagem anterior")
    backend = FakeBackend([old])
    source = UserNotificationListenerSource(backend)

    assert source.observe() == []

    current = _record(11, "Pessoa nova", "mensagem nova", created_at=NOW + timedelta(seconds=1))
    backend.records = [old, current]
    first = source.observe()
    second = source.observe()

    assert len(first) == 1
    assert second == []
    assert first[0].raw_type == "MD"
    assert first[0].sender == "Pessoa nova"
    assert first[0].body == "mensagem nova"
    assert first[0].occurred_at == NOW + timedelta(seconds=1)
    assert first[0].external_key and first[0].external_key.startswith("windows-toast:")


@pytest.mark.parametrize(
    "record",
    [
        _record(1, "Pessoa", "texto", display="Teams", app_id="msteams", package="msteams"),
        _record(2, "#suporte", "texto"),
        _record(3, "Pessoa in #support", "texto"),
        _record(4, "Pessoa em #suporte", "texto"),
        _record(8, "Pessoa (#suporte)", "texto"),
        _record(5, "Menção no Slack", "texto"),
        _record(6, "Slack Huddle", "começou"),
        _record(7, "somente um elemento"),
    ],
)
def test_source_fails_closed_for_non_slack_or_ambiguous_toasts(
    record: WindowsNotificationRecord,
) -> None:
    backend = FakeBackend()
    source = UserNotificationListenerSource(backend)
    source.observe()

    backend.records = [record]

    assert source.observe() == []


def test_source_uses_minimal_metadata_and_compound_identity() -> None:
    backend = FakeBackend()
    source = UserNotificationListenerSource(backend)
    source.observe()
    first_record = _record(20, "  Alice  ", " segredo   sintético ")
    backend.records = [first_record]

    first = source.observe()[0]
    backend.records = [
        _record(20, "Alice", "segredo sintético", created_at=NOW + timedelta(microseconds=1))
    ]
    second = source.observe()[0]

    assert first.external_key != second.external_key
    assert first.title == "Mensagem direta no Slack"
    assert first.sender == "Alice"
    assert first.body == "segredo sintético"
    assert set(first.raw_metadata) == {
        "adapter_version",
        "notification_id",
        "app_user_model_id",
        "package_family_name",
    }
    assert "segredo" not in repr(first.raw_metadata)


def test_winrt_record_filters_app_before_reading_notification_content() -> None:
    class ForbiddenNotification:
        def __init__(self) -> None:
            self.accessed = False

        @property
        def visual(self) -> object:
            self.accessed = True
            raise AssertionError("non-Slack content must not be read")

    notification = ForbiddenNotification()
    item = SimpleNamespace(
        app_info=SimpleNamespace(
            display_info=SimpleNamespace(display_name="Teams"),
            app_user_model_id="msteams",
            package=SimpleNamespace(id=SimpleNamespace(family_name="msteams")),
        ),
        notification=notification,
    )

    record = _record_from_winrt(item, object(), lambda _display, _aumid, _package: False)

    assert record is None
    assert not notification.accessed


def test_slack_app_policy_requires_both_name_and_identity() -> None:
    policy = SlackDirectMessagePolicy()

    assert policy.is_slack_app("Slack", "com.squirrel.slack.slack", "")
    assert not policy.is_slack_app("Slack", "unrelated", "unrelated")
    assert not policy.is_slack_app("Unrelated", "com.squirrel.slack.slack", "")


def _install_fake_winrt(
    monkeypatch: pytest.MonkeyPatch,
    listener: object,
) -> None:
    notifications = ModuleType("winrt.windows.ui.notifications")
    notifications.KnownNotificationBindings = SimpleNamespace(TOAST_GENERIC="toast-generic")
    notifications.NotificationKinds = SimpleNamespace(TOAST="toast")
    management = ModuleType("winrt.windows.ui.notifications.management")
    management.UserNotificationListener = SimpleNamespace(current=listener)
    monkeypatch.setitem(
        sys.modules,
        "winrt.windows.ui.notifications",
        notifications,
    )
    monkeypatch.setitem(
        sys.modules,
        "winrt.windows.ui.notifications.management",
        management,
    )


def _winrt_item() -> object:
    binding = SimpleNamespace(
        get_text_elements=lambda: [SimpleNamespace(text="Alice"), SimpleNamespace(text="Olá")]
    )
    visual = SimpleNamespace(get_binding=lambda binding_name: binding)
    return SimpleNamespace(
        id=42,
        creation_time=NOW,
        app_info=SimpleNamespace(
            display_info=SimpleNamespace(display_name="Slack"),
            app_user_model_id="com.squirrel.slack.slack",
            package=SimpleNamespace(id=SimpleNamespace(family_name="com.tinyspeck.slackdesktop")),
        ),
        notification=SimpleNamespace(visual=visual),
    )


def test_winrt_backend_reads_allowed_slack_toasts(monkeypatch: pytest.MonkeyPatch) -> None:
    class Listener:
        def get_access_status(self) -> object:
            return SimpleNamespace(name="ALLOWED")

        async def get_notifications_async(self, kind: object) -> list[Any]:
            assert kind == "toast"
            return [_winrt_item()]

    _install_fake_winrt(monkeypatch, Listener())
    monkeypatch.setattr("watchdog.adapters.windows_notifications.sys.platform", "win32")
    backend = WinRTUserNotificationBackend(SlackDirectMessagePolicy().is_slack_app)

    records = backend.list_toasts()

    assert len(records) == 1
    assert records[0].notification_id == 42
    assert records[0].text_elements == ("Alice", "Olá")


def test_winrt_backend_requests_access_and_reports_denial(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Listener:
        def __init__(self) -> None:
            self.requested = False

        def get_access_status(self) -> object:
            return SimpleNamespace(name="UNSPECIFIED")

        async def request_access_async(self) -> object:
            self.requested = True
            return SimpleNamespace(name="DENIED")

    listener = Listener()
    _install_fake_winrt(monkeypatch, listener)
    monkeypatch.setattr("watchdog.adapters.windows_notifications.sys.platform", "win32")

    with pytest.raises(WindowsNotificationError) as caught:
        WinRTUserNotificationBackend(SlackDirectMessagePolicy().is_slack_app).list_toasts()

    assert listener.requested
    assert caught.value.code is WindowsNotificationErrorCode.ACCESS_DENIED


def test_winrt_backend_fails_explicitly_off_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("watchdog.adapters.windows_notifications.sys.platform", "linux")

    with pytest.raises(WindowsNotificationError) as caught:
        WinRTUserNotificationBackend(SlackDirectMessagePolicy().is_slack_app).list_toasts()

    assert caught.value.code is WindowsNotificationErrorCode.UNSUPPORTED_PLATFORM
    assert not caught.value.retriable
