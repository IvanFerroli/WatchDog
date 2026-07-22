"""Small production composition rooted in the accepted ports."""

from __future__ import annotations

from pathlib import Path

from watchdog.adapters.slack_ui import (
    ActivitySelectors,
    PywinautoActivityNavigator,
    PywinautoActivityReader,
    PywinautoWindowProvider,
    SlackUIAdapter,
    SlackWindowLifecycle,
)
from watchdog.classification import EventClassifier, NotificationRules
from watchdog.core.config import AppConfig
from watchdog.core.deduplication import DeduplicationService
from watchdog.core.normalizer import EventNormalizer
from watchdog.notifications import NullNotifier, WindowsNotifier
from watchdog.persistence import SQLiteEventStore

from .runtime import MonitorRuntime, SystemClock


def build_runtime(
    config: AppConfig,
    *,
    data_directory: Path,
    selectors: ActivitySelectors,
) -> tuple[MonitorRuntime, SQLiteEventStore]:
    storage_path = (
        Path(config.storage.path).expanduser()
        if config.storage.path
        else data_directory / "watchdog.db"
    )
    if config.storage.path and not storage_path.is_absolute():
        storage_path = data_directory / storage_path
    store = SQLiteEventStore(
        storage_path,
        preview_length=config.storage.content_preview_length,
        history_enabled=config.notification.persist_history,
    )
    adapter = SlackUIAdapter(
        SlackWindowLifecycle(PywinautoWindowProvider(), config.slack.process_names),
        PywinautoActivityReader(
            selectors,
            direct_label=config.slack.direct_mention_labels[0],
            group_label=config.slack.group_mention_labels[0],
        ),
        PywinautoActivityNavigator(automation_id="activity-inbox"),
    )
    notifier = (
        WindowsNotifier(
            sound_enabled=config.notification.sound_enabled,
            sound_file=config.notification.sound_file,
            preview_length=config.storage.content_preview_length,
            show_preview=config.notification.show_preview,
        )
        if config.notification.enabled
        else NullNotifier()
    )
    runtime = MonitorRuntime(
        adapter=adapter,
        normalizer=EventNormalizer(),
        classifier=EventClassifier(
            direct_mention_labels=config.slack.direct_mention_labels,
            group_mention_labels=config.slack.group_mention_labels,
        ),
        deduplication=DeduplicationService(store),
        rules=NotificationRules(),
        store=store,
        notifier=notifier,
        clock=SystemClock(),
        poll_interval_seconds=config.watchdog.poll_interval_ms / 1000,
    )
    store.apply_retention(
        SystemClock().now(),
        relevant_days=config.storage.relevant_retention_days,
        ignored_days=config.storage.ignored_retention_days,
    )
    if not config.watchdog.enabled:
        runtime.pause()
    return runtime, store
