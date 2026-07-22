# TASK-WDG-015 - Implementar orquestração, health e recuperação do monitor

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-015-implementar-orquestracao-health-e-recuperacao.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- application runtime

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 8.1, 8.5, 9, 10.1/I e 18 critérios 4, 5, 7 e 8.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Ligar adapter, normalizador, classificador, dedup, store e regras em ciclos canceláveis com health explícito, pausa e recuperação.

## Contexto mínimo
A aplicação precisa explicar seu estado e nunca parar silenciosamente.

## Inputs
- TASK-WDG-010 a TASK-WDG-014
- configuração da TASK-WDG-009

## Dependências
### Satisfeitas
- TASK-WDG-010 a TASK-WDG-014 concluídas
### Em aberto
- intervalo default respeitando meta de latência e consumo

## Alvos explícitos
- src/application
- health monitor e estado de execução

## Fora de escopo
- tray/UI concreta
- notificação Windows concreta
- serviço do Windows

## Checklist de execução
- [ ] implementar fluxo da seção 9 e cancelamento limpo
- [ ] implementar todos os estados health sugeridos
- [ ] registrar scan, falha, degradação, retomada, pausa e shutdown

## Acceptance Criteria
- fluxo aguarda Slack, monitora, degrada e retoma sem intervenção
- health transita por STARTING, MONITORING, estados Slack/Activity, DEGRADED, PAUSED e ERROR
- falha de leitura é registrada e reprocessada sem alertar indevidamente

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: testes de aplicação com adapters fakes e relógio controlado
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- testes de transição/recuperação
- timeline de health

## Riscos
- loop duplicado após reconexão
- retry infinito consumindo recursos

## Blockers possíveis
- contratos anteriores não permitirem cancelamento/erro tipado

## Próximo passo provável
- TASK-WDG-016

## Feedback obrigatório de retorno
- transições; política de retry; resultados de recovery
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_runtime_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

