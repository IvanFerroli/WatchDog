# TASK-WDG-024 - Documentar instalação, operação, privacidade e troubleshooting

## Metadata
- status: proposed
- owner: olympus-orchestrator (routing)
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/TASK-WDG-024-documentar-instalacao-operacao-e-troubleshooting.md

## Modo
- mode: planning
- generation-mode: derivação inicial

## Capability
- documentação operacional

## Origem documental
- Documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- Base específica: Seções 12/Arquivos recomendados, 15–18, 19/Fases 4–5 e 24.
- Memória operacional: docs/operations/taskyfier-memory.md

## Objetivo único
Entregar documentação suficiente para instalar, operar, diagnosticar e usar responsavelmente a release candidate.

## Contexto mínimo
Documentação de instalação e troubleshooting é critério explícito de aceite.

## Inputs
- artefato da TASK-WDG-023
- evidências do spike, testes e piloto

## Dependências
### Satisfeitas
- TASK-WDG-023 concluída
### Em aberto
- limitações finais e versões suportadas vindas dos testes

## Alvos explícitos
- README.md
- docs/operations/troubleshooting.md
- docs/operations/privacy-and-security.md
- docs/testing/test-strategy.md
- notas de release/limitações

## Fora de escopo
- documentar features P2
- copiar logs ou conversas reais
- prometer compatibilidade futura absoluta

## Checklist de execução
- [ ] documentar instalação, configuração, tray, painel, histórico, pause/resume e autostart
- [ ] documentar estados health, diagnóstico, recuperação e coleta segura de evidência
- [ ] documentar privacidade, políticas, versões suportadas, limitações e resultados do piloto

## Acceptance Criteria
- uma pessoa sem ambiente de desenvolvimento instala e opera seguindo o README
- troubleshooting cobre Slack ausente/inacessível, Activity, estrutura alterada, duplicata e logs
- privacidade/test strategy explicam dados locais, retenção, redaction e validações executadas

## Definition of Done
- acceptance criteria satisfeitos e evidenciados
- testes/validações aplicáveis passam e erros são tratados
- nenhuma informação sensível é exposta
- documentação afetada e retorno operacional são atualizados

## Validação
- método: walkthrough documental em máquina limpa por revisor diferente
- resultado esperado: objetivo observável sem regressão fora do escopo

## Evidência esperada
- docs versionados
- checklist do walkthrough e links válidos

## Riscos
- docs divergirem do binário
- instruções de diagnóstico exporem dados

## Blockers possíveis
- comportamento final do pacote não estar estável

## Próximo passo provável
- TASK-WDG-025

## Feedback obrigatório de retorno
- walkthrough; lacunas; versões e limitações documentadas
- informar arquivos alterados, comandos/checks, resultado e regressões
- indicar updates sugeridos para docs/operations e próxima task

## Handoff
- handoff_to: olympus-orchestrator
- execution_expectation: task executada ou bloqueada, com evidência, validação, updates sugeridos de docs/operations e próximo passo recomendado
- expected_specialist: olympus_docs_formalizer
- feedback_contract: status; artefatos; validação; evidência; riscos; blocker; próximo passo
- constraints: sem escopo novo; sem implementação fora desta task; preservar dados sensíveis

