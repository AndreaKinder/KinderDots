# Busqueda Semantica: `notes_index.py`

Indice de embeddings (Ollama `snowflake-arctic-embed2` + SQLite FTS5) sobre las notas `.md` de la boveda (excluye `archived/` y `assets/`). Los chunks se vectorizan con una cabecera que inyecta los metadatos del frontmatter (`TITULO | ALIAS | TAGS | DESCRIPCION | EVENTOS | SECCION`), por lo que las etiquetas, alias y eventos son buscables por significado, no solo por coincidencia literal. La BD vive fuera de la boveda: `$HOME/.local/share/notas-index/index.db`.

1. **Busqueda hibrida:**
   ```bash
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/notes_index.py find "qué llevarme de viaje" -k 5
   ```

2. **Con filtros de metadatos:**
   ```bash
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/notes_index.py find "impuestos" --type finanzas --since 2026-01
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/notes_index.py find "visita" --type journal --tag daily-notes
   ```
   Tipos validos: `journal`, `zettelkasten`, `projects`, `finanzas`, `todo`, `inbox`, `templates`, `prompts`.

3. **Salida para consumo del agente:** anade `--json` (path, title, type, date, tags, score, heading, snippet).

4. **Mantenimiento:** el indice se refresca solo (lazy resync por sha256) al ejecutar `find`. Usalo manualmente solo si quieres:
   ```bash
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/notes_index.py status
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/notes_index.py build          # incremental
   $DOTFILES_PATH/ai/agents/skills/notas/scripts/notes_index.py build --full   # reconstruccion total (~7 min)
   ```

**Regla para el agente:** para consultas tematicas o en lenguaje natural usa `find` como via principal; `resolve_note.py search` queda para coincidencias literales exactas. Si `find` falla (Ollama caido o indice vacio), degrada a `search`.
