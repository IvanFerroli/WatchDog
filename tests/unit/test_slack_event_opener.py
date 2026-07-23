from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

import watchdog.adapters.slack_ui.event_opener as event_opener_module
from watchdog.adapters.slack_ui import (
    PywinautoSlackEventOpener,
    SlackOpenResult,
    SlackWindow,
)
from watchdog.core.models import EventCategory, EventPriority, OperationalEvent


class FakeElementInfo:
    def __init__(self, *, automation_id: str = "", name: str = "") -> None:
        self.automation_id = automation_id
        self.name = name


class FakeControl:
    def __init__(
        self,
        *,
        automation_id: str = "",
        name: str = "",
        fail_invoke: bool = False,
        fail_click_input: bool = False,
    ) -> None:
        self.element_info = FakeElementInfo(automation_id=automation_id, name=name)
        self.fail_invoke = fail_invoke
        self.fail_click_input = fail_click_input
        self.actions: list[str] = []

    def invoke(self) -> None:
        self.actions.append("invoke")
        if self.fail_invoke:
            raise RuntimeError("synthetic invoke failure")

    def select(self) -> None:
        self.actions.append("select")

    def click_input(self) -> None:
        self.actions.append("click_input")
        if self.fail_click_input:
            raise RuntimeError("synthetic click failure")


class FakeRoot:
    def __init__(
        self,
        *,
        list_items: list[FakeControl] | None = None,
        tabs: list[FakeControl] | None = None,
        buttons: list[FakeControl] | None = None,
    ) -> None:
        self.list_items = list_items or []
        self.tabs = tabs or []
        self.buttons = buttons or []
        self.restored = False
        self.focused = False

    def descendants(self, **criteria: str) -> list[FakeControl]:
        return {
            "ListItem": self.list_items,
            "TabItem": self.tabs,
            "Button": self.buttons,
        }[criteria["control_type"]]

    def restore(self) -> None:
        self.restored = True

    def set_focus(self) -> None:
        self.focused = True


class FakeProvider:
    def __init__(self, root: FakeRoot) -> None:
        self.window = SlackWindow(root, "slack.exe")
        self.calls = 0

    def find_window(self, process_names: tuple[str, ...]) -> SlackWindow:
        assert process_names == ("slack.exe",)
        self.calls += 1
        return self.window

    def is_alive(self, window: SlackWindow) -> bool:
        return True


class RevealingNavigator:
    def __init__(self, root: FakeRoot, target: FakeControl | None) -> None:
        self.root = root
        self.target = target
        self.calls = 0

    def open_activity(self, window: SlackWindow) -> None:
        assert window.native is self.root
        self.calls += 1
        if self.target is not None:
            self.root.list_items.append(self.target)


def test_captured_safe_destination_takes_precedence_over_uia() -> None:
    provider = FakeProvider(FakeRoot())
    launched: list[str] = []
    opener = PywinautoSlackEventOpener(
        provider,
        ("slack.exe",),
        destination_launcher=launched.append,
    )
    event = _event(
        source="slack.desktop.uia",
        category=EventCategory.DIRECT_MENTION,
        external_key="at_user-C123-1",
        metadata={"slack_destination": "slack://channel?team=T123&id=C123"},
    )

    result = opener.open(event)

    assert result is SlackOpenResult.EXACT_EVENT
    assert launched == ["slack://channel?team=T123&id=C123"]
    assert provider.calls == 0


def test_direct_mention_opens_exact_list_item_and_falls_back_between_patterns() -> None:
    target = FakeControl(automation_id="at_user-C123-1", fail_click_input=True)
    root = FakeRoot(
        list_items=[
            FakeControl(automation_id="at_user-C123-other"),
            target,
        ]
    )
    provider = FakeProvider(root)
    launched: list[str] = []
    opener = PywinautoSlackEventOpener(
        provider,
        ("slack.exe",),
        destination_launcher=launched.append,
    )

    result = opener.open(
        _event(
            source="slack.desktop.uia",
            category=EventCategory.DIRECT_MENTION,
            external_key="at_user-C123-1",
        )
    )

    assert result is SlackOpenResult.EXACT_EVENT
    assert target.actions == ["click_input", "invoke"]
    assert root.restored and root.focused
    assert launched == []


def test_direct_mention_navigates_only_on_explicit_open_then_retries_exact_item() -> None:
    target = FakeControl(automation_id="at_user-C123-1")
    root = FakeRoot()
    navigator = RevealingNavigator(root, target)
    opener = PywinautoSlackEventOpener(
        FakeProvider(root),
        ("slack.exe",),
        activity_navigator=navigator,
        destination_launcher=lambda _destination: None,
    )

    assert navigator.calls == 0
    result = opener.open(
        _event(
            source="slack.desktop.uia",
            category=EventCategory.DIRECT_MENTION,
            external_key="at_user-C123-1",
        )
    )

    assert result is SlackOpenResult.EXACT_EVENT
    assert navigator.calls == 1
    assert target.actions == ["click_input"]


def test_direct_mention_reports_activity_when_virtualized_item_is_not_found() -> None:
    root = FakeRoot()
    navigator = RevealingNavigator(root, None)
    launched: list[str] = []
    opener = PywinautoSlackEventOpener(
        FakeProvider(root),
        ("slack.exe",),
        activity_navigator=navigator,
        destination_launcher=launched.append,
    )

    result = opener.open(
        _event(
            source="slack.desktop.uia",
            category=EventCategory.DIRECT_MENTION,
            external_key="at_user-C123-stale",
        )
    )

    assert result is SlackOpenResult.ACTIVITY
    assert navigator.calls == 1
    assert launched == []


def test_direct_message_opens_unique_actor_conversation_without_typing_search() -> None:
    dm_tab = FakeControl(automation_id="dms")
    conversation = FakeControl(name="  Slackbot — conversa direta  ")
    root = FakeRoot(
        tabs=[dm_tab],
        buttons=[
            FakeControl(name="Outra Pessoa"),
            conversation,
        ],
    )
    waits: list[float] = []
    launched: list[str] = []
    opener = PywinautoSlackEventOpener(
        FakeProvider(root),
        ("slack.exe",),
        destination_launcher=launched.append,
        settle_seconds=0.25,
        sleeper=waits.append,
    )

    result = opener.open(
        _event(
            source="windows.user_notification_listener.slack",
            category=EventCategory.DIRECT_MESSAGE,
            actor="slackBOT",
        )
    )

    assert result is SlackOpenResult.CONVERSATION
    assert dm_tab.actions == ["click_input"]
    assert conversation.actions == ["click_input"]
    assert root.restored and root.focused
    assert waits == [0.25]
    assert launched == []


def test_ambiguous_direct_message_uses_signaled_generic_fallback() -> None:
    root = FakeRoot(
        tabs=[FakeControl(automation_id="dms")],
        buttons=[
            FakeControl(name="Ana — conversa"),
            FakeControl(name="Ana (externa) — conversa"),
        ],
    )
    launched: list[str] = []
    opener = PywinautoSlackEventOpener(
        FakeProvider(root),
        ("slack.exe",),
        destination_launcher=launched.append,
        settle_seconds=0,
    )

    result = opener.open(
        _event(
            source="windows.user_notification_listener.slack",
            category=EventCategory.DIRECT_MESSAGE,
            actor="Ana",
        )
    )

    assert result is SlackOpenResult.GENERIC
    assert launched == ["slack://open"]
    assert all(not button.actions for button in root.buttons)


def test_missing_dm_actor_uses_generic_fallback_without_uia_navigation() -> None:
    provider = FakeProvider(FakeRoot())
    launched: list[str] = []
    opener = PywinautoSlackEventOpener(
        provider,
        ("slack.exe",),
        destination_launcher=launched.append,
    )

    result = opener.open(
        _event(
            source="windows.user_notification_listener.slack",
            category=EventCategory.DIRECT_MESSAGE,
        )
    )

    assert result is SlackOpenResult.GENERIC
    assert launched == ["slack://open"]
    assert provider.calls == 0


def test_lock_contention_falls_back_without_waiting_forever(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class UnavailableLock:
        def acquire(self, *, timeout: float) -> bool:
            assert timeout == 0.1
            return False

        def release(self) -> None:
            raise AssertionError("an unacquired lock must not be released")

    launched: list[str] = []
    provider = FakeProvider(FakeRoot())
    opener = PywinautoSlackEventOpener(
        provider,
        ("slack.exe",),
        destination_launcher=launched.append,
        lock_timeout_seconds=0.1,
    )
    monkeypatch.setattr(
        event_opener_module,
        "SLACK_UI_AUTOMATION_LOCK",
        UnavailableLock(),
    )

    result = opener.open(
        _event(
            source="windows.user_notification_listener.slack",
            category=EventCategory.DIRECT_MESSAGE,
            actor="Alice",
        )
    )

    assert result is SlackOpenResult.GENERIC
    assert launched == ["slack://open"]
    assert provider.calls == 0


def test_lock_timeout_must_not_be_negative() -> None:
    with pytest.raises(ValueError, match="lock_timeout_seconds"):
        PywinautoSlackEventOpener(
            FakeProvider(FakeRoot()),
            ("slack.exe",),
            lock_timeout_seconds=-0.1,
        )


def _event(
    *,
    source: str,
    category: EventCategory,
    external_key: str | None = None,
    actor: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> OperationalEvent:
    return OperationalEvent(
        id="event-1",
        source=source,
        category=category,
        priority=EventPriority.HIGH,
        observed_at=datetime(2026, 7, 23, 12, tzinfo=UTC),
        deduplication_key="dedupe-1",
        classifier_version="test-v1",
        external_key=external_key,
        actor=actor,
        metadata=metadata or {},
    )
