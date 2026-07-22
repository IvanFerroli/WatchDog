"""Windows toast and sound adapter with optional imports and test seams."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from watchdog.core.models import OperationalEvent


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
        toast_factory: Callable[..., Any] | None = None,
        sound_player: Callable[[str | None], None] | None = None,
    ) -> None:
        if preview_length <= 0:
            raise ValueError("preview_length must be positive")
        self.sound_enabled = sound_enabled
        self.sound_file = sound_file
        self.preview_length = preview_length
        self.show_preview = show_preview
        self._toast_factory = toast_factory
        self._sound_player = sound_player

    def notify(self, event: OperationalEvent) -> None:
        title = "Menção direta no Slack"
        message = (
            _message(event, self.preview_length) if self.show_preview else "Nova menção direta"
        )
        try:
            toast = self._factory()(app_id="AlwaysTrack Watchdog", title=title, msg=message)
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
    preview = (event.body or event.title or "Nova menção direta").strip()
    if len(preview) > limit:
        preview = preview[: max(1, limit - 1)].rstrip() + "…"
    return f"{context}\n{preview}" if context else preview
