# TASK-WDG-014 - Implementar deduplicação e processamento idempotente

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-014-implementar-deduplicacao-idempotente.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- deduplicação

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 8.1–8.3, 10.1/D, 14 e 21/Risco 5.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Gerar chave tolerante e persistir o processamento de modo que cada item direto possa alertar no máximo uma vez, inclusive após reinício.

## Contexto mínimo
A assinatura deve usar identificador acessível quando houver e fallback comprovado quando não houver.

## Inputs
- estratégia de identidade da TASK-WDG-008
- store da TASK-WDG-013
- eventos da TASK-WDG-012

## Dependências
### Satisfeitas
- TASK-WDG-012 e TASK-WDG-013 concluídas
### Em aberto
- janela temporal e pesos finais definidos pelo spike/piloto

## Alvos explícitos
- deduplication service
- transação/fluxo de status no store

## Fora de escopo
- deduplicar somente em memória
- considerar itens visualmente similares sempre iguais
- emitir notificação real

## Checklist de execução
- [ ] implementar chave e raw fingerprint versionados
- [ ] consultar/persistir processado de forma atômica
- [ ] testar pequenas mudanças, repetição visível e restart

## Acceptance Criteria
- mesmo evento observado repetidamente produz uma única decisão de alerta
- reiniciar a aplicação não reabilita item antigo
- eventos distintos próximos não colidem no corpus de teste

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: testes determinísticos de repetição, restart, colisão e concorrência relevante
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- vetores de dedup
- testes de idempotência

## Riscos
- colisão causar falso negativo
- condição de corrida entre persistência e alerta

## Blockers possíveis
- ausência de campos suficientes para assinatura confiável

## Próximo passo provável
- TASK-WDG-015

## Feedback obrigatório de retorno
- algoritmo/janela; colisões; comportamento sem external id
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_runtime_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

