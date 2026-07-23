from __future__ import annotations

from datetime import UTC, datetime

import pytest

from watchdog.adapters.composite import CompositeEventAdapter
from watchdog.adapters.slack_ui import AdapterErrorCode, SlackAdapterError
from watchdog.core.models import ObservedEvent


class StaticAdapter:
    def __init__(self, events: list[ObservedEvent]) -> None:
        self.events = events

    def observe(self) -> list[ObservedEvent]:
        return self.events


class FailedAdapter:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def observe(self) -> list[ObservedEvent]:
        raise self.error


def test_composite_requires_at_least_one_source() -> None:
    with pytest.raises(ValueError, match="at least one"):
        CompositeEventAdapter()


def test_composite_keeps_healthy_source_and_exposes_safe_partial_failure() -> None:
    event = ObservedEvent("windows", datetime(2026, 7, 22, tzinfo=UTC), external_key="dm-1")
    adapter = CompositeEventAdapter(
        slack_uia=FailedAdapter(
            SlackAdapterError(AdapterErrorCode.ACTIVITY_NOT_FOUND, "private diagnostic")
        ),
        windows_notifications=StaticAdapter([event]),
    )

    assert adapter.observe() == [event]
    assert len(adapter.last_failures) == 1
    assert adapter.last_failures[0].source == "slack_uia"
    assert adapter.last_failures[0].code == "ACTIVITY_NOT_FOUND"
    assert "private diagnostic" not in repr(adapter.last_failures)


def test_composite_raises_first_error_if_every_source_fails() -> None:
    first = SlackAdapterError(AdapterErrorCode.SLACK_NOT_RUNNING, "not found")
    adapter = CompositeEventAdapter(
        slack_uia=FailedAdapter(first),
        windows_notifications=FailedAdapter(RuntimeError("unavailable")),
    )

    with pytest.raises(SlackAdapterError) as caught:
        adapter.observe()

    assert caught.value is first
    assert len(adapter.last_failures) == 2


def test_composite_deduplicates_same_message_across_sources_only() -> None:
    now = datetime(2026, 7, 22, tzinfo=UTC)
    ui_event = ObservedEvent(
        "slack.desktop.uia",
        now,
        external_key="uia-1",
        raw_type="direct mention",
        sender="Alice",
        body="mensagem sintética",
    )
    toast_duplicate = ObservedEvent(
        "windows.user_notification_listener.slack",
        now,
        external_key="toast-1",
        raw_type="MD",
        sender=" alice ",
        body="Mensagem sintética",
    )
    adapter = CompositeEventAdapter(
        slack_uia=StaticAdapter([ui_event]),
        windows_notifications=StaticAdapter([toast_duplicate]),
    )

    assert adapter.observe() == [ui_event]
