# TASK-WDG-022 - Executar piloto de confiabilidade durante expediente

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-022-executar-piloto-de-confiabilidade.md

## Modo
- mode: verification
- generation-mode: derivação inicial

## Capability
- piloto

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 17.4, 18/Meta de qualidade, 19/Fase 4 e 21.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Operar o Watchdog por um expediente completo e medir detecção, falsos positivos/negativos, duplicatas, latência, CPU e memória.

## Contexto mínimo
Termos qualitativos como baixo e adequado não serão convertidos em números inventados; o relatório registra valores e decisão explícita do responsável.

## Inputs
- matriz manual aprovada da TASK-WDG-021
- instrumentação TASK-WDG-019

## Dependências
### Satisfeitas
- TASK-WDG-021 aprovada
### Em aberto
- amostra suficiente de menções diretas e grupos durante o piloto
- aceitação do responsável sobre detecção adequada e recursos compatíveis

## Alvos explícitos
- relatório de piloto
- dados agregados anonimizados
- lista rastreável de rework se necessário

## Fora de escopo
- prometer confiabilidade absoluta
- mascarar falsos negativos
- adicionar features P2

## Checklist de execução
- [ ] rodar durante expediente e manter diário de ground truth
- [ ] comparar reais/detectadas e calcular métricas exigidas
- [ ] registrar limitações, consumo e qualquer quebra por Slack

## Acceptance Criteria
- relatório contém contagens de reais/detectadas, FP, FN, duplicatas, latência, CPU e memória
- metas zero ideal de FN/duplicata, FP próximo de zero e latência até 10s são avaliadas sem ocultar desvio
- qualquer desvio crítico bloqueia release e retorna à task responsável

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: reconciliação manual do ground truth com store/logs e revisão do relatório pelo responsável
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- relatório e métricas agregadas
- decisão aprovado, rework ou bloqueado

## Riscos
- amostra pequena gerar falsa confiança
- erro humano no ground truth

## Blockers possíveis
- falso negativo crítico, duplicata, instabilidade ou política corporativa

## Próximo passo provável
- TASK-WDG-023 se aprovado; rework rastreável se não

## Feedback obrigatório de retorno
- métricas; decisão; limitações; tasks que precisam reabrir
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_quality_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

