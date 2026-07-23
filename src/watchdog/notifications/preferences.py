"""Dynamic notification filtering backed by persisted user preferences."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from watchdog.core.config import NotificationConfig
from watchdog.core.models import EventCategory, OperationalEvent


class EventNotifier(Protocol):
    def notify(self, event: OperationalEvent) -> None: ...


class PreferenceAwareNotifier:
    """Apply the latest category preferences immediately before dispatch."""

    def __init__(
        self,
        notifier: EventNotifier,
        preferences: Callable[[], NotificationConfig],
    ) -> None:
        self._notifier = notifier
        self._preferences = preferences

    def notify(self, event: OperationalEvent) -> None:
        preferences = self._preferences()
        if not preferences.enabled:
            return
        if (
            event.category is EventCategory.DIRECT_MENTION
            and not preferences.direct_mentions_enabled
        ):
            return
        if (
            event.category is EventCategory.DIRECT_MESSAGE
            and not preferences.direct_messages_enabled
        ):
            return
        self._notifier.notify(event)
