# Troubleshooting

## Slack não encontrado

Confirme que o Slack Desktop está aberto, que `slack.process_names` inclui
`slack.exe` e aguarde o retry. O health esperado é `SLACK_NOT_RUNNING`, sem
encerrar o Watchdog.

## Slack inacessível ou Activity ausente

Verifique idioma/versão do Slack e se a Activity está no estado aprovado pelo
spike. `SLACK_NOT_ACCESSIBLE`, `ACTIVITY_NOT_FOUND` ou `DEGRADED` devem aparecer
com erro estruturado. Não habilite OCR ou leitura de cache como improviso.

## Estrutura alterada após update

Pause o monitor, execute o helper de inspeção apenas com eventos controlados e
compare o export anonimizado. Uma mudança incompatível exige revalidação do
adapter; não adicione seletores de posição sem evidência.

## Alerta duplicado

Não apague o banco primeiro. Registre a versão, horário e dedup key
anonimizada, pause o monitor e preserve os logs sanitizados para diagnóstico.

## Sem alerta

Consulte health, última leitura e último erro. Confirme se o item foi
classificado como `DIRECT_MENTION`, `GROUP_MENTION` ou `UNKNOWN`. Eventos
desconhecidos são registrados e nunca alertam por padrão.

## Logs e dados

Use o caminho exibido no painel. Antes de compartilhar, remova previews,
nomes, canais e qualquer dump bruto. Não publique o banco local.
