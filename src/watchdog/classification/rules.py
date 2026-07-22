"""Notification decision table. Only a new direct mention can alert."""

from watchdog.core.models import AlertDecision, EventCategory, OperationalEvent


class NotificationRules:
    def decide(self, event: OperationalEvent, *, is_new: bool = True) -> AlertDecision:
        if not is_new:
            return AlertDecision(False, "event.already_processed")
        if event.category is EventCategory.DIRECT_MENTION:
            return AlertDecision(True, "category.direct_mention")
        if event.category is EventCategory.GROUP_MENTION:
            return AlertDecision(False, "category.group_mention")
        return AlertDecision(False, "category.not_actionable")
