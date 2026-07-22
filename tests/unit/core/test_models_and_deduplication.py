from datetime import UTC, datetime

import pytest

from watchdog.core.deduplication import DeduplicationService
from watchdog.core.models import Classification, EventCategory, ObservedEvent
from watchdog.core.normalizer import EventNormalizer
from watchdog.persistence import SQLiteEventStore

NOW = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)


def observed(**changes: object) -> ObservedEvent:
    values = {
        "source": "slack",
        "external_key": "activity-42",
        "raw_type": " Menção na conversa do canal ",
        "sender": " Alice ",
        "channel": " suporte ",
        "body": " Preciso   de ajuda ",
        "observed_at": NOW,
    }
    values.update(changes)
    return ObservedEvent(**values)  # type: ignore[arg-type]


def test_normalizer_removes_only_presentation_noise() -> None:
    result = EventNormalizer().normalize(observed())
    assert result.body == "Preciso de ajuda"
    assert result.sender == "Alice"
    assert result.external_key == "activity-42"


def test_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        observed(observed_at=datetime(2026, 7, 22))


def test_dedup_is_stable_for_whitespace_and_persists_across_restart(tmp_path) -> None:
    path = tmp_path / "events.db"
    classification = Classification(EventCategory.DIRECT_MENTION, "rules-v1", "fixture.direct")
    first_observation = observed(external_key=None)
    same_visual_item = observed(external_key=None, body="Preciso de ajuda")

    with SQLiteEventStore(path) as store:
        service = DeduplicationService(store)
        assert service.claim(first_observation, classification).is_new
        assert not service.claim(same_visual_item, classification).is_new

    with SQLiteEventStore(path) as restarted_store:
        assert (
            not DeduplicationService(restarted_store)
            .claim(first_observation, classification)
            .is_new
        )


def test_nearby_distinct_events_do_not_collide(tmp_path) -> None:
    classification = Classification(EventCategory.DIRECT_MENTION, "rules-v1", "fixture.direct")
    with SQLiteEventStore(tmp_path / "events.db") as store:
        service = DeduplicationService(store)
        assert service.claim(observed(external_key=None, body="primeiro"), classification).is_new
        assert service.claim(observed(external_key=None, body="segundo"), classification).is_new
