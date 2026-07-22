"""Command-line entrypoint for one-shot diagnostics or the background runtime."""

from __future__ import annotations

import argparse
import json
import signal
import sys
import threading
from pathlib import Path

from watchdog import __version__
from watchdog.adapters.slack_ui import ActivitySelectors
from watchdog.core.models import HealthState
from watchdog.observability.logging import configure_logging

from .composition import build_runtime
from .configuration import JsonConfigRepository, default_data_directory
from .single_instance import AlreadyRunningError, SingleInstanceLock


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="watchdog")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--once", action="store_true", help="execute one scan and exit")
    parser.add_argument("--headless", action="store_true", help="do not start tray/panel")
    parser.add_argument("--activity-automation-id")
    parser.add_argument("--activity-title")
    parser.add_argument("--activity-control-type")
    parser.add_argument("--item-automation-id")
    parser.add_argument("--item-control-type")
    parser.add_argument("--event-type-automation-id")
    parser.add_argument("--sender-automation-id")
    parser.add_argument("--channel-automation-id")
    parser.add_argument("--body-automation-id")
    parser.add_argument("--external-key-automation-id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    data_directory = default_data_directory()
    config_path = args.config or data_directory / "config.json"
    repository = JsonConfigRepository(config_path)
    try:
        config = repository.load()
    except (OSError, ValueError) as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2
    data_directory.mkdir(parents=True, exist_ok=True)
    configure_logging(data_directory / "logs" / "watchdog.jsonl", config.logging.level)
    selectors = ActivitySelectors(
        activity_automation_id=args.activity_automation_id,
        activity_title=args.activity_title,
        activity_control_type=args.activity_control_type,
        item_automation_id=args.item_automation_id,
        item_control_type=args.item_control_type,
        event_type_automation_id=args.event_type_automation_id,
        sender_automation_id=args.sender_automation_id,
        channel_automation_id=args.channel_automation_id,
        body_automation_id=args.body_automation_id,
        external_key_automation_id=args.external_key_automation_id,
    )
    instance_lock = SingleInstanceLock(data_directory / "watchdog.lock")
    try:
        instance_lock.acquire()
    except AlreadyRunningError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    try:
        runtime, store = build_runtime(config, data_directory=data_directory, selectors=selectors)
        try:
            if args.once:
                snapshot = runtime.run_once()
                print(_snapshot_json(snapshot))
                return 2 if snapshot.state is HealthState.ERROR else 0
            if args.headless or sys.platform != "win32":
                return _run_headless(runtime)
            return _run_desktop(runtime, store, repository, data_directory)
        finally:
            runtime.stop()
            store.close()
    finally:
        instance_lock.release()


def _run_headless(runtime: object) -> int:
    stop = threading.Event()

    def request_stop(*_: object) -> None:
        stop.set()
        runtime.stop()

    signal.signal(signal.SIGINT, request_stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, request_stop)
    runtime.run_forever()
    return 0


def _run_desktop(runtime: object, store: object, repository: object, data_directory: Path) -> int:
    from watchdog.ui.desktop import DesktopApplication

    app = DesktopApplication(
        runtime=runtime,
        store=store,
        config_repository=repository,
        logs_directory=data_directory / "logs",
    )
    app.run()
    return 0


def _snapshot_json(snapshot: object) -> str:
    payload = {
        "state": snapshot.state.value,
        "last_successful_scan_at": _iso(snapshot.last_successful_scan_at),
        "last_error_at": _iso(snapshot.last_error_at),
        "last_error_code": snapshot.last_error_code,
        "items_read_last_scan": snapshot.items_read_last_scan,
        "new_items_last_scan": snapshot.new_items_last_scan,
        "direct_mentions_today": snapshot.direct_mentions_today,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _iso(value: object) -> str | None:
    return value.isoformat() if value is not None else None


if __name__ == "__main__":
    raise SystemExit(main())
