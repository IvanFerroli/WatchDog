from __future__ import annotations

from datetime import UTC, datetime

import pytest

from watchdog.adapters.slack_ui import (
    ActivitySelectors,
    AdapterErrorCode,
    PywinautoActivityNavigator,
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


class RecoveringReader:
    adapter_version = "recovering-v1"

    def __init__(self, *, fail_after_recovery: bool = False) -> None:
        self.calls = 0
        self.fail_after_recovery = fail_after_recovery

    def read(self, window: SlackWindow) -> list[object]:
        self.calls += 1
        if self.calls == 1 or self.fail_after_recovery:
            raise SlackAdapterError(
                AdapterErrorCode.ACTIVITY_NOT_FOUND,
                "Activity is not currently visible",
            )
        return ["restored"]


class FakeNavigator:
    def __init__(self) -> None:
        self.calls = 0

    def open_activity(self, window: SlackWindow) -> None:
        self.calls += 1


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


def test_adapter_restores_activity_and_retries_read_once() -> None:
    provider = FakeProvider()
    reader = RecoveringReader()
    navigator = FakeNavigator()
    adapter = SlackUIAdapter(
        SlackWindowLifecycle(provider, ("slack.exe",)),
        reader,
        navigator,
    )

    assert adapter.observe() == ["restored"]
    assert reader.calls == 2
    assert navigator.calls == 1


def test_adapter_does_not_loop_when_activity_is_still_missing() -> None:
    reader = RecoveringReader(fail_after_recovery=True)
    navigator = FakeNavigator()
    adapter = SlackUIAdapter(
        SlackWindowLifecycle(FakeProvider(), ("slack.exe",)),
        reader,
        navigator,
    )

    with pytest.raises(SlackAdapterError) as error:
        adapter.observe()

    assert error.value.code is AdapterErrorCode.ACTIVITY_NOT_FOUND
    assert reader.calls == 2
    assert navigator.calls == 1


def test_adapter_wraps_unexpected_navigation_failure_and_invalidates_window() -> None:
    class BrokenNavigator:
        def open_activity(self, window: SlackWindow) -> None:
            raise RuntimeError("synthetic navigation failure")

    provider = FakeProvider()
    adapter = SlackUIAdapter(
        SlackWindowLifecycle(provider, ("slack.exe",)),
        RecoveringReader(),
        BrokenNavigator(),
    )

    with pytest.raises(SlackAdapterError) as error:
        adapter.observe()

    assert error.value.code is AdapterErrorCode.READ_FAILED
    provider.alive = True
    adapter.observe()
    assert provider.find_calls == 2


class FakeNavigationTarget:
    def __init__(self, *, exists: bool = True, select_error: Exception | None = None) -> None:
        self.present = exists
        self.select_error = select_error
        self.selected = False

    def exists(self, timeout: float = 0) -> bool:
        return self.present

    def wrapper_object(self) -> FakeNavigationTarget:
        return self

    def select(self) -> None:
        if self.select_error:
            raise self.select_error
        self.selected = True


class FakeNavigationRoot:
    def __init__(self, target: FakeNavigationTarget) -> None:
        self.target = target

    def child_window(self, **criteria: str) -> FakeNavigationTarget:
        assert criteria == {"auto_id": "activity-inbox", "control_type": "TabItem"}
        return self.target


def test_activity_navigator_selects_validated_activity_tab() -> None:
    target = FakeNavigationTarget()
    waits: list[float] = []
    navigator = PywinautoActivityNavigator(
        settle_seconds=0.25,
        sleeper=waits.append,
    )

    navigator.open_activity(SlackWindow(FakeNavigationRoot(target), "slack.exe"))

    assert target.selected
    assert waits == [0.25]


@pytest.mark.parametrize(
    "target",
    [
        FakeNavigationTarget(exists=False),
        FakeNavigationTarget(select_error=RuntimeError("UIA failure")),
    ],
)
def test_activity_navigator_keeps_failures_structured(target: FakeNavigationTarget) -> None:
    navigator = PywinautoActivityNavigator(settle_seconds=0)

    with pytest.raises(SlackAdapterError) as error:
        navigator.open_activity(SlackWindow(FakeNavigationRoot(target), "slack.exe"))

    assert error.value.code is AdapterErrorCode.ACTIVITY_NOT_FOUND


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
            "destination": FakeElement("slack://channel?team=T123&id=C123"),
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
            destination_automation_id="destination",
        ),
        clock=lambda: datetime(2026, 7, 22, tzinfo=UTC),
    )

    events = reader.read(SlackWindow(root, "slack.exe"))

    assert len(events) == 1
    assert events[0].raw_type == "Menção na conversa do canal"
    assert events[0].sender == "Pessoa Teste"
    assert events[0].body is None
    assert events[0].raw_metadata["slack_destination"] == ("slack://channel?team=T123&id=C123")


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
