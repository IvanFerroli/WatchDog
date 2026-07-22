# AlwaysTrack Watchdog

Agente local Windows que observa a Activity do Slack Desktop por UI Automation,
alerta menções diretas e ignora menções coletivas como `@sac`.

## Estado do MVP

O código portátil, o runtime, a UI, a persistência, os testes e o pipeline de
empacotamento estão implementados. A release permanece bloqueada até executar o
spike, a matriz e o piloto em Windows com Slack Desktop real. O repositório não
finge que fixtures validam a árvore de acessibilidade real.

## Instalação para desenvolvimento

Requer Python 3.12. No Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
watchdog --version
```

Na primeira execução, configuração, banco e logs ficam em
`%LOCALAPPDATA%\AlwaysTrack\Watchdog`. Nenhum token, cookie ou credencial do
Slack é solicitado.

## Gate UIA obrigatório

Os seletores devem vir do procedimento aprovado em
[`docs/research/slack-ui-automation-spike.md`](docs/research/slack-ui-automation-spike.md).
Sem eles, o Watchdog falha fechado com `STRATEGY_NOT_CONFIGURED`.

Em Slack 4.50.143, interface `pt-BR`, o spike real confirmou a lista `Menções`,
itens `ListItem`, menções diretas com prefixo `at_user-` e menções a grupo com
prefixo `at_user_group-`. Para esse ambiente, use:

```powershell
./scripts/run_watchdog_windows.ps1 -Once
./scripts/run_watchdog_windows.ps1
```

A versão atual requer a tela `Activity > Menções` acessível. O helper pode
navegar até ela durante o diagnóstico com `--navigate-automation-id activity-inbox`.

Uma leitura diagnóstica pode ser executada assim, substituindo apenas pelos
valores realmente comprovados no spike:

```powershell
watchdog --once `
  --activity-title "Menções" `
  --activity-control-type List `
  --item-control-type ListItem `
  --direct-item-automation-id-prefix "at_user-" `
  --group-item-automation-id-prefix "at_user_group-" `
  --item-name-as-body
```

Depois do gate aprovado, execute sem `--once` para abrir tray/painel. O menu
permite abrir o painel, pausar/retomar e encerrar. Fechar o painel não encerra o
monitor.

## Qualidade

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest --cov --cov-report=term-missing
python -m build
```

O build Windows reproduzível usa:

```powershell
./scripts/build_windows.ps1
```

Ele produz bundle PyInstaller `onedir`, instalador Inno Setup per-user e hashes
SHA-256. O workflow `package-windows` também pode ser disparado manualmente.

## Operação e privacidade

- [Troubleshooting](docs/operations/troubleshooting.md)
- [Privacidade e segurança](docs/operations/privacy-and-security.md)
- [Estratégia de testes](docs/testing/test-strategy.md)
- [Matriz manual Windows/Slack](tests/manual/windows-slack-matrix.md)
- [Gate final de aceite](docs/testing/mvp-acceptance.md)

Limitações atuais: seletores e identidade UIA não comprovados, smoke do
instalador/toast/tray pendente e piloto de quatro horas não executado. Se o Slack
não expuser `external_key` nem horário do evento, a estratégia de deduplicação
precisa ser fechada com evidência antes da liberação.

O documento canônico é
[`doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md`](doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md).
