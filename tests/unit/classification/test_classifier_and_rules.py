from datetime import UTC, datetime

import pytest

from watchdog.classification import EventClassifier, NotificationRules
from watchdog.core.deduplication import DeduplicationService
from watchdog.core.models import EventCategory, ObservedEvent
from watchdog.persistence import SQLiteEventStore

NOW = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)


@pytest.fixture
def classifier() -> EventClassifier:
    return EventClassifier(
        direct_mention_labels=["Menção na conversa do canal", "Mention in channel"],
        group_mention_labels=["Menção ao grupo na conversa do canal", "Group mention in channel"],
    )


@pytest.mark.parametrize(
    ("label", "category", "alerts"),
    [
        ("  MENÇÃO   na conversa do canal ", EventCategory.DIRECT_MENTION, True),
        ("MD", EventCategory.DIRECT_MESSAGE, True),
        ("Group mention in channel", EventCategory.GROUP_MENTION, False),
        ("Uma reação foi adicionada", EventCategory.UNKNOWN, False),
    ],
)
def test_fixture_matrix(
    classifier: EventClassifier, label: str, category: EventCategory, alerts: bool
) -> None:
    observed = ObservedEvent(source="slack", raw_type=label, observed_at=NOW)
    classification = classifier.classify(observed)
    assert classification.category is category
    with SQLiteEventStore(":memory:") as store:
        result = DeduplicationService(store).claim(observed, classification)
        decision = NotificationRules().decide(result.event, is_new=result.is_new)
    assert decision.alert is alerts
    assert "Uma reação" not in decision.reason


def test_old_direct_mention_does_not_alert_twice(classifier: EventClassifier) -> None:
    observed = ObservedEvent(
        source="slack", external_key="stable", raw_type="Mention in channel", observed_at=NOW
    )
    classification = classifier.classify(observed)
    with SQLiteEventStore(":memory:") as store:
        service = DeduplicationService(store)
        first = service.claim(observed, classification)
        second = service.claim(observed, classification)
        assert NotificationRules().decide(first.event, is_new=first.is_new).alert
        assert not NotificationRules().decide(second.event, is_new=second.is_new).alert


def test_old_direct_message_does_not_alert_twice(classifier: EventClassifier) -> None:
    observed = ObservedEvent(
        source="slack", external_key="dm-stable", raw_type="MD", observed_at=NOW
    )
    classification = classifier.classify(observed)
    with SQLiteEventStore(":memory:") as store:
        service = DeduplicationService(store)
        first = service.claim(observed, classification)
        second = service.claim(observed, classification)
        first_decision = NotificationRules().decide(first.event, is_new=first.is_new)
        assert first_decision.alert
        assert first_decision.reason == "category.direct_message"
        assert not NotificationRules().decide(second.event, is_new=second.is_new).alert
