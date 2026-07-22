# TASK-WDG-005 - Preparar protocolo seguro e casos do spike de UI Automation

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-005-preparar-protocolo-seguro-do-spike.md

## Modo
- mode: planning
- generation-mode: derivação inicial

## Capability
- descoberta

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 7, 15, 17.3, 21 e 25.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Definir o roteiro reproduzível e seguro para inspecionar menção direta e menção ao grupo sac sem registrar conversas reais.

## Contexto mínimo
O spike é gate obrigatório e depende de dados controlados, estados de janela conhecidos e tratamento sensível de dumps/screenshots.

## Inputs
- baseline técnica e ferramentas de inspeção
- cenários das seções 7 e 25
- regras de privacidade da seção 15

## Dependências
### Satisfeitas
- TASK-WDG-004 concluída
### Em aberto
- disponibilidade de Slack Desktop Windows e de exemplos controlados de menção direta e grupo

## Alvos explícitos
- docs/research/slack-ui-automation-spike.md
- tests/fixtures ou diretório temporário aprovado para evidências anonimizadas

## Fora de escopo
- implementar adapter definitivo
- capturar token, cookie, tráfego ou conversas reais
- definir fallback antes da evidência

## Checklist de execução
- [ ] descrever ambiente, versões e ferramenta de inspeção
- [ ] preparar matriz de cenários e campos a coletar
- [ ] definir anonimização, retenção e descarte de artefatos

## Acceptance Criteria
- roteiro cobre foco, segundo plano, minimizado, Activity fechada e outro canal
- há exemplos controlados de menção direta e sac sem dados reais no repositório
- cada campo e evidência possui regra de anonimização

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- validações aplicáveis passam sem exposição de dados sensíveis
- comportamento, riscos e decisões duráveis são documentados
- retorno ao Taskyfier informa execução ou blocker real

## Validação
- método: revisão manual do roteiro e dry-run sem persistir conteúdo corporativo
- resultado esperado: objetivo único observável sem expansão de escopo

## Evidência esperada
- protocolo versionado
- checklist de segurança aprovado

## Riscos
- vazamento em dump ou screenshot
- cenários artificiais não representarem o Slack real

## Blockers possíveis
- sem acesso ao Slack Windows ou sem autorização para criar casos de teste

## Próximo passo provável
- TASK-WDG-006

## Feedback obrigatório de retorno
- ambiente disponível; versões; limitações de segurança e dados
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_docs_formalizer
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

