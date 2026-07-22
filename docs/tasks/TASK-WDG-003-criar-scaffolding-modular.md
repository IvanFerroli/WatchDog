# TASK-WDG-003 - Criar scaffolding modular do Watchdog

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-003-criar-scaffolding-modular.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- scaffolding

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 10, 11.1, 12 e 19/Fase 0.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Materializar a estrutura mínima do repositório para core, adapter Slack, classificação, persistência, notificações, aplicação, UI, testes, configuração e packaging.

## Contexto mínimo
O scaffolding só pode refletir a baseline técnica aprovada e deve manter detalhes de UI Automation fora do núcleo.

## Inputs
- ADRs da TASK-WDG-002
- estrutura conceitual da seção 12

## Dependências
### Satisfeitas
- TASK-WDG-002 concluída
### Em aberto
- nomes finais de projetos/pacotes conforme a stack

## Alvos explícitos
- src/core
- src/adapters/slack_ui
- src/classification
- src/persistence
- src/notifications
- src/application
- src/ui
- tests
- config
- assets
- scripts
- packaging

## Fora de escopo
- implementar comportamento funcional
- criar API local ou módulo AlwaysTrack
- adicionar fontes além de Slack

## Checklist de execução
- [ ] criar módulos e dependências permitidas
- [ ] adicionar entrypoint mínimo sem lógica de produto
- [ ] documentar mapa de módulos e regras de acoplamento

## Acceptance Criteria
- build vazio da solução/projeto conclui
- core não referencia UI, tray nem detalhes do Slack
- adapter, notifier e store são fronteiras substituíveis

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- validações aplicáveis passam sem exposição de dados sensíveis
- comportamento, riscos e decisões duráveis são documentados
- retorno ao Taskyfier informa execução ou blocker real

## Validação
- método: executar build da stack e inspecionar grafo/referências entre módulos
- resultado esperado: objetivo único observável sem expansão de escopo

## Evidência esperada
- árvore criada
- output de build
- diff do mapa arquitetural

## Riscos
- scaffolding excessivo
- dependência circular entre core, aplicação e UI

## Blockers possíveis
- ADRs incompletas ou ferramentas ausentes no ambiente

## Próximo passo provável
- TASK-WDG-004

## Feedback obrigatório de retorno
- artefatos criados; build; desvios inevitáveis da estrutura conceitual
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_scaffolding_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

