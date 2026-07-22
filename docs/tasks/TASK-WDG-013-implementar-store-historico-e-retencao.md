# TASK-WDG-013 - Implementar store local, histórico e retenção

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-013-implementar-store-historico-e-retencao.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- persistência

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 8.4, 10.1/G, 14 e 15.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Criar armazenamento local versionado para eventos, estado, falhas e configuração, com histórico mínimo e retenção segura.

## Contexto mínimo
O store deve evitar conteúdo completo e sobreviver a reinícios e futuras migrações do próprio MVP.

## Inputs
- decisões da TASK-WDG-002
- contratos da TASK-WDG-009

## Dependências
### Satisfeitas
- TASK-WDG-009 concluída
### Em aberto
- prazo curto exato para ignorados se não fixado na ADR

## Alvos explícitos
- src/persistence
- migrations/schema
- diretório de dados local configurado

## Fora de escopo
- sincronização externa
- armazenar mensagens completas
- API de consulta externa

## Checklist de execução
- [ ] criar schema de eventos e estado da seção 14
- [ ] implementar repositórios e migrations idempotentes
- [ ] aplicar retenção de 30 dias para relevantes, política curta para ignorados e limpeza manual

## Acceptance Criteria
- histórico contém todos os campos mínimos disponíveis e classifier version
- estado inclui scans/erros/versões e persiste entre execuções
- limpeza automática/manual não remove dados fora da política e não guarda corpo completo

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: testes com banco real temporário, migrations e relógio controlado
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- schema/migrations
- testes de CRUD, reinício e retenção

## Riscos
- corrupção ou migration destrutiva
- preview excessivamente sensível

## Blockers possíveis
- decisão de banco/path não aprovada

## Próximo passo provável
- TASK-WDG-014

## Feedback obrigatório de retorno
- schema/version; política efetiva; resultados de migration/retenção
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_runtime_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

