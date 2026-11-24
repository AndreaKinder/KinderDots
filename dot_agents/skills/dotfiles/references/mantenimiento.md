# Mantenimiento diario

## Flujo de trabajo (máquina actual)

```bash
# 1. Editar el archivo live
nvim ~/.config/niri/config.d/binds.kdl

# 2. Sincronizar al source state de chezmoi
chezmoi add ~/.config/niri/config.d/binds.kdl

# 3. Revisar qué cambiaría
chezmoi diff

# 4. Aplicar (normalmente ya coincide)
chezmoi apply

# 5. Commit en el repo de dotfiles (source state)
cd ~/.local/share/chezmoi
git add -A && git commit -m "niri: ajustar atajo X"
# push lo hace Andrea manualmente
```

## Comandos clave

| Comando | Para qué |
|---|---|
| `chezmoi status` | Qué difiere entre source y destino |
| `chezmoi diff` | Diff concreto |
| `chezmoi add <path>` | Añadir/sincronizar archivo live al source |
| `chezmoi re-add <path>` | Re-sincronizar si el destino cambió a mano |
| `chezmoi edit <path>` | Editar el source directamente |
| `chezmoi apply` | Aplicar source → destino (¡clona/actualiza externals!) |
| `chezmoi update` | Actualiza externals (KinderNvim) + aplica |

## Neovim (external)

- `~/.config/nvim` **es** el repo KinderNvim. Editar ahí, commitear en ese repo.
- Para que el dotfiles lo refleje: push del repo KinderNvim + `chezmoi update` en la otra máquina.
- `lazy-lock.json` se commitea en KinderNvim cuando lazy.nvim lo modifica.

## Añadir un archivo nuevo

```bash
chezmoi add ~/.config/foo/config.conf
# Si es ejecutable, chezmoi usa prefijo executable_ automáticamente.
# Si es secreto: NO añadir. Si hay que cifrarlo, configurar age/gpg primero
# (private_ sin cifrado configurado no protege nada).
```

## Troubleshooting

- **`chezmoi apply` falla en `.config/nvim`**: el external ya existe con cambios locales. Commitea/pushea KinderNvim primero, o mueve `~/.config/nvim` y deja que chezmoi cloné.
- **Drift detection**: `chezmoi diff` muestra archivos que cambiaron fuera de chezmoi. Re-add si el cambio es intencional.
- **fastfetch sin logo**: verificar `~/.config/branding/about.txt` y el `source` en `config.jsonc`.
- **calendar-menu no abre nada**: verificar permisos (`chmod +x ~/.local/bin/calendar-menu`), que fuzzel esté instalado, y que `~/Notas/journal/` exista.
- **voxtype no dicta**: `systemctl --user status voxtype`; el modelo se descarga en primer uso (`~/.local/share/voxtype/models`).
- **Waybar no muestra cambios**: reiniciar waybar tras editar (`pkill -USR1 waybar` o relogin).
- **IDs de PWA rotos**: ver `variables-a-adaptar.md` — se regeneran por instalación.

## Política de seguridad

- Nada de credenciales, tokens, `.env` reales, ni datos de cuentas en el repo.
- `fish_variables` y demás estado generado: nunca.
- Antes de `chezmoi add`, revisar el contenido; ante la duda, `chezmoi diff` y leer.
