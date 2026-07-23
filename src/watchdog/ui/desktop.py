"""Desktop lifecycle: monitor thread, tray and hidden-capable panel."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from watchdog.application.configuration import JsonConfigRepository

from .panel import PanelViewModel, TkPanel
from .resources import application_icon_path
from .tray import PystrayTray, TrayController


class DesktopApplication:
    def __init__(
        self,
        *,
        runtime: Any,
        store: Any,
        config_repository: JsonConfigRepository,
        logs_directory: Path,
    ) -> None:
        self.runtime = runtime
        icon_path = application_icon_path()
        self.panel = TkPanel(
            PanelViewModel(
                health=runtime.health,
                store=store,
                config_repository=config_repository,
                logs_directory=logs_directory,
            ),
            icon_path=icon_path,
        )
        self.tray = PystrayTray(
            TrayController(runtime, open_panel=self.panel.show, shutdown=self._shutdown),
            icon_path=icon_path,
        )
        self._thread = threading.Thread(target=runtime.run_forever, name="watchdog-monitor")

    def run(self) -> None:
        self._thread.start()
        try:
            self.tray.run_detached()
            self.panel.run()
        finally:
            self.runtime.stop()
            self.tray.stop()
            self._thread.join(timeout=10)

    def _shutdown(self) -> None:
        self.tray.stop()
        self.panel.shutdown()
