"""JSON-serializable and validated application configuration."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    pass


def _positive_int(value: Any, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ConfigError(f"{name} must be a positive integer")
    return value


def _bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(f"{name} must be a boolean")
    return value


def _string(value: Any, name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ConfigError(f"{name} must be a string" + ("" if allow_empty else " and not empty"))
    return value


def _strings(value: Any, name: str, *, nonempty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ConfigError(f"{name} must be an array of non-empty strings")
    result = tuple(item.strip() for item in value)
    if nonempty and not result:
        raise ConfigError(f"{name} must not be empty")
    return result


def _section(data: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    value = data.get(name, {})
    if not isinstance(value, Mapping):
        raise ConfigError(f"{name} must be an object")
    return value


def _reject_unknown(data: Mapping[str, Any], allowed: set[str], name: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise ConfigError(f"unknown {name} key(s): {', '.join(sorted(unknown))}")


@dataclass(frozen=True, slots=True)
class WatchdogConfig:
    enabled: bool = True
    poll_interval_ms: int = 5_000
    start_with_windows: bool = False


@dataclass(frozen=True, slots=True)
class SlackConfig:
    process_names: tuple[str, ...] = ("slack.exe",)
    language: str = "pt-BR"
    direct_mention_labels: tuple[str, ...] = ("Menção na conversa do canal",)
    group_mention_labels: tuple[str, ...] = ("Menção ao grupo na conversa do canal",)
    user_display_names: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class NotificationConfig:
    enabled: bool = True
    sound_enabled: bool = True
    sound_file: str | None = None
    persist_history: bool = True


@dataclass(frozen=True, slots=True)
class StorageConfig:
    path: str = "watchdog.db"
    relevant_retention_days: int = 30
    ignored_retention_days: int = 7
    content_preview_length: int = 240


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    level: str = "INFO"


@dataclass(frozen=True, slots=True)
class AppConfig:
    watchdog: WatchdogConfig = field(default_factory=WatchdogConfig)
    slack: SlackConfig = field(default_factory=SlackConfig)
    notification: NotificationConfig = field(default_factory=NotificationConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json() + "\n", encoding="utf-8")

    @classmethod
    def from_json(cls, value: str) -> AppConfig:
        try:
            data = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"invalid JSON: {exc.msg}") from exc
        if not isinstance(data, Mapping):
            raise ConfigError("configuration root must be an object")
        return cls.from_dict(data)

    @classmethod
    def load(cls, path: str | Path) -> AppConfig:
        return cls.from_json(Path(path).read_text(encoding="utf-8"))

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> AppConfig:
        _reject_unknown(
            data,
            {"schema_version", "watchdog", "slack", "notification", "storage", "logging"},
            "root",
        )
        defaults = cls()
        schema_version = _positive_int(
            data.get("schema_version", defaults.schema_version), "schema_version"
        )
        if schema_version != 1:
            raise ConfigError(f"unsupported schema_version: {schema_version}")

        wd = _section(data, "watchdog")
        _reject_unknown(wd, {"enabled", "poll_interval_ms", "start_with_windows"}, "watchdog")
        watchdog = WatchdogConfig(
            enabled=_bool(wd.get("enabled", defaults.watchdog.enabled), "watchdog.enabled"),
            poll_interval_ms=_positive_int(
                wd.get("poll_interval_ms", defaults.watchdog.poll_interval_ms),
                "watchdog.poll_interval_ms",
            ),
            start_with_windows=_bool(
                wd.get("start_with_windows", defaults.watchdog.start_with_windows),
                "watchdog.start_with_windows",
            ),
        )

        sl = _section(data, "slack")
        _reject_unknown(
            sl,
            {
                "process_names",
                "language",
                "direct_mention_labels",
                "group_mention_labels",
                "user_display_names",
            },
            "slack",
        )
        slack = SlackConfig(
            process_names=_strings(
                sl.get("process_names", defaults.slack.process_names),
                "slack.process_names",
                nonempty=True,
            ),
            language=_string(sl.get("language", defaults.slack.language), "slack.language"),
            direct_mention_labels=_strings(
                sl.get("direct_mention_labels", defaults.slack.direct_mention_labels),
                "slack.direct_mention_labels",
                nonempty=True,
            ),
            group_mention_labels=_strings(
                sl.get("group_mention_labels", defaults.slack.group_mention_labels),
                "slack.group_mention_labels",
                nonempty=True,
            ),
            user_display_names=_strings(
                sl.get("user_display_names", defaults.slack.user_display_names),
                "slack.user_display_names",
            ),
        )

        nt = _section(data, "notification")
        _reject_unknown(
            nt, {"enabled", "sound_enabled", "sound_file", "persist_history"}, "notification"
        )
        sound_file = nt.get("sound_file", defaults.notification.sound_file)
        if sound_file is not None:
            sound_file = _string(sound_file, "notification.sound_file")
        notification = NotificationConfig(
            enabled=_bool(nt.get("enabled", defaults.notification.enabled), "notification.enabled"),
            sound_enabled=_bool(
                nt.get("sound_enabled", defaults.notification.sound_enabled),
                "notification.sound_enabled",
            ),
            sound_file=sound_file,
            persist_history=_bool(
                nt.get("persist_history", defaults.notification.persist_history),
                "notification.persist_history",
            ),
        )

        st = _section(data, "storage")
        _reject_unknown(
            st,
            {"path", "relevant_retention_days", "ignored_retention_days", "content_preview_length"},
            "storage",
        )
        storage = StorageConfig(
            path=_string(st.get("path", defaults.storage.path), "storage.path"),
            relevant_retention_days=_positive_int(
                st.get("relevant_retention_days", defaults.storage.relevant_retention_days),
                "storage.relevant_retention_days",
            ),
            ignored_retention_days=_positive_int(
                st.get("ignored_retention_days", defaults.storage.ignored_retention_days),
                "storage.ignored_retention_days",
            ),
            content_preview_length=_positive_int(
                st.get("content_preview_length", defaults.storage.content_preview_length),
                "storage.content_preview_length",
            ),
        )

        lg = _section(data, "logging")
        _reject_unknown(lg, {"level"}, "logging")
        level = _string(lg.get("level", defaults.logging.level), "logging.level").upper()
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ConfigError("logging.level is invalid")
        return cls(watchdog, slack, notification, storage, LoggingConfig(level), schema_version)
