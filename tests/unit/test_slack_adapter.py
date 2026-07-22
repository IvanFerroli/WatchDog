from __future__ import annotations

from datetime import UTC, datetime

import pytest

from watchdog.adapters.slack_ui import (
    ActivitySelectors,
    AdapterErrorCode,
    PywinautoActivityReader,
    PywinautoWindowProvider,
    SlackAdapterError,
    SlackUIAdapter,
    SlackWindow,
    SlackWindowLifecycle,
)
from watchdog.adapters.slack_ui import provider as provider_module


class FakeNative:
    def exists(self, timeout: float = 0) -> bool:
        return True


class FakeProvider:
    def __init__(self) -> None:
        self.window = SlackWindow(FakeNative(), "slack.exe", 42)
        self.alive = True
        self.find_calls = 0

    def find_window(self, process_names: tuple[str, ...]) -> SlackWindow:
        self.find_calls += 1
        return self.window

    def is_alive(self, window: SlackWindow) -> bool:
        return self.alive


class FakeReader:
    adapter_version = "fake-v1"

    def read(self, window: SlackWindow) -> list[object]:
        return []


def test_window_lifecycle_reconnects_after_loss() -> None:
    provider = FakeProvider()
    lifecycle = SlackWindowLifecycle(provider, ("slack.exe",))
    adapter = SlackUIAdapter(lifecycle, FakeReader())

    adapter.observe()
    adapter.observe()
    assert provider.find_calls == 1

    provider.alive = False
    adapter.observe()
    assert provider.find_calls == 2


def test_pywinauto_provider_distinguishes_process_absence() -> None:
    process_not_found = type("ProcessNotFoundError", (RuntimeError,), {})

    class MissingApplication:
        def connect(self, **_: str) -> MissingApplication:
            raise process_not_found()

    provider = PywinautoWindowProvider(lambda **_: MissingApplication())

    with pytest.raises(SlackAdapterError) as error:
        provider.find_window(("slack.exe",))

    assert error.value.code is AdapterErrorCode.SLACK_NOT_RUNNING


class FakeRectangle:
    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height

    def width(self) -> int:
        return self._width

    def height(self) -> int:
        return self._height


class FakeDesktopWindow:
    def __init__(self, handle: int, *, visible: bool, width: int, height: int, pid: int) -> None:
        self.handle = handle
        self._visible = visible
        self._rectangle = FakeRectangle(width, height)
        self.element_info = type("ElementInfo", (), {"process_id": pid})()

    def is_visible(self) -> bool:
        return self._visible

    def rectangle(self) -> FakeRectangle:
        return self._rectangle


class FakeDesktop:
    def __init__(self, windows: list[FakeDesktopWindow]) -> None:
        self._windows = windows

    def windows(self, **_: object) -> list[FakeDesktopWindow]:
        return self._windows

    def window(self, *, handle: int) -> FakeNative:
        assert handle == 2
        return FakeNative()


def test_pywinauto_provider_selects_largest_visible_desktop_window(monkeypatch) -> None:
    desktop = FakeDesktop(
        [
            FakeDesktopWindow(1, visible=False, width=2000, height=1200, pid=10),
            FakeDesktopWindow(2, visible=True, width=800, height=600, pid=20),
        ]
    )
    monkeypatch.setattr(provider_module.sys, "platform", "win32")
    provider = PywinautoWindowProvider(desktop_factory=lambda **_: desktop)

    window = provider.find_window(("slack.exe",))

    assert window.process_id == 20
    assert window.process_name == "slack.exe"
    assert isinstance(window.native, FakeNative)


def test_pywinauto_provider_reports_missing_desktop_window(monkeypatch) -> None:
    monkeypatch.setattr(provider_module.sys, "platform", "win32")
    provider = PywinautoWindowProvider(desktop_factory=lambda **_: FakeDesktop([]))

    with pytest.raises(SlackAdapterError) as error:
        provider.find_window(("slack.exe",))

    assert error.value.code is AdapterErrorCode.SLACK_NOT_RUNNING


def test_activity_requires_complete_spike_selectors() -> None:
    reader = PywinautoActivityReader(ActivitySelectors())

    with pytest.raises(SlackAdapterError) as error:
        reader.read(SlackWindow(FakeNative(), "slack.exe"))

    assert error.value.code is AdapterErrorCode.STRATEGY_NOT_CONFIGURED
    assert error.value.retriable is False


class FakeElementInfo:
    def __init__(self, automation_id: str = "") -> None:
        self.automation_id = automation_id


class FakeElement:
    def __init__(
        self,
        text: str = "",
        *,
        automation_id: str = "",
        children: dict[str, FakeElement] | None = None,
    ) -> None:
        self.text = text
        self.element_info = FakeElementInfo(automation_id)
        self.children = children or {}

    def exists(self, timeout: float = 0) -> bool:
        return True

    def child_window(self, **criteria: str) -> FakeElement:
        if "auto_id" in criteria:
            return self.children[criteria["auto_id"]]
        if self.children:
            return next(iter(self.children.values()))
        return self

    def descendants(self, **criteria: str) -> list[FakeElement]:
        return list(self.children.values())

    def window_text(self) -> str:
        return self.text


def test_activity_extracts_only_explicitly_mapped_fields() -> None:
    item = FakeElement(
        children={
            "type": FakeElement("Menção na conversa do canal"),
            "sender": FakeElement("Pessoa Teste"),
        }
    )
    container = FakeElement(children={"item": item})
    root = FakeElement(children={"activity": container})
    reader = PywinautoActivityReader(
        ActivitySelectors(
            activity_automation_id="activity",
            item_control_type="ListItem",
            event_type_automation_id="type",
            sender_automation_id="sender",
        ),
        clock=lambda: datetime(2026, 7, 22, tzinfo=UTC),
    )

    events = reader.read(SlackWindow(root, "slack.exe"))

    assert len(events) == 1
    assert events[0].raw_type == "Menção na conversa do canal"
    assert events[0].sender == "Pessoa Teste"
    assert events[0].body is None


@pytest.mark.parametrize(
    ("automation_id", "expected_type"),
    [
        ("at_user-C123-1784760246.639139", "Menção na conversa do canal"),
        ("at_user_group-C123-1784760246.639139", "Menção ao grupo na conversa do canal"),
    ],
)
def test_activity_extracts_type_and_stable_key_from_real_item_prefix(
    automation_id: str, expected_type: str
) -> None:
    item = FakeElement("Conteúdo local", automation_id=automation_id)
    container = FakeElement(children={"item": item})
    root = FakeElement(children={"activity": container})
    reader = PywinautoActivityReader(
        ActivitySelectors(
            activity_title="Menções",
            item_control_type="ListItem",
            direct_item_automation_id_prefix="at_user-",
            group_item_automation_id_prefix="at_user_group-",
            item_name_as_body=True,
        ),
        clock=lambda: datetime(2026, 7, 22, tzinfo=UTC),
    )

    events = reader.read(SlackWindow(root, "slack.exe"))

    assert len(events) == 1
    assert events[0].external_key == automation_id
    assert events[0].raw_type == expected_type
    assert events[0].body == "Conteúdo local"
