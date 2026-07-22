"""Structured local logging with conservative redaction."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_SENSITIVE_KEYS = {"body", "content", "content_preview", "message", "sender", "channel", "title"}
_TOKEN_PATTERN = re.compile(
    r"(?i)(xox[abprs]-[a-z0-9-]+|bearer\s+[a-z0-9._-]+|cookie\s*[:=]\s*[^\s,;]+)"
)


def fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16]


def redact(value: Any, key: str | None = None) -> Any:
    if key and key.casefold() in _SENSITIVE_KEYS and value not in (None, ""):
        text = str(value)
        return {"redacted": True, "length": len(text), "fingerprint": fingerprint(text)}
    if isinstance(value, dict):
        return {
            str(item_key): redact(item_value, str(item_key))
            for item_key, item_value in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return _TOKEN_PATTERN.sub("[REDACTED_SECRET]", value)
    return value


@dataclass(slots=True)
class JsonLogFormatter(logging.Formatter):
    """Serialize known structured fields without leaking message content."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "event": redact(record.getMessage()),
        }
        context = getattr(record, "context", None)
        if isinstance(context, dict):
            payload["context"] = redact(context)
        if record.exc_info:
            payload["exception"] = record.exc_info[0].__name__
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging(log_path: Path, level: str = "INFO") -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(JsonLogFormatter())
    root = logging.getLogger("watchdog")
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
    root.propagate = False
