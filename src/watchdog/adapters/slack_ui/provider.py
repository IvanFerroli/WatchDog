"""Slack process/window discovery isolated from the application runtime."""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from .errors import AdapterErrorCode, SlackAdapterError


@dataclass(slots=True)
class SlackWindow:
    native: Any
    process_name: str
    process_id: int | None = None


class WindowProvider(Protocol):
    def find_window(self, process_names: tuple[str, ...]) -> SlackWindow: ...

    def is_alive(self, window: SlackWindow) -> bool: ...


class PywinautoWindowProvider:
    """Discover a top-level Slack window; import pywinauto only on Windows."""

    def __init__(
        self,
        application_factory: Callable[..., Any] | None = None,
        *,
        desktop_factory: Callable[..., Any] | None = None,
    ) -> None:
        self._application_factory = application_factory
        self._desktop_factory = desktop_factory

    def _factory(self) -> Callable[..., Any]:
        if self._application_factory is not None:
            return self._application_factory
        if sys.platform != "win32":
            raise SlackAdapterError(
                AdapterErrorCode.UNSUPPORTED_PLATFORM,
                "Windows UI Automation is available only on Windows",
                retriable=False,
            )
        try:
            from pywinauto import Application
        except ImportError as exc:
            raise SlackAdapterError(
                AdapterErrorCode.SLACK_NOT_ACCESSIBLE,
                "pywinauto is not installed",
                retriable=False,
            ) from exc
        return Application

    def find_window(self, process_names: tuple[str, ...]) -> SlackWindow:
        if not process_names:
            raise ValueError("process_names must not be empty")
        if self._application_factory is None:
            return self._find_desktop_window(process_names)
        factory = self._factory()
        had_access_error = False
        for process_name in process_names:
            try:
                app = factory(backend="uia").connect(path=process_name)
                native = app.top_window()
                if native.exists(timeout=0.5):
                    process_id = _safe_process_id(native)
                    return SlackWindow(native, process_name, process_id)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as exc:
                if type(exc).__name__ not in {"ElementNotFoundError", "ProcessNotFoundError"}:
                    had_access_error = True
        code = (
            AdapterErrorCode.SLACK_NOT_ACCESSIBLE
            if had_access_error
            else AdapterErrorCode.SLACK_NOT_RUNNING
        )
        raise SlackAdapterError(code, "Slack window was not found")

    def _find_desktop_window(self, process_names: tuple[str, ...]) -> SlackWindow:
        if sys.platform != "win32":
            raise SlackAdapterError(
                AdapterErrorCode.UNSUPPORTED_PLATFORM,
                "Windows UI Automation is available only on Windows",
                retriable=False,
            )
        try:
            if self._desktop_factory is None:
                from pywinauto import Desktop

                desktop_factory = Desktop
            else:
                desktop_factory = self._desktop_factory

            desktop = desktop_factory(backend="uia")
            windows = desktop.windows(title_re="(?i).*slack.*", visible_only=False)
            if not windows:
                raise SlackAdapterError(
                    AdapterErrorCode.SLACK_NOT_RUNNING,
                    "Slack window was not found",
                )
            selected = max(
                windows,
                key=lambda window: (window.is_visible(), _window_area(window)),
            )
            native = desktop.window(handle=selected.handle)
            return SlackWindow(
                native,
                process_names[0],
                int(selected.element_info.process_id),
            )
        except SlackAdapterError:
            raise
        except Exception as exc:
            raise SlackAdapterError(
                AdapterErrorCode.SLACK_NOT_ACCESSIBLE,
                "Slack window could not be enumerated",
            ) from exc

    def is_alive(self, window: SlackWindow) -> bool:
        try:
            return bool(window.native.exists(timeout=0))
        except Exception:
            return False


class SlackWindowLifecycle:
    """Cache a live window and reconnect after loss without leaking native objects."""

    def __init__(self, provider: WindowProvider, process_names: tuple[str, ...]) -> None:
        if not process_names:
            raise ValueError("process_names must not be empty")
        self._provider = provider
        self._process_names = tuple(process_names)
        self._current: SlackWindow | None = None

    def current(self) -> SlackWindow:
        if self._current is not None and self._provider.is_alive(self._current):
            return self._current
        self._current = None
        self._current = self._provider.find_window(self._process_names)
        return self._current

    def invalidate(self) -> None:
        self._current = None


def _safe_process_id(native: Any) -> int | None:
    try:
        value = native.process_id()
        return int(value)
    except Exception:
        return None


def _window_area(window: Any) -> int:
    rectangle = window.rectangle()
    return max(0, rectangle.width()) * max(0, rectangle.height())
