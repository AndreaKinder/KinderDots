# 📝 Catálogo y Esquemas de Tipos de Notas

Este documento define la estructura interna, frontmatter y convenciones de contenido de los tipos de nota presentes en la bóveda `~/Notas`.

---

## 📅 1. Nota Diaria (`journal/YYYY-MM-DD.md`)

* **Ubicación:** `journal/YYYY-MM-DD.md`
* **Plantilla base:** [`templates/plantilla-diaria.md`]($HOME/Notas/templates/plantilla-diaria.md)
* **Atajos de usuario:** Neovim `<leader>od` (Obsidian Today).

### Frontmatter YAML
```yaml
---
id: YYYY-MM-DD
description: ""
events:
  - "Evento destacado del día" # Opcional / lista de strings
weight: 78.5 # Opcional / número (seguimiento de bajada de peso)
aliases:
  - YYYY-MM-DD
tags:
  - daily-notes
---
```

### Secciones Estándar
```markdown
# YYYY-MM-DD

## TODO

### Casa / Personal
- [ ] Tarea personal 1
- [x] Tarea completada

### Trabajo
- [ ] Tarea de desarrollo o trabajo

### Social
- [ ] Planes o compromisos sociales
```

---

## 💳 2. Finanzas, Recibos y Facturas (`finanzas/`)

Cada año (`finanzas/YYYY/`) se divide en 3 subcarpetas organizativas:
* `finanzas/YYYY/cuentas/`: Balances mensuales compuestos por la pareja **`YYYY-MM.md`** (resumen ejecutivo + desglose en Markdown) y **`YYYY-MM.xlsx`** (libro Excel OOXML con hojas `Resumen`, `Gastos`, `Deudas`, `Comida` e `Ingresos`, con fórmulas nativas y tablas para inspeccionar en Neovim con `xleak.nvim`). Plantilla base: [`templates/plantilla-cuentas-mes.md`]($HOME/Notas/templates/plantilla-cuentas-mes.md).
* `finanzas/YYYY/recibos/`: Recibos, facturas simplificadas y justificantes de gastos (PDFs, imágenes, etc.).
* `finanzas/YYYY/facturas/`: Facturas emitidas por el usuario (PDFs, justificantes fiscales).
* `finanzas/resumen-anual-YYYY.md` + `finanzas/resumen-anual-YYYY.xlsx`: Cuadro de mando y consolidado financiero anual en la raíz de `finanzas/`.
* `finanzas/deudas-actuales.md` + `finanzas/deudas-actuales.xlsx`: Snapshot consolidado de deudas vivas.

Siempre que se cree o modifique una nota de finanzas, ejecuta `$DOTFILES_PATH/ai/agents/skills/notas/scripts/resolve_note.py finance sync` para regenerar el `.xlsx` emparejado y actualizar el bloque `<!-- EXCEL-SUMMARY:START -->` en el `.md`.

### Frontmatter YAML (Mensual)
```yaml
---
id: YYYY-MM-finanzas
description: "Cuentas y balance mensual de YYYY-MM"
aliases:
  - "Cuentas YYYY-MM"
  - "YYYY-MM"
tags:
  - finanzas
  - finanzas/mensual
year: YYYY
month: "MM"
status: en-curso
total_ingresos: 0.00
total_gastos: 0.00
balance_neto: 0.00
excel: "finanzas/YYYY/cuentas/YYYY-MM.xlsx"
---
```

### Secciones Típicas
* `## 📥 1. Ingresos`
* `## 📺 2. Suscripciones`
* `## 🏠 3. Hogar: Alquiler, Suministros y Limpieza`
* `## 🤝 4. Deudas y Financiaciones`
* `## 🥖 5. Comida Semanal`
* `## 💊 6. Medicación y Salud`
* `## 🏛️ 7. Impuestos y Autónomos`
* `## 📊 8. Resumen General del Mes`

---

## 🧠 3. Notas Atómicas / Zettelkasten (`zettelkasten/`)

* **Ubicación:** `zettelkasten/<TIMESTAMP>-<SLUG/ACRONIMO>.md`
* **Plantilla base:** [`templates/plantilla-nota.md`]($HOME/Notas/templates/plantilla-nota.md)
* **Generación de ID:** Timestamp unix (`date +%s`), seguido de guion y acrónimo (4 letras mayúsculas aleatorias o título en kebab-case limpio). Ejemplos: `1789593709-macos-control-marcos-esquinas-ventanas.md`, `1786543620-CAGF.md`.

### Frontmatter YAML
```yaml
---
id: <TIMESTAMP-SUFFIX>
description: "Resumen conciso del contenido en 1-2 frases"
aliases:
  - "Título legible de la nota"
  - "Nombre alternativo"
tags:
  - tema-principal
  - tecnologia
---
```

---

## 🚀 4. Documentación de Proyectos (`projects/`)

* **Ubicación:** `projects/<nombre-proyecto>/`
* **Estructura típica de proyecto:**
  ```text
  projects/<nombre-proyecto>/
  ├── README.md              # Visión general y estado actual
  ├── ROADMAP.md             # Fases y objetivos (opcional)
  ├── docs/                  # Especificaciones técnicas y guías
  ├── fases/                 # Desglose de hitos de entrega
  ├── backups/               # Scripts, volcados SQL y dumps
  └── assets/                # Recursos propios del proyecto
  ```

---

## 📋 5. Tareas Fechadas Granulares (`todo/`)

* **Ubicación:** `todo/YYYY-MM-DD/<TIMESTAMP-ACRONIMO>.md`
* **Propósito:** Se utiliza para proyectos con desgloses extensos de checkboxes que no encajan en la nota diaria general.
