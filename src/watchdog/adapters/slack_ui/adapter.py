"""EventAdapter composition for Slack window lifecycle and Activity reading."""

from __future__ import annotations

from typing import Protocol

from watchdog.core.models import ObservedEvent

from .errors import AdapterErrorCode, SlackAdapterError
from .provider import SlackWindow, SlackWindowLifecycle


class ActivityReader(Protocol):
    adapter_version: str

    def read(self, window: SlackWindow) -> list[ObservedEvent]: ...


class ActivityNavigator(Protocol):
    def open_activity(self, window: SlackWindow) -> None: ...


class SlackUIAdapter:
    def __init__(
        self,
        lifecycle: SlackWindowLifecycle,
        reader: ActivityReader,
        navigator: ActivityNavigator | None = None,
    ) -> None:
        self._lifecycle = lifecycle
        self._reader = reader
        self._navigator = navigator
        self._navigation_attempted = False
        self.adapter_version = reader.adapter_version

    def observe(self) -> list[ObservedEvent]:
        window = self._lifecycle.current()
        try:
            events = self._reader.read(window)
            # Never steal focus later just because the user intentionally left
            # Activity after a successful startup scan.
            self._navigation_attempted = True
            return events
        except SlackAdapterError as exc:
            navigator = self._navigator
            if (
                exc.code is AdapterErrorCode.ACTIVITY_NOT_FOUND
                and navigator is not None
                and not self._navigation_attempted
            ):
                self._navigation_attempted = True
                return self._restore_activity_and_retry(window, navigator)
            self._handle_failure(exc)
            raise

    def _restore_activity_and_retry(
        self,
        window: SlackWindow,
        navigator: ActivityNavigator,
    ) -> list[ObservedEvent]:
        try:
            navigator.open_activity(window)
            return self._reader.read(window)
        except SlackAdapterError as exc:
            self._handle_failure(exc)
            raise
        except Exception as exc:
            error = SlackAdapterError(
                AdapterErrorCode.READ_FAILED,
                "Slack Activity recovery failed",
            )
            self._handle_failure(error)
            raise error from exc

    def _handle_failure(self, error: SlackAdapterError) -> None:
        if error.code in {
            AdapterErrorCode.WINDOW_LOST,
            AdapterErrorCode.SLACK_NOT_ACCESSIBLE,
            AdapterErrorCode.READ_FAILED,
        }:
            self._lifecycle.invalidate()
