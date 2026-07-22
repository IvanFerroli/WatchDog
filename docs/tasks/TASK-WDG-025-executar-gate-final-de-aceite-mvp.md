# TASK-WDG-025 - Executar gate final de aceite e liberar o MVP

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-025-executar-gate-final-de-aceite-mvp.md

## Modo
- mode: verification
- generation-mode: derivação inicial

## Capability
- release verification

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 18, 19/Fase 5 e 24.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Validar a release candidate contra os 12 critérios de aceite e a meta de qualidade, concluindo em aprovado, rework ou bloqueado.

## Contexto mínimo
Nenhum critério pode ser considerado atendido apenas por intenção; cada um precisa apontar evidência.

## Inputs
- package TASK-WDG-023
- docs TASK-WDG-024
- piloto TASK-WDG-022
- testes TASK-WDG-020/021

## Dependências
### Satisfeitas
- TASK-WDG-020 a TASK-WDG-024 aprovadas
### Em aberto
- decisão final do responsável sobre taxa adequada e consumo compatível

## Alvos explícitos
- relatório final de aceite
- manifesto de release e matriz critério → evidência
- status da versão candidata

## Fora de escopo
- alterar código durante o gate sem rework
- aprovar com critério crítico sem evidência
- incluir P2 na release

## Checklist de execução
- [ ] executar smoke de instalação e operação por ao menos quatro horas
- [ ] revalidar fechamento/reabertura, direta, sac, duplicata, health, erro, histórico e segurança
- [ ] mapear cada critério e meta ao teste/relatório/artefato correspondente

## Acceptance Criteria
- os 12 critérios da seção 18 possuem evidência objetiva e status aprovado
- operação de quatro horas não exige intervenção e não repete eventos
- release é aprovada somente se piloto, recursos, latência, docs, segurança e install smoke estiverem aceitos

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: revisão independente da matriz e execução dos checks finais no artefato exato da release
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- relatório final assinado/classificado
- hash da release e matriz completa de evidências

## Riscos
- testar build diferente do artefato liberado
- aceitar taxa adequada sem decisão registrada

## Blockers possíveis
- qualquer critério sem evidência, falha crítica ou política impeditiva

## Próximo passo provável
- encerrar MVP e derivar apenas correções reais; evoluções exigem nova formalização

## Feedback obrigatório de retorno
- classificação approved/rework/blocked; critérios; evidências; versão liberada
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_quality_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

