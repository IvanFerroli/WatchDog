# TASK-WDG-023 - Empacotar release candidate instalável no Windows

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-023-empacotar-release-candidate-windows.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- packaging e rollout

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 8.5, 13, 15, 19/Fase 5 e 23 questão 13.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Produzir executável/instalador distribuível com configuração persistente, autostart opcional, logs acessíveis e atualização controlada.

## Contexto mínimo
O pacote deve preservar dados locais e migrations; atualização automática só entra se foi escolhida na baseline, caso contrário o fluxo é manual controlado.

## Inputs
- piloto aprovado da TASK-WDG-022
- build/versionamento TASK-WDG-004
- baseline técnica TASK-WDG-002

## Dependências
### Satisfeitas
- TASK-WDG-022 aprovada
### Em aberto
- assinatura do binário e canal de distribuição, se exigidos pelo ambiente

## Alvos explícitos
- packaging
- installer/executable
- configuração de autostart
- migrations/upgrade e uninstall

## Fora de escopo
- publicar externamente sem autorização
- auto-update não decidido
- remover histórico do usuário no uninstall sem escolha explícita

## Checklist de execução
- [ ] gerar artefato versionado e reproduzível
- [ ] implementar install/upgrade/uninstall e autostart opt-in
- [ ] validar LocalAppData, config, logs e migrations entre versões

## Acceptance Criteria
- usuário instala e executa o Watchdog sem montar ambiente de desenvolvimento
- autostart pode ser habilitado/desabilitado e o pacote não requer privilégio do workspace
- upgrade controlado preserva configuração/schema compatíveis e uninstall trata dados conforme escolha explícita

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: smoke em instalação limpa e upgrade sobre instalação anterior controlada
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- hash/versão do artefato
- checklist install/upgrade/uninstall/autostart

## Riscos
- antivírus bloquear binário
- upgrade corromper banco/config

## Blockers possíveis
- restrição de assinatura/distribuição corporativa

## Próximo passo provável
- TASK-WDG-024

## Feedback obrigatório de retorno
- artefato/hashes; plataformas testadas; migrações; ressalvas de distribuição
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_scaffolding_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

