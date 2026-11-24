---
name: notas
description: |
  Identifica, resuelve, consulta y gestiona notas en la boveda personal de Obsidian y Neovim.
  Herramientas: resolve_note.py, notes_index.py, vault en $HOME/Notas.
  No usar para: notas fuera de ~/Notas, crear archivos en la raiz de la vault, ignorar AGENTS.md.
version: 1.0.0
---

# Skill: Gestor y Resolutor de Notas

Esta skill ensena al agente a operar con la boveda personal en `$HOME/Notas`, respetando `AGENTS.md` y la integracion con Neovim/Obsidian.

## Reglas globales

1. Nunca crear archivos en la raiz de `$HOME/Notas/`. Toda nota pertenece a una subcarpeta.
2. Las notas diarias residen en `journal/YYYY-MM-DD.md`.
3. Toda nueva nota debe incluir frontmatter YAML con `id`, `description`, `aliases` y `tags`.
4. Las notas diarias llevan siempre la etiqueta `daily-notes`.
5. Volcados `.sql` o scripts pesados van en `projects/<nombre-proyecto>/backups/`.

## Enrutamiento

| Tarea | Archivo |
| --- | --- |
| Arquitectura y reglas de la boveda | [references/vault_architecture.md](references/vault_architecture.md) |
| Catalogo de tipos de nota | [references/note_types.md](references/note_types.md) |
| Comandos de resolve_note.py | [references/resolve_note.md](references/resolve_note.md) |
| Busqueda semantica con notes_index.py | [references/notes_index.md](references/notes_index.md) |
| Protocolos de actuacion del agente | [references/protocols.md](references/protocols.md) |
| Ejemplos de resolucion de consultas | [examples/resolving_queries.md](examples/resolving_queries.md) |
| Flujos de trabajo con la nota diaria | [examples/daily_note_workflows.md](examples/daily_note_workflows.md) |
| Validar esta skill | [scripts/lint_skill.py](scripts/lint_skill.py) |

## Flujo de trabajo

1. Identifica la entidad que el usuario menciona.
2. Consulta el archivo de referencia correspondiente.
3. Ejecuta el helper o edita la nota directamente.
4. Verifica el resultado (ejecuta `scripts/lint_skill.py` solo si modificaste esta skill).
