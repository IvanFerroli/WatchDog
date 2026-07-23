"""Panel view-model and small tkinter surface."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Protocol

from watchdog.application.configuration import JsonConfigRepository
from watchdog.application.health import HealthMonitor
from watchdog.core.config import AppConfig
from watchdog.core.models import EventCategory, OperationalEvent

_STATUS_LABELS = {
    "STARTING": "Iniciando",
    "MONITORING": "Monitorando",
    "SLACK_NOT_RUNNING": "Slack fechado",
    "SLACK_NOT_ACCESSIBLE": "Slack inacessível",
    "ACTIVITY_NOT_FOUND": "Recuperando tela de menções",
    "DEGRADED": "Funcionamento parcial",
    "PAUSED": "Pausado",
    "ERROR": "Erro",
}

_ERROR_LABELS = {
    "SLACK_NOT_RUNNING": "Slack não está aberto",
    "SLACK_NOT_ACCESSIBLE": "Slack não está acessível",
    "WINDOW_LOST": "Janela do Slack foi perdida",
    "ACTIVITY_NOT_FOUND": "Tela de menções não encontrada",
    "STRUCTURE_CHANGED": "A interface do Slack mudou",
    "READ_FAILED": "Não foi possível ler o Slack",
    "SOURCE_PARTIAL_FAILURE": "Uma fonte está indisponível; as demais continuam ativas",
    "WINDOWS_NOTIFICATIONS_ACCESS_DENIED": "Acesso às notificações do Windows foi negado",
    "WINDOWS_NOTIFICATIONS_READ_FAILED": "Não foi possível ler as notificações do Windows",
}

_CATEGORY_LABELS = {
    EventCategory.DIRECT_MENTION: "Menção direta",
    EventCategory.GROUP_MENTION: "Menção de grupo",
    EventCategory.DIRECT_MESSAGE: "Mensagem direta",
    EventCategory.THREAD_REPLY: "Resposta em thread",
    EventCategory.REACTION: "Reação",
    EventCategory.UNKNOWN: "Outro evento",
}

_SLACK_RAW_MARKERS = tuple(
    sorted(
        (
            "Menção ao grupo na conversa do canal",
            "Menção na conversa do canal",
            "Menção ao canal",
            "Menção no canal",
        ),
        key=len,
        reverse=True,
    )
)
_WHITESPACE = re.compile(r"\s+")


class HistoryStore(Protocol):
    def list_events(self, *, limit: int = 100) -> list[OperationalEvent]: ...


@dataclass(frozen=True, slots=True)
class PanelSnapshot:
    status: str
    slack_status: str
    last_successful_scan_at: datetime | None
    items_read_last_scan: int
    new_items_last_scan: int
    direct_mentions_today: int
    last_error_code: str | None
    history: tuple[OperationalEvent, ...]
    logs_directory: Path


class PanelViewModel:
    def __init__(
        self,
        *,
        health: HealthMonitor,
        store: HistoryStore,
        config_repository: JsonConfigRepository,
        logs_directory: Path,
    ) -> None:
        self.health = health
        self.store = store
        self.config_repository = config_repository
        self.logs_directory = logs_directory

    def snapshot(self, *, history_limit: int = 50) -> PanelSnapshot:
        health = self.health.snapshot()
        preferences = self.config_repository.load_notification_preferences()
        enabled_categories: set[EventCategory] = set()
        if preferences.enabled:
            if preferences.direct_mentions_enabled:
                enabled_categories.add(EventCategory.DIRECT_MENTION)
            if preferences.direct_messages_enabled:
                enabled_categories.add(EventCategory.DIRECT_MESSAGE)
        history = tuple(
            event
            for event in self.store.list_events(limit=history_limit)
            if event.category in enabled_categories
        )
        slack_status = {
            "SLACK_NOT_RUNNING": "Não detectado",
            "SLACK_NOT_ACCESSIBLE": "Inacessível",
        }.get(health.state.value, "Detectado" if health.last_successful_scan_at else "Aguardando")
        return PanelSnapshot(
            status=health.state.value,
            slack_status=slack_status,
            last_successful_scan_at=health.last_successful_scan_at,
            items_read_last_scan=health.items_read_last_scan,
            new_items_last_scan=health.new_items_last_scan,
            direct_mentions_today=health.direct_mentions_today,
            last_error_code=health.last_error_code,
            history=history,
            logs_directory=self.logs_directory,
        )

    def load_preferences(self) -> AppConfig:
        return self.config_repository.load()

    def save_preferences(
        self,
        *,
        poll_interval_ms: int,
        notification_enabled: bool,
        direct_mentions_enabled: bool,
        direct_messages_enabled: bool,
        sound_enabled: bool,
        start_with_windows: bool,
    ) -> AppConfig:
        def update(current: AppConfig) -> AppConfig:
            return replace(
                current,
                watchdog=replace(
                    current.watchdog,
                    poll_interval_ms=poll_interval_ms,
                    start_with_windows=start_with_windows,
                ),
                notification=replace(
                    current.notification,
                    enabled=notification_enabled,
                    direct_mentions_enabled=direct_mentions_enabled,
                    direct_messages_enabled=direct_messages_enabled,
                    sound_enabled=sound_enabled,
                ),
            )

        return self.config_repository.update(update)

    def save_alert_preferences(
        self,
        *,
        direct_mentions_enabled: bool,
        direct_messages_enabled: bool,
    ) -> AppConfig:
        def update(current: AppConfig) -> AppConfig:
            return replace(
                current,
                notification=replace(
                    current.notification,
                    enabled=direct_mentions_enabled or direct_messages_enabled,
                    direct_mentions_enabled=direct_mentions_enabled,
                    direct_messages_enabled=direct_messages_enabled,
                ),
            )

        return self.config_repository.update(update)


class TkPanel:
    """A compact tkinter status and event-history panel."""

    def __init__(self, view_model: PanelViewModel, *, icon_path: Path | None = None) -> None:
        import tkinter as tk
        from tkinter import ttk

        self._tk = tk
        self._root = tk.Tk()
        self._root.title("AlwaysTrack Watchdog")
        self._root.geometry("820x530")
        self._root.minsize(700, 460)
        self._root.protocol("WM_DELETE_WINDOW", self.hide)
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)
        self._view_model = view_model
        self._icon_image = None
        if icon_path is not None and icon_path.is_file():
            try:
                self._icon_image = tk.PhotoImage(file=str(icon_path))
                self._root.iconphoto(True, self._icon_image)
            except tk.TclError:
                self._icon_image = None

        preferences = view_model.load_preferences()
        self._status = tk.StringVar()
        self._details = tk.StringVar()
        self._error = tk.StringVar()
        self._direct_mentions_enabled = tk.BooleanVar(
            value=(
                preferences.notification.enabled
                and preferences.notification.direct_mentions_enabled
            )
        )
        self._direct_messages_enabled = tk.BooleanVar(
            value=(
                preferences.notification.enabled
                and preferences.notification.direct_messages_enabled
            )
        )
        self._preference_status = tk.StringVar()
        frame = ttk.Frame(self._root, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(4, weight=1)
        ttk.Label(frame, textvariable=self._status, font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(frame, textvariable=self._details, wraplength=740).grid(
            row=1, column=0, pady=(4, 0), sticky="w"
        )
        ttk.Label(frame, textvariable=self._error, wraplength=740).grid(
            row=2, column=0, pady=(2, 0), sticky="w"
        )
        ttk.Label(frame, text="Atividades recentes", font=("Segoe UI", 10, "bold")).grid(
            row=3, column=0, pady=(12, 4), sticky="w"
        )

        history_frame = ttk.Frame(frame)
        history_frame.grid(row=4, column=0, sticky="nsew")
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        self._history = ttk.Treeview(
            history_frame,
            columns=("when", "category", "summary"),
            show="headings",
            selectmode="browse",
            height=10,
        )
        self._history.heading("when", text="Data e hora")
        self._history.heading("category", text="Tipo")
        self._history.heading("summary", text="Resumo")
        self._history.column("when", width=125, minwidth=115, stretch=False)
        self._history.column("category", width=135, minwidth=120, stretch=False)
        self._history.column("summary", width=450, minwidth=240, stretch=True)
        self._history.grid(row=0, column=0, sticky="nsew")
        self._history_rows: tuple[tuple[str, str, str], ...] = ()
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self._history.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._history.configure(yscrollcommand=scrollbar.set)

        alert_frame = ttk.LabelFrame(frame, text="Alertas popup", padding=(10, 8))
        alert_frame.grid(row=5, column=0, pady=(10, 0), sticky="ew")
        alert_frame.columnconfigure(2, weight=1)
        ttk.Checkbutton(
            alert_frame,
            text="Menções diretas",
            variable=self._direct_mentions_enabled,
        ).grid(row=0, column=0, padx=(0, 16), sticky="w")
        ttk.Checkbutton(
            alert_frame,
            text="Mensagens privadas (DM)",
            variable=self._direct_messages_enabled,
        ).grid(row=0, column=1, padx=(0, 16), sticky="w")
        ttk.Label(alert_frame, textvariable=self._preference_status).grid(
            row=0, column=2, padx=(0, 8), sticky="e"
        )
        ttk.Button(alert_frame, text="Salvar", command=self._save_alert_preferences).grid(
            row=0, column=3, sticky="e"
        )
        ttk.Label(frame, text=f"Logs: {view_model.logs_directory}").grid(
            row=6, column=0, pady=(8, 0), sticky="w"
        )
        self.refresh()

    def run(self) -> None:
        self._root.mainloop()

    def show(self) -> None:
        self._root.after(0, self._root.deiconify)

    def hide(self) -> None:
        self._root.withdraw()

    def shutdown(self) -> None:
        self._root.after(0, self._root.destroy)

    def _save_alert_preferences(self) -> None:
        try:
            self._view_model.save_alert_preferences(
                direct_mentions_enabled=self._direct_mentions_enabled.get(),
                direct_messages_enabled=self._direct_messages_enabled.get(),
            )
        except (OSError, ValueError):
            self._preference_status.set("Não foi possível salvar")
        else:
            self._preference_status.set("Preferências salvas")
            self._refresh_history()

    def refresh(self) -> None:
        snapshot = self._view_model.snapshot()
        status = _STATUS_LABELS.get(snapshot.status, snapshot.status)
        self._status.set(f"{status}  •  Slack {snapshot.slack_status.lower()}")
        last_scan = _format_datetime(snapshot.last_successful_scan_at)
        self._details.set(
            f"Última leitura: {last_scan}  •  Lidos: {snapshot.items_read_last_scan}  •  "
            f"Novos: {snapshot.new_items_last_scan}  •  "
            f"Alertas enviados hoje: {snapshot.direct_mentions_today}"
        )
        error = _ERROR_LABELS.get(
            snapshot.last_error_code or "",
            snapshot.last_error_code or "Nenhum",
        )
        prefix = "Último erro recuperado" if snapshot.status == "MONITORING" else "Último erro"
        self._error.set(f"{prefix}: {error}")
        self._render_history(snapshot.history)
        self._root.after(1_000, self.refresh)

    def _refresh_history(self) -> None:
        self._render_history(self._view_model.snapshot().history)

    def _render_history(self, history: tuple[OperationalEvent, ...]) -> None:
        history_rows = tuple(_history_row(event) for event in history)
        if history_rows != self._history_rows:
            for item_id in self._history.get_children():
                self._history.delete(item_id)
            for row in history_rows:
                self._history.insert("", self._tk.END, values=row)
            self._history_rows = history_rows


def _history_row(event: OperationalEvent) -> tuple[str, str, str]:
    occurred_at = event.occurred_at or event.observed_at
    category = _CATEGORY_LABELS.get(event.category, event.category.value)
    context = " · ".join(_clean_text(value) for value in (event.actor, event.location) if value)
    preview = _compact_preview(event.title or event.body)
    summary = " — ".join(value for value in (context, preview) if value)
    return _format_datetime(occurred_at), category, summary or "Sem resumo disponível"


def _compact_preview(value: str | None, *, limit: int = 100) -> str:
    text = _clean_text(value)
    if not text:
        return ""

    # The accessible name of a Slack card glues its title, badge and metadata.
    # Keep only the useful prefix instead of exposing the entire raw UIA string.
    marker_positions = (text.find(marker) for marker in _SLACK_RAW_MARKERS)
    positions = [position for position in marker_positions if position >= 0]
    if positions:
        text = text[: min(positions)].strip(" -·:")
    if not text:
        return ""
    if len(text) > limit:
        return f"{text[: limit - 1].rstrip()}…"
    return text


def _clean_text(value: str | None) -> str:
    return _WHITESPACE.sub(" ", str(value or "")).strip()


def _format_datetime(value: datetime | None) -> str:
    if value is None:
        return "Ainda não realizada"
    return value.astimezone().strftime("%d/%m/%Y %H:%M")
