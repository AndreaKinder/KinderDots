---
name: NOMBRE_SKILL
description: |
  ACCION_PRINCIPAL en una linea concreta.
  Tecnologias: TEC1, TEC2, TEC3.
  No usar para: EXCLUSION_1, EXCLUSION_2.
version: 0.1.0
author: Pi Coding Agent
---

# Reglas globales

1. `SKILL.md` ≤ 120 lineas. Contiene solo frontmatter, enrutamiento y reglas innegociables.
2. Prohibido hardcodear rutas de usuario. Usa `$DOTFILES_PATH`, `$HOME` o rutas relativas.
3. Cada archivo en `references/` es autocontenido. Sin cadenas `references/` -> `references/`.
4. Si existe un script para validar o generar, ejecutalo. No verifiques manualmente.

# Enrutamiento

| Tarea | Archivo |
| --- | --- |
| DESCRIPCION_TAREA_1 | [references/ARCHIVO_1.md](references/ARCHIVO_1.md) |
| DESCRIPCION_TAREA_2 | [references/ARCHIVO_2.md](references/ARCHIVO_2.md) |
| Validar esta skill | [scripts/lint_skill.py](scripts/lint_skill.py) |

# Flujo de trabajo

1. Identifica el contexto actual y las variables disponibles.
2. Determina el archivo de referencia que aplica.
3. Ejecuta las instrucciones atomicas del archivo seleccionado.
4. Valida con el linter antes de finalizar.
