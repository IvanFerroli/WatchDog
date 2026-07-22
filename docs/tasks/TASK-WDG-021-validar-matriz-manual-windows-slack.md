# TASK-WDG-021 - Validar matriz manual Windows e Slack

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-021-validar-matriz-manual-windows-slack.md

## Modo
- mode: verification
- generation-mode: derivação inicial

## Capability
- qualidade

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seção 17.3, 18 critérios 1–3, 5, 7–10 e 21.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Executar os cenários manuais obrigatórios em ambiente real e registrar resultado reproduzível por versão do Slack/Windows.

## Contexto mínimo
Tema, escala, minimização e Activity dependem do comportamento real e não podem ser aprovados só com fixtures.

## Inputs
- suíte e release de desenvolvimento da TASK-WDG-020
- protocolo seguro da TASK-WDG-005

## Dependências
### Satisfeitas
- TASK-WDG-020 concluída
### Em aberto
- máquina Windows, Slack real e geradores controlados de eventos

## Alvos explícitos
- tests/manual
- relatório de validação e evidências anonimizadas

## Fora de escopo
- piloto de expediente completo
- alterações de escopo sem nova task
- captura de conversas reais

## Checklist de execução
- [ ] executar todos os 11 cenários da tabela 17.3
- [ ] registrar versões, configuração, latência e health por cenário
- [ ] abrir rework rastreável para falhas antes do piloto

## Acceptance Criteria
- direta alerta uma vez; sac não alerta; repetição/restart não duplicam
- Slack fechado/aberto recupera; minimizado e Activity fechada seguem estratégia aprovada
- update simulado, tema e escala não causam falha silenciosa e qualquer limitação fica explícita

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: revisão do checklist assinado e correspondência entre logs e resultados observados
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- matriz completa passa/falha
- logs/screenshots sanitizados quando indispensáveis

## Riscos
- evidência insuficiente de cenário intermitente
- variação por versão Slack

## Blockers possíveis
- cenário crítico falhar ou ambiente indisponível

## Próximo passo provável
- TASK-WDG-022 após passes; rework da task responsável se falhar

## Feedback obrigatório de retorno
- matriz; versões; falhas; rework requerido
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_quality_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

