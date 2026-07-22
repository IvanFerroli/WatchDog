# Privacidade e segurança

O Watchdog é local-first. Ele não usa API oficial do Slack, token, cookie,
senha, interceptação de tráfego ou telemetria externa.

## Dados locais

Por padrão, configuração, banco e logs ficam em
`%LOCALAPPDATA%\AlwaysTrack\Watchdog`. O histórico mantém somente preview
mínimo e metadados disponíveis. Eventos relevantes expiram em 30 dias e
ignorados em 7 dias, salvo configuração válida diferente.

## Logs e diagnóstico

- corpo completo, credenciais e identificadores reconhecíveis não devem ir para logs;
- export UIA substitui nomes acessíveis por presença, tamanho e fingerprint;
- screenshots e dumps brutos não pertencem ao repositório;
- fixtures versionadas usam somente conteúdo sintético;
- nenhum export é enviado automaticamente.

## Uso responsável

Antes do piloto, o responsável deve confirmar que automação de acessibilidade
e retenção local são compatíveis com a política corporativa. Ausência dessa
confirmação bloqueia piloto e release.
