"""Normalization that removes presentation noise without erasing identity fields."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import replace

from .models import ObservedEvent

_SPACE = re.compile(r"\s+")


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = _SPACE.sub(" ", unicodedata.normalize("NFKC", value)).strip()
    return normalized or None


def canonical_text(value: str | None) -> str:
    return (normalize_text(value) or "").casefold()


class EventNormalizer:
    def normalize(self, event: ObservedEvent) -> ObservedEvent:
        return replace(
            event,
            external_key=normalize_text(event.external_key),
            raw_type=normalize_text(event.raw_type),
            title=normalize_text(event.title),
            sender=normalize_text(event.sender),
            channel=normalize_text(event.channel),
            body=normalize_text(event.body),
        )
