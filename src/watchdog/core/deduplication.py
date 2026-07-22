"""Versioned identity generation and atomic processing reservation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

from .models import Classification, EventCategory, EventPriority, ObservedEvent, OperationalEvent
from .normalizer import canonical_text, normalize_text

DEDUPLICATION_VERSION = "v1"
FINGERPRINT_VERSION = "v1"
_ROUTING_METADATA_KEYS = ("slack_destination", "slack_activity_destination")


class AtomicEventClaimer(Protocol):
    def claim(self, event: OperationalEvent) -> bool: ...


@dataclass(frozen=True, slots=True)
class DeduplicationResult:
    event: OperationalEvent
    is_new: bool


class DeduplicationService:
    def __init__(self, store: AtomicEventClaimer, *, time_bucket_seconds: int = 60) -> None:
        if (
            not isinstance(time_bucket_seconds, int)
            or isinstance(time_bucket_seconds, bool)
            or time_bucket_seconds <= 0
        ):
            raise ValueError("time_bucket_seconds must be a positive integer")
        self._store = store
        self._bucket_seconds = time_bucket_seconds

    def raw_fingerprint(self, observed: ObservedEvent) -> str:
        # observed_at is the scanner timestamp and changes on every poll. Using it
        # here would re-enable a still-visible card at each bucket boundary.
        occurred_bucket = (
            int(observed.occurred_at.timestamp()) // self._bucket_seconds
            if observed.occurred_at is not None
            else None
        )
        payload = {
            "source": canonical_text(observed.source),
            "external_key": canonical_text(observed.external_key),
            "raw_type": canonical_text(observed.raw_type),
            "title": canonical_text(observed.title),
            "sender": canonical_text(observed.sender),
            "channel": canonical_text(observed.channel),
            "body": canonical_text(observed.body),
            "occurred_bucket": occurred_bucket,
        }
        return f"fingerprint:{FINGERPRINT_VERSION}:{_digest(payload)}"

    def generate_key(self, observed: ObservedEvent) -> str:
        external_key = normalize_text(observed.external_key)
        identity = (
            {
                "source": canonical_text(observed.source),
                "external_key": canonical_text(external_key),
            }
            if external_key
            else {"raw_fingerprint": self.raw_fingerprint(observed)}
        )
        return f"dedup:{DEDUPLICATION_VERSION}:{_digest(identity)}"

    def build_event(
        self, observed: ObservedEvent, classification: Classification
    ) -> OperationalEvent:
        metadata = {"classification_reason": classification.reason}
        metadata.update(
            {
                key: value
                for key in _ROUTING_METADATA_KEYS
                if isinstance((value := observed.raw_metadata.get(key)), str) and value
            }
        )
        return OperationalEvent(
            id=str(uuid4()),
            source=observed.source,
            external_key=observed.external_key,
            category=classification.category,
            priority=EventPriority.HIGH
            if classification.category is EventCategory.DIRECT_MENTION
            else EventPriority.NORMAL,
            title=observed.title,
            body=observed.body,
            actor=observed.sender,
            location=observed.channel,
            occurred_at=observed.occurred_at,
            observed_at=observed.observed_at,
            deduplication_key=self.generate_key(observed),
            raw_fingerprint=self.raw_fingerprint(observed),
            metadata=metadata,
            classifier_version=classification.classifier_version,
        )

    def claim(self, observed: ObservedEvent, classification: Classification) -> DeduplicationResult:
        event = self.build_event(observed, classification)
        return DeduplicationResult(event, self._store.claim(event))


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()
