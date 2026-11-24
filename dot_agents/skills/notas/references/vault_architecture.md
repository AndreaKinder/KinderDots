# 🏛️ Arquitectura y Reglas de la Bóveda de Notas (`~/Notas`)

Este documento complementa las directrices establecidas en [`AGENTS.md`]($HOME/Notas/AGENTS.md) y detalla la organización técnica de la bóveda para garantizar la coherencia absoluta en las operaciones de agentes y herramientas.

---

## 📁 1. Arquitectura de Directorios

La raíz `$HOME/Notas/` se mantiene estrictamente limpia. Toda nota o recurso pertenece a una de las siguientes carpetas:

| Directorio | Propósito | Nomenclatura / Formato |
| :--- | :--- | :--- |
| `journal/` | **Bitácora diaria (Daily Notes).** Sincronizada con Neovim (`<leader>od`) y Obsidian. | `YYYY-MM-DD.md` |
| `finanzas/` | **Gestión financiera, facturación y recibos.** Estructurado por año con 3 subcarpetas: `cuentas/` (balances mensuales `.md` + su libro Excel `.xlsx`), `recibos/` (recibos y justificantes de gastos) y `facturas/` (facturas emitidas por mí). | `finanzas/YYYY/cuentas/YYYY-MM.{md,xlsx}`, `finanzas/YYYY/recibos/`, `finanzas/YYYY/facturas/` y `finanzas/resumen-anual-YYYY.{md,xlsx}` |
| `todo/` | **Listas de tareas fechadas y desglosadas.** Seguimiento detallado por día. | `todo/YYYY-MM-DD/<ID>.md` |
| `zettelkasten/` | **Notas genéricas y conocimiento atómico.** Soluciones técnicas, guías, aprendizajes e investigación. | `<TIMESTAMP>-<ACRONIMO>.md` o `<TIMESTAMP>-<kebab-case>.md` |
| `projects/` | **Documentación de proyectos de desarrollo/trabajo.** Subcarpetas por proyecto. | `projects/<nombre-proyecto>/` (`docs/`, `fases/`, `backups/`, `README.md`) |
| `templates/` | **Plantillas oficiales** para Obsidian y Neovim. | `plantilla-*.md` |
| `prompts/` | **Instrucciones y plantillas para agentes de IA.** | `prompts/` y `prompts/templates/` |
| `assets/` | **Recursos gráficos y binarios adjuntos.** Diagramas SVG, imágenes, PDFs en `assets/pdf/`. | `.svg`, `.png`, `.pdf` |
| `archived/` | **Histórico y proyectos congelados.** | `archived/projects/`, `archived/areas/` |
| `.obsidian/` | **Configuración interna de Obsidian.** *(Solo lectura/No modificar).* | Archivos de configuración JSON |

---

## 🚫 2. Reglas Invariantes para Agentes

1. **PROHIBIDO CREAR ARCHIVOS EN LA RAÍZ:** Nunca crear notas, volcados o scripts sueltos en `$HOME/Notas/`.
2. **METADATOS FRONTMATTER OBLIGATORIOS:** Toda nueva nota DEBE comenzar con bloque YAML delimitado por `---`:
   ```yaml
   ---
   id: <ID-UNICO>
   description: "Descripción breve en una o dos frases"
   aliases:
     - "Nombre Principal de la Nota"
   tags:
     - tag1
     - tag2
   ---
   ```
3. **RESPETO A LA TAXONOMÍA:**
   - No inventar carpetas raíz (`daily/`, `diario/`, `notes/` NO deben usarse; la carpeta oficial es `journal/`).
   - Las notas diarias SIEMPRE llevan la etiqueta `daily-notes`.
   - Las cuentas mensuales llevan las etiquetas `finanzas` y `finanzas/mensual`.
4. **INTEGRIDAD DE ARCHIVOS BINARIOS:**
   - Volcados `.sql`, scripts bash pesados o artefactos compilados NO van en la raíz ni en `zettelkasten/`. Pertenecen a `projects/<proyecto>/backups/` o en `~/Work/`.

---

## 🔒 3. Respaldo y Sincronización

* **Git (Opcional):** Puedes sincronizar la bóveda con un repositorio Git privado propio mediante `obsidian-git`.
* **Copias de seguridad:** Se recomienda mantener copias cifradas periódicas fuera del equipo.

