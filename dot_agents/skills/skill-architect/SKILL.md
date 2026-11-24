---
name: skill-architect
description: |
  Diseña skills compatibles con el estandar Agent Skills.
  Genera SKILL.md enrutador, references tecnicos, scripts deterministas y assets.
  No usar para: documentacion general, tutoriales, scripts de aplicacion, skills sin carpeta references/.
version: 1.0.0
author: Pi Coding Agent
---

# Reglas globales

1. `SKILL.md` ≤ 120 lineas. Contiene solo frontmatter, enrutamiento y reglas innegociables.
2. Prohibido hardcodear rutas de usuario. Usa `$DOTFILES_PATH`, `$HOME`, `$XDG_CONFIG_HOME` o rutas relativas.
3. Cada archivo en `references/` es autocontenido. Sin cadenas `references/` -> `references/`.
4. Si existe un script para validar o generar, ejecutalo. No verifiques manualmente.

# Flujo de trabajo

1. Pregunta brevemente: dominio tecnico, ruta destino, necesita `scripts/` o `assets/`.
2. Diseña: `SKILL.md` como enrutador, `references/` por area tecnica, `scripts/` para automatizar, `assets/` para plantillas.
3. Genera archivos usando [assets/skill-template.md](assets/skill-template.md) como esqueleto.
4. Valida con [scripts/lint_skill.py](scripts/lint_skill.py).

# Enrutamiento

| Tarea | Archivo |
| --- | --- |
| Definir reglas de densidad, frontmatter y modelos locales | [references/optimization-rules.md](references/optimization-rules.md) |
| Validar una skill generada | [scripts/lint_skill.py](scripts/lint_skill.py) |
| Crear el esqueleto de una skill nueva | [assets/skill-template.md](assets/skill-template.md) |
