# TASK-WDG-008 - Fechar gate de viabilidade e estratégia definitiva do MVP

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-008-fechar-gate-de-viabilidade.md

## Modo
- mode: planning
- generation-mode: derivação inicial

## Capability
- estratégia

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 7/Resultado esperado, 19/Fase 1, 21 e 23.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Registrar uma das cinco conclusões permitidas e transformar a evidência do spike na estratégia executável do adapter, classificação e deduplicação.

## Contexto mínimo
Se UI Automation for insuficiente, o backlog de implementação deve parar e ser rederivado após uma spec de fallback; não se inventa fallback nesta task.

## Inputs
- resultados das TASK-WDG-006 e TASK-WDG-007
- ADRs da baseline técnica

## Dependências
### Satisfeitas
- TASK-WDG-006 e TASK-WDG-007 concluídas
### Em aberto
- conclusão final de viabilidade
- rótulos/seletores e estratégia de identidade definitivos

## Alvos explícitos
- docs/research/slack-ui-automation-spike.md
- ADR de estratégia do adapter
- fixtures anonimizadas representativas

## Fora de escopo
- implementar o adapter
- aprovar OCR/websocket/cache sem nova decisão e análise de segurança
- prosseguir se o gate for inviável

## Checklist de execução
- [ ] classificar conclusão em uma das cinco opções da spec
- [ ] documentar seletores, navegação, polling, retry e sinais de quebra
- [ ] converter capturas seguras em fixtures e listar limitações

## Acceptance Criteria
- relatório contém todos os campos do entregável da seção 25
- há decisão go para estratégia comprovada ou no-go explícito com blocker
- fixtures distinguem direta, grupo e desconhecido sem dados reais

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- validações aplicáveis passam sem exposição de dados sensíveis
- comportamento, riscos e decisões duráveis são documentados
- retorno ao Taskyfier informa execução ou blocker real

## Validação
- método: revisão contra as seções 7 e 25 e execução do classificador planejado sobre fixtures
- resultado esperado: objetivo único observável sem expansão de escopo

## Evidência esperada
- relatório final e ADR
- registro go/no-go
- fixtures anonimizadas

## Riscos
- forçar go apesar de evidência parcial
- acoplar regras a posição visual frágil

## Blockers possíveis
- conclusão UI Automation insuficiente ou inviável

## Próximo passo provável
- TASK-WDG-009 se go; nova formalização de fallback fora deste backlog se no-go

## Feedback obrigatório de retorno
- conclusão escolhida; blockers; seletores e fixtures aprovados
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_docs_formalizer
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

