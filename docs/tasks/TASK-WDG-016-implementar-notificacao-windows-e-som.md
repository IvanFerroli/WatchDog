# TASK-WDG-016 - Implementar notificação Windows e som distintivo

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-016-implementar-notificacao-windows-e-som.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- integração Windows

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 8.3, 10.1/F, 18 critérios 1–3 e 23 questão 12.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Emitir notificação nativa perceptível com som distinto e conteúdo mínimo disponível, uma única vez após decisão idempotente.

## Contexto mínimo
Abrir/focar o Slack ao clicar é P2 e não entra.

## Inputs
- porta notifier da TASK-WDG-009
- dedup/orquestração TASK-WDG-014/015
- biblioteca decidida na TASK-WDG-002

## Dependências
### Satisfeitas
- TASK-WDG-014 e TASK-WDG-015 concluídas
### Em aberto
- comportamento de persistência suportado pela versão Windows

## Alvos explícitos
- src/notifications
- assets de som licenciados ou gerados
- integração da aplicação com a porta notifier

## Fora de escopo
- click action para abrir item
- toast para grupo ou UNKNOWN
- som do Slack reutilizado

## Checklist de execução
- [ ] renderizar sender/canal/preview apenas quando disponíveis
- [ ] tocar som habilitado/configurado e distinto
- [ ] registrar sucesso/falha e alerted_at sem duplicação

## Acceptance Criteria
- menção direta gera um toast e um som quando habilitado
- grupo, unknown e repetição não geram toast
- campos ausentes não quebram a notificação e falha é observável

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: teste de integração com notifier substituível e smoke manual Windows
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- resultado do smoke sem conversa real
- testes da porta e status alerted_at

## Riscos
- API de toast variar por Windows
- vazar preview em tela bloqueada

## Blockers possíveis
- biblioteca não funcionar no ambiente alvo

## Próximo passo provável
- TASK-WDG-017

## Feedback obrigatório de retorno
- versões Windows testadas; persistência/percepção; política de conteúdo
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_runtime_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

