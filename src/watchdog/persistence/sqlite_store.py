"""Versioned SQLite store for history, state and atomic idempotency."""

from __future__ import annotations

import json
import sqlite3
import threading
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from watchdog.core.models import (
    EventCategory,
    EventPriority,
    EventStatus,
    OperationalEvent,
    OperationalState,
)

DATABASE_SCHEMA_VERSION = 1


class UnsupportedSchemaError(RuntimeError):
    pass


class SQLiteEventStore:
    def __init__(
        self,
        path: str | Path,
        *,
        preview_length: int = 240,
        history_enabled: bool = True,
        metadata_allowlist: Iterable[str] = (
            "classification_reason",
            "slack_destination",
            "slack_activity_destination",
        ),
    ) -> None:
        if (
            not isinstance(preview_length, int)
            or isinstance(preview_length, bool)
            or preview_length <= 0
        ):
            raise ValueError("preview_length must be a positive integer")
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).expanduser().parent.mkdir(parents=True, exist_ok=True)
        self._preview_length = preview_length
        self._history_enabled = history_enabled
        self._metadata_allowlist = frozenset(metadata_allowlist)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(
            self.path, timeout=10, check_same_thread=False, isolation_level=None
        )
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA busy_timeout = 10000")
        if self.path != ":memory:":
            self._connection.execute("PRAGMA journal_mode = WAL")
        self.migrate()

    @property
    def schema_version(self) -> int:
        with self._lock:
            return int(self._connection.execute("PRAGMA user_version").fetchone()[0])

    def migrate(self) -> None:
        with self._transaction() as connection:
            version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            if version > DATABASE_SCHEMA_VERSION:
                raise UnsupportedSchemaError(
                    f"database schema {version} is newer than supported {DATABASE_SCHEMA_VERSION}"
                )
            if version < 1:
                for statement in _MIGRATION_1:
                    connection.execute(statement)
                connection.execute("PRAGMA user_version = 1")

    def claim(self, event: OperationalEvent) -> bool:
        """Atomically reserve an event; only the successful caller may process it."""
        now = _iso(event.observed_at)
        status = (
            EventStatus.PROCESSED
            if event.category is EventCategory.DIRECT_MENTION
            else EventStatus.IGNORED
        )
        with self._transaction() as connection:
            cursor = connection.execute(
                """INSERT INTO events (
                    id, source, external_key, classification, sender, channel,
                    content_preview, title_preview, occurred_at, observed_at,
                    first_seen_at, last_seen_at, alerted_at, status,
                    classifier_version, deduplication_key, raw_fingerprint,
                    metadata_json, event_schema_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(deduplication_key) DO NOTHING""",
                self._event_values(event, status, now),
            )
            inserted = cursor.rowcount == 1
            if not inserted:
                connection.execute(
                    "UPDATE events SET last_seen_at = ? WHERE deduplication_key = ?",
                    (now, event.deduplication_key),
                )
            return inserted

    def mark_alerted(self, deduplication_key: str, alerted_at: datetime) -> None:
        with self._transaction() as connection:
            cursor = connection.execute(
                "UPDATE events SET alerted_at = ?, status = ? WHERE deduplication_key = ?",
                (_iso(alerted_at), EventStatus.ALERTED.value, deduplication_key),
            )
            if cursor.rowcount != 1:
                raise KeyError(deduplication_key)

    def is_alerted(self, deduplication_key: str) -> bool:
        with self._lock:
            row = self._connection.execute(
                "SELECT alerted_at FROM events WHERE deduplication_key = ?",
                (deduplication_key,),
            ).fetchone()
        return bool(row and row["alerted_at"])

    def get_event(self, deduplication_key: str) -> OperationalEvent | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM events WHERE deduplication_key = ?", (deduplication_key,)
            ).fetchone()
        return _row_to_event(row) if row else None

    def list_events(self, *, limit: int = 100) -> list[OperationalEvent]:
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        if not self._history_enabled:
            return []
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM events ORDER BY observed_at DESC, id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [_row_to_event(row) for row in rows]

    def save_state(self, state: OperationalState) -> None:
        with self._transaction() as connection:
            connection.execute(
                """INSERT INTO operational_state (
                    singleton, last_successful_scan_at, last_error_at, last_error_code,
                    slack_version, adapter_version, schema_version
                ) VALUES (1, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(singleton) DO UPDATE SET
                    last_successful_scan_at=excluded.last_successful_scan_at,
                    last_error_at=excluded.last_error_at,
                    last_error_code=excluded.last_error_code,
                    slack_version=excluded.slack_version,
                    adapter_version=excluded.adapter_version,
                    schema_version=excluded.schema_version""",
                (
                    _iso_optional(state.last_successful_scan_at),
                    _iso_optional(state.last_error_at),
                    state.last_error_code,
                    state.slack_version,
                    state.adapter_version,
                    state.schema_version,
                ),
            )

    def load_state(self) -> OperationalState:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM operational_state WHERE singleton = 1"
            ).fetchone()
        if row is None:
            return OperationalState(schema_version=self.schema_version)
        return OperationalState(
            last_successful_scan_at=_datetime_optional(row["last_successful_scan_at"]),
            last_error_at=_datetime_optional(row["last_error_at"]),
            last_error_code=row["last_error_code"],
            slack_version=row["slack_version"],
            adapter_version=row["adapter_version"],
            schema_version=row["schema_version"],
        )

    def record_failure(
        self, code: str, occurred_at: datetime, *, detail: str | None = None
    ) -> None:
        if not code.strip():
            raise ValueError("code must not be empty")
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO failures (occurred_at, code, detail) VALUES (?, ?, ?)",
                (_iso(occurred_at), code.strip(), _preview(detail, self._preview_length)),
            )

    def save_config(self, config: Mapping[str, Any], *, schema_version: int = 1) -> None:
        payload = json.dumps(config, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with self._transaction() as connection:
            connection.execute(
                """INSERT INTO configuration
                (singleton, payload_json, schema_version) VALUES (1, ?, ?)
                ON CONFLICT(singleton) DO UPDATE SET
                  payload_json=excluded.payload_json, schema_version=excluded.schema_version""",
                (payload, schema_version),
            )

    def load_config(self) -> dict[str, Any] | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT payload_json FROM configuration WHERE singleton = 1"
            ).fetchone()
        return json.loads(row[0]) if row else None

    def apply_retention(
        self, now: datetime, *, relevant_days: int = 30, ignored_days: int = 7
    ) -> int:
        if relevant_days <= 0 or ignored_days <= 0:
            raise ValueError("retention periods must be positive")
        relevant_cutoff = _iso(now - timedelta(days=relevant_days))
        ignored_cutoff = _iso(now - timedelta(days=ignored_days))
        with self._transaction() as connection:
            cursor = connection.execute(
                """DELETE FROM events
                WHERE (classification = ? AND last_seen_at < ?)
                   OR (classification <> ? AND last_seen_at < ?)""",
                (
                    EventCategory.DIRECT_MENTION.value,
                    relevant_cutoff,
                    EventCategory.DIRECT_MENTION.value,
                    ignored_cutoff,
                ),
            )
            return cursor.rowcount

    def clear_history(self, *, before: datetime | None = None) -> int:
        with self._transaction() as connection:
            cursor = (
                connection.execute("DELETE FROM events")
                if before is None
                else connection.execute(
                    "DELETE FROM events WHERE last_seen_at < ?", (_iso(before),)
                )
            )
            return cursor.rowcount

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def __enter__(self) -> SQLiteEventStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _event_values(
        self, event: OperationalEvent, status: EventStatus, now: str
    ) -> tuple[Any, ...]:
        metadata = {
            key: event.metadata[key] for key in self._metadata_allowlist if key in event.metadata
        }
        preview = self._history_enabled
        return (
            event.id,
            event.source,
            event.external_key,
            event.category.value,
            _preview(event.actor, self._preview_length) if preview else None,
            _preview(event.location, self._preview_length) if preview else None,
            _preview(event.body, self._preview_length) if preview else None,
            _preview(event.title, self._preview_length) if preview else None,
            _iso_optional(event.occurred_at),
            _iso(event.observed_at),
            now,
            now,
            None,
            status.value,
            event.classifier_version,
            event.deduplication_key,
            event.raw_fingerprint,
            json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
            event.schema_version,
        )

    class _Transaction:
        def __init__(self, owner: SQLiteEventStore) -> None:
            self.owner = owner

        def __enter__(self) -> sqlite3.Connection:
            self.owner._lock.acquire()
            try:
                self.owner._connection.execute("BEGIN IMMEDIATE")
                return self.owner._connection
            except BaseException:
                self.owner._lock.release()
                raise

        def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
            try:
                self.owner._connection.execute("ROLLBACK" if exc_type else "COMMIT")
            finally:
                self.owner._lock.release()

    def _transaction(self) -> SQLiteEventStore._Transaction:
        return self._Transaction(self)


_MIGRATION_1 = (
    """CREATE TABLE IF NOT EXISTS events (
      id TEXT PRIMARY KEY, source TEXT NOT NULL, external_key TEXT,
      classification TEXT NOT NULL, sender TEXT, channel TEXT,
      content_preview TEXT, title_preview TEXT, occurred_at TEXT, observed_at TEXT NOT NULL,
      first_seen_at TEXT NOT NULL, last_seen_at TEXT NOT NULL,
      alerted_at TEXT, status TEXT NOT NULL,
      classifier_version TEXT NOT NULL, deduplication_key TEXT NOT NULL UNIQUE,
      raw_fingerprint TEXT, metadata_json TEXT NOT NULL DEFAULT '{}',
      event_schema_version INTEGER NOT NULL
    )""",
    "CREATE INDEX IF NOT EXISTS idx_events_observed_at ON events(observed_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_events_retention ON events(classification, last_seen_at)",
    """CREATE TABLE IF NOT EXISTS operational_state (
      singleton INTEGER PRIMARY KEY CHECK (singleton = 1), last_successful_scan_at TEXT,
      last_error_at TEXT, last_error_code TEXT, slack_version TEXT, adapter_version TEXT,
      schema_version INTEGER NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS failures (
      id INTEGER PRIMARY KEY AUTOINCREMENT, occurred_at TEXT NOT NULL,
      code TEXT NOT NULL, detail TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS configuration (
      singleton INTEGER PRIMARY KEY CHECK (singleton = 1), payload_json TEXT NOT NULL,
      schema_version INTEGER NOT NULL
    )""",
)


def _preview(value: str | None, length: int) -> str | None:
    return " ".join(value.split())[:length] if value is not None else None


def _iso(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware")
    return value.astimezone(UTC).isoformat(timespec="microseconds")


def _iso_optional(value: datetime | None) -> str | None:
    return _iso(value) if value is not None else None


def _datetime_optional(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _row_to_event(row: sqlite3.Row) -> OperationalEvent:
    direct = row["classification"] == EventCategory.DIRECT_MENTION.value
    return OperationalEvent(
        id=row["id"],
        source=row["source"],
        external_key=row["external_key"],
        category=EventCategory(row["classification"]),
        priority=EventPriority.HIGH if direct else EventPriority.NORMAL,
        title=row["title_preview"],
        body=row["content_preview"],
        actor=row["sender"],
        location=row["channel"],
        occurred_at=_datetime_optional(row["occurred_at"]),
        observed_at=datetime.fromisoformat(row["observed_at"]),
        deduplication_key=row["deduplication_key"],
        raw_fingerprint=row["raw_fingerprint"],
        metadata=json.loads(row["metadata_json"]),
        classifier_version=row["classifier_version"],
        schema_version=row["event_schema_version"],
        status=EventStatus(row["status"]),
        first_seen_at=datetime.fromisoformat(row["first_seen_at"]),
        last_seen_at=datetime.fromisoformat(row["last_seen_at"]),
        alerted_at=_datetime_optional(row["alerted_at"]),
    )
