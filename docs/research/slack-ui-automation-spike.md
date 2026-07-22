# Spike de UI Automation do Slack Desktop

## Metadata
- status: partially-confirmed-windows-slack
- owner: runtime + validação manual Windows
- last-updated: 2026-07-22
- source-of-truth: docs/research/slack-ui-automation-spike.md
- tasks: TASK-WDG-005, TASK-WDG-006, TASK-WDG-007, TASK-WDG-008

## Objetivo e regra do gate
Provar em ambiente real se a árvore UIA do Slack Desktop distingue menção direta de menção a grupo e se a fonte permanece utilizável nos estados exigidos. Os estados ainda não exercitados permanecem `NÃO EXECUTADO`; resultados preenchidos abaixo vêm de evidência Windows real sanitizada.

Nenhuma fixture sintética, dump fabricado ou inspeção no DOM/web pode promover este gate. Um go requer execução em Windows interativo com Slack Desktop e casos controlados.

## Estado atual e blocker
- Host de preparação inicial: Linux 6.6.87.2-microsoft-standard-WSL2 x86_64.
- Execução real: Windows build 26200, escala 100%, cultura `pt-BR`.
- Python Windows: 3.12.10.
- Slack Desktop: 4.50.143.
- Backend UIA: executado com `pywinauto` 0.6.9 em sessão desktop interativa.
- TASK-WDG-005: protocolo materializado.
- TASK-WDG-006: evidência técnica confirmada em Activity/Menções.
- TASK-WDG-007: parcial; foreground e navegação confirmados, estados background/minimizado pendentes.
- TASK-WDG-008: parcial; implementação atual é viável com Activity/Menções acessível.

## Resultado real observado em 22/07/2026
- Navegação principal: `automation_id=activity-inbox`, `TabItem`.
- Container: título `Menções`, `control_type=List`.
- Cartão: `control_type=ListItem`.
- Menção direta: `automation_id` iniciado por `at_user-`.
- Menção a grupo: `automation_id` iniciado por `at_user_group-`.
- Identidade estável: o próprio `automation_id` do cartão, contendo referência de canal e timestamp.
- Leitura inicial: 14 itens; 8 diretos, 4 de grupo e 2 separadores/desconhecidos.
- Repetição: 11 scans registrados sem duplicatas, falhas ou alertas de grupo.
- Evidência bruta sanitizada permaneceu em diretório temporário e não foi commitada.
- Conclusão provisória: **Viável, mas requer Activity/Menções acessível**.
- Pendências: segundo emissor/casos novos controlados, background, minimizado, Activity fechada e piloto.

## Pré-requisitos do ambiente Windows
- Windows 10/11 em sessão desktop interativa do usuário.
- CPython 3.12 e dependências do projeto instaladas em ambiente isolado.
- Slack Desktop instalado, autenticado e com versão registrada.
- Ferramenta de inspeção UIA aprovada, por exemplo Accessibility Insights for Windows ou Inspect.exe.
- Workspace/canal de teste autorizado e duas pessoas de teste, sem conteúdo corporativo real.
- Permissão para criar menções controladas e exportar somente evidência anonimizada.
- Diretório temporário fora do repositório para dumps/screenshots brutos, com descarte ao final.

## Casos controlados
Use aliases fictícios e mensagens sem contexto real:

| Caso | Ação do emissor | Resultado semântico esperado |
|---|---|---|
| C-DIRECT-01 | enviar `@PessoaTeste ping direto WDG-D01` | candidato a `DIRECT_MENTION` |
| C-GROUP-01 | enviar `@grupo-teste ping coletivo WDG-G01` | candidato a `GROUP_MENTION` |
| C-UNKNOWN-01 | gerar atividade não classificada, se autorizado | `UNKNOWN`, sem alerta |

Os resultados esperados são oráculos do caso, não evidência de que o Slack os expõe corretamente.

## Protocolo seguro de captura
1. Registrar data/hora, Windows, Slack, Python, idioma, tema, escala e ferramenta de inspeção.
2. Fechar qualquer conversa corporativa não relacionada e usar somente o canal/casos controlados.
3. Criar C-DIRECT-01 e C-GROUP-01 com códigos únicos.
4. Abrir Activity/Mentions e localizar janela, container e cartões por UIA.
5. Para cada cartão, coletar somente `control_type`, `name` redigido, `automation_id`, `class_name`, caminho hierárquico redigido, bounds normalizados, padrões UIA e estado offscreen/enabled.
6. Substituir pessoas, workspace e canais por `PERSON_A`, `WORKSPACE_A`, `CHANNEL_A`; substituir corpo por `BODY_DIRECT_01` ou `BODY_GROUP_01`.
7. Calcular fingerprints apenas sobre valores anonimizados; não salvar a árvore inteira se o recorte do cartão bastar.
8. Repetir no mínimo três vezes por caso/estado, sem alterar a ordem dos itens deliberadamente.
9. Guardar artefatos brutos somente no diretório temporário; revisar manualmente antes de copiar qualquer derivado para o repositório.
10. Descartar dumps e screenshots brutos após aprovação dos derivados, conforme política local.

## Harness de coleta
O protótipo descartável deve aceitar parâmetros explícitos e produzir JSON Lines redigido. Interface esperada, a ser implementada/executada em Windows pela frente runtime:

```text
python scripts/slack_uia_spike.py inspect \
  --case C-DIRECT-01 \
  --state foreground_activity_open \
  --output <temp-dir>/direct-foreground.jsonl \
  --redact
```

Cada registro derivado deve conter, no máximo:

```json
{
  "schema_version": 1,
  "provenance": "real_windows_slack_redacted",
  "case_id": "C-DIRECT-01",
  "state": "foreground_activity_open",
  "run": 1,
  "environment": {
    "windows": "REQUIRED",
    "slack": "REQUIRED",
    "python": "3.12.x",
    "language": "REQUIRED",
    "theme": "REQUIRED",
    "scale_percent": "REQUIRED"
  },
  "card": {
    "control_type": "OBSERVED_OR_NULL",
    "name_token": "REDACTED_OR_NULL",
    "automation_id": "OBSERVED_OR_NULL",
    "class_name": "OBSERVED_OR_NULL",
    "hierarchy_tokens": [],
    "patterns": [],
    "is_offscreen": null
  },
  "available_fields": {
    "event_type": false,
    "sender": false,
    "channel": false,
    "preview": false,
    "stable_id": false
  },
  "scan_duration_ms": null,
  "navigation_performed": false,
  "user_interference": "none|visible_focus_change|unknown",
  "notes": "NO_REAL_CONTENT"
}
```

O harness deve falhar fechado se `--redact` não estiver ativo, se detectar padrões de e-mail/URL corporativa, ou se campos obrigatórios de ambiente estiverem ausentes.

## Matriz de execução obrigatória

| Estado | Activity | Foco | Runs direta | Runs grupo | Resultado | Evidência |
|---|---|---|---:|---:|---|---|
| foreground_activity_open | aberta | Slack | 3/3 | 3/3 | FUNCIONA | logs sanitizados; 11 scans estáveis |
| background_activity_open | aberta | outro app | 0/3 | 0/3 | NÃO EXECUTADO | ausente |
| minimized_activity_open | aberta | minimizado | 0/3 | 0/3 | NÃO EXECUTADO | ausente |
| foreground_activity_closed | fechada | Slack/outro canal | 0/3 | 0/3 | NÃO EXECUTADO | ausente |
| background_activity_closed | fechada | outro app | 0/3 | 0/3 | NÃO EXECUTADO | ausente |

Classificação permitida por célula: `FUNCIONA`, `PARCIAL`, `NÃO FUNCIONA`. Sempre anexar motivo e referência à evidência anonimizada.

## Comparação direta versus grupo

| Campo | Menção direta | Menção a grupo | Discrimina? | Estabilidade |
|---|---|---|---|---|
| control type | `ListItem` | `ListItem` | não | estável nos scans |
| accessible name/rótulo | presente, redigido | presente, redigido | não utilizado | estável nos scans |
| automation id | prefixo `at_user-` | prefixo `at_user_group-` | sim | estável nos scans |
| class name | não necessário | não necessário | não | n/a |
| hierarquia | lista `Menções` | lista `Menções` | não | estável nos scans |
| outro padrão UIA | ID contém canal/timestamp | ID contém canal/timestamp | sim | estável nos scans |

## Identidade, navegação e custo
- Identificador estável disponível: SIM, `automation_id` do `ListItem`.
- Candidato de fingerprint: fallback apenas; identidade principal é o ID do cartão.
- Activity precisa estar aberta: SIM na implementação atual.
- Navegação automática necessária: SIM quando Activity não estiver acessível.
- Interferência da navegação: mudança visível para a aba Activity.
- Tempo de captura sanitizada observado: cerca de 1,5 s; p50/p95 ainda pendentes.
- Lista virtualizada/itens offscreen: NÃO AVALIADO.

Para estabilidade, repetir captura sem novos eventos, após troca de canal, após minimizar/restaurar e após reiniciar Slack. Um campo só é candidato estável se persistir nos runs relevantes sem incorporar PII/conteúdo completo.

## Anonimização, retenção e descarte
| Campo/artefato | Regra antes do repositório | Retenção |
|---|---|---|
| pessoa/remetente | token `PERSON_<n>` | somente derivado |
| canal/workspace | tokens `CHANNEL_<n>`/`WORKSPACE_<n>` | somente derivado |
| preview/body | token do caso; nunca texto real | somente derivado mínimo |
| timestamps | arredondar/remover quando não necessários | somente métrica |
| automation id/class/control type | manter apenas se não contiver PII | fixture aprovada |
| hierarchy | manter recorte mínimo e redigido | fixture aprovada |
| dump bruto | nunca commitar | apagar após revisão |
| screenshot | evitar; se indispensável, redigir e revisar visualmente | fora do repo por padrão |
| logs do protótipo | redigidos por construção | até fechar o spike |

## Critérios de aprovação por task

### TASK-WDG-006
- Um item direto e um de grupo encontrados em pelo menos três runs no estado foreground/activity aberta.
- Campo discriminador observável que não dependa apenas do literal `@PessoaTeste`.
- Disponibilidade de sender, canal, preview e identificador registrada, inclusive quando ausente.

### TASK-WDG-007
- Todas as linhas da matriz classificadas com evidência.
- Estabilidade de identidade, necessidade/interferência de navegação e custo p50/p95/max registrados.
- Ambiente completo e qualquer virtualização/variação documentados.

### TASK-WDG-008
- Relatório final contém os campos da seção 25 do master spec.
- Somente uma das cinco conclusões permitidas é escolhida, derivada da matriz.
- Go apenas para estratégia comprovada; insuficiência/inviabilidade bloqueia TASK-WDG-009–025 e exige nova formalização de fallback.
- Fixtures só entram em `tests/fixtures/slack_ui/` com `provenance=real_windows_slack_redacted`, revisão humana e nenhum conteúdo real.

## Registro final do gate
- Hipótese: PARCIALMENTE CONFIRMADA.
- Activity precisa estar aberta: SIM na implementação atual.
- Slack minimizado funciona: NÃO EXECUTADO.
- Campo que diferencia menção direta: prefixo `at_user-` no `automation_id`.
- Campo que diferencia grupo: prefixo `at_user_group-` no `automation_id`.
- Identificador estável disponível: SIM, ID completo do cartão.
- Próxima abordagem recomendada: validar estados background/minimizado/Activity fechada e evento novo controlado.
- Decisão provisória: VIÁVEL COM ACTIVITY/MENÇÕES ACESSÍVEL; gate completo ainda parcial.

## Sinais de interrupção imediata
- Evidência contém conversa, URL, e-mail, nome ou canal real.
- Caso controlado não pode ser isolado do conteúdo corporativo.
- Política impede inspeção/navegação/exportação.
- Harness necessita token, cookie, tráfego, injeção, OCR ou cache interno.
- Resultado depende apenas de posição visual ou literal do usuário.

## Próximo passo
Disponibilizar uma estação Windows autorizada, Slack Desktop autenticado, casos controlados e executor humano. Após a execução, revisar derivados, preencher a matriz e somente então fechar TASK-WDG-006–008 e criar fixtures/ADR de estratégia se a evidência suportar.
