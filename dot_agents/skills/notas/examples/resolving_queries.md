# 🔍 Ejemplos de Resolución de Consultas y Modificación de Notas

Este documento ilustra la resolución paso a paso de peticiones comunes de usuario.

---

### Ejemplo 1: "Añade a mi nota diaria una tarea para comprar fruta"

1. **Resolución de la entidad:**
   * Frase: `"nota diaria"` -> Tipo: `daily_note`.
   * Fecha actual: `2026-10-01`.
   * Archivo objetivo: `$HOME/Notas/journal/2026-10-01.md`.
2. **Acción:**
   * La tarea es de ámbito doméstico -> Sección: `### Casa / Personal`.
   * Ejecutar helper o modificar archivo:
     ```bash
     $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily add-task "Comprar fruta" --category "Casa / Personal"
     ```
   * O editar mediante `replace_file_content` añadiendo `- [ ] Comprar fruta` bajo `### Casa / Personal`.

---

### Ejemplo 2: "¿Qué tareas tengo pendientes hoy?"

1. **Resolución:**
   * Frase: `"tareas de hoy"` -> `journal/<HOY>.md`.
2. **Acción:**
   * Consultar vía script:
     ```bash
     $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily get
     ```
   * O abrir con `view_file` `$HOME/Notas/journal/2026-10-01.md` y extraer las líneas con `- [ ]`.
   * Responder al usuario listando los puntos pendientes clasificados por sección (`Casa / Personal`, `Trabajo`, etc.).

---

### Ejemplo 3: "¿Qué hice o apunté ayer?"

1. **Resolución:**
   * Frase: `"ayer"` -> Restar 1 día a la fecha actual (`2026-09-30`).
   * Archivo: `$HOME/Notas/journal/2026-09-30.md`.
2. **Acción:**
   * Consultar vía script:
     ```bash
     $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py daily get --date ayer
     ```
   * O leer directamente con `view_file`.

---

### Ejemplo 4: "Revisa mis gastos y suscripciones de este mes"

1. **Resolución:**
   * Frase: `"gastos y suscripciones de este mes"` -> `finance_monthly`.
   * Fecha: Mes actual (`2026-10`).
   * Archivo objetivo: `$HOME/Notas/finanzas/2026/Cuentas/2026-10.md` (o `2026-09.md` si el mes recién empieza).
2. **Acción:**
   * Leer con `view_file` para inspeccionar las tablas de suscripciones y balance neto.

---

### Ejemplo 5: "Crea una nota técnica sobre cómo configurar Traefik con Docker"

1. **Resolución:**
   * Frase: `"nota técnica sobre cómo configurar Traefik..."` -> Tipo: `zettelkasten`.
   * Clasificación:
     ```bash
     $DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py classify "Configuración de Traefik con Docker"
     ```
   * Destino: `$HOME/Notas/zettelkasten/<TIMESTAMP>-configuracion-traefik-docker.md`.
2. **Acción:**
   * Crear la nota con su frontmatter completo (`id`, `description`, `aliases`, `tags`) y contenido técnico estructurado.
