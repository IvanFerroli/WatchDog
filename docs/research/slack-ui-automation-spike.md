# Spike de UI Automation do Slack Desktop

## Metadata
- status: blocked-awaiting-windows-slack
- owner: runtime + validação manual Windows
- last-updated: 2026-07-22
- source-of-truth: docs/research/slack-ui-automation-spike.md
- tasks: TASK-WDG-005, TASK-WDG-006, TASK-WDG-007, TASK-WDG-008

## Objetivo e regra do gate
Provar em ambiente real se a árvore UIA do Slack Desktop distingue menção direta de menção a grupo e se a fonte permanece utilizável nos estados exigidos. Este documento é protocolo e harness documental; campos de resultado permanecem `NÃO EXECUTADO` até evidência Windows real.

Nenhuma fixture sintética, dump fabricado ou inspeção no DOM/web pode promover este gate. Um go requer execução em Windows interativo com Slack Desktop e casos controlados.

## Estado atual e blocker
- Host de preparação: Linux 6.6.87.2-microsoft-standard-WSL2 x86_64.
- Python disponível no host: 3.12.3.
- Slack Desktop real com sessão/casos controlados: não disponibilizado a esta execução.
- Backend UIA Windows executável pelo processo Python deste host Linux: não disponível.
- TASK-WDG-005: protocolo materializado.
- TASK-WDG-006: bloqueada, sem evidência direta/grupo real.
- TASK-WDG-007: bloqueada por dependência da 006 e ausência dos estados reais.
- TASK-WDG-008: bloqueada; nenhuma das cinco conclusões pode ser escolhida honestamente.

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
| foreground_activity_open | aberta | Slack | 0/3 | 0/3 | NÃO EXECUTADO | ausente |
| background_activity_open | aberta | outro app | 0/3 | 0/3 | NÃO EXECUTADO | ausente |
| minimized_activity_open | aberta | minimizado | 0/3 | 0/3 | NÃO EXECUTADO | ausente |
| foreground_activity_closed | fechada | Slack/outro canal | 0/3 | 0/3 | NÃO EXECUTADO | ausente |
| background_activity_closed | fechada | outro app | 0/3 | 0/3 | NÃO EXECUTADO | ausente |

Classificação permitida por célula: `FUNCIONA`, `PARCIAL`, `NÃO FUNCIONA`. Sempre anexar motivo e referência à evidência anonimizada.

## Comparação direta versus grupo

| Campo | Menção direta | Menção a grupo | Discrimina? | Estabilidade |
|---|---|---|---|---|
| control type | NÃO OBSERVADO | NÃO OBSERVADO | incerto | incerta |
| accessible name/rótulo | NÃO OBSERVADO | NÃO OBSERVADO | incerto | incerta |
| automation id | NÃO OBSERVADO | NÃO OBSERVADO | incerto | incerta |
| class name | NÃO OBSERVADO | NÃO OBSERVADO | incerto | incerta |
| hierarquia | NÃO OBSERVADO | NÃO OBSERVADO | incerto | incerta |
| outro padrão UIA | NÃO OBSERVADO | NÃO OBSERVADO | incerto | incerta |

## Identidade, navegação e custo
- Identificador estável disponível: NÃO EXECUTADO.
- Candidato de fingerprint: NÃO DEFINIDO; depende dos campos observados.
- Activity precisa estar aberta: INCERTO.
- Navegação automática necessária: INCERTO.
- Interferência da navegação: NÃO MEDIDA.
- Tempo de scan p50/p95/max: NÃO MEDIDO.
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
- Hipótese: NÃO AVALIADA.
- Activity precisa estar aberta: INCERTO.
- Slack minimizado funciona: NÃO EXECUTADO.
- Campo que diferencia menção direta: NÃO OBSERVADO.
- Campo que diferencia grupo: NÃO OBSERVADO.
- Identificador estável disponível: NÃO EXECUTADO.
- Próxima abordagem recomendada: executar este protocolo em Windows + Slack real.
- Decisão: BLOQUEADO; SEM GO e SEM NO-GO TÉCNICO.

## Sinais de interrupção imediata
- Evidência contém conversa, URL, e-mail, nome ou canal real.
- Caso controlado não pode ser isolado do conteúdo corporativo.
- Política impede inspeção/navegação/exportação.
- Harness necessita token, cookie, tráfego, injeção, OCR ou cache interno.
- Resultado depende apenas de posição visual ou literal do usuário.

## Próximo passo
Disponibilizar uma estação Windows autorizada, Slack Desktop autenticado, casos controlados e executor humano. Após a execução, revisar derivados, preencher a matriz e somente então fechar TASK-WDG-006–008 e criar fixtures/ADR de estratégia se a evidência suportar.
