# Protocolos de Actuacion del Agente

## Caso A: consultar "nota diaria" o "lo que tiene hoy"

1. Ejecuta `$DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily get` o lee el archivo `$HOME/Notas/journal/<YYYY-MM-DD>.md`.
2. Lee los eventos en el frontmatter y las tareas bajo `## TODO`.
3. Presenta al usuario un resumen limpio distinguiendo tareas completadas (`[x]`), pospuestas (`[>]`) y pendientes (`[ ]`), agrupadas por categoria.

## Caso B: apuntar una tarea en la "nota diaria"

1. Determina la categoria (`Casa / Personal`, `Trabajo` o `Social`).
2. Usa el helper `$DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily add-task "<tarea>" --category "<categoria>"`.
3. Si la nota diaria aun no existe, el helper la crea automaticamente.

## Caso C: marcar una tarea como hecha

1. Localiza la linea con `- [ ] <nombre de tarea>` en `$HOME/Notas/journal/<YYYY-MM-DD>.md`.
2. Sustituyela por `- [x] <nombre de tarea>`.

## Caso D: posponer una tarea

1. Usa el helper:
   ```bash
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily postpone-task "<nombre de tarea>" --to <fecha_destino>
   ```
2. Si editas manualmente:
   - Cambia el checkbox de `- [ ]` a `- [>]` en la nota origen y anade `⏳ pospuesto a [[<YYYY-MM-DD-destino>]]`.
   - Crea o abre la nota destino y anade la tarea con `- [>]` y `⏳ pospuesto desde [[<YYYY-MM-DD-origen>]]`.
   - Si la nota destino no existe, creala con frontmatter YAML (`id`, `description`, `events`, `aliases`, `tags: [daily-notes]`).

## Caso E: crear un apunte o nota conceptual

1. Genera un ID con formato `<TIMESTAMP>-<SLUG/ACRONIMO>.md`.
2. Crea el archivo en `$HOME/Notas/zettelkasten/`.
3. Incluye el frontmatter YAML obligatorio (`id`, `description`, `aliases`, `tags`).

**Regla de enlaces:** siempre que referencies un dia concreto, usa el formato de enlace Obsidian `[[YYYY-MM-DD]]` apuntando al archivo `journal/YYYY-MM-DD.md`.
