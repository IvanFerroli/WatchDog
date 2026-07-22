"""Panel view-model and small tkinter surface."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Protocol

from watchdog.application.configuration import JsonConfigRepository
from watchdog.application.health import HealthMonitor
from watchdog.core.config import AppConfig
from watchdog.core.models import OperationalEvent


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
            history=tuple(self.store.list_events(limit=history_limit)),
            logs_directory=self.logs_directory,
        )

    def save_preferences(
        self,
        *,
        poll_interval_ms: int,
        notification_enabled: bool,
        sound_enabled: bool,
        start_with_windows: bool,
    ) -> AppConfig:
        current = self.config_repository.load()
        candidate = replace(
            current,
            watchdog=replace(
                current.watchdog,
                poll_interval_ms=poll_interval_ms,
                start_with_windows=start_with_windows,
            ),
            notification=replace(
                current.notification,
                enabled=notification_enabled,
                sound_enabled=sound_enabled,
            ),
        )
        validated = AppConfig.from_dict(candidate.to_dict())
        self.config_repository.save(validated)
        return validated


class TkPanel:
    """A real but deliberately small tkinter diagnostics panel."""

    def __init__(self, view_model: PanelViewModel) -> None:
        import tkinter as tk
        from tkinter import ttk

        self._tk = tk
        self._root = tk.Tk()
        self._root.title("AlwaysTrack Watchdog")
        self._root.protocol("WM_DELETE_WINDOW", self.hide)
        self._view_model = view_model
        self._status = tk.StringVar()
        self._details = tk.StringVar()
        self._error = tk.StringVar()
        frame = ttk.Frame(self._root, padding=12)
        frame.grid(sticky="nsew")
        ttk.Label(frame, textvariable=self._status, font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(frame, textvariable=self._details).grid(row=1, column=0, sticky="w")
        ttk.Label(frame, textvariable=self._error).grid(row=2, column=0, sticky="w")
        self._history = tk.Listbox(frame, width=78, height=12)
        self._history.grid(row=3, column=0, pady=(8, 0), sticky="nsew")
        ttk.Label(frame, text=f"Logs: {view_model.logs_directory}").grid(
            row=4, column=0, pady=(8, 0), sticky="w"
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

    def refresh(self) -> None:
        snapshot = self._view_model.snapshot()
        self._status.set(f"Status: {snapshot.status} · Slack: {snapshot.slack_status}")
        last_scan = (
            snapshot.last_successful_scan_at.isoformat()
            if snapshot.last_successful_scan_at
            else "—"
        )
        self._details.set(
            f"Última leitura: {last_scan} · Itens: {snapshot.items_read_last_scan} · "
            f"Novos: {snapshot.new_items_last_scan} · "
            f"Diretas hoje: {snapshot.direct_mentions_today}"
        )
        self._error.set(f"Último erro: {snapshot.last_error_code or 'Nenhum'}")
        self._history.delete(0, self._tk.END)
        for event in snapshot.history:
            context = " · ".join(part for part in (event.actor, event.location) if part)
            preview = event.body or event.title or "Sem trecho disponível"
            self._history.insert(self._tk.END, f"{context}: {preview}" if context else preview)
        self._root.after(1_000, self.refresh)
