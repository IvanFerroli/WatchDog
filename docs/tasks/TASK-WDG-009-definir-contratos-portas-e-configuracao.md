# TASK-WDG-009 - Definir contratos, portas e configuração do núcleo

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-009-definir-contratos-portas-e-configuracao.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- contratos

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 10/B–I, 11.1, 11.3, 13 e 14.2.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Implementar modelos ObservedEvent e OperationalEvent, enums, portas substituíveis e schema serializável de configuração necessários ao MVP.

## Contexto mínimo
O contrato genérico serve apenas para desacoplar o MVP; nenhuma API ou integração AlwaysTrack será criada.

## Inputs
- gate go e fixtures da TASK-WDG-008
- baseline técnica da TASK-WDG-002

## Dependências
### Satisfeitas
- TASK-WDG-008 concluída com go
### Em aberto
- campos realmente disponíveis no Slack devem aceitar ausência

## Alvos explícitos
- src/core
- interfaces/ports de adapter, store, clock e notifier
- config/schema e defaults

## Fora de escopo
- API local
- biblioteca compartilhada
- tipos específicos do painel AlwaysTrack
- mensagem direta opcional

## Checklist de execução
- [ ] definir eventos, categorias e versões de schema/classifier
- [ ] definir interfaces e eventos internos
- [ ] definir todas as chaves mínimas da seção 13 com validação/defaults

## Acceptance Criteria
- contratos cobrem ids, tempos, actor/location, dedup key, metadata e schema version
- DIRECT_MENTION, GROUP_MENTION, UNKNOWN e demais enums arquiteturais existem sem torná-los gatilhos
- core não depende de UI, Windows notifier, SQLite concreto ou UI Automation

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- validações aplicáveis passam sem exposição de dados sensíveis
- comportamento, riscos e decisões duráveis são documentados
- retorno ao Taskyfier informa execução ou blocker real

## Validação
- método: typecheck/build e testes de serialização/validação de configuração
- resultado esperado: objetivo único observável sem expansão de escopo

## Evidência esperada
- diff dos contratos
- output de build/testes de contrato

## Riscos
- contrato genérico demais para os dados reais
- vazar metadata bruta sensível

## Blockers possíveis
- fixtures não definirem campos mínimos observáveis

## Próximo passo provável
- TASK-WDG-010

## Feedback obrigatório de retorno
- contratos finais; campos opcionais; mudanças de schema e limitações
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_contracts_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

