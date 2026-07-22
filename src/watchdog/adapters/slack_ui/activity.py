"""Configurable Activity extraction without unproved Slack selectors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from watchdog.core.models import ObservedEvent

from .errors import AdapterErrorCode, SlackAdapterError
from .provider import SlackWindow


@dataclass(frozen=True, slots=True)
class ActivitySelectors:
    """Selectors supplied by a validated Windows spike, never inferred here."""

    activity_automation_id: str | None = None
    activity_title: str | None = None
    activity_control_type: str | None = None
    item_control_type: str | None = None
    item_automation_id: str | None = None
    event_type_automation_id: str | None = None
    direct_item_automation_id_prefix: str | None = None
    group_item_automation_id_prefix: str | None = None
    sender_automation_id: str | None = None
    channel_automation_id: str | None = None
    body_automation_id: str | None = None
    external_key_automation_id: str | None = None
    item_name_as_body: bool = False
    max_items: int = 50

    def __post_init__(self) -> None:
        if self.max_items <= 0:
            raise ValueError("max_items must be positive")
        prefixes = (
            self.direct_item_automation_id_prefix,
            self.group_item_automation_id_prefix,
        )
        if any(prefix is not None and not prefix for prefix in prefixes):
            raise ValueError("item automation id prefixes must not be empty")
        if all(prefixes) and prefixes[0] == prefixes[1]:
            raise ValueError("direct and group item prefixes must differ")

    @property
    def configured(self) -> bool:
        has_activity = bool(self.activity_automation_id or self.activity_title)
        has_item = bool(self.item_automation_id or self.item_control_type)
        has_event_type = bool(self.event_type_automation_id) or bool(
            self.direct_item_automation_id_prefix and self.group_item_automation_id_prefix
        )
        return has_activity and has_item and has_event_type


class PywinautoActivityReader:
    """Read only fields explicitly mapped by selectors from the real spike."""

    def __init__(
        self,
        selectors: ActivitySelectors,
        *,
        clock: Callable[[], datetime] | None = None,
        adapter_version: str = "uia-configurable-v1",
        direct_label: str = "Menção na conversa do canal",
        group_label: str = "Menção ao grupo na conversa do canal",
    ) -> None:
        self.selectors = selectors
        self._clock = clock or (lambda: datetime.now(UTC))
        self.adapter_version = adapter_version
        self._direct_label = direct_label
        self._group_label = group_label

    def read(self, window: SlackWindow) -> list[ObservedEvent]:
        if not self.selectors.configured:
            raise SlackAdapterError(
                AdapterErrorCode.STRATEGY_NOT_CONFIGURED,
                "Activity selectors require evidence from the Windows spike",
                retriable=False,
            )
        criteria = _criteria(
            automation_id=self.selectors.activity_automation_id,
            title=self.selectors.activity_title,
            control_type=self.selectors.activity_control_type,
        )
        try:
            container = window.native.child_window(**criteria)
            if not container.exists(timeout=1):
                raise SlackAdapterError(
                    AdapterErrorCode.ACTIVITY_NOT_FOUND,
                    "Configured Activity container was not found",
                )
            items = container.descendants(
                **_criteria(
                    automation_id=self.selectors.item_automation_id,
                    control_type=self.selectors.item_control_type,
                )
            )
        except SlackAdapterError:
            raise
        except Exception as exc:
            raise SlackAdapterError(
                AdapterErrorCode.READ_FAILED,
                "Activity could not be read",
            ) from exc

        events: list[ObservedEvent] = []
        for item in list(items)[: self.selectors.max_items]:
            try:
                events.append(self._extract(item))
            except Exception as exc:
                raise SlackAdapterError(
                    AdapterErrorCode.STRUCTURE_CHANGED,
                    "Configured Activity item structure did not match",
                ) from exc
        return events

    def _extract(self, item: Any) -> ObservedEvent:
        item_automation_id = _automation_id(item)
        raw_type = _child_text(item, self.selectors.event_type_automation_id)
        if not raw_type and item_automation_id:
            if _has_prefix(item_automation_id, self.selectors.group_item_automation_id_prefix):
                raw_type = self._group_label
            elif _has_prefix(item_automation_id, self.selectors.direct_item_automation_id_prefix):
                raw_type = self._direct_label
        body = _child_text(item, self.selectors.body_automation_id)
        if body is None and self.selectors.item_name_as_body:
            body = _window_text(item)
        fields = {
            "external_key": _child_text(item, self.selectors.external_key_automation_id)
            or item_automation_id,
            "raw_type": raw_type,
            "sender": _child_text(item, self.selectors.sender_automation_id),
            "channel": _child_text(item, self.selectors.channel_automation_id),
            "body": body,
        }
        return ObservedEvent(
            source="slack.desktop.uia",
            observed_at=self._clock(),
            external_key=fields["external_key"],
            raw_type=fields["raw_type"],
            sender=fields["sender"],
            channel=fields["channel"],
            body=fields["body"],
            raw_metadata={
                "adapter_version": self.adapter_version,
                "available_fields": tuple(key for key, value in fields.items() if value),
            },
        )


def _criteria(
    *,
    automation_id: str | None = None,
    title: str | None = None,
    control_type: str | None = None,
) -> dict[str, str]:
    values = {
        "auto_id": automation_id,
        "title": title,
        "control_type": control_type,
    }
    return {key: value for key, value in values.items() if value}


def _child_text(item: Any, automation_id: str | None) -> str | None:
    if not automation_id:
        return None
    child = item.child_window(auto_id=automation_id)
    if not child.exists(timeout=0.5):
        return None
    text = child.window_text()
    return str(text).strip() or None


def _automation_id(item: Any) -> str | None:
    element_info = getattr(item, "element_info", None)
    value = getattr(element_info, "automation_id", None)
    if value is None and hasattr(item, "automation_id"):
        value = item.automation_id()
    if value is None:
        return None
    return str(value).strip() or None


def _has_prefix(value: str, prefix: str | None) -> bool:
    return bool(prefix and value.startswith(prefix))


def _window_text(item: Any) -> str | None:
    value = item.window_text()
    return str(value).strip() or None
