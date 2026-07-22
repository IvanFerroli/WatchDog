# TASK-WDG-011 - Implementar acesso e extração resiliente da Activity

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-011-implementar-acesso-e-extracao-da-activity.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- runtime adapter

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 6.1, 8.1, 10.1/A, 16 e estratégia da TASK-WDG-008.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Implementar a estratégia comprovada para encontrar/navegar à Activity, extrair itens brutos e detectar mudança de estrutura sem derrubar a aplicação.

## Contexto mínimo
Seletores, navegação e campos devem vir do spike, não de suposição.

## Inputs
- adapter de janela da TASK-WDG-010
- relatório, ADR e fixtures da TASK-WDG-008

## Dependências
### Satisfeitas
- TASK-WDG-010 concluída
### Em aberto
- limitações documentadas para minimizado e Activity fechada

## Alvos explícitos
- src/adapters/slack_ui
- fixtures e testes específicos do adapter

## Fora de escopo
- classificar semântica
- deduplicar
- usar OCR/websocket/cache

## Checklist de execução
- [ ] implementar localização/navegação conforme gate
- [ ] converter controles em modelo bruto com campos opcionais
- [ ] emitir erros tipados e sinal de estrutura alterada

## Acceptance Criteria
- itens recentes são extraídos nos estados aprovados pelo spike
- Activity ausente produz estado degradado e retry, não silêncio
- mudança incompatível de estrutura é detectada e registra versões Slack/adapter

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: testes com fixtures e smoke nos estados viáveis documentados
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- testes do adapter
- logs de Activity encontrada/ausente e estrutura alterada

## Riscos
- seletor frágil por posição
- navegação interferir no usuário

## Blockers possíveis
- Slack atualizado invalidar a estratégia comprovada

## Próximo passo provável
- TASK-WDG-012

## Feedback obrigatório de retorno
- estados suportados; campos extraídos; qualquer divergência do spike
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_runtime_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

