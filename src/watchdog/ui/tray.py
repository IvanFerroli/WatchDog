"""Tray commands separated from optional pystray rendering."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol


class RuntimeControls(Protocol):
    paused: bool
    health: Any

    def pause(self) -> None: ...

    def resume(self) -> None: ...

    def stop(self) -> None: ...


class TrayController:
    def __init__(
        self,
        runtime: RuntimeControls,
        *,
        open_panel: Callable[[], None],
        shutdown: Callable[[], None],
    ) -> None:
        self.runtime = runtime
        self.open_panel = open_panel
        self.shutdown = shutdown

    def toggle_pause(self) -> None:
        self.runtime.resume() if self.runtime.paused else self.runtime.pause()

    def status(self) -> str:
        return self.runtime.health.snapshot().state.value

    def exit(self) -> None:
        self.runtime.stop()
        self.shutdown()


class PystrayTray:
    def __init__(self, controller: TrayController) -> None:
        self.controller = controller
        self._icon: Any = None

    def run_detached(self) -> None:
        try:
            import pystray
            from PIL import Image, ImageDraw
        except ImportError as exc:
            raise RuntimeError("pystray and Pillow are required for tray mode") from exc
        image = Image.new("RGB", (64, 64), "#17212b")
        draw = ImageDraw.Draw(image)
        draw.ellipse((12, 12, 52, 52), outline="#36c5f0", width=6)
        menu = pystray.Menu(
            pystray.MenuItem("Abrir painel", lambda *_: self.controller.open_panel()),
            pystray.MenuItem("Pausar/retomar", lambda *_: self.controller.toggle_pause()),
            pystray.MenuItem(lambda _: f"Status: {self.controller.status()}", None, enabled=False),
            pystray.MenuItem("Encerrar", lambda *_: self.controller.exit()),
        )
        self._icon = pystray.Icon("alwaystrack-watchdog", image, "AlwaysTrack Watchdog", menu)
        self._icon.run_detached()

    def stop(self) -> None:
        if self._icon is not None:
            self._icon.stop()
