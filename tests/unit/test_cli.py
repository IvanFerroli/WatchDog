from __future__ import annotations

import json
import sys

import pytest

from watchdog.application.cli import main


@pytest.mark.skipif(sys.platform == "win32", reason="validates structured non-Windows fallback")
def test_cli_once_reports_unsupported_platform(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    result = main(["--once"])
    output = json.loads(capsys.readouterr().out)

    assert result == 2
    assert output["state"] == "ERROR"
    assert output["last_error_code"] == "UNSUPPORTED_PLATFORM"
