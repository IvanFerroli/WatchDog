# TASK-WDG-006 - Provar detecção de menção direta e grupo em primeiro plano

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-006-provar-deteccao-direta-e-grupo.md

## Modo
- mode: audit
- generation-mode: derivação inicial

## Capability
- descoberta

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 6.1, 7, 21/Risco 1 e 25 passos 1–6.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Demonstrar que a árvore de acessibilidade permite localizar Slack, Activity, conteúdo mínimo e o campo que separa menção direta de menção ao grupo sac.

## Contexto mínimo
Nenhum núcleo funcional deve avançar antes desta evidência.

## Inputs
- protocolo da TASK-WDG-005
- Slack Desktop com casos controlados

## Dependências
### Satisfeitas
- TASK-WDG-005 concluída
### Em aberto
- estrutura real exposta pela versão instalada do Slack

## Alvos explícitos
- protótipo descartável de inspeção em scripts ou área de spike
- docs/research/slack-ui-automation-spike.md
- evidências anonimizadas

## Fora de escopo
- adapter de produção
- navegação automática definitiva
- OCR, websocket, cache ou API oficial

## Checklist de execução
- [ ] localizar processo/janela e árvore
- [ ] identificar controles da Activity e extrair tipo/trecho
- [ ] comparar tipo, nome, automation id e hierarquia entre direta e grupo

## Acceptance Criteria
- um item direto e um item sac são encontrados de forma reproduzível
- ao menos um campo observável diferencia os dois sem depender apenas de @ivan
- remetente, canal e trecho têm disponibilidade registrada, inclusive quando ausentes

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- validações aplicáveis passam sem exposição de dados sensíveis
- comportamento, riscos e decisões duráveis são documentados
- retorno ao Taskyfier informa execução ou blocker real

## Validação
- método: repetir inspeção com os dois casos e revisão cruzada das evidências anonimizadas
- resultado esperado: objetivo único observável sem expansão de escopo

## Evidência esperada
- saída do protótipo sem conteúdo sensível
- tabela comparativa no relatório

## Riscos
- rótulos variarem por idioma/versão
- virtualização da lista ocultar itens

## Blockers possíveis
- Slack não expor Activity ou campo discriminador

## Próximo passo provável
- TASK-WDG-007

## Feedback obrigatório de retorno
- campos encontrados; seletor candidato; limitações e comportamento ausente
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_runtime_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

