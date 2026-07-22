# TASK-WDG-002 - Decidir stack e baseline técnica do aplicativo Windows

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-002-decidir-stack-e-baseline-tecnica.md

## Modo
- mode: planning
- generation-mode: derivação inicial

## Capability
- arquitetura

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 6, 10, 12, 19/Fase 0, 22 e questões 1, 2, 10–13.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Registrar em ADRs a stack e o conjunto mínimo de decisões técnicas que tornam o MVP executável e distribuível no Windows.

## Contexto mínimo
A spec define responsabilidades e restrições, mas deixa stack, formato de configuração, banco, biblioteca de notificações e política de atualização em aberto.

## Inputs
- intake aceito da TASK-WDG-001
- master spec
- restrição de UI Automation, local-first e standalone-first

## Dependências
### Satisfeitas
- TASK-WDG-001 concluída
### Em aberto
- escolha de runtime/UI, banco, configuração, notifier/tray, empacotamento e atualização

## Alvos explícitos
- docs/adr/
- docs/specs/ ou decisão técnica equivalente para a baseline do MVP

## Fora de escopo
- implementar scaffolding
- escolher integração com AlwaysTrack
- introduzir API oficial Slack, tokens, OCR, interceptação ou cache interno

## Checklist de execução
- [ ] comparar opções compatíveis com Windows UI Automation
- [ ] registrar decisões, trade-offs e versões suportadas
- [ ] definir como build, configuração, SQLite equivalente, tray, notifier e update se encaixam

## Acceptance Criteria
- cada questão técnica 1, 2 e 10–13 recebe decisão ou justificativa explícita de adiamento sem bloquear o MVP
- as escolhas preservam adapter substituível, core sem dependência da UI e armazenamento versionado
- há estratégia de distribuição sem exigir privilégio administrativo no workspace Slack

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- validações aplicáveis passam sem exposição de dados sensíveis
- comportamento, riscos e decisões duráveis são documentados
- retorno ao Taskyfier informa execução ou blocker real

## Validação
- método: revisão das ADRs contra as restrições das seções 5, 6, 10, 11 e 15
- resultado esperado: objetivo único observável sem expansão de escopo

## Evidência esperada
- ADRs aceitas com alternativas e consequências
- matriz decisão → requisito

## Riscos
- fechar stack antes de verificar suporte real à UI Automation
- misturar preparação de AlwaysTrack com escopo do MVP

## Blockers possíveis
- ausência de uma opção tecnicamente viável para UI Automation/notificações na stack escolhida

## Próximo passo provável
- TASK-WDG-003

## Feedback obrigatório de retorno
- decisões aceitas; versões e bibliotecas escolhidas; riscos que alterem o spike
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_docs_formalizer
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

