"""Local, validated configuration repository with atomic replacement."""

from __future__ import annotations

import os
import threading
from collections.abc import Callable
from pathlib import Path
from tempfile import NamedTemporaryFile

from watchdog.core.config import AppConfig, NotificationConfig


def default_data_directory() -> Path:
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return root / "AlwaysTrack" / "Watchdog"
    root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return root / "alwaystrack" / "watchdog"


class JsonConfigRepository:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        self._lock = threading.RLock()

    def load(self) -> AppConfig:
        with self._lock:
            return AppConfig.load(self.path) if self.path.exists() else AppConfig()

    def load_notification_preferences(self) -> NotificationConfig:
        """Load current popup preferences safely from the monitor thread."""

        return self.load().notification

    def update(self, transform: Callable[[AppConfig], AppConfig]) -> AppConfig:
        """Atomically read, validate and persist a configuration update."""

        with self._lock:
            updated = AppConfig.from_dict(transform(self.load()).to_dict())
            self.save(updated)
            return updated

    def save(self, config: AppConfig) -> None:
        with self._lock:
            validated = AppConfig.from_dict(config.to_dict())
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
                handle.write(validated.to_json() + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            temporary.replace(self.path)
