# TASK-WDG-018 - Implementar painel mínimo, histórico e preferências

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-018-implementar-painel-historico-e-preferencias.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- UI

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 8.4, 8.5, 10.1/H, 13 e 16/Painel.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Exibir estado, última leitura, contadores, último erro, histórico mínimo e preferências necessárias ao MVP.

## Contexto mínimo
A UI consome portas da aplicação/store e não acessa UI Automation diretamente.

## Inputs
- health/orquestração TASK-WDG-015
- store TASK-WDG-013
- tray TASK-WDG-017
- config TASK-WDG-009

## Dependências
### Satisfeitas
- TASK-WDG-013, TASK-WDG-015 e TASK-WDG-017 concluídas
### Em aberto
- layout mínimo conforme framework

## Alvos explícitos
- src/ui/panel
- views de status, histórico, preferências e acesso a logs

## Fora de escopo
- dashboard avançado
- filtros extras
- marcar menção como vista
- editar regras não previstas

## Checklist de execução
- [ ] exibir todos os campos do painel diagnóstico mínimo
- [ ] listar histórico sem conteúdo completo
- [ ] persistir preferências básicas e fornecer caminho de logs

## Acceptance Criteria
- status Slack/monitor e última leitura/erro refletem health atual
- histórico mostra eventos diretos e metadados mínimos persistidos
- alterações válidas persistem e configuração inválida mostra erro sem quebrar monitor

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: testes de view-model e walkthrough manual
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- screenshots com dados sintéticos
- testes de binding/config

## Riscos
- UI travar loop de monitoramento
- expor conteúdo sensível em excesso

## Blockers possíveis
- framework UI não suportar atualização thread-safe

## Próximo passo provável
- TASK-WDG-019

## Feedback obrigatório de retorno
- campos exibidos; preferências suportadas; falhas de UX
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_runtime_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

