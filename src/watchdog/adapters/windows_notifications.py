"""Windows UserNotificationListener source for focus-free Slack direct messages."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import sys
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Protocol

from watchdog.core.models import ObservedEvent


class WindowsNotificationErrorCode(StrEnum):
    UNSUPPORTED_PLATFORM = "WINDOWS_NOTIFICATIONS_UNSUPPORTED"
    ACCESS_DENIED = "WINDOWS_NOTIFICATIONS_ACCESS_DENIED"
    READ_FAILED = "WINDOWS_NOTIFICATIONS_READ_FAILED"


class WindowsNotificationError(RuntimeError):
    def __init__(self, code: WindowsNotificationErrorCode, *, retriable: bool) -> None:
        super().__init__(code.value)
        self.code = code
        self.retriable = retriable


@dataclass(frozen=True, slots=True)
class WindowsNotificationRecord:
    notification_id: int
    creation_time: datetime
    app_display_name: str
    app_user_model_id: str
    package_family_name: str
    text_elements: tuple[str, ...]


class WindowsNotificationBackend(Protocol):
    def list_toasts(self) -> Iterable[WindowsNotificationRecord]: ...


class SlackDirectMessagePolicy:
    """Conservative Slack/DM filter; ambiguous Slack toasts are ignored."""

    _channel_markers = re.compile(
        r"(^|[\s(\[])(#|canal\b|channel\b|menção\b|mention\b|thread\b|tópico\b)",
        re.IGNORECASE,
    )
    _non_message_markers = re.compile(
        r"\b(huddle|chamada|call|lembrete|reminder|rea[cç][aã]o|reaction|workflow|canvas)\b",
        re.IGNORECASE,
    )

    def is_slack_app(
        self,
        app_display_name: str,
        app_user_model_id: str,
        package_family_name: str,
    ) -> bool:
        display = _normalized(app_display_name)
        identity = _normalized(f"{app_user_model_id} {package_family_name}")
        return display in {"slack", "slack beta", "slack (beta)"} and (
            "slack" in identity or "tinyspeck" in identity
        )

    def is_slack_direct_message(self, record: WindowsNotificationRecord) -> bool:
        if not self.is_slack_app(
            record.app_display_name,
            record.app_user_model_id,
            record.package_family_name,
        ):
            return False
        texts = tuple(
            text for text in (_safe_text(value, 240) for value in record.text_elements) if text
        )
        if len(texts) < 2:
            return False
        title = texts[0]
        return not (
            _normalized(title) == "slack"
            or self._channel_markers.search(title)
            or self._non_message_markers.search(title)
        )


class UserNotificationListenerSource:
    """Convert only confidently identified Slack DMs into domain observations."""

    adapter_version = "windows-user-notification-listener-v1"

    def __init__(
        self,
        backend: WindowsNotificationBackend | None = None,
        *,
        policy: SlackDirectMessagePolicy | None = None,
    ) -> None:
        self._policy = policy or SlackDirectMessagePolicy()
        self._backend = backend or WinRTUserNotificationBackend(self._policy.is_slack_app)
        self._logger = logging.getLogger("watchdog.windows_notifications")
        self._baseline_initialized = False
        self._known_keys: set[str] = set()

    def observe(self) -> list[ObservedEvent]:
        events: list[ObservedEvent] = []
        current_keys: set[str] = set()
        for record in self._backend.list_toasts():
            if not self._policy.is_slack_direct_message(record):
                continue
            texts = tuple(
                text for text in (_safe_text(value, 240) for value in record.text_elements) if text
            )
            app_identity = (
                f"{record.app_display_name}|{record.app_user_model_id}|{record.package_family_name}"
            )
            notification_key = _notification_key(record, app_identity)
            if notification_key in current_keys:
                continue
            current_keys.add(notification_key)
            if not self._baseline_initialized or notification_key in self._known_keys:
                continue
            events.append(
                ObservedEvent(
                    source="windows.user_notification_listener.slack",
                    external_key=notification_key,
                    raw_type="MD",
                    title="Mensagem direta no Slack",
                    sender=_safe_text(texts[0], 120),
                    body=_safe_text(texts[1], 240),
                    occurred_at=_as_utc(record.creation_time),
                    observed_at=datetime.now(UTC),
                    raw_metadata={
                        "adapter_version": self.adapter_version,
                        "notification_id": record.notification_id,
                        "app_user_model_id": _safe_text(record.app_user_model_id, 160),
                        "package_family_name": _safe_text(record.package_family_name, 160),
                    },
                )
            )
        if not self._baseline_initialized:
            self._baseline_initialized = True
            self._known_keys = current_keys
            self._logger.info(
                "windows_notifications.baseline_initialized",
                extra={"context": {"items": len(current_keys)}},
            )
            return []
        self._known_keys = current_keys
        self._logger.debug("windows_notifications.scan", extra={"context": {"items": len(events)}})
        return events


class WinRTUserNotificationBackend:
    """Lazy WinRT bridge; imports Windows projections only on the target OS."""

    def __init__(self, app_filter: Callable[[str, str, str], bool]) -> None:
        self._app_filter = app_filter

    def list_toasts(self) -> list[WindowsNotificationRecord]:
        if sys.platform != "win32":
            raise WindowsNotificationError(
                WindowsNotificationErrorCode.UNSUPPORTED_PLATFORM,
                retriable=False,
            )
        try:
            return _run_async(self._list_toasts())
        except WindowsNotificationError:
            raise
        except Exception as exc:
            raise WindowsNotificationError(
                WindowsNotificationErrorCode.READ_FAILED,
                retriable=True,
            ) from exc

    async def _list_toasts(self) -> list[WindowsNotificationRecord]:
        try:
            from winrt.windows.ui.notifications import (
                KnownNotificationBindings,
                NotificationKinds,
            )
            from winrt.windows.ui.notifications.management import UserNotificationListener
        except ImportError as exc:
            raise WindowsNotificationError(
                WindowsNotificationErrorCode.UNSUPPORTED_PLATFORM,
                retriable=False,
            ) from exc

        listener = UserNotificationListener.current
        status = listener.get_access_status()
        if _enum_name(status) == "UNSPECIFIED":
            status = await listener.request_access_async()
        if _enum_name(status) != "ALLOWED":
            raise WindowsNotificationError(
                WindowsNotificationErrorCode.ACCESS_DENIED,
                retriable=False,
            )
        notifications = await listener.get_notifications_async(NotificationKinds.TOAST)
        records: list[WindowsNotificationRecord] = []
        for item in notifications:
            record = _record_from_winrt(
                item,
                KnownNotificationBindings.TOAST_GENERIC,
                self._app_filter,
            )
            if record is not None:
                records.append(record)
        return records


def _record_from_winrt(
    item: Any,
    toast_binding: Any,
    app_filter: Callable[[str, str, str], bool],
) -> WindowsNotificationRecord | None:
    try:
        app_info = item.app_info
        app_display_name = str(app_info.display_info.display_name or "")
        app_user_model_id = str(getattr(app_info, "app_user_model_id", "") or "")
        try:
            package = getattr(app_info, "package", None)
            package_id = getattr(package, "id", None)
            package_family_name = str(getattr(package_id, "family_name", "") or "")
        except Exception:
            # Package is optional for classic desktop apps; AUMID remains enough
            # to prove Slack identity when the projection cannot expose it.
            package_family_name = ""
        # App identity is checked before touching the notification payload. This
        # keeps non-Slack notification contents outside the adapter boundary.
        if not app_filter(app_display_name, app_user_model_id, package_family_name):
            return None
        binding = item.notification.visual.get_binding(toast_binding)
        if binding is None:
            return None
        text_elements = tuple(
            str(element.text) for element in binding.get_text_elements() if element.text
        )
        return WindowsNotificationRecord(
            notification_id=int(item.id),
            creation_time=_as_utc(item.creation_time),
            app_display_name=app_display_name,
            app_user_model_id=app_user_model_id,
            package_family_name=package_family_name,
            text_elements=text_elements,
        )
    except Exception:
        return None


def _notification_key(record: WindowsNotificationRecord, app_identity: str) -> str:
    creation = _as_utc(record.creation_time).isoformat(timespec="microseconds")
    payload = f"{app_identity}|{record.notification_id}|{creation}"
    return f"windows-toast:{hashlib.sha256(payload.encode()).hexdigest()}"


def _safe_text(value: object, limit: int) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split()).strip()
    return text[:limit] or None


def _normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _enum_name(value: object) -> str:
    name = getattr(value, "name", None)
    if isinstance(name, str):
        return name.upper()
    text = str(value).rsplit(".", 1)[-1]
    return text.upper()


def _run_async(
    awaitable: Awaitable[list[WindowsNotificationRecord]],
) -> list[WindowsNotificationRecord]:
    return asyncio.run(awaitable)
