# Project Intake - AlwaysTrack Watchdog

## Metadata
- status: accepted
- owner: projeto
- last-updated: 2026-07-22
- source-of-truth: docs/project/intake.md
- baseline-source-status: planejamento inicial, versão 0.1

## Fonte canônica
- documento central: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- referências auxiliares: docs/adr/ADR-001-governanca-documental-operacional.md; docs/tasks/ALWAYSTRACK_WATCHDOG_TASK_MANIFEST.md
- protocolo operacional equivalente vigente: docs/pipeline/protocol.md

## Objetivo em uma frase
Entregar um agente local e instalável para Windows que observe o Slack Desktop, alerte uma única vez para cada nova menção direta e ignore menções a grupos, especialmente `@sac`.

## Recorte do MVP
- Provar primeiro, em Slack Desktop real no Windows, que UI Automation distingue menção direta de menção a grupo.
- Implementar somente monitoramento, classificação mínima, deduplicação persistente, alerta nativo e som, histórico mínimo, health, tray/painel básico e recuperação.
- Validar a matriz manual, executar piloto de confiabilidade e distribuir um instalador Windows per-user.
- Encerrar o recorte quando os 12 critérios de aceite da seção 18 estiverem ligados a evidência do mesmo release candidate.

## Restrições explícitas
- Windows é o único sistema operacional alvo do MVP.
- A primeira abordagem é Windows UI Automation; sua viabilidade continua condicionada ao spike real.
- Operação local-first, sem telemetria externa por padrão e com dados no diretório do usuário.
- Não capturar token, cookie, senha, tráfego ou cache interno do Slack.
- Não exigir app oficial, aprovação administrativa ou privilégios administrativos no workspace Slack.
- Core, adapter, UI, persistência e notificação permanecem desacoplados.
- Conteúdo corporativo não entra no repositório; dumps e screenshots são sensíveis e fixtures devem ser anonimizadas.

## Decisões já tomadas
- O Watchdog nasce como projeto independente e standalone-first.
- O núcleo será preparado para integração futura por contratos, sem implementar integração com AlwaysTrack no MVP.
- UI Automation é a primeira tentativa e o spike é gate obrigatório antes do produto.
- Menção direta é o único gatilho obrigatório; grupo e desconhecido não alertam.
- Dados, logs e histórico permanecem locais por padrão.
- API oficial Slack, OCR, interceptação, injeção e leitura de cache não fazem parte da abordagem inicial.

## Incertezas e gates
- Se, quando e em quais estados a Activity e seus cartões permanecem acessíveis.
- Qual campo real diferencia menção direta e menção a grupo em diferentes idiomas/versões.
- Se existe identificador estável por item e qual deduplicação ele permite.
- Se navegar até Activity é necessário e quanto isso interfere no usuário.
- Política corporativa aplicável ao uso em máquina de trabalho.
- Limites aceitáveis de detecção e recursos, a serem medidos no piloto sem promessa antecipada.

## Fora do MVP
- P2 da seção 20, inclusive abrir/focar item, marcar como visto e filtros extras.
- Mensagens diretas como gatilho obrigatório e classificação de urgência por IA.
- API/painel do AlwaysTrack ou absorção como biblioteca/serviço.
- Outlook, Teams, WhatsApp, Jira, AlwaysChat ou qualquer outra fonte.
- Outros sistemas operacionais, atualização automática e compatibilidade futura sem manutenção.
- Qualquer fallback invasivo sem nova spec, ADR e derivação de backlog.

## Capacidades candidatas
- adapter isolado para Slack UI Automation;
- normalização e classificação determinística;
- deduplicação e histórico local versionado;
- notificação Windows, tray/painel e health;
- diagnóstico seguro, empacotamento e operação per-user.

## Primeira fatia recomendada
Executar o protocolo seguro do spike em Windows com Slack Desktop real e casos controlados, encerrando o gate com uma das cinco conclusões permitidas pelo master spec antes de implementar o adapter de produção.

## O que não assumir
- que o Slack minimizado expõe a mesma árvore;
- que Activity pode ficar fechada;
- que rótulos, hierarchy ou automation ids são estáveis;
- que fixtures sintéticas comprovam UI Automation real;
- que a baseline técnica comprova a hipótese do spike;
- que um fallback está autorizado se UI Automation falhar.
