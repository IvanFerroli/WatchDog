# TASK-WDG-020 - Implementar suíte automatizada unitária e de integração

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-020-implementar-suite-automatizada-do-mvp.md

## Modo
- mode: verification
- generation-mode: derivação inicial

## Capability
- qualidade

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 17.1, 17.2, 18 e 24.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Cobrir automaticamente regras puras e integrações críticas do adapter ao notifier/store, incluindo falhas e reinício.

## Contexto mínimo
Esta task consolida os testes exigidos sem substituir os cenários manuais dependentes do Slack real.

## Inputs
- implementação TASK-WDG-009 a TASK-WDG-019
- fixtures anonimizadas da TASK-WDG-008

## Dependências
### Satisfeitas
- TASK-WDG-009 a TASK-WDG-019 concluídas
### Em aberto
- partes Windows que exigem fake/runner Windows

## Alvos explícitos
- tests/unit
- tests/integration
- tests/fixtures
- pipeline CI

## Fora de escopo
- teste manual do Slack real
- piloto de expediente
- declarar aceite apenas por cobertura

## Checklist de execução
- [ ] cobrir classificação, normalização, dedup, regras, serialização, retenção e idioma
- [ ] cobrir adapter com fixtures, store real e notifier substituível
- [ ] cobrir falha, mudança de janela, restart, health e recuperação

## Acceptance Criteria
- cada item das seções 17.1 e 17.2 possui teste ou justificativa explícita de teste manual
- cenários direta, sac, unknown, duplicata e restart passam
- CI executa a suíte e falha em regressão crítica

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: executar comandos canônicos de lint, testes, cobertura aplicável e build
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- outputs da CI/local
- matriz requisito → teste

## Riscos
- mock esconder falha de UI Automation real
- teste flaky por tempo/thread

## Blockers possíveis
- runner Windows indisponível para parte nativa

## Próximo passo provável
- TASK-WDG-021

## Feedback obrigatório de retorno
- matriz/cobertura; falhas; cenários mantidos manuais
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_quality_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

