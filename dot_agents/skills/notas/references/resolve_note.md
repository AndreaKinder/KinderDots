# Herramienta Helper CLI: `resolve_note.py`

Script de ayuda ubicado en `$DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py`.

## Comandos principales

1. **Identificar y resolver una entidad:**
   ```bash
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py resolve "nota diaria"
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py resolve "ayer"
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py resolve "cuentas de septiembre"
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py resolve "resumen anual" --json
   ```

2. **Consultar la nota diaria:**
   ```bash
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily get
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily get --date ayer
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily get --date 2026-10-01 --json
   ```

3. **Añadir una tarea a la nota diaria:**
   ```bash
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily add-task "Comprar pan"
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily add-task "Revisar logs de despliegue" --category "Trabajo"
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily add-task "Cita médica" --date mañana
   ```

4. **Posponer una tarea:**
   ```bash
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily postpone-task "Cita médica" --to mañana
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily postpone-task "Comprar pan" --date 2026-10-01 --to 2026-10-05
   ```

5. **Registrar un evento en el frontmatter:**
   ```bash
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily add-event "Reunión de equipo"
   ```

6. **Registrar peso corporal:**
   ```bash
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily set-weight 78.5
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily set-weight 78.2 --date mañana
   ```

7. **Clasificar una nueva nota:**
   ```bash
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py classify "Auditoría servidor Traefik"
   ```

8. **Buscar notas:**
   ```bash
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py search "ciberseguridad"
   ```

9. **Sincronizar finanzas:**
   ```bash
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py finance sync
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py finance sync --year 2026 --month 11 --create
   ```
