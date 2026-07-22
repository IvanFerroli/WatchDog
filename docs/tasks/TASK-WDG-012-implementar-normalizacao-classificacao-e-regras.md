# TASK-WDG-012 - Implementar normalização, classificação e regras de alerta

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-012-implementar-normalizacao-classificacao-e-regras.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- classificação

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 8.2, 10.1/B, C e E, 13, 17.1 e 22/Decisão 006.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Transformar itens brutos em eventos e decidir de forma determinística que somente menção direta nova alerta; grupo e desconhecido não alertam.

## Contexto mínimo
Mensagens diretas e outras categorias podem existir no enum, mas não recebem comportamento opcional no MVP.

## Inputs
- contratos/config da TASK-WDG-009
- fixtures aprovadas da TASK-WDG-008
- extração da TASK-WDG-011

## Dependências
### Satisfeitas
- TASK-WDG-011 concluída
### Em aberto
- rótulos por idioma e aliases reais configuráveis

## Alvos explícitos
- src/classification
- src/core normalizer
- notification rules

## Fora de escopo
- IA de urgência
- mensagem direta como gatilho
- regras não sustentadas por fixture

## Checklist de execução
- [ ] normalizar texto sem perder campos de identidade
- [ ] classificar direta, grupo e desconhecido com versão
- [ ] aplicar tabela de decisão e registrar motivo sem mensagem completa

## Acceptance Criteria
- fixture direta resulta em DIRECT_MENTION e alert=true
- fixture sac resulta em GROUP_MENTION e alert=false
- evento não reconhecido resulta em UNKNOWN, registro e alert=false

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: testes table-driven para rótulos, aliases, idioma, normalização e regras
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- suite de classificação
- matriz fixture → classificação → decisão

## Riscos
- falso negativo por variação de rótulo
- classificação dependente apenas de @nome

## Blockers possíveis
- fixtures não representarem rótulos reais

## Próximo passo provável
- TASK-WDG-013

## Feedback obrigatório de retorno
- regras/versionamento; casos desconhecidos; cobertura de idioma
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_runtime_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

