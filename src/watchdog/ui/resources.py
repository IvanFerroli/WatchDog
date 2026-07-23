"""Paths for UI resources in source checkouts and PyInstaller bundles."""

from __future__ import annotations

import sys
from pathlib import Path

_ICON_RELATIVE_PATH = Path("assets") / "alwaystrack.png"


def application_icon_path() -> Path:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root is not None:
        return Path(bundle_root) / _ICON_RELATIVE_PATH
    return Path(__file__).resolve().parents[3] / _ICON_RELATIVE_PATH
