from __future__ import annotations

import json
import sys

import pytest

from watchdog.application.cli import build_parser, main


def test_packaged_cli_defaults_to_validated_slack_activity_selectors() -> None:
    args = build_parser().parse_args([])

    assert args.activity_title == "Menções"
    assert args.activity_control_type == "List"
    assert args.item_control_type == "ListItem"
    assert args.direct_item_automation_id_prefix == "at_user-"
    assert args.group_item_automation_id_prefix == "at_user_group-"
    assert args.item_name_as_body is True


@pytest.mark.skipif(sys.platform == "win32", reason="validates structured non-Windows fallback")
def test_cli_once_reports_unsupported_platform(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    result = main(["--once"])
    output = json.loads(capsys.readouterr().out)

    assert result == 2
    assert output["state"] == "ERROR"
    assert output["last_error_code"] == "UNSUPPORTED_PLATFORM"
