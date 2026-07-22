from __future__ import annotations

from pathlib import Path

import pytest

from watchdog.application.configuration import JsonConfigRepository
from watchdog.application.health import HealthMonitor
from watchdog.core.config import ConfigError
from watchdog.ui.panel import PanelViewModel
from watchdog.ui.tray import TrayController


class FakeStore:
    def list_events(self, *, limit: int = 100) -> list[object]:
        return []


class FakeRuntime:
    def __init__(self) -> None:
        self.paused = False
        self.stopped = False
        self.health = HealthMonitor()

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def stop(self) -> None:
        self.stopped = True


def test_tray_commands_control_runtime() -> None:
    runtime = FakeRuntime()
    calls: list[str] = []
    controller = TrayController(
        runtime,
        open_panel=lambda: calls.append("open"),
        shutdown=lambda: calls.append("shutdown"),
    )

    controller.toggle_pause()
    assert runtime.paused
    controller.toggle_pause()
    assert not runtime.paused
    controller.open_panel()
    controller.exit()

    assert runtime.stopped
    assert calls == ["open", "shutdown"]


def test_panel_view_model_persists_valid_preferences(tmp_path: Path) -> None:
    repository = JsonConfigRepository(tmp_path / "config.json")
    view_model = PanelViewModel(
        health=HealthMonitor(),
        store=FakeStore(),
        config_repository=repository,
        logs_directory=tmp_path / "logs",
    )

    saved = view_model.save_preferences(
        poll_interval_ms=2_000,
        notification_enabled=False,
        sound_enabled=False,
        start_with_windows=True,
    )

    assert saved.watchdog.poll_interval_ms == 2_000
    assert repository.load().notification.enabled is False
    with pytest.raises(ConfigError):
        view_model.save_preferences(
            poll_interval_ms=0,
            notification_enabled=True,
            sound_enabled=True,
            start_with_windows=False,
        )
