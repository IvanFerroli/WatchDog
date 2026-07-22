# Tasks

## Objetivo
Registrar entregas pequenas, executaveis, rastreaveis e validaveis.

## Quando usar
- quebrar uma spec aceita em uma entrega pequena;
- definir alvo, DoD, validacao e evidencia;
- orientar execucao sem abrir escopo.

## Convencao minima
- ID: `TASK-<TRACK>-###`
- Arquivo: `TASK-<TRACK>-###-<slug>.md`
- Template: `docs/tasks/_template.md`

Tracks sao definidos por projeto. Evite herdar tracks de outro projeto sem necessidade.

## Campos obrigatorios
- `status`
- `owner`
- `last-updated`
- `source-of-truth`

## Fora de escopo
- task grande com varios objetivos;
- implementacao sem validacao;
- registro narrativo sem artefato esperado.

## Backlog atual
- AlwaysTrack Watchdog MVP: [ALWAYSTRACK_WATCHDOG_TASK_MANIFEST.md](ALWAYSTRACK_WATCHDOG_TASK_MANIFEST.md)
- Sequencia executavel: TASK-WDG-001 a TASK-WDG-025.
