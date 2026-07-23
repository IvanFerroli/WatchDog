# -*- mode: python ; coding: utf-8 -*-

import os

from PyInstaller.utils.hooks import collect_submodules

project_root = os.path.abspath(os.path.join(SPECPATH, os.pardir))
icon_png = os.path.join(project_root, "assets", "alwaystrack.png")
icon_ico = os.path.join(project_root, "assets", "alwaystrack.ico")

hiddenimports = (
    collect_submodules("pystray")
    + collect_submodules("winotify")
    + collect_submodules("winrt.windows.applicationmodel")
    + collect_submodules("winrt.windows.data.xml.dom")
    + collect_submodules("winrt.windows.foundation")
    + collect_submodules("winrt.windows.foundation.collections")
    + collect_submodules("winrt.windows.ui.notifications")
    + collect_submodules("winrt.windows.ui.notifications.management")
)

a = Analysis(
    [os.path.join(project_root, "packaging", "entrypoint.py")],
    pathex=[project_root, os.path.join(project_root, "src")],
    binaries=[],
    datas=[
        (os.path.join(project_root, "config", "default.json"), "config"),
        (icon_png, "assets"),
    ],
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
    icon=icon_ico,
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
