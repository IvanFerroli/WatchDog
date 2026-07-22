"""Platform-neutral event contracts used by the Watchdog core."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

SCHEMA_VERSION = 1


class EventCategory(StrEnum):
    DIRECT_MENTION = "DIRECT_MENTION"
    GROUP_MENTION = "GROUP_MENTION"
    DIRECT_MESSAGE = "DIRECT_MESSAGE"
    THREAD_REPLY = "THREAD_REPLY"
    REACTION = "REACTION"
    UNKNOWN = "UNKNOWN"


class EventPriority(StrEnum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"


class EventStatus(StrEnum):
    PROCESSED = "PROCESSED"
    ALERTED = "ALERTED"
    IGNORED = "IGNORED"
    FAILED = "FAILED"


class HealthState(StrEnum):
    STARTING = "STARTING"
    MONITORING = "MONITORING"
    SLACK_NOT_RUNNING = "SLACK_NOT_RUNNING"
    SLACK_NOT_ACCESSIBLE = "SLACK_NOT_ACCESSIBLE"
    ACTIVITY_NOT_FOUND = "ACTIVITY_NOT_FOUND"
    DEGRADED = "DEGRADED"
    PAUSED = "PAUSED"
    ERROR = "ERROR"


def _utc_datetime(value: datetime, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class ObservedEvent:
    """Data observed by an adapter, before semantic classification.

    Adapter-specific values are intentionally optional because availability varies
    with the Slack accessibility tree and window state.
    """

    source: str
    observed_at: datetime
    external_key: str | None = None
    raw_type: str | None = None
    title: str | None = None
    sender: str | None = None
    channel: str | None = None
    body: str | None = None
    occurred_at: datetime | None = None
    raw_metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must not be empty")
        object.__setattr__(self, "source", self.source.strip())
        object.__setattr__(self, "observed_at", _utc_datetime(self.observed_at, "observed_at"))
        if self.occurred_at is not None:
            object.__setattr__(self, "occurred_at", _utc_datetime(self.occurred_at, "occurred_at"))
        object.__setattr__(self, "raw_metadata", dict(self.raw_metadata))


@dataclass(frozen=True, slots=True)
class OperationalEvent:
    id: str
    source: str
    category: EventCategory
    priority: EventPriority
    observed_at: datetime
    deduplication_key: str
    classifier_version: str
    title: str | None = None
    body: str | None = None
    actor: str | None = None
    location: str | None = None
    occurred_at: datetime | None = None
    external_key: str | None = None
    raw_fingerprint: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in ("id", "source", "deduplication_key", "classifier_version"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must not be empty")
        if isinstance(self.category, str):
            object.__setattr__(self, "category", EventCategory(self.category))
        if isinstance(self.priority, str):
            object.__setattr__(self, "priority", EventPriority(self.priority))
        if (
            not isinstance(self.schema_version, int)
            or isinstance(self.schema_version, bool)
            or self.schema_version < 1
        ):
            raise ValueError("schema_version must be a positive integer")
        object.__setattr__(self, "observed_at", _utc_datetime(self.observed_at, "observed_at"))
        if self.occurred_at is not None:
            object.__setattr__(self, "occurred_at", _utc_datetime(self.occurred_at, "occurred_at"))
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True, slots=True)
class AlertDecision:
    alert: bool
    reason: str


@dataclass(frozen=True, slots=True)
class Classification:
    category: EventCategory
    classifier_version: str
    reason: str


@dataclass(frozen=True, slots=True)
class OperationalState:
    last_successful_scan_at: datetime | None = None
    last_error_at: datetime | None = None
    last_error_code: str | None = None
    slack_version: str | None = None
    adapter_version: str | None = None
    schema_version: int = SCHEMA_VERSION
