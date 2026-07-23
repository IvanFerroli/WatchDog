"""Windows toast and sound adapter with optional imports and test seams."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

from watchdog.core.models import EventCategory, OperationalEvent

DEFAULT_SLACK_DESTINATION = "slack://open"
_DESTINATION_METADATA_KEYS = ("slack_destination", "slack_activity_destination")


class NotificationError(RuntimeError):
    pass


class NullNotifier:
    def notify(self, event: OperationalEvent) -> None:
        return None


class WindowsNotifier:
    def __init__(
        self,
        *,
        sound_enabled: bool = True,
        sound_file: str | None = None,
        preview_length: int = 160,
        show_preview: bool = True,
        icon_path: str | Path | None = None,
        toast_factory: Callable[..., Any] | None = None,
        sound_player: Callable[[str | None], None] | None = None,
    ) -> None:
        if preview_length <= 0:
            raise ValueError("preview_length must be positive")
        self.sound_enabled = sound_enabled
        self.sound_file = sound_file
        self.preview_length = preview_length
        self.show_preview = show_preview
        self.icon_path = _existing_absolute_path(icon_path)
        self._toast_factory = toast_factory
        self._sound_player = sound_player

    def notify(self, event: OperationalEvent) -> None:
        title = _title(event)
        fallback_message = _fallback_message(event)
        message = _message(event, self.preview_length) if self.show_preview else fallback_message
        destination = _xml_attribute(notification_destination(event))
        try:
            toast = self._factory()(
                app_id="AlwaysTrack Watchdog",
                title=title,
                msg=_powershell_cdata(message),
                icon=self.icon_path,
                duration="long",
                launch=destination,
            )
            add_action = getattr(toast, "add_actions", None)
            if callable(add_action):
                add_action(label="Abrir no Slack", launch=destination)
            toast.show()
            if self.sound_enabled:
                self._player()(self.sound_file)
        except NotificationError:
            raise
        except Exception as exc:
            raise NotificationError("Windows notification failed") from exc

    def _factory(self) -> Callable[..., Any]:
        if self._toast_factory is not None:
            return self._toast_factory
        if sys.platform != "win32":
            raise NotificationError("Windows notifications are unavailable on this platform")
        try:
            from winotify import Notification
        except ImportError as exc:
            raise NotificationError("winotify is not installed") from exc
        return Notification

    def _player(self) -> Callable[[str | None], None]:
        if self._sound_player is not None:
            return self._sound_player
        if sys.platform != "win32":
            raise NotificationError("Windows sound is unavailable on this platform")
        import winsound

        def play(path: str | None) -> None:
            if path:
                sound = str(Path(path).expanduser())
                winsound.PlaySound(sound, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

        return play


def _message(event: OperationalEvent, limit: int) -> str:
    context = " · ".join(part for part in (event.actor, event.location) if part)
    preview = (event.body or event.title or _fallback_message(event)).strip()
    if len(preview) > limit:
        preview = preview[: max(1, limit - 1)].rstrip() + "…"
    return f"{context}\n{preview}" if context else preview


def _title(event: OperationalEvent) -> str:
    if event.category is EventCategory.DIRECT_MESSAGE:
        return "Nova mensagem privada no Slack"
    return "Menção direta no Slack"


def _fallback_message(event: OperationalEvent) -> str:
    if event.category is EventCategory.DIRECT_MESSAGE:
        return "Nova mensagem privada"
    return "Nova menção direta"


def notification_destination(event: OperationalEvent) -> str:
    """Choose a captured Slack target or the documented client-open fallback."""

    for key in _DESTINATION_METADATA_KEYS:
        value = event.metadata.get(key)
        if isinstance(value, str) and _is_safe_slack_destination(value):
            return value
    return DEFAULT_SLACK_DESTINATION


def _is_safe_slack_destination(value: str) -> bool:
    if not value or any(
        ord(character) < 0x20 or character in {'"', "<", ">", "$", "`"} for character in value
    ):
        return False
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    if parsed.scheme.casefold() == "slack":
        return True
    if parsed.scheme.casefold() != "https" or parsed.username or parsed.password:
        return False
    host = (parsed.hostname or "").casefold()
    return host == "slack.com" or host.endswith(".slack.com")


def _xml_attribute(value: str) -> str:
    # winotify 1.1 interpolates launch directly into a quoted XML attribute.
    return escape(value, {'"': "&quot;"})


def _powershell_cdata(value: str) -> str:
    """Make remote text inert inside winotify's expandable PowerShell here-string."""

    single_line = " ".join(value.splitlines())
    xml_safe = single_line.replace("]]>", "]]]]><![CDATA[>")
    return xml_safe.replace("`", "``").replace("$", "`$")


def _existing_absolute_path(value: str | Path | None) -> str:
    if value is None:
        return ""
    path = Path(value).expanduser().resolve()
    return str(path) if path.is_file() else ""
