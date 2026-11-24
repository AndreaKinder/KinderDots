# 📆 Flujos de Trabajo con la Nota Diaria (Daily Note / Journal)

Guía práctica de manipulación de la nota diaria en `$HOME/Notas/journal/YYYY-MM-DD.md`.

---

## 1. Comprobación y Creación

Antes de leer o editar, verificar si la nota diaria existe:
* Ruta: `$HOME/Notas/journal/<YYYY-MM-DD>.md`
* Si NO existe:
  - Crear a partir de [`plantilla-diaria.md`]($HOME/Notas/templates/plantilla-diaria.md) sustituyendo `{{date}}` por la fecha en formato `YYYY-MM-DD`.
  - O ejecutar:
    ```bash
    $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily create [--date hoy|ayer|mañana|YYYY-MM-DD]
    ```

---

## 2. Inserción de Tareas por Categoría

Las notas diarias de la bóveda agrupan las tareas bajo `## TODO` con encabezados de nivel 3:
* `### Casa / Personal`: Recados, compras, tareas domésticas.
* `### Trabajo`: Tareas laborales y de programación.
* `### Social`: Cenas, regalos, compromisos.

### Inserción mediante script helper:
```bash
# Tarea personal en la nota de hoy
$DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily add-task "Limpiar filtros aire" --category "Casa / Personal"

# Tarea de trabajo en la nota de hoy
$DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily add-task "Revisar logs de despliegue" --category "Trabajo"

# Tarea en la nota de mañana
$DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily add-task "Comprar billete tren" --category "Social" --date mañana
```

### Inserción directa con `replace_file_content`:
Buscar la sección correspondiente:
```markdown
### Casa / Personal

- [ ] Tarea existente
```
Y sustituir por:
```markdown
### Casa / Personal

- [ ] Nueva tarea
- [ ] Tarea existente
```

---

## 3. Registro de Eventos en Frontmatter

Los eventos especiales del día se anotan en el campo `events:` del bloque frontmatter YAML:
```yaml
---
id: 2026-10-01
description: ""
events:
  - "Cita médica"
  - "Reunión técnica de equipo"
aliases:
  - 2026-10-01
tags:
  - daily-notes
---
```

Vía script helper:
```bash
$DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily add-event "Cena con amigos"
```

---

## 4. Marcar Tareas como Completadas

En Markdown, una tarea completada cambia `- [ ]` a `- [x]`.
Se realiza localizando la línea exacta mediante `replace_file_content`:
```markdown
- [ ] Pagar alquiler
```
reemplazado por:
```markdown
- [x] Pagar alquiler
```
