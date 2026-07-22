# TASKYFIER MEMORY

## Metadata
- status: active
- owner: olympus_taskyfier
- last-updated: 2026-07-22
- source-of-truth: docs/operations/taskyfier-memory.md

## Status do projeto
- classificação oficial de prontidão: backlog do MVP derivado; implementação ainda não iniciada
- status adicional: gate documental e spike obrigatórios antes do núcleo
- documento canônico vigente: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md, versão 0.1
- macro-objetivo atual: entregar MVP Windows instalável que alerta somente menção direta no Slack e passa a seção 18

## Equivalência operacional
- docs/operations/engineering-pipeline-protocol.md está ausente.
- fallback vigente autorizado: docs/pipeline/protocol.md.
- esta equivalência deve permanecer visível até o caminho esperado ser restaurado ou oficialmente aposentado.

## Ordem de precedência em uso
1. Documento canônico vigente
2. ADRs aceitas
3. Specs aceitas
4. Task manifests existentes
5. Esta memória operacional
6. GitFlow vigente
7. Legado compatível

## Capability atualmente ativa
- governança documental

## Frente atualmente ativa
- Fase 0 — intake e baseline canônica

## ADRs aceitas relevantes
- docs/adr/ADR-001-governanca-documental-operacional.md
- baseline técnica do produto ainda pendente em TASK-WDG-002

## Specs aceitas relevantes
- doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md é a fonte canônica de derivação
- status formal de execução será esclarecido em TASK-WDG-001

## Task manifests existentes
- docs/tasks/ALWAYSTRACK_WATCHDOG_TASK_MANIFEST.md
- TASK-WDG-001 a TASK-WDG-025, todos com status proposed

## Tasks concluídas
- nenhuma

## Tasks em andamento
- nenhuma

## Tasks bloqueadas
- nenhuma oficialmente
- TASK-WDG-009 a TASK-WDG-025 dependem estruturalmente do go em TASK-WDG-008

## Dependências abertas
- aceite do intake/baseline canônica
- decisões de stack e baseline técnica
- ambiente Windows com Slack Desktop e casos controlados
- comprovação da hipótese de UI Automation
- confirmação de conformidade com política corporativa antes do piloto
- decisão do responsável sobre taxa adequada e recursos compatíveis após medição
- confirmação da política de versionamento, pois o .gitignore atual ignora docs/

## Decisões práticas recentes
- backlog limitado ao MVP pronto, instalável e aprovado
- Fase 6, integrações e P2 não possuem task package
- contrato genérico/portas entram apenas como desacoplamento mínimo do MVP
- fallback não será inventado: no-go no spike interrompe a sequência e exige nova formalização

## Padrões já adotados
- Compact Docs-First Mode
- uma task por ciclo com handoff ao olympus-orchestrator
- IDs estáveis TASK-WDG-001 a TASK-WDG-025
- evidência anonimizada e local-first

## Pontos sensíveis
- dumps, screenshots, nomes de controles e previews podem conter conteúdo corporativo
- falso negativo tem impacto alto
- Slack minimizado/Activity fechada são hipóteses até o spike
- seletores podem quebrar por idioma ou update
- tasks e memória existem no workspace, mas não aparecem no git status enquanto docs/ permanecer ignorado

## Último feedback recebido
- origem: usuário via coordenação do agente raiz
- resumo: manter somente o caminho necessário até MVP pronto e funcional, com aproximadamente 15–25 tasks
- impacto na sequência: removidos todos os packages P2/pós-MVP; backlog fechado em 25 tasks

## Próxima menor tarefa útil sugerida
- TASK-WDG-001 — Formalizar intake e baseline canônica do MVP
- modo sugerido: derivação inicial / planning
- justificativa curta: resolve a lacuna de instância apontada pela auditoria e impede execução sobre uma spec ainda marcada como planejamento

## Próximo macro-passo após a próxima task
- TASK-WDG-002 — decidir stack e baseline técnica sem antecipar integração futura

## Notas de continuidade
- Não iniciar scaffolding antes das decisões de TASK-WDG-002.
- Não iniciar produto antes do go/no-go de TASK-WDG-008.
- Se o gate falhar, marcar o ciclo blocked e rederivar somente após spec/ADR de fallback.
- Após cada execução, registrar evidência real, blocker e próxima task; não promover estado por expectativa.
