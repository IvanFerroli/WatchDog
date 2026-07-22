# TASK-WDG-004 - Configurar qualidade, build, CI e versionamento

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-004-configurar-qualidade-build-e-ci.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- qualidade e infraestrutura

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 12, 19/Fase 0 e 24.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Configurar lint, formatação, testes, build reproduzível, CI, versionamento e convenção de releases para o projeto.

## Contexto mínimo
A Definition of Done exige validações aplicáveis; o projeto precisa desses gates antes do spike virar código definitivo.

## Inputs
- scaffolding da TASK-WDG-003
- decisões de tooling da TASK-WDG-002

## Dependências
### Satisfeitas
- TASK-WDG-003 concluída
### Em aberto
- executor de CI e política exata de versão definidos na baseline

## Alvos explícitos
- configuração de lint/format/test/build
- .github/workflows ou equivalente
- arquivos de versão e release

## Fora de escopo
- empacotar release final
- implementar testes funcionais do produto

## Checklist de execução
- [ ] configurar comandos locais únicos
- [ ] configurar pipeline CI com cache somente se seguro
- [ ] registrar esquema de versão de app, adapter, classifier e banco

## Acceptance Criteria
- lint, testes vazios e build executam localmente e na CI
- falha em qualquer gate impede artefato de release
- versões de app, adapter, classifier e schema têm origem identificável

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- validações aplicáveis passam sem exposição de dados sensíveis
- comportamento, riscos e decisões duráveis são documentados
- retorno ao Taskyfier informa execução ou blocker real

## Validação
- método: executar lint, testes e build e revisar resultado da CI
- resultado esperado: objetivo único observável sem expansão de escopo

## Evidência esperada
- outputs dos comandos
- workflow/configurações versionados

## Riscos
- CI dependente de ambiente Windows indisponível
- gates lentos demais para ciclos curtos

## Blockers possíveis
- runner Windows necessário e não disponível

## Próximo passo provável
- TASK-WDG-005

## Feedback obrigatório de retorno
- comandos canônicos; status da CI; limitações do runner
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_quality_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

