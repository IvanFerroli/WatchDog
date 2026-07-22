# ADR-002 - Baseline técnica do MVP Windows

## Metadata
- status: accepted
- owner: projeto
- last-updated: 2026-07-22
- source-of-truth: docs/adr/ADR-002-baseline-tecnica-windows.md

## Contexto
O master spec fixa Windows, UI Automation, operação local-first, adapter substituível e distribuição sem privilégios no workspace, mas deixa abertas as questões 1, 2 e 10–13. A baseline precisa viabilizar scaffolding, testes e empacotamento sem transformar a hipótese sobre a árvore real do Slack em fato.

## Decisão

### Runtime e forma do aplicativo
- Adotar CPython 3.12 como baseline do MVP.
- Entregar um aplicativo desktop per-user com processo único, tray e painel sob demanda; não usar Windows Service no MVP.
- Separar core/aplicação de adapters Windows, persistência, notificações e UI. O core não importa `pywinauto`, `tkinter`, `pystray` ou `winotify`.

### UI Automation, painel e tray
- Usar `pywinauto` com backend UIA no adapter descartável do spike e, somente após go, no adapter de produção.
- Usar `tkinter` para painel/histórico/preferências mínimos e `pystray` para o ícone e comandos da bandeja.
- Manter toda chamada de UI no thread apropriado e comunicar o monitor por filas/eventos internos; detalhes serão fechados nos contratos e no runtime.

### Notificação e som
- Usar `winotify` para toast do Windows e `winsound` da biblioteca padrão para som local.
- Tratar toast e som como portas de saída substituíveis. Clique para abrir item específico fica fora do MVP.

### Configuração e armazenamento
- Adotar JSON UTF-8 versionado para configuração serializável, com defaults versionados no pacote e override em `%LOCALAPPDATA%\AlwaysTrack\Watchdog\config.json`.
- Validar configuração na entrada, rejeitar chaves/valores inválidos com erro acionável e nunca guardar credenciais Slack.
- Adotar SQLite por meio do módulo `sqlite3` da biblioteca padrão, com schema versionado e migrations explícitas.
- Armazenar banco, logs e estado em `%LOCALAPPDATA%\AlwaysTrack\Watchdog\`; persistir apenas previews mínimos e fingerprints necessários.

### Build, instalação e atualização
- Gerar o executável Windows com PyInstaller. Preferir bundle `onedir` no MVP para startup e diagnóstico mais previsíveis; qualquer mudança para `onefile` exige smoke test equivalente.
- Gerar instalador per-user com Inno Setup, `PrivilegesRequired=lowest`, destino sob `%LOCALAPPDATA%\Programs\AlwaysTrack Watchdog` e autostart opt-in.
- Atualização será manual no MVP: release versionado, download explícito pelo usuário e upgrade preservando configuração/banco mediante migrations. Não haverá updater residente.
- Builds distribuíveis devem ser produzidos e testados em Windows; execução de testes portáveis em Linux não substitui smoke de Windows.

### Política de versões
- O projeto declara `requires-python >=3.12`; Python 3.12 é a baseline obrigatória de build/test do MVP, e versões posteriores só recebem suporte declarado após smoke Windows equivalente.
- Dependências diretas usam ranges compatíveis no manifesto e versões resolvidas/pinadas no artefato de build ou lock adotado pelo projeto.
- Upgrades de `pywinauto`, Slack Desktop, Python, PyInstaller ou installer exigem reexecução dos checks Windows afetados.

## Questões abertas resolvidas
| Questão do master spec | Resposta da baseline |
|---:|---|
| 1. Stack | Python 3.12 + pywinauto/UIA + tkinter/pystray + winotify/winsound + SQLite |
| 2. Forma | aplicativo desktop/tray standalone per-user; não serviço |
| 10. Configuração | JSON versionado em LocalAppData, defaults no pacote |
| 11. Banco | SQLite via biblioteca padrão, schema e migrations versionados |
| 12. Notificação | winotify; som por winsound; porta substituível |
| 13. Atualização | manual no MVP, com upgrade per-user e migrations |

## Alternativas consideradas
1. C#/.NET com Windows App SDK e UI Automation nativa: integração Windows forte, mas amplia o custo inicial e diverge da baseline solicitada para o primeiro spike.
2. Python com Qt: UI mais rica, porém bundle e licença/dependências são maiores que o necessário para o painel mínimo.
3. Electron: familiar ao ecossistema Slack, mas consumo e complexidade são desproporcionais ao agente local.
4. Windows Service com UI separada: aumenta complexidade de sessão/desktop interativo e não é adequado para automação da UI do usuário.
5. Registro/INI para configuração e arquivo plano para histórico: simples no início, mas inferiores a JSON serializável e SQLite versionado para evolução e deduplicação.
6. Atualização automática: conveniente, porém adiciona superfície de segurança, assinatura, rollback e operação antes do piloto.

## Consequências
- positivas: stack pequena, adequada a protótipo e app local, bibliotecas Windows isoláveis, persistência sem servidor e instalação sem elevação.
- negativas: Python/PyInstaller aumenta o tamanho do bundle; tkinter limita sofisticação visual; pywinauto e winotify dependem de comportamento real do Windows.
- trade-offs: privilegia velocidade, diagnóstico e reversibilidade; não promete que UIA do Slack é viável nem congela seletores antes do spike.

## Limites arquiteturais
- Imports Windows ficam nos adapters; modelos, classificação, regras e contratos permanecem testáveis fora do Windows.
- O adapter expõe observações brutas e erros tipados; não vaza objetos `pywinauto` ao core.
- UI/tray/notifier consomem portas da aplicação e não acessam diretamente o Slack ou o SQLite.
- O processo não solicita credenciais Slack nem privilégios administrativos de workspace.

## Impacto em artefatos
- specs relacionadas: doc/ALWAYSTRACK_WATCHDOG_MASTER_SPEC.md
- tasks relacionadas: TASK-WDG-002, TASK-WDG-003, TASK-WDG-004, TASK-WDG-005, TASK-WDG-009, TASK-WDG-013, TASK-WDG-016–018, TASK-WDG-023
- runbooks relacionados: docs/research/slack-ui-automation-spike.md

## Validação e evidência esperada
- validação portátil: importar e testar core sem dependências Windows em Python 3.12.
- validação Windows: executar smoke de pywinauto/UIA, toast, som, tray, painel, SQLite, bundle PyInstaller e instalação/upgrade/uninstall per-user.
- evidência: relatórios automatizados mais checklist Windows ligado à versão do Python, Slack e artefato construído.

## Riscos e sinais de revisão
- `winotify` ou pystray não operar corretamente no alvo corporativo.
- políticas de notificação/execução/autostart bloquearem o app.
- antivirus ou SmartScreen sinalizar o bundle sem assinatura.
- Slack deixar de expor os controles necessários por UIA.
- mudança de Python/dependência quebrar o build Windows.

## Fora de escopo
Provar a árvore do Slack, definir seletores, implementar o adapter, escolher fallback, integrar AlwaysTrack, criar updater automático ou definir assinatura/canal de distribuição corporativo.
