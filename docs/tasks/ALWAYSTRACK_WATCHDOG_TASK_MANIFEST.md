# AlwaysTrack Watchdog — Manifesto de Tasks do MVP

## Metadata
- status: proposed
- owner: olympus_taskyfier
- last-updated: 2026-07-22
- source-of-truth: docs/tasks/ALWAYSTRACK_WATCHDOG_TASK_MANIFEST.md
- documento canônico: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- modo: derivação inicial

## Objetivo
Sequenciar todas e somente as entregas necessárias para chegar a um MVP Windows instalável, funcional e aprovado contra a seção 18 do master spec.

## Leitura do estado
- Não há implementação do produto nem tasks anteriores concluídas.
- O master spec 0.1 está marcado como planejamento inicial; TASK-WDG-001 formaliza a baseline antes da execução.
- docs/operations/engineering-pipeline-protocol.md não existe. Nesta derivação, docs/pipeline/protocol.md é o equivalente operacional vigente.
- A memória esperada também não existia e foi inicializada em docs/operations/taskyfier-memory.md.
- O .gitignore atual ignora docs/. Os artefatos estão materializados no workspace, mas a política de versionamento dessa superfície precisa ser confirmada antes de commit/release.
- A estratégia UI Automation é hipótese, não fato. TASK-WDG-008 é gate obrigatório.

## Premissas e gates
1. UI Automation só autoriza as tasks de produto após evidência real do spike.
2. Se TASK-WDG-008 concluir UI Automation insuficiente ou inviável, TASK-WDG-009 a TASK-WDG-025 ficam bloqueadas e o fallback deve receber nova spec/ADR e nova derivação.
3. Stack, banco, configuração, notifier, tray, packaging e update serão decididos em TASK-WDG-002; SQLite continua sugestão, não decisão antecipada.
4. Campos ausentes de sender, canal e preview são tratados como opcionais.
5. Baixo consumo, memória compatível e taxa adequada não recebem números inventados. TASK-WDG-022 mede e o responsável registra a decisão.
6. O contrato genérico e as portas substituíveis existem apenas para desacoplar o MVP. Não autorizam API, painel ou integração AlwaysTrack.
7. Toda task aplica a Definition of Done da seção 24 além de seus acceptance criteria próprios.

## Prioridade
- G0: gate que bloqueia todo trabalho posterior.
- M0: obrigatório para o funcionamento e aceite do MVP.
- M1: obrigatório para readiness, distribuição ou operação do MVP.
- R0: gate final de liberação.

## Sequência operacional completa

### Fase 0 — Setup e decisões

| Ordem | ID | Task | Prioridade | Depende de | Resultado verificável |
|---:|---|---|---|---|---|
| 1 | TASK-WDG-001 | Formalizar intake e baseline canônica | G0 | nenhuma | intake vincula fonte, recorte, decisões, incertezas e primeira fatia sem inventar stack |
| 2 | TASK-WDG-002 | Decidir stack e baseline técnica | G0 | 001 | ADRs resolvem questões técnicas que bloqueiam scaffold, Windows e distribuição |
| 3 | TASK-WDG-003 | Criar scaffolding modular | M0 | 002 | build mínimo passa e core não depende de UI/Slack concreto |
| 4 | TASK-WDG-004 | Configurar qualidade, build, CI e versionamento | M0 | 003 | lint, testes e build reproduzíveis passam localmente/CI |

### Fase 1 — Spike e go/no-go

| Ordem | ID | Task | Prioridade | Depende de | Resultado verificável |
|---:|---|---|---|---|---|
| 5 | TASK-WDG-005 | Preparar protocolo seguro do spike | G0 | 004 | matriz de estados, casos controlados e política de anonimização aprovados |
| 6 | TASK-WDG-006 | Provar menção direta versus grupo | G0 | 005 | árvore distingue direta de sac e registra campos disponíveis |
| 7 | TASK-WDG-007 | Validar estados, identidade e navegação | G0 | 006 | foco, background, minimizado, Activity fechada e outro canal têm evidência |
| 8 | TASK-WDG-008 | Fechar gate de viabilidade | G0 | 006, 007 | uma das cinco conclusões da spec, ADR de estratégia e fixtures anonimizadas |

### Fase 2 — Núcleo funcional

| Ordem | ID | Task | Prioridade | Depende de | Resultado verificável |
|---:|---|---|---|---|---|
| 9 | TASK-WDG-009 | Definir contratos, portas e configuração | M0 | 008 go | eventos, enums, portas e config serializável compilam sem acoplamento à UI |
| 10 | TASK-WDG-010 | Descoberta e ciclo da janela Slack | M0 | 009 | Slack ausente espera; abrir/reabrir retoma; perda não derruba o processo |
| 11 | TASK-WDG-011 | Acesso e extração da Activity | M0 | 010 | itens brutos são lidos na estratégia aprovada e quebra estrutural é observável |
| 12 | TASK-WDG-012 | Normalização, classificação e regras | M0 | 011 | direta alerta; grupo e desconhecido não alertam; decisão é versionada |
| 13 | TASK-WDG-013 | Store, histórico e retenção | M0 | 009 | schema/migrations, histórico mínimo, estado e retenção sobrevivem a restart |
| 14 | TASK-WDG-014 | Deduplicação e idempotência | M0 | 012, 013 | mesmo item alerta no máximo uma vez, inclusive após reinício |
| 15 | TASK-WDG-015 | Orquestração, health e recuperação | M0 | 010–014 | fluxo completo monitora, degrada, pausa, recupera e encerra sem silêncio |

### Fase 3 — Windows, UI e hardening

| Ordem | ID | Task | Prioridade | Depende de | Resultado verificável |
|---:|---|---|---|---|---|
| 16 | TASK-WDG-016 | Notificação Windows e som | M0 | 014, 015 | um toast/som por direta; nenhum por grupo, unknown ou duplicata |
| 17 | TASK-WDG-017 | Tray e execução em background | M0 | 015 | painel pode fechar; tray pausa, retoma, mostra status e encerra corretamente |
| 18 | TASK-WDG-018 | Painel, histórico e preferências | M1 | 013, 015, 017 | status/contadores/erro, histórico e config mínima refletem o runtime |
| 19 | TASK-WDG-019 | Observabilidade, diagnóstico, privacidade e segurança | M0 | 010–018 | falhas explicáveis, exports anonimizados, dados locais e nenhuma credencial/telemetria |

### Fase 4 — Testes e piloto

| Ordem | ID | Task | Prioridade | Depende de | Resultado verificável |
|---:|---|---|---|---|---|
| 20 | TASK-WDG-020 | Suíte automatizada do MVP | M0 | 009–019 | itens 17.1/17.2 cobertos ou justificados; CI bloqueia regressão |
| 21 | TASK-WDG-021 | Matriz manual Windows/Slack | M0 | 020 | todos os cenários 17.3 têm passa/falha, versão e evidência segura |
| 22 | TASK-WDG-022 | Piloto de confiabilidade | G0 | 021 aprovada | expediente mede FN, FP, duplicatas, latência, CPU e memória e decide go/rework |

### Fase 5 — Empacotamento e aceite

| Ordem | ID | Task | Prioridade | Depende de | Resultado verificável |
|---:|---|---|---|---|---|
| 23 | TASK-WDG-023 | Empacotar release candidate Windows | M1 | 022 aprovada | instalador/exe, autostart opt-in, upgrade, migrations e uninstall passam smoke |
| 24 | TASK-WDG-024 | Documentar instalação e operação | M1 | 023 | README, troubleshooting, privacidade, testes e limitações passam walkthrough |
| 25 | TASK-WDG-025 | Gate final de aceite e liberação | R0 | 020–024 | 12 critérios e metas apontam evidência do mesmo artefato e versão é aprovada |

## Mapa dos packages
- TASK-WDG-001 a TASK-WDG-025 possuem packages individuais completos em docs/tasks/.
- Cada package contém objetivo único, inputs, dependências, alvos, fora de escopo, checklist, acceptance criteria, DoD, validação, evidência, riscos, blockers, feedback e handoff ao olympus-orchestrator.
- A execução deve ocorrer em sequência, uma task por ciclo; feedback real pode reabrir a task responsável, mas não autoriza feature nova.

## Rastreabilidade por seção do master spec

| Seção/requisito | Task IDs |
|---|---|
| 1. Fonte central, atualização junto da decisão | 001, 024 |
| 2. Agente local, background, observar, classificar, deduplicar, alertar, histórico | 003, 009–018, 023–025 |
| 3. Problema de ruído e risco operacional | 001, 006, 012, 021, 022 |
| 4. Objetivo principal e objetivos secundários | 009–019, 022–025 |
| 5. Não objetivos do MVP | 001, 002, 005, 008, 009, 019, seção Fora do MVP |
| 6.1 UI Automation e categorias/rótulos | 005–008, 011, 012, 020, 021 |
| 6.2 Não depender da API oficial | 002, 019, 025 |
| 6.3 OCR, websocket e cache descartados no início | 005, 008, 019 |
| 7. Hipótese, spike, estados e cinco conclusões | 005–008 |
| 8.1 Monitoramento e recuperação | 010, 011, 014, 015, 020, 021 |
| 8.2 Classificação mínima | 008, 009, 012, 020, 021 |
| 8.3 Toast, som, conteúdo disponível e uma vez | 014, 016, 020, 021 |
| 8.4 Campos do histórico | 009, 013, 018, 020, 025 |
| 8.5 Background, tray e comandos | 015, 017, 018, 023, 025 |
| 9. Fluxo operacional completo | 010–016 |
| 10. Arquitetura e separação de responsabilidades | 002, 003, 009–019 |
| 10.1/A Slack UI Adapter | 008, 010, 011 |
| 10.1/B Event Normalizer | 009, 012 |
| 10.1/C Event Classifier | 009, 012 |
| 10.1/D Deduplication Service | 013, 014 |
| 10.1/E Notification Rules | 012, 014 |
| 10.1/F Windows Notifier | 009, 016 |
| 10.1/G Local Event Store | 009, 013 |
| 10.1/H Tray/UI | 017, 018 |
| 10.1/I Health Monitor | 015, 018, 019 |
| 11.1 Desacoplamento mínimo, configuração serializável, schema versionado e eventos internos | 002, 003, 009, 013, 015 |
| 11.2/11.3 Preparação futura sem integrar | 009 somente para envelope/portas; opções A/B/C ficam fora do MVP |
| 12. Estrutura e arquivos iniciais | 003, 004, 005, 008, 024 |
| 13. Configuração e aliases/idioma/rótulos | 002, 009, 012, 018, 023 |
| 14. Persistência, dados mínimos, dedup e retenção | 013, 014, 020 |
| 15. Privacidade, LocalAppData, dados sensíveis e política | 005, 013, 019, 023, 024, 025 |
| 16. Logs, painel diagnóstico e modo diagnóstico | 011, 015, 018, 019, 024 |
| 17.1 Unitários | 020 |
| 17.2 Integração | 020 |
| 17.3 Manuais | 021 |
| 17.4 Confiabilidade | 022 |
| 18. Critérios e metas | 022, 025; detalhamento na matriz abaixo |
| 19. Fase 0 | 001–004 |
| 19. Fase 1 | 005–008 |
| 19. Fase 2 | 009–015 |
| 19. Fase 3 | 016–019 |
| 19. Fase 4 | 020–022 |
| 19. Fase 5 | 023–025 |
| 19. Fase 6 | fora do MVP por direção explícita |
| 20. P0 | 005–016, 018, 020–022, 025 |
| 20. P1 necessário até Fase 5 | 004, 017–019, 023, 024 |
| 20. P2 | fora do MVP, sem package |
| 21. Riscos e mitigações | 005–008, 010–016, 019–022 |
| 22. Decisões 001–006 | 001–003, 005–009, 012, 019 |
| 23. Questões em aberto | 002, 006–009, 013, 014, 016, 019, 022, 023 |
| 24. Definition of Done | todos os packages; verificação agregada em 025 |
| 25. Primeira sessão e entregável do spike | 005–008 |
| 26. Resumo executivo | backlog completo 001–025 |
| 27. Changelog | 001 e 024 quando decisões/versão mudarem |

## Cobertura dos 12 critérios de aceite

| Critério da seção 18 | Tasks que implementam/validam |
|---:|---|
| 1. Detectar nova menção direta | 006, 008, 011, 012, 016, 021, 025 |
| 2. Ignorar menção ao grupo sac | 006, 008, 012, 021, 025 |
| 3. Não alertar duas vezes | 013, 014, 016, 021, 022, 025 |
| 4. Background por quatro horas | 015, 017, 022, 025 |
| 5. Recuperar após Slack fechar/abrir | 010, 015, 020, 021, 025 |
| 6. Histórico mínimo de diretas | 013, 018, 020, 025 |
| 7. Estado de saúde | 015, 018, 019, 025 |
| 8. Registrar erro de acesso | 011, 015, 019, 021, 025 |
| 9. Sem privilégio administrativo no workspace | 002, 005, 019, 023, 025 |
| 10. Sem token, senha ou cookie | 002, 005, 019, 025 |
| 11. Instalação e troubleshooting | 023, 024, 025 |
| 12. Taxa adequada no campo | 022, 025 |

## Cobertura das metas de qualidade

| Meta | Tasks |
|---|---|
| Falsos negativos idealmente zero | 012, 020–022, 025 |
| Falsos positivos próximos de zero | 012, 020–022, 025 |
| Duplicatas zero após estabilização | 014, 020–022, 025 |
| Latência até 10 segundos | 009, 015, 019, 022, 025 |
| CPU em repouso baixa | 010, 015, 019, 022, 025 |
| Memória compatível com agente leve | 019, 022, 025 |
| Sem promessa de confiabilidade absoluta antes do piloto | 022, 024, 025 |

## Cobertura dos riscos principais

| Risco | Mitigação em tasks |
|---|---|
| Slack não expõe dados | 005–008 |
| Elementos somem minimizado | 007, 008, 021 |
| Update quebra seletores | 008, 011, 019–021 |
| Falsos negativos | 012, 019–022 |
| Duplicatas | 013, 014, 020–022 |
| Política corporativa | 005, 019, 024, 025 |
| Consumo excessivo | 007, 010, 015, 019, 022 |
| Idioma/rótulos mudam | 007–009, 012, 019, 020 |

## Resolução das questões em aberto

| Questão | Task |
|---:|---|
| 1–2 stack e forma do aplicativo | 002 |
| 3–6 árvore, Activity, navegação e minimizado | 006–008 |
| 7 identificador estável | 007, 008 |
| 8 deduplicação | 008, 014, 022 |
| 9 clique abre item | fora do MVP; não necessário ao aceite |
| 10 configuração | 002, 009 |
| 11 banco | 002, 013 |
| 12 notificação Windows | 002, 016 |
| 13 atualização manual/automática | 002, 023 |
| 14 consulta pelo AlwaysTrack | fora do MVP |
| 15 política interna | 005, 019, 025 |

## Fora do MVP
- API local, painel no AlwaysTrack ou qualquer integração real com AlwaysTrack.
- Converter/extrair o núcleo como biblioteca compartilhada, serviço local comum ou incorporação direta.
- Mensagens diretas como gatilho, outros tipos opcionais, filtros extras e classificação de urgência por IA.
- Abrir/focar o item no Slack, marcar menção como vista ou responder/enviar mensagens.
- Outlook, Teams, WhatsApp, Jira, AlwaysChat, GitHub ou outras fontes.
- App oficial Slack, tokens, cookies, credenciais, interceptação de tráfego, injeção ou leitura de cache/banco interno.
- OCR como implementação do backlog atual; se UI Automation falhar, qualquer fallback exige nova formalização.
- Outros sistemas operacionais, painel de produtividade amplo e compatibilidade futura sem manutenção.

## Handoff inicial
- handoff_to: olympus-orchestrator
- task_package: docs/tasks/TASK-WDG-001-formalizar-intake-e-baseline-canonica.md
- execution_expectation: executar ou bloquear TASK-WDG-001, devolver evidência/validação e sugerir update de memória
- constraints: uma task por ciclo; sem antecipar stack; sem produto antes do go de TASK-WDG-008; sem P2
- feedback_contract: status; artefatos; checks; evidência; riscos; blocker; próximo passo recomendado
