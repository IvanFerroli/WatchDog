from __future__ import annotations

import json

from watchdog.observability.diagnostics import compare_snapshots, export_snapshot
from watchdog.observability.logging import redact


def test_redacts_content_and_token() -> None:
    result = redact({"body": "mensagem confidencial", "detail": "Bearer abc.def"})
    assert result["body"]["redacted"] is True
    assert "mensagem confidencial" not in json.dumps(result)
    assert result["detail"] == "[REDACTED_SECRET]"


def test_diagnostic_export_never_writes_accessible_name(tmp_path) -> None:
    destination = tmp_path / "snapshot.json"
    export_snapshot(
        [{"control_type": "ListItem", "automation_id": "item", "name": "Pessoa: segredo"}],
        destination,
        slack_version="test",
        adapter_version="1",
        elapsed_ms=1.2,
    )
    content = destination.read_text(encoding="utf-8")
    assert "Pessoa: segredo" not in content
    assert compare_snapshots(json.loads(content), json.loads(content))["unchanged"] == 1
