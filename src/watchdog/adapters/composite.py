"""Composition of independent event sources with observable partial fallback."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from watchdog.core.models import ObservedEvent
from watchdog.core.normalizer import canonical_text
from watchdog.core.ports import EventAdapter


@dataclass(frozen=True, slots=True)
class SourceFailure:
    source: str
    code: str


class CompositeEventAdapter:
    def __init__(self, **sources: EventAdapter) -> None:
        if not sources:
            raise ValueError("at least one event source is required")
        self._sources = tuple(sources.items())
        self.last_failures: tuple[SourceFailure, ...] = ()
        self.adapter_version = "+".join(
            str(getattr(adapter, "adapter_version", name)) for name, adapter in self._sources
        )
        self._logger = logging.getLogger("watchdog.composite_adapter")

    def observe(self) -> list[ObservedEvent]:
        events: list[ObservedEvent] = []
        failures: list[SourceFailure] = []
        first_error: Exception | None = None
        successful_sources = 0
        prior_source_signatures: set[tuple[str, str]] = set()
        for name, source in self._sources:
            try:
                source_events = list(source.observe())
                events.extend(
                    event
                    for event in source_events
                    if (signature := _message_signature(event)) is None
                    or signature not in prior_source_signatures
                )
                prior_source_signatures.update(
                    signature
                    for event in source_events
                    if (signature := _message_signature(event)) is not None
                )
                successful_sources += 1
            except Exception as exc:
                first_error = first_error or exc
                failures.append(SourceFailure(name, _error_code(exc)))
        self.last_failures = tuple(failures)
        if failures:
            self._logger.warning(
                "event_sources.partial_failure",
                extra={
                    "context": {
                        "failures": [
                            {"source": item.source, "code": item.code} for item in failures
                        ]
                    }
                },
            )
        if successful_sources == 0 and first_error is not None:
            raise first_error
        return events


def _error_code(error: Exception) -> str:
    code: Any = getattr(error, "code", None)
    value = getattr(code, "value", code)
    return str(value or type(error).__name__)


def _message_signature(event: ObservedEvent) -> tuple[str, str] | None:
    sender = canonical_text(event.sender)
    body = canonical_text(event.body)
    return (sender, body) if sender and body else None
