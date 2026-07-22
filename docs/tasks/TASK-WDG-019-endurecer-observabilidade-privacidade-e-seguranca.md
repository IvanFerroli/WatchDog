# TASK-WDG-019 - Endurecer observabilidade, diagnóstico, privacidade e segurança

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-019-endurecer-observabilidade-privacidade-e-seguranca.md

## Modo
- mode: implementation
- generation-mode: derivação inicial

## Capability
- observabilidade e segurança

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 15, 16, 21/Riscos 3, 4, 6, 7 e 8 e 23 questão 15.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Tornar falhas explicáveis sem expor conteúdo corporativo, mantendo todos os dados locais, logs redigidos e diagnóstico anonimizado.

## Contexto mínimo
Observabilidade e privacidade compartilham a mesma fronteira de dados; o hardening é gate antes dos testes reais e do piloto.

## Inputs
- runtime/UI TASK-WDG-010 a TASK-WDG-018
- política local-first da spec

## Dependências
### Satisfeitas
- TASK-WDG-010 a TASK-WDG-018 concluídas
### Em aberto
- confirmação de política corporativa antes do piloto

## Alvos explícitos
- logging estruturado
- métricas e snapshots de health
- modo diagnóstico e export anonimizado
- configurações de segurança, permissões e ignore de artefatos

## Fora de escopo
- telemetria externa
- mensagens completas em logs
- tokens/cookies/credenciais Slack
- upload automático de dumps/screenshots

## Checklist de execução
- [ ] instrumentar todos os logs essenciais e métricas de tempo/recursos
- [ ] implementar export de árvore anonimizada e comparação de estrutura
- [ ] aplicar redaction, armazenamento em LocalAppData, permissões, secrets hygiene e política de fixtures

## Acceptance Criteria
- o sistema explica Activity ausente, classificação, duplicidade, alerta, erro e retomada sem corpo completo
- modo diagnóstico exporta tipos/nomes anonimizados, tempos e versões e pode comparar snapshots
- não existe telemetria externa, captura de credencial ou fixture/conversa real; revisão de política corporativa fica registrada

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: testes de redaction e inspeção de logs/export/config/repositório com dados sintéticos sensíveis
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- amostras sanitizadas de log/export
- checklist de privacidade/segurança e conformidade

## Riscos
- redaction insuficiente
- diagnóstico detalhado virar canal de vazamento

## Blockers possíveis
- política corporativa proibir automação ou captura mesmo anonimizada

## Próximo passo provável
- TASK-WDG-020

## Feedback obrigatório de retorno
- campos redigidos; artefatos produzidos; decisão de conformidade; overhead medido
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_quality_builder
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

