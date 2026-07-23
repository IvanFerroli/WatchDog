"""User-triggered navigation from persisted events to Slack."""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from enum import StrEnum
from time import sleep
from typing import Any, Protocol

from watchdog.core.models import EventCategory, OperationalEvent
from watchdog.core.normalizer import canonical_text
from watchdog.notifications.windows import DEFAULT_SLACK_DESTINATION, notification_destination

from .errors import AdapterErrorCode, SlackAdapterError
from .provider import SlackWindow, WindowProvider

_SLACK_UI_SOURCE = "slack.desktop.uia"
_DM_SOURCE = "windows.user_notification_listener.slack"
_DM_TAB_AUTOMATION_ID = "dms"
_MAX_EXTERNAL_KEY_LENGTH = 512
_MAX_ACTOR_LENGTH = 120


class ActivityNavigator(Protocol):
    def open_activity(self, window: SlackWindow) -> None: ...


class SlackOpenResult(StrEnum):
    EXACT_EVENT = "EXACT_EVENT"
    CONVERSATION = "CONVERSATION"
    ACTIVITY = "ACTIVITY"
    GENERIC = "GENERIC"


class PywinautoSlackEventOpener:
    """Open a persisted event only after an explicit panel action."""

    def __init__(
        self,
        provider: WindowProvider,
        process_names: tuple[str, ...],
        *,
        activity_navigator: ActivityNavigator | None = None,
        destination_launcher: Callable[[str], None] | None = None,
        settle_seconds: float = 0.25,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        if not process_names:
            raise ValueError("process_names must not be empty")
        if settle_seconds < 0:
            raise ValueError("settle_seconds must not be negative")
        self._provider = provider
        self._process_names = tuple(process_names)
        self._activity_navigator = activity_navigator
        self._destination_launcher = destination_launcher or _launch_destination
        self._settle_seconds = settle_seconds
        self._sleeper = sleeper

    def open(self, event: OperationalEvent) -> SlackOpenResult:
        destination = notification_destination(event)
        if destination != DEFAULT_SLACK_DESTINATION:
            self._destination_launcher(destination)
            return SlackOpenResult.EXACT_EVENT

        try:
            if (
                event.source == _SLACK_UI_SOURCE
                and event.category is EventCategory.DIRECT_MENTION
                and _usable_external_key(event.external_key)
            ):
                return self._open_direct_mention(event.external_key or "")
            if (
                event.source == _DM_SOURCE
                and event.category is EventCategory.DIRECT_MESSAGE
                and _usable_actor(event.actor)
            ):
                result = self._open_direct_message(event.actor or "")
                if result is not SlackOpenResult.GENERIC:
                    return result
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            # A stale/virtualized UIA target must not make the panel callback fail.
            # The explicit generic fallback still opens or focuses Slack.
            pass

        self._destination_launcher(DEFAULT_SLACK_DESTINATION)
        return SlackOpenResult.GENERIC

    def _open_direct_mention(self, external_key: str) -> SlackOpenResult:
        window = self._provider.find_window(self._process_names)
        target = _find_by_automation_id(window, "ListItem", external_key)
        if target is None and self._activity_navigator is not None:
            self._activity_navigator.open_activity(window)
            target = _find_by_automation_id(window, "ListItem", external_key)
        if target is None:
            return SlackOpenResult.ACTIVITY
        _restore_and_focus(window)
        _activate(target, methods=("click_input", "invoke", "select"))
        return SlackOpenResult.EXACT_EVENT

    def _open_direct_message(self, actor: str) -> SlackOpenResult:
        window = self._provider.find_window(self._process_names)
        dm_tab = _find_by_automation_id(window, "TabItem", _DM_TAB_AUTOMATION_ID)
        if dm_tab is None:
            raise SlackAdapterError(
                AdapterErrorCode.ACTIVITY_NOT_FOUND,
                "Slack direct messages tab was not found",
            )
        _restore_and_focus(window)
        _activate(dm_tab, methods=("click_input", "invoke", "select"))
        if self._settle_seconds:
            self._sleeper(self._settle_seconds)

        matches = [
            control
            for control in window.native.descendants(control_type="Button")
            if _name_contains_actor(_control_name(control), actor)
        ]
        if len(matches) != 1:
            return SlackOpenResult.GENERIC
        _activate(matches[0], methods=("click_input", "invoke", "select"))
        return SlackOpenResult.CONVERSATION


def _find_by_automation_id(
    window: SlackWindow,
    control_type: str,
    automation_id: str,
) -> Any | None:
    for control in window.native.descendants(control_type=control_type):
        if _automation_id(control) == automation_id:
            return control
    return None


def _restore_and_focus(window: SlackWindow) -> None:
    restore = getattr(window.native, "restore", None)
    if callable(restore):
        restore()
    focus = getattr(window.native, "set_focus", None)
    if callable(focus):
        focus()


def _activate(control: Any, *, methods: tuple[str, ...]) -> None:
    last_error: Exception | None = None
    for method_name in methods:
        method = getattr(control, method_name, None)
        if not callable(method):
            continue
        try:
            method()
            return
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as exc:
            last_error = exc
    raise SlackAdapterError(
        AdapterErrorCode.ACTIVITY_NOT_FOUND,
        "Slack target could not be activated",
    ) from last_error


def _automation_id(control: Any) -> str:
    element_info = getattr(control, "element_info", None)
    return str(getattr(element_info, "automation_id", "") or "").strip()


def _control_name(control: Any) -> str:
    element_info = getattr(control, "element_info", None)
    value = getattr(element_info, "name", "") or ""
    if not value:
        window_text = getattr(control, "window_text", None)
        value = window_text() if callable(window_text) else ""
    return str(value)


def _usable_external_key(value: str | None) -> bool:
    return bool(value and 0 < len(value) <= _MAX_EXTERNAL_KEY_LENGTH)


def _usable_actor(value: str | None) -> bool:
    actor = canonical_text(value)
    return 2 <= len(actor) <= _MAX_ACTOR_LENGTH


def _name_contains_actor(name: str, actor: str) -> bool:
    normalized_name = canonical_text(name)[:500]
    normalized_actor = canonical_text(actor)
    if not _usable_actor(normalized_actor):
        return False
    return (
        re.search(
            rf"(?<!\w){re.escape(normalized_actor)}(?!\w)",
            normalized_name,
        )
        is not None
    )


def _launch_destination(destination: str) -> None:
    startfile = getattr(os, "startfile", None)
    if not callable(startfile):
        raise OSError("Slack links can only be opened by the Windows desktop application")
    startfile(destination)
