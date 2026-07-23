from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from watchdog.core.config import NotificationConfig
from watchdog.core.models import EventCategory, EventPriority, OperationalEvent
from watchdog.notifications import PreferenceAwareNotifier


class RecordingNotifier:
    def __init__(self) -> None:
        self.events: list[OperationalEvent] = []

    def notify(self, event: OperationalEvent) -> None:
        self.events.append(event)


def _event(category: EventCategory, event_id: str) -> OperationalEvent:
    return OperationalEvent(
        id=event_id,
        source="slack",
        category=category,
        priority=EventPriority.HIGH,
        observed_at=datetime(2026, 7, 22, tzinfo=UTC),
        deduplication_key=f"dedupe:{event_id}",
        classifier_version="test",
    )


def test_preferences_are_loaded_again_for_every_notification() -> None:
    preferences = NotificationConfig()
    recorded = RecordingNotifier()
    notifier = PreferenceAwareNotifier(recorded, lambda: preferences)

    notifier.notify(_event(EventCategory.DIRECT_MENTION, "mention-enabled"))
    preferences = replace(preferences, direct_mentions_enabled=False)
    notifier.notify(_event(EventCategory.DIRECT_MENTION, "mention-disabled"))
    notifier.notify(_event(EventCategory.DIRECT_MESSAGE, "dm-enabled"))
    preferences = replace(preferences, direct_messages_enabled=False)
    notifier.notify(_event(EventCategory.DIRECT_MESSAGE, "dm-disabled"))

    assert [event.id for event in recorded.events] == ["mention-enabled", "dm-enabled"]


def test_master_preference_disables_all_notifications() -> None:
    recorded = RecordingNotifier()
    notifier = PreferenceAwareNotifier(
        recorded,
        lambda: NotificationConfig(enabled=False),
    )

    notifier.notify(_event(EventCategory.DIRECT_MENTION, "mention"))
    notifier.notify(_event(EventCategory.DIRECT_MESSAGE, "dm"))

    assert recorded.events == []
