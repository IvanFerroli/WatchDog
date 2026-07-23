# Troubleshooting

## Slack não encontrado

Confirme que o Slack Desktop está aberto, que `slack.process_names` inclui
`slack.exe` e aguarde o retry. O health esperado é `SLACK_NOT_RUNNING`, sem
encerrar o Watchdog.

## Slack inacessível ou Activity ausente

Verifique idioma/versão do Slack e se a Activity está no estado aprovado pelo
spike. `SLACK_NOT_ACCESSIBLE`, `ACTIVITY_NOT_FOUND` ou `DEGRADED` devem aparecer
com erro estruturado. O Watchdog não abre abas nem envia atalhos: reabra
`Activity > Menções` manualmente. Não habilite OCR ou leitura de cache como
improviso.

## Mensagens diretas não aparecem

Confirme que as notificações do Slack e do Windows estão habilitadas. O source
requer `UserNotificationListener.GetAccessStatus()` igual a `Allowed`; acesso
negado aparece como `WINDOWS_NOTIFICATIONS_ACCESS_DENIED`. A primeira varredura
é somente baseline, portanto toasts que já existiam ao iniciar não geram alerta.

`SOURCE_PARTIAL_FAILURE` significa que uma fonte falhou, mas a outra continua
operando. Notificações que não sejam inequivocamente uma DM do Slack são
ignoradas por segurança; não relaxe o filtro sem nova evidência controlada.

## Estrutura alterada após update

Pause o monitor, execute o helper de inspeção apenas com eventos controlados e
compare o export anonimizado. Uma mudança incompatível exige revalidação do
adapter; não adicione seletores de posição sem evidência.

## Alerta duplicado

Não apague o banco primeiro. Registre a versão, horário e dedup key
anonimizada, pause o monitor e preserve os logs sanitizados para diagnóstico.

## Sem alerta

Consulte health, última leitura e último erro. Confirme se o item foi
classificado como `DIRECT_MENTION`, `DIRECT_MESSAGE`, `GROUP_MENTION` ou
`UNKNOWN`. Eventos desconhecidos são registrados e nunca alertam por padrão.

## Logs e dados

Use o caminho exibido no painel. Antes de compartilhar, remova previews,
nomes, canais e qualquer dump bruto. Não publique o banco local.
