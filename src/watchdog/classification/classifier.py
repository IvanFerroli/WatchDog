"""Deterministic classification rules for Slack activity labels."""

from __future__ import annotations

from collections.abc import Iterable

from watchdog.core.models import Classification, EventCategory, ObservedEvent
from watchdog.core.normalizer import canonical_text

CLASSIFIER_VERSION = "rules-v1"


class EventClassifier:
    def __init__(
        self,
        *,
        direct_mention_labels: Iterable[str],
        group_mention_labels: Iterable[str],
        classifier_version: str = CLASSIFIER_VERSION,
    ) -> None:
        self._direct = _canonical_labels(direct_mention_labels, "direct_mention_labels")
        self._group = _canonical_labels(group_mention_labels, "group_mention_labels")
        if self._direct & self._group:
            raise ValueError("direct and group mention labels must not overlap")
        if not classifier_version.strip():
            raise ValueError("classifier_version must not be empty")
        self.classifier_version = classifier_version.strip()

    def classify(self, event: ObservedEvent) -> Classification:
        candidates = {canonical_text(event.raw_type), canonical_text(event.title)} - {""}
        if candidates & self._group:
            return Classification(
                EventCategory.GROUP_MENTION, self.classifier_version, "label.group_mention"
            )
        if candidates & self._direct:
            return Classification(
                EventCategory.DIRECT_MENTION, self.classifier_version, "label.direct_mention"
            )
        return Classification(EventCategory.UNKNOWN, self.classifier_version, "label.unrecognized")


def _canonical_labels(values: Iterable[str], name: str) -> frozenset[str]:
    labels = frozenset(canonical_text(value) for value in values if canonical_text(value))
    if not labels:
        raise ValueError(f"{name} must not be empty")
    return labels
