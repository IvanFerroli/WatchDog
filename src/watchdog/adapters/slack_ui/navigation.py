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
        settle_seconds: float = 1.0,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        if not automation_id.strip():
            raise ValueError("automation_id must not be empty")
        if settle_seconds < 0:
            raise ValueError("settle_seconds must not be negative")
        self.automation_id = automation_id.strip()
        self._settle_seconds = settle_seconds
        self._sleeper = sleeper

    def open_activity(self, window: SlackWindow) -> None:
        try:
            target = window.native.child_window(
                auto_id=self.automation_id,
                control_type="TabItem",
            )
            if not target.exists(timeout=1):
                raise SlackAdapterError(
                    AdapterErrorCode.ACTIVITY_NOT_FOUND,
                    "Slack Activity navigation item was not found",
                )
            control = target.wrapper_object() if hasattr(target, "wrapper_object") else target
            if hasattr(control, "select"):
                control.select()
            elif hasattr(control, "click_input"):
                control.click_input()
            else:
                raise SlackAdapterError(
                    AdapterErrorCode.ACTIVITY_NOT_FOUND,
                    "Slack Activity navigation item could not be selected",
                )
            if self._settle_seconds:
                self._sleeper(self._settle_seconds)
        except SlackAdapterError:
            raise
        except Exception as exc:
            raise SlackAdapterError(
                AdapterErrorCode.ACTIVITY_NOT_FOUND,
                "Slack Activity navigation failed",
            ) from exc
