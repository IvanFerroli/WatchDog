"""Structured, content-free Slack adapter failures."""

from __future__ import annotations

from enum import StrEnum


class AdapterErrorCode(StrEnum):
    UNSUPPORTED_PLATFORM = "UNSUPPORTED_PLATFORM"
    STRATEGY_NOT_CONFIGURED = "STRATEGY_NOT_CONFIGURED"
    SLACK_NOT_RUNNING = "SLACK_NOT_RUNNING"
    SLACK_NOT_ACCESSIBLE = "SLACK_NOT_ACCESSIBLE"
    WINDOW_LOST = "WINDOW_LOST"
    ACTIVITY_NOT_FOUND = "ACTIVITY_NOT_FOUND"
    STRUCTURE_CHANGED = "STRUCTURE_CHANGED"
    READ_FAILED = "READ_FAILED"


class SlackAdapterError(RuntimeError):
    """Failure safe to expose in health/logs without Slack content."""

    def __init__(
        self,
        code: AdapterErrorCode,
        message: str,
        *,
        retriable: bool = True,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.retriable = retriable
