# TASK-WDG-010 - Implementar descoberta e ciclo de vida da janela Slack

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-010-implementar-descoberta-e-ciclo-da-janela-slack.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- runtime adapter

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 8.1, 10.1/A, 21/Riscos 2 e 23 questões 3–6.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Implementar a fronteira que detecta processo/janela Slack, espera quando ausente e se reconecta após perda ou reabertura.

## Contexto mínimo
Esta task cobre somente presença e ciclo da janela; leitura da Activity fica na task seguinte.

## Inputs
- contratos da TASK-WDG-009
- estratégia aprovada na TASK-WDG-008

## Dependências
### Satisfeitas
- TASK-WDG-009 concluída
### Em aberto
- nomes de processo e critérios de seleção vindos da configuração

## Alvos explícitos
- src/adapters/slack_ui
- test doubles mínimos do processo/janela

## Fora de escopo
- ler cartões da Activity
- classificar eventos
- iniciar o Slack automaticamente

## Checklist de execução
- [ ] implementar descoberta configurável
- [ ] modelar Slack ausente e janela perdida sem exceção fatal
- [ ] adicionar retry/backoff e retomada observável

## Acceptance Criteria
- Slack fechado resulta em estado de espera sem crash
- ao abrir ou reabrir Slack, a janela volta a ser exposta ao monitor
- perda temporária não exige reiniciar Watchdog e gera erro estruturado

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: testes com provider falso e smoke no Slack real fechado/aberto
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- testes passando
- logs de transição sem conteúdo sensível

## Riscos
- selecionar janela errada entre múltiplos processos
- polling agressivo

## Blockers possíveis
- API de automação da stack não localizar a janela conforme o spike

## Próximo passo provável
- TASK-WDG-011

## Feedback obrigatório de retorno
- estados testados; tempos de retry; falhas reais encontradas
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_runtime_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

