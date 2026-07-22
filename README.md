# AlwaysTrack Watchdog

Agente local para Windows que observa a Activity do Slack Desktop por Windows UI
Automation, alerta somente menções diretas e ignora menções coletivas.

O projeto está em implementação de MVP. A validação real depende de Windows,
Slack Desktop e eventos controlados; fixtures sintéticas não substituem esse gate.

## Desenvolvimento

Requer Python 3.12.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m build
```

O documento canônico está em
[`doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md`](doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md).
As limitações, instalação e operação serão consolidadas antes da release candidate.
