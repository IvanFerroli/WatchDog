"""Paths for UI resources in source checkouts and PyInstaller bundles."""

from __future__ import annotations

import sys
from pathlib import Path
from shutil import copy2

_ICON_RELATIVE_PATH = Path("assets") / "alwaystrack.png"


def application_icon_path() -> Path:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root is not None:
        return Path(bundle_root) / _ICON_RELATIVE_PATH
    return Path(__file__).resolve().parents[3] / _ICON_RELATIVE_PATH


def staged_application_icon_path(data_directory: Path) -> Path | None:
    """Copy the icon to a local app-data path accepted by Windows toasts."""

    source = application_icon_path()
    if not source.is_file():
        return None
    target = data_directory / _ICON_RELATIVE_PATH
    try:
        if source.resolve() == target.resolve():
            return source
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.is_file() or source.read_bytes() != target.read_bytes():
            copy2(source, target)
    except OSError:
        return None
    return target
