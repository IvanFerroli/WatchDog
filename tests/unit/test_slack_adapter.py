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


def test_activity_requires_complete_spike_selectors() -> None:
    reader = PywinautoActivityReader(ActivitySelectors())

    with pytest.raises(SlackAdapterError) as error:
        reader.read(SlackWindow(FakeNative(), "slack.exe"))

    assert error.value.code is AdapterErrorCode.STRATEGY_NOT_CONFIGURED
    assert error.value.retriable is False


class FakeElement:
    def __init__(self, text: str = "", *, children: dict[str, FakeElement] | None = None) -> None:
        self.text = text
        self.children = children or {}

    def exists(self, timeout: float = 0) -> bool:
        return True

    def child_window(self, **criteria: str) -> FakeElement:
        if "auto_id" in criteria:
            return self.children[criteria["auto_id"]]
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
