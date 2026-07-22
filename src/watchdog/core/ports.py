"""Replaceable boundaries for core infrastructure."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Protocol, runtime_checkable

from .models import ObservedEvent, OperationalEvent, OperationalState


@runtime_checkable
class EventAdapter(Protocol):
    def observe(self) -> Iterable[ObservedEvent]: ...


@runtime_checkable
class EventStore(Protocol):
    def claim(self, event: OperationalEvent) -> bool: ...
    def mark_alerted(self, deduplication_key: str, alerted_at: datetime) -> None: ...
    def get_event(self, deduplication_key: str) -> OperationalEvent | None: ...
    def list_events(self, *, limit: int = 100) -> list[OperationalEvent]: ...
    def save_state(self, state: OperationalState) -> None: ...
    def load_state(self) -> OperationalState: ...


@runtime_checkable
class Clock(Protocol):
    def now(self) -> datetime: ...


@runtime_checkable
class Notifier(Protocol):
    def notify(self, event: OperationalEvent) -> None: ...
