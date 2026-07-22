# TASK-WDG-007 - Validar estados da janela, identidade do item e navegação

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-007-validar-estados-identidade-e-navegacao.md

## Modo
- mode: audit
- generation-mode: derivação inicial

## Capability
- descoberta

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 7, 17.3, 21/Riscos 2, 3, 7, 8, 23 questões 4–9 e 25.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Medir como a fonte se comporta em todos os estados exigidos e se há identificador, navegação e custo suficientes para a estratégia do MVP.

## Contexto mínimo
O comportamento minimizado e com Activity fechada não pode ser presumido.

## Inputs
- evidência da TASK-WDG-006
- matriz do protocolo da TASK-WDG-005

## Dependências
### Satisfeitas
- TASK-WDG-006 concluída
### Em aberto
- necessidade de Activity aberta ou navegação automatizada
- estabilidade de identificador acessível

## Alvos explícitos
- protótipo do spike
- docs/research/slack-ui-automation-spike.md

## Fora de escopo
- implementar clique da notificação
- otimizar prematuramente o polling
- escolher fallback invasivo

## Checklist de execução
- [ ] repetir em foco, sem foco, minimizado, Activity fechada e outro canal
- [ ] avaliar identificador e efeitos de navegar até Activity
- [ ] medir tempo de varredura e registrar versão/idioma/tema/escala

## Acceptance Criteria
- cada estado tem resultado funciona, parcial ou não funciona com evidência
- identificador estável é confirmado ou sua ausência é registrada
- interferência da navegação e custo de scan têm medição suficiente para decisão

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- validações aplicáveis passam sem exposição de dados sensíveis
- comportamento, riscos e decisões duráveis são documentados
- retorno ao Taskyfier informa execução ou blocker real

## Validação
- método: execução repetida da matriz e comparação entre capturas anonimizadas
- resultado esperado: objetivo único observável sem expansão de escopo

## Evidência esperada
- matriz preenchida
- tempos e fingerprints anonimizados

## Riscos
- teste único mascarar comportamento intermitente
- automação interferir no trabalho do usuário

## Blockers possíveis
- estado não reproduzível ou política impedir navegação automatizada

## Próximo passo provável
- TASK-WDG-008

## Feedback obrigatório de retorno
- matriz; estabilidade; custo; interferência; dúvidas remanescentes
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_runtime_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

