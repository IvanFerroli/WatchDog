from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from watchdog.application.configuration import JsonConfigRepository
from watchdog.application.health import HealthMonitor
from watchdog.core.config import ConfigError
from watchdog.core.models import EventCategory, EventPriority, OperationalEvent
from watchdog.ui.panel import PanelViewModel, _compact_preview, _history_row
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


def test_panel_history_row_translates_category_and_removes_raw_slack_card_text() -> None:
    event = OperationalEvent(
        id="event-1",
        source="slack.desktop.uia",
        category=EventCategory.DIRECT_MENTION,
        priority=EventPriority.HIGH,
        observed_at=datetime(2026, 7, 22, 18, 30, tzinfo=UTC),
        deduplication_key="dedupe-1",
        classifier_version="test-v1",
        body=(
            "Solicitação de Reenvio"
            "Menção na conversa do canal"
            "solicitação-reenvio Quarta-feira conteúdo bruto"
        ),
    )

    when, category, summary = _history_row(event)

    assert when.startswith("22/07/2026 ")
    assert category == "Menção direta"
    assert summary == "Solicitação de Reenvio"


def test_panel_compacts_whitespace_and_long_previews() -> None:
    preview = _compact_preview("  uma   mensagem\ncom detalhes adicionais  ", limit=24)

    assert preview == "uma mensagem com detalh…"
    assert len(preview) == 24


def test_panel_omits_card_text_when_it_only_contains_slack_metadata() -> None:
    assert _compact_preview("Menção ao canal projeto interno dados brutos") == ""
