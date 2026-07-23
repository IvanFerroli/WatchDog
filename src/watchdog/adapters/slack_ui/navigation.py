"""Navigation helpers for restoring Slack's Activity view."""

from __future__ import annotations

from collections.abc import Callable
from time import sleep

from .errors import AdapterErrorCode, SlackAdapterError
from .provider import SlackWindow


class PywinautoActivityNavigator:
    """Select the validated Slack Activity tab through Windows UI Automation."""

    def __init__(
        self,
        automation_id: str = "activity-inbox",
        *,
        secondary_title: str | None = None,
        secondary_control_type: str = "Button",
        shortcut: str | None = None,
        shortcut_sender: Callable[[str], None] | None = None,
        settle_seconds: float = 1.0,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        if not automation_id.strip():
            raise ValueError("automation_id must not be empty")
        if settle_seconds < 0:
            raise ValueError("settle_seconds must not be negative")
        self.automation_id = automation_id.strip()
        self.secondary_title = secondary_title.strip() if secondary_title else None
        self.secondary_control_type = secondary_control_type
        self.shortcut = shortcut
        self._shortcut_sender = shortcut_sender
        self._settle_seconds = settle_seconds
        self._sleeper = sleeper

    def open_activity(self, window: SlackWindow) -> None:
        try:
            if self.shortcut:
                window.native.set_focus()
                self._sender()(self.shortcut)
                if self._settle_seconds:
                    self._sleeper(self._settle_seconds)
                if self.secondary_title:
                    self._open_secondary(window)
                return
            targets = [
                control
                for control in window.native.descendants(control_type="TabItem")
                if str(getattr(control.element_info, "automation_id", "") or "").strip()
                == self.automation_id
            ]
            if not targets:
                raise SlackAdapterError(
                    AdapterErrorCode.ACTIVITY_NOT_FOUND,
                    "Slack Activity navigation item was not found",
                )
            control = targets[0]
            # Slack exposes this as a generic UIA wrapper. A physical click is
            # the only operation validated to change the view, so the adapter
            # permits it only during its single startup recovery attempt.
            if hasattr(control, "click_input"):
                control.click_input()
            elif hasattr(control, "select"):
                control.select()
            else:
                raise SlackAdapterError(
                    AdapterErrorCode.ACTIVITY_NOT_FOUND,
                    "Slack Activity navigation item could not be selected",
                )
            if self._settle_seconds:
                self._sleeper(self._settle_seconds)
            if self.secondary_title:
                self._open_secondary(window)
        except SlackAdapterError:
            raise
        except Exception as exc:
            raise SlackAdapterError(
                AdapterErrorCode.ACTIVITY_NOT_FOUND,
                "Slack Activity navigation failed",
            ) from exc

    def _open_secondary(self, window: SlackWindow) -> None:
        controls = window.native.descendants(control_type=self.secondary_control_type)
        candidates = [
            control
            for control in controls
            if str(getattr(control.element_info, "name", "") or "").strip() == self.secondary_title
        ]
        if not candidates:
            raise SlackAdapterError(
                AdapterErrorCode.ACTIVITY_NOT_FOUND,
                "Slack Mentions navigation item was not found",
            )
        control = candidates[0]
        if hasattr(control, "select"):
            control.select()
        elif hasattr(control, "invoke"):
            control.invoke()
        elif hasattr(control, "click_input"):
            control.click_input()
        else:
            raise SlackAdapterError(
                AdapterErrorCode.ACTIVITY_NOT_FOUND,
                "Slack Mentions navigation item could not be selected",
            )
        if self._settle_seconds:
            self._sleeper(self._settle_seconds)

    def _sender(self) -> Callable[[str], None]:
        if self._shortcut_sender is not None:
            return self._shortcut_sender
        from pywinauto.keyboard import send_keys

        return send_keys
