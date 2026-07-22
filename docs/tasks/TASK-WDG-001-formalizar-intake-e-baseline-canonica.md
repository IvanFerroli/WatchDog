# TASK-WDG-001 - Formalizar intake e baseline canônica do MVP

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-001-formalizar-intake-e-baseline-canonica.md

## Modo
- mode: planning
- generation-mode: derivação inicial

## Capability
- governança documental

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 1–5, 19/Fase 0, 22 e 23; docs/project/README.md; ADR-001.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Criar o intake curto que reconhece o master spec como fonte canônica, fixa o recorte do MVP e registra as incertezas sem inventar decisões.

## Contexto mínimo
O repositório ainda não possui intake da instância. O protocolo operacional esperado em docs/operations não existe; docs/pipeline/protocol.md será registrado como equivalente vigente.

## Inputs
- doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- docs/project/_intake-template.md e docs/pipeline/protocol.md
- docs/adr/ADR-001-governanca-documental-operacional.md

## Dependências
### Satisfeitas
- documento central disponível e integralmente lido
- direção do usuário restringindo o backlog ao MVP
### Em aberto
- confirmação formal de que a versão 0.1 passa de planejamento para baseline aceita de execução

## Alvos explícitos
- docs/project/intake.md
- referências operacionais ao protocolo equivalente, sem duplicar seu conteúdo

## Fora de escopo
- decidir stack ou bibliotecas
- alterar código do produto
- copiar integralmente o master spec sem justificativa

## Checklist de execução
- [ ] preencher metadata e vínculo canônico
- [ ] resumir objetivo, restrições, decisões e fora do MVP
- [ ] listar gates e indicar o spike como primeira fatia técnica

## Acceptance Criteria
- o intake aponta exatamente para o master spec e preserva seu status
- o recorte termina no MVP instalável/piloto aprovado e exclui P2
- stack, fallback e thresholds não são inventados; aparecem como decisões abertas

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- validações aplicáveis passam sem exposição de dados sensíveis
- comportamento, riscos e decisões duráveis são documentados
- retorno ao Taskyfier informa execução ou blocker real

## Validação
- método: revisão documental contra as seções 1–5, 22 e 23 e busca por expansões de escopo
- resultado esperado: objetivo único observável sem expansão de escopo

## Evidência esperada
- diff de docs/project/intake.md
- checklist de cobertura das decisões e incertezas

## Riscos
- tratar uma recomendação como decisão final
- duplicar documentação canônica e criar divergência

## Blockers possíveis
- baseline não ser aceita pelo responsável do projeto

## Próximo passo provável
- TASK-WDG-002

## Feedback obrigatório de retorno
- status de aceitação do intake; dúvidas mantidas; qualquer mudança no recorte do MVP
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_docs_formalizer
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

