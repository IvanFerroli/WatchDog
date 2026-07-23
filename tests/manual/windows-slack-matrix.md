# Matriz manual Windows/Slack

Status: `BLOCKED_ENVIRONMENT` até execução em Windows com Slack real e dados controlados.

Preencher versões de Windows, Slack, Watchdog, idioma, tema, escala e hash do
artefato. Evidências devem ser anonimizadas.

| Cenário | Esperado | Resultado | Latência | Health | Evidência |
|---|---|---|---|---|---|
| menção direta | um alerta | pendente | pendente | pendente | pendente |
| DM nova com Slack sem foco | um alerta, sem mudança de foco | pendente | pendente | pendente | pendente |
| toast de DM existente ao iniciar | nenhum replay | pendente | n/a | pendente | pendente |
| toast de canal/menção | nenhum alerta de DM | pendente | n/a | pendente | pendente |
| acesso a notificações negado | erro estruturado e UIA continua | pendente | n/a | pendente | pendente |
| menção `@sac` | nenhum alerta | pendente | n/a | pendente | pendente |
| item permanece visível | sem repetição | pendente | n/a | pendente | pendente |
| reinício do Watchdog | sem repetição | pendente | n/a | pendente | pendente |
| Slack fechado | espera sem falha | pendente | n/a | pendente | pendente |
| Slack reaberto | retoma sozinho | pendente | pendente | pendente | pendente |
| Slack minimizado | conforme gate 008 | pendente | pendente | pendente | pendente |
| Activity fechada | conforme gate 008 | pendente | pendente | pendente | pendente |
| update/estrutura incompatível | erro observável | pendente | n/a | pendente | pendente |
| tema claro/escuro | sem diferença funcional | pendente | pendente | pendente | pendente |
| escala diferente | sem diferença funcional | pendente | pendente | pendente | pendente |
