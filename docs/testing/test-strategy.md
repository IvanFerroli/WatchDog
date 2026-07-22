# Estratégia de testes do MVP

## Status

- Suíte automatizada: executável em Linux e Windows.
- Integrações nativas: exercitadas por fakes fora do Windows.
- Slack Desktop real: gate manual obrigatório, ainda não substituído por fixtures.
- Piloto de expediente: obrigatório antes da liberação.

## Comandos canônicos

```text
python -m ruff check .
python -m ruff format --check .
python -m pytest --cov --cov-report=term-missing
python -m build
```

## Cobertura

| Requisito | Automatizado | Gate manual |
|---|---|---|
| normalização/classificação/regras | unitário com dados sintéticos | confirmar rótulos reais |
| configuração/serialização | unitário | preferências no painel |
| SQLite/migrations/retenção | integração com banco temporário | upgrade do pacote |
| dedup/restart | unitário e integração | Slack real |
| adapter UIA | fixtures e providers falsos | Windows/Slack obrigatório |
| health/recovery | runtime com fakes | fechar/reabrir Slack |
| notifier/tray/painel | portas e view-model | smoke Windows |
| privacidade/diagnóstico | redaction e export sintético | revisão do artefato |

Testes marcados `windows` ou `slack_real` não podem ser promovidos a aprovados
em outro sistema operacional.
