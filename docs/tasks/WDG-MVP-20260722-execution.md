# Execution report — WDG-MVP-20260722

## Pacote

- task range: TASK-WDG-001–025
- mode: single-turn pipeline / execution artifact mode
- branch: `main`
- strategy: implementar toda a base verificável e bloquear gates que exigem evidência real

## Resultado por task

| Tasks | Verifier | Resultado material |
|---|---|---|
| 001 | approved | intake canônico |
| 002 | approved-with-notes | ADR-002; smoke Windows pendente |
| 003–004 | approved-with-notes | scaffold, CI, lint, testes e build portáteis |
| 005 | approved | protocolo seguro do spike |
| 006–008 | blocked | Windows interativo, Slack real e casos controlados ausentes; sem go/no-go inventado |
| 009–013 | approved-with-notes | contratos, config, adapter configurável, classificação e SQLite; dados reais pendentes |
| 014 | rework/blocked | id estável/occurred_at depende do spike; fallback sem ambos pode colidir eventos idênticos |
| 015–020 | approved-with-notes | runtime, notifier, tray, painel, privacidade e 37 testes/80,43%; smoke Windows pendente |
| 021–022 | blocked | matriz real e piloto de expediente não executados |
| 023 | blocked | pipeline/installer preparados; install/upgrade/uninstall Windows não executados |
| 024 | approved-with-notes | README, troubleshooting, privacidade e testes documentados; walkthrough Windows pendente |
| 025 | blocked | depende dos gates 008, 021, 022 e 023 e da decisão do responsável |

## Evidência local

- Ruff e format: aprovados.
- Pytest: 37 passed.
- Cobertura: 80,43% com precisão de duas casas e threshold de 80%.
- Wheel/sdist: construídos.
- PyInstaller `onedir`: construído no host Linux para validar a receita.
- Bundle: `--version` retornou `0.1.0`; `--once` falhou fechado com `UNSUPPORTED_PLATFORM`.
- Scan de segredos: nenhum segredo real encontrado; somente tokens sintéticos de teste.

## Commits publicados

1. `5544273` — baseline, tasks e gates.
2. `c76d78e` — core, classificação, dedup e SQLite.
3. `b8f2a80` — adapter e runtime resiliente.
4. `a7c1747` — notifier, tray, painel e CLI.
5. `5cd3b32` — retries, privacidade, retenção e instância única.
6. `efadc10` — empacotamento Windows onedir/Inno.
7. `32916d8` — status e timestamps completos do histórico.

## Handoff para verificação real

1. Executar o protocolo do spike e decidir TASK-WDG-008.
2. Se go, persistir os seletores/identidade aprovados e revalidar dedup.
3. Executar matriz manual, piloto e smoke do mesmo artefato Windows.
4. Preencher relatórios sem dados corporativos e obter decisão do responsável.
5. Somente então classificar TASK-WDG-025 como approved/rework/blocked.
