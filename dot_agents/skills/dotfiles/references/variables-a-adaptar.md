# Variables a adaptar en cada máquina

Al instalar estos dotfiles en otro ordenador (o para otra persona), revisa y ajusta:

## 1. IDs de PWAs (cambian en cada instalación)

Los IDs de `firefoxpwa site launch` **no son reproducibles**. Tras instalar las PWAs:

- WhatsApp → actualizar en `dot_config/niri/config.d/binds.kdl`:
  ```kdl
  Mod+W ... { spawn "firefoxpwa" "site" "launch" "<ID_NUEVO>"; }
  ```
- HEY Mail → verificar el `.desktop` regenerado en `~/.local/share/applications/`.

## 2. Rutas de usuario (ya portables)

Todos los archivos usan `$HOME`, `~` o `{{ .chezmoi.homeDir }}` sin rutas absolutas de usuario:
- `dot_config/environment.d/10-kinder.conf.tmpl` → `{{ .chezmoi.homeDir }}`. Verificar que el vault se llame `Notas` y esté en `$HOME`.
- `private_dot_local/bin/executable_calendar-menu` → `$HOME`. Verificar `~/Notas/journal/` y `~/Notas/templates/plantilla-diaria.md`.
- `dot_config/fish/config.fish` → `fish_add_path -p "$HOME/.local/bin"`.
- `dot_config/waybar/config.jsonc` → `$HOME/.local/bin/...` en todos los módulos.
- `dot_config/btop/btop.conf` → `color_theme = "tuigreet-mono"`.
- `dot_config/niri/config.d/startup.kdl` → `$HOME/Imágenes/Wallpapers/06-kinder-midnight-oled.png`.
- `private_dot_local/bin/executable_sysmenu` → `"$HOME/.local/bin/osd"`.

## 3. Formato de notas diarias

El vault de Obsidian usa `journal/AAAA-MM-DD.md` con plantilla `templates/plantilla-diaria.md`. Si el vault nuevo usa otra carpeta o formato, ajustar:
- `OBSIDIAN_DAILY_FOLDER` / `OBSIDIAN_DAILY_TEMPLATE` en `environment.d`
- La construcción de la ruta en `calendar-menu`
- La config de obsidian.nvim en KinderNvim (`lua/plugins/obsidian.lua`)

## 4. Hardware

- TrackPoint: `dot_config/niri/scripts/trackpoint-nav.py` asume TrackPoint ThinkPad (ajustar si no hay).
- Brillo: waybar usa `intel_backlight` (cambiar si la GPU es distinta).
- Teclado: `dot_config/niri/input/keymap.xkb` con Super+C/V → XF86Copy/Paste (verificar distribución).

## 5. Software

- Voxtype: modelo `whisper small` (CPU). Si hay GPU potente, considerar parakeet en `dot_config/voxtype/config.toml`.
- fastfetch: el logo ASCII es custom (`dot_config/branding/about.txt`); regenerar si cambia la marca.
- Nombre del repo en la URL de `chezmoi init` (`KinderDots`).

## 6. Nunca adaptar/versionar

`.env` reales, tokens, `fish_variables`, perfiles de navegador, `.sync_*.db` de Obsidian, `~/.config/hey-cli/`, `~/.config/zen/`, `~/.config/mozilla/`, `~/.config/Nextcloud/`.
