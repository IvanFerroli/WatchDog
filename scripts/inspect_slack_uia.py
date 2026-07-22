"""Safe UIA spike helper for controlled Slack test data on Windows.

The script emits control metadata and hashes only. Accessible names are never
written verbatim because they may contain corporate conversation content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16]


def _walk(controls: Iterable[Any], max_depth: int, depth: int = 0) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    if depth > max_depth:
        return result
    for control in controls:
        try:
            info = control.element_info
            name = str(info.name or "")
            item = {
                "depth": depth,
                "control_type": str(info.control_type or ""),
                "automation_id": str(info.automation_id or ""),
                "name_present": bool(name),
                "name_length": len(name),
                "name_fingerprint": _fingerprint(name) if name else None,
            }
            result.append(item)
            result.extend(_walk(control.children(), max_depth, depth + 1))
        except Exception as exc:  # UI trees can mutate during enumeration.
            result.append({"depth": depth, "read_error": type(exc).__name__})
    return result


def inspect(output: Path, max_depth: int, navigate_automation_id: str | None = None) -> int:
    if sys.platform != "win32":
        print("blocked: this spike requires Windows and Slack Desktop", file=sys.stderr)
        return 2

    from pywinauto import Desktop  # Imported only on the supported platform.

    windows = Desktop(backend="uia").windows(title_re=".*Slack.*", visible_only=False)
    if not windows:
        print("blocked: no Slack window found", file=sys.stderr)
        return 3

    candidates = [_window_metadata(window) for window in windows]
    selected_index = max(
        range(len(windows)),
        key=lambda index: (
            candidates[index]["visible"],
            candidates[index]["area"],
        ),
    )
    selected = windows[selected_index]
    navigation_performed = False
    if navigate_automation_id:
        targets = [
            control
            for control in selected.descendants()
            if str(control.element_info.automation_id or "") == navigate_automation_id
        ]
        if not targets:
            print("blocked: requested navigation control was not found", file=sys.stderr)
            return 4
        target = targets[0]
        if hasattr(target, "select"):
            target.select()
        else:
            target.click_input()
        time.sleep(1)
        navigation_performed = True
    started = time.perf_counter()
    controls = _walk(selected.children(), max_depth=max_depth)
    payload = {
        "schema_version": 1,
        "captured_at_epoch": int(time.time()),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "window_count": len(windows),
        "window_candidates": candidates,
        "selected_window_index": selected_index,
        "navigation_performed": navigation_performed,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        "controls": controls,
        "privacy": "accessible names replaced by length and sha256 prefix",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote sanitized metadata for {len(controls)} controls to {output}")
    return 0


def _window_metadata(window: Any) -> dict[str, Any]:
    rectangle = window.rectangle()
    width = max(0, rectangle.width())
    height = max(0, rectangle.height())
    name = str(window.element_info.name or "")
    return {
        "process_id": window.element_info.process_id,
        "control_type": str(window.element_info.control_type or ""),
        "visible": bool(window.is_visible()),
        "enabled": bool(window.is_enabled()),
        "width": width,
        "height": height,
        "area": width * height,
        "name_present": bool(name),
        "name_length": len(name),
        "name_fingerprint": _fingerprint(name) if name else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-depth", type=int, default=8)
    parser.add_argument("--navigate-automation-id")
    args = parser.parse_args()
    return inspect(args.output, args.max_depth, args.navigate_automation_id)


if __name__ == "__main__":
    raise SystemExit(main())
