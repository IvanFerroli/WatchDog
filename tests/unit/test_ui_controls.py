from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

import watchdog.ui.panel as panel_module
from watchdog.adapters.slack_ui import SlackOpenResult
from watchdog.application.configuration import JsonConfigRepository
from watchdog.application.health import HealthMonitor
from watchdog.core.config import ConfigError
from watchdog.core.models import EventCategory, EventPriority, OperationalEvent
from watchdog.ui.panel import (
    PanelViewModel,
    TkPanel,
    _compact_preview,
    _filter_history,
    _history_row,
)
from watchdog.ui.tray import TrayController


class FakeStore:
    def __init__(self, events: list[OperationalEvent] | None = None) -> None:
        self.events = events or []

    def list_events(self, *, limit: int = 100) -> list[OperationalEvent]:
        return self.events[:limit]


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


class FakeHistorySelection:
    def __init__(self, item_id: str | None) -> None:
        self.item_id = item_id

    def selection(self) -> tuple[str, ...]:
        return (self.item_id,) if self.item_id else ()


class FakeStringVar:
    def __init__(self, value: str = "") -> None:
        self.value = value

    def set(self, value: str) -> None:
        self.value = value

    def get(self) -> str:
        return self.value


class FakeHistoryTree:
    def __init__(self) -> None:
        self.items: dict[str, tuple[str, str, str]] = {}
        self.selected: tuple[str, ...] = ()
        self.focused: str | None = None

    def get_children(self) -> tuple[str, ...]:
        return tuple(self.items)

    def delete(self, item_id: str) -> None:
        del self.items[item_id]

    def insert(
        self,
        _parent: str,
        _index: str,
        *,
        iid: str,
        values: tuple[str, str, str],
    ) -> None:
        self.items[iid] = values

    def selection(self) -> tuple[str, ...]:
        return self.selected

    def selection_set(self, item_id: str) -> None:
        self.selected = (item_id,)

    def focus(self, item_id: str) -> None:
        self.focused = item_id


class FakeAfterRoot:
    def __init__(self) -> None:
        self.pending: dict[str, tuple[object, tuple[object, ...]]] = {}
        self._sequence = 0

    def after(self, delay: int, callback: object, *args: object) -> str:
        self._sequence += 1
        callback_id = f"after-{self._sequence}"
        if delay == 0:
            callback(*args)
        else:
            self.pending[callback_id] = (callback, args)
        return callback_id

    def after_cancel(self, callback_id: str) -> None:
        self.pending.pop(callback_id, None)

    def run_pending(self) -> None:
        pending = tuple(self.pending.values())
        self.pending.clear()
        for callback, args in pending:
            callback(*args)


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
        direct_mentions_enabled=False,
        direct_messages_enabled=True,
        sound_enabled=False,
        start_with_windows=True,
    )

    assert saved.watchdog.poll_interval_ms == 2_000
    assert repository.load().notification.enabled is False
    assert repository.load().notification.direct_mentions_enabled is False
    assert repository.load().notification.direct_messages_enabled is True
    assert repository.load_notification_preferences() == saved.notification

    alerts = view_model.save_alert_preferences(
        direct_mentions_enabled=True,
        direct_messages_enabled=False,
    )
    assert alerts.notification.enabled is True
    assert alerts.notification.direct_mentions_enabled is True
    assert alerts.notification.direct_messages_enabled is False
    assert alerts.watchdog.poll_interval_ms == 2_000

    with pytest.raises(ConfigError):
        view_model.save_preferences(
            poll_interval_ms=0,
            notification_enabled=True,
            direct_mentions_enabled=True,
            direct_messages_enabled=True,
            sound_enabled=True,
            start_with_windows=False,
        )


def test_panel_history_follows_enabled_popup_categories_immediately(tmp_path: Path) -> None:
    events = [
        _event("mention", EventCategory.DIRECT_MENTION),
        _event("dm", EventCategory.DIRECT_MESSAGE),
        _event(
            "false-dm",
            EventCategory.DIRECT_MESSAGE,
            source="windows.user_notification_listener.slack",
            actor="solicitação-cancelamento-assinatura",
        ),
        _event("group", EventCategory.GROUP_MENTION),
        _event("unknown", EventCategory.UNKNOWN),
    ]
    view_model = PanelViewModel(
        health=HealthMonitor(),
        store=FakeStore(events),
        config_repository=JsonConfigRepository(tmp_path / "config.json"),
        logs_directory=tmp_path / "logs",
    )

    assert [event.id for event in view_model.snapshot().history] == ["mention", "dm"]

    view_model.save_alert_preferences(
        direct_mentions_enabled=False,
        direct_messages_enabled=True,
    )
    assert [event.id for event in view_model.snapshot().history] == ["dm"]

    view_model.save_alert_preferences(
        direct_mentions_enabled=False,
        direct_messages_enabled=False,
    )
    assert view_model.snapshot().history == ()


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


@pytest.mark.parametrize(
    ("query", "expected_id"),
    [
        ("jose", "mention"),
        ("operaÇAO", "mention"),
        ("solicitacao urgente", "mention"),
        ("mensagem privada", "dm"),
    ],
)
def test_panel_history_search_is_instant_normalized_and_accent_insensitive(
    query: str,
    expected_id: str,
) -> None:
    history = (
        _event(
            "mention",
            EventCategory.DIRECT_MENTION,
            actor="José",
            location="Operação",
            title="Solicitação",
            body="urgente",
        ),
        _event(
            "dm",
            EventCategory.DIRECT_MESSAGE,
            actor="Ana",
            body="Mensagem   privada",
        ),
    )

    visible = _filter_history(history, query=query, event_type="Todos")

    assert [event.id for event in visible] == [expected_id]


def test_panel_history_type_filter_is_fail_closed_to_enabled_event_types() -> None:
    history = (
        _event("mention", EventCategory.DIRECT_MENTION),
        _event("dm", EventCategory.DIRECT_MESSAGE),
        _event("group", EventCategory.GROUP_MENTION),
    )

    mentions = _filter_history(history, query="", event_type="Menções")
    dms = _filter_history(history, query="", event_type="DMs")

    assert [event.id for event in mentions] == ["mention"]
    assert [event.id for event in dms] == ["dm"]


def test_panel_opens_selected_event_only_from_explicit_user_action(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    event = _event("mention", EventCategory.DIRECT_MENTION)
    opened: list[OperationalEvent] = []
    panel = object.__new__(TkPanel)
    panel._history = FakeHistorySelection("row-1")
    panel._history_events = {"row-1": event}
    panel._event_opener = lambda selected: opened.append(selected) or SlackOpenResult.EXACT_EVENT
    panel._history_action_status = FakeStringVar()
    panel._event_open_in_progress = False
    panel._root = FakeAfterRoot()
    monkeypatch.setattr(panel_module, "_start_background", lambda callback: callback())

    assert opened == []
    panel._open_selected_history_event()

    assert opened == [event]
    assert panel._history_action_status.value == "Atividade exata aberta no Slack"
    assert panel._event_open_in_progress is False


def test_panel_signals_when_only_the_generic_slack_fallback_was_opened(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    panel = object.__new__(TkPanel)
    panel._history = FakeHistorySelection("row-1")
    panel._history_events = {"row-1": _event("dm", EventCategory.DIRECT_MESSAGE)}
    panel._event_opener = lambda _event: SlackOpenResult.GENERIC
    panel._history_action_status = FakeStringVar()
    panel._event_open_in_progress = False
    panel._root = FakeAfterRoot()
    monkeypatch.setattr(panel_module, "_start_background", lambda callback: callback())

    panel._open_selected_history_event()

    assert panel._history_action_status.value == "Slack aberto; conversa não localizada"


def test_panel_ignores_open_action_without_a_selected_event() -> None:
    opened: list[str] = []
    panel = object.__new__(TkPanel)
    panel._history = FakeHistorySelection(None)
    panel._history_events = {}
    panel._event_opener = opened.append
    panel._history_action_status = FakeStringVar()

    panel._open_selected_history_event()

    assert opened == []


def test_panel_reports_event_open_failure_without_crashing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    panel = object.__new__(TkPanel)
    panel._history = FakeHistorySelection("row-1")
    panel._history_events = {"row-1": _event("mention", EventCategory.DIRECT_MENTION)}
    panel._event_opener = lambda _event: (_ for _ in ()).throw(OSError("synthetic"))
    panel._history_action_status = FakeStringVar()
    panel._event_open_in_progress = False
    panel._root = FakeAfterRoot()
    monkeypatch.setattr(panel_module, "_start_background", lambda callback: callback())

    panel._open_selected_history_event()

    assert panel._history_action_status.value == "Não foi possível abrir o Slack"


def test_panel_stops_showing_open_progress_after_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    panel = object.__new__(TkPanel)
    panel._history = FakeHistorySelection("row-1")
    panel._history_events = {"row-1": _event("dm", EventCategory.DIRECT_MESSAGE)}
    panel._event_opener = lambda _event: SlackOpenResult.CONVERSATION
    panel._history_action_status = FakeStringVar()
    panel._event_open_in_progress = False
    panel._event_open_generation = 0
    panel._event_open_timeout_id = None
    panel._root = FakeAfterRoot()
    monkeypatch.setattr(panel_module, "_start_background", lambda _callback: None)

    panel._open_selected_history_event()
    assert panel._event_open_in_progress is True
    assert panel._history_action_status.value == "Abrindo no Slack…"

    panel._root.run_pending()

    assert panel._event_open_in_progress is False
    assert panel._history_action_status.value == "O Slack demorou demais; tente novamente"


def test_panel_refresh_preserves_selection_and_row_to_event_mapping() -> None:
    mention = _event(
        "mention",
        EventCategory.DIRECT_MENTION,
        body="primeira versão",
    )
    dm = _event("dm", EventCategory.DIRECT_MESSAGE)
    panel = object.__new__(TkPanel)
    panel._history = FakeHistoryTree()
    panel._history_rows = ()
    panel._history_events = {}
    panel._all_history = ()
    panel._history_query = FakeStringVar()
    panel._history_type = FakeStringVar("Todos")
    panel._history_count = FakeStringVar()
    panel._history_empty = FakeStringVar()
    panel._tk = type("FakeTk", (), {"END": "end"})()

    panel._render_history((mention, dm))
    panel._history.selection_set("mention")
    updated_mention = _event(
        "mention",
        EventCategory.DIRECT_MENTION,
        body="versão atualizada",
    )

    panel._render_history((updated_mention, dm))

    assert panel._history.selection() == ("mention",)
    assert panel._history.focused == "mention"
    assert panel._history_events["mention"] is updated_mention
    assert panel._history_count.value == "2 atividades"

    panel._history_query.set("sem correspondência")
    panel._render_history((updated_mention, dm))

    assert panel._history.items == {}
    assert panel._history_count.value == "0 de 2 atividades"
    assert panel._history_empty.value == ("Nenhum resultado para a busca e o filtro atuais")


def _event(
    event_id: str,
    category: EventCategory,
    *,
    actor: str | None = None,
    location: str | None = None,
    title: str | None = None,
    body: str | None = None,
    source: str = "slack",
) -> OperationalEvent:
    return OperationalEvent(
        id=event_id,
        source=source,
        category=category,
        priority=EventPriority.HIGH,
        observed_at=datetime(2026, 7, 22, 18, 30, tzinfo=UTC),
        deduplication_key=f"dedupe-{event_id}",
        classifier_version="test-v1",
        actor=actor,
        location=location,
        title=title,
        body=body,
    )
