from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

from watchdog.core.models import (
    EventCategory,
    EventPriority,
    EventStatus,
    OperationalEvent,
    OperationalState,
)
from watchdog.persistence import DATABASE_SCHEMA_VERSION, SQLiteEventStore

NOW = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)


def event(
    key: str,
    *,
    category: EventCategory = EventCategory.DIRECT_MENTION,
    observed_at: datetime = NOW,
    body: str = "preview",
) -> OperationalEvent:
    return OperationalEvent(
        id=f"id-{key}",
        source="slack",
        category=category,
        priority=EventPriority.NORMAL,
        observed_at=observed_at,
        deduplication_key=key,
        classifier_version="rules-v1",
        body=body,
        raw_fingerprint=f"raw-{key}",
        metadata={"unsafe": "secret"},
    )


def test_migration_crud_state_config_and_preview_policy(tmp_path) -> None:
    path = tmp_path / "events.db"
    with SQLiteEventStore(path, preview_length=12) as store:
        assert store.schema_version == DATABASE_SCHEMA_VERSION
        assert store.claim(event("one", body="texto corporativo muito comprido"))
        stored = store.get_event("one")
        assert stored is not None
        assert stored.body == "texto corpor"
        assert stored.metadata == {}
        assert stored.status is EventStatus.PROCESSED
        assert stored.first_seen_at == NOW
        assert stored.last_seen_at == NOW
        assert stored.alerted_at is None
        state = OperationalState(
            last_successful_scan_at=NOW, slack_version="1", adapter_version="2"
        )
        store.save_state(state)
        assert store.load_state() == state
        store.save_config({"watchdog": {"enabled": True}})
        assert store.load_config() == {"watchdog": {"enabled": True}}

    with SQLiteEventStore(path) as restarted:
        assert restarted.schema_version == DATABASE_SCHEMA_VERSION
        assert restarted.get_event("one") is not None


def test_atomic_claim_allows_one_winner(tmp_path) -> None:
    with SQLiteEventStore(tmp_path / "events.db") as store:
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(lambda _: store.claim(event("same")), range(20)))
        assert results.count(True) == 1


def test_retention_keeps_only_items_inside_category_policy(tmp_path) -> None:
    with SQLiteEventStore(tmp_path / "events.db") as store:
        store.claim(event("direct-old", observed_at=NOW - timedelta(days=31)))
        store.claim(event("direct-recent", observed_at=NOW - timedelta(days=29)))
        store.claim(
            event(
                "ignored-old", category=EventCategory.UNKNOWN, observed_at=NOW - timedelta(days=8)
            )
        )
        store.claim(
            event(
                "ignored-recent",
                category=EventCategory.GROUP_MENTION,
                observed_at=NOW - timedelta(days=6),
            )
        )
        assert store.apply_retention(NOW) == 2
        assert {item.deduplication_key for item in store.list_events()} == {
            "direct-recent",
            "ignored-recent",
        }


def test_history_can_be_hidden_without_disabling_dedup(tmp_path) -> None:
    stored_event = event("private")
    with SQLiteEventStore(tmp_path / "hidden.db", history_enabled=False) as store:
        assert store.claim(stored_event)
        assert store.get_event(stored_event.deduplication_key) is not None
        assert store.list_events() == []
