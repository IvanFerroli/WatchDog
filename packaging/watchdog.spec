# -*- mode: python ; coding: utf-8 -*-

import os

from PyInstaller.utils.hooks import collect_submodules

project_root = os.path.abspath(os.path.join(SPECPATH, os.pardir))

hiddenimports = collect_submodules("pystray") + collect_submodules("winotify")

a = Analysis(
    [os.path.join(project_root, "packaging", "entrypoint.py")],
    pathex=[project_root, os.path.join(project_root, "src")],
    binaries=[],
    datas=[(os.path.join(project_root, "config", "default.json"), "config")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    name="AlwaysTrackWatchdog",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    exclude_binaries=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AlwaysTrackWatchdog",
)
