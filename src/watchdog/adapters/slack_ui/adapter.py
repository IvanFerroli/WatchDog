"""EventAdapter composition for Slack window lifecycle and Activity reading."""

from __future__ import annotations

from typing import Protocol

from watchdog.core.models import ObservedEvent

from .errors import AdapterErrorCode, SlackAdapterError
from .provider import SlackWindow, SlackWindowLifecycle


class ActivityReader(Protocol):
    adapter_version: str

    def read(self, window: SlackWindow) -> list[ObservedEvent]: ...


class SlackUIAdapter:
    def __init__(self, lifecycle: SlackWindowLifecycle, reader: ActivityReader) -> None:
        self._lifecycle = lifecycle
        self._reader = reader
        self.adapter_version = reader.adapter_version

    def observe(self) -> list[ObservedEvent]:
        window = self._lifecycle.current()
        try:
            return self._reader.read(window)
        except SlackAdapterError as exc:
            if exc.code in {
                AdapterErrorCode.WINDOW_LOST,
                AdapterErrorCode.SLACK_NOT_ACCESSIBLE,
                AdapterErrorCode.READ_FAILED,
            }:
                self._lifecycle.invalidate()
            raise
