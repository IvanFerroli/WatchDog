# TASK-WDG-017 - Implementar tray e execução em segundo plano

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-017-implementar-tray-e-execucao-em-background.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- UI Windows

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 8.5, 10.1/H e 19/Fase 3.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Manter o Watchdog na bandeja e expor abrir painel, pausar, retomar, status e encerrar com shutdown correto.

## Contexto mínimo
Inicialização com Windows será instalada na preparação da release, mas a preferência deve ser suportada.

## Inputs
- orquestração e health da TASK-WDG-015
- baseline UI da TASK-WDG-002

## Dependências
### Satisfeitas
- TASK-WDG-015 concluída
### Em aberto
- framework de tray já decidido

## Alvos explícitos
- src/ui/tray
- entrypoint/lifecycle do aplicativo

## Fora de escopo
- interface completa de produtividade
- painel AlwaysTrack
- serviço do Windows

## Checklist de execução
- [ ] criar ícone/menu e sincronizar comandos com runtime
- [ ] manter execução sem janela principal
- [ ] encerrar workers/store com segurança

## Acceptance Criteria
- fechar painel não encerra monitoramento
- pausar/retomar muda health e impede/retoma scans
- encerrar pelo tray finaliza processos e persiste estado sem corrupção

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: testes de comandos e smoke manual de lifecycle
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- checklist do tray
- logs de pause/resume/shutdown

## Riscos
- processo órfão
- dupla instância

## Blockers possíveis
- framework não oferecer tray confiável

## Próximo passo provável
- TASK-WDG-018

## Feedback obrigatório de retorno
- comandos; lifecycle; comportamento de múltiplas instâncias
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_runtime_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

