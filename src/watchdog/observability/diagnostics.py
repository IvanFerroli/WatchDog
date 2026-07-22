"""Sanitized accessibility diagnostics."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .logging import fingerprint


def sanitize_control(control: Mapping[str, Any]) -> dict[str, Any]:
    name = str(control.get("name") or "")
    return {
        "control_type": str(control.get("control_type") or ""),
        "automation_id": str(control.get("automation_id") or ""),
        "name_present": bool(name),
        "name_length": len(name),
        "name_fingerprint": fingerprint(name) if name else None,
        "depth": int(control.get("depth", 0)),
    }


def export_snapshot(
    controls: Iterable[Mapping[str, Any]],
    destination: Path,
    *,
    slack_version: str | None,
    adapter_version: str,
    elapsed_ms: float,
) -> Path:
    payload = {
        "schema_version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "slack_version": slack_version,
        "adapter_version": adapter_version,
        "elapsed_ms": round(elapsed_ms, 2),
        "controls": [sanitize_control(control) for control in controls],
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return destination


def compare_snapshots(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, Any]:
    def signatures(snapshot: Mapping[str, Any]) -> set[tuple[Any, ...]]:
        return {
            (
                item.get("control_type"),
                item.get("automation_id"),
                item.get("name_fingerprint"),
                item.get("depth"),
            )
            for item in snapshot.get("controls", [])
        }

    left, right = signatures(before), signatures(after)
    return {
        "added": len(right - left),
        "removed": len(left - right),
        "unchanged": len(left & right),
    }
