# Componentes: qué hace cada archivo

## Ventana / compositor (Niri)

| Archivo | Función |
|---|---|
| `dot_config/niri/config.kdl` | Punto de entrada: carga `config.d/*.kdl` |
| `dot_config/niri/config.d/binds.kdl` | Atajos. `Mod+W` = WhatsApp PWA (ID hardcoded), `Mod+S` = sysmenu, `Mod+Alt+V` = cliphist, `Alt+Space` = voxtype, `Super+C/V` = copiar/pegar global (vía keymap XKB `XF86Copy/Paste`) |
| `dot_config/niri/config.d/startup.kdl` | Arranque: waybar, mako, polkit, swaybg (wallpaper), wl-clip-persist, cliphist watch, swayidle/swaylock |
| `dot_config/niri/config.d/rules.kdl` | Reglas de ventana (btop flotante, etc.) |
| `dot_config/niri/config.d/input.kdl`, `input/keymap.xkb` | Teclado: Super+C/V → XF86Copy/Paste, Super+Esc bloqueo |
| `dot_config/niri/scripts/copy-paste.sh` | Helper del portapapeles global |
| `dot_config/niri/scripts/trackpoint-nav.py` | TrackPoint: clic/scroll con los botones físicos (ThinkPad) |

## Barra / notificaciones / menú

| Archivo | Función |
|---|---|
| `dot_config/waybar/config.jsonc` | Barra. Clock `on-click` → `calendar-menu`; módulos: workspaces, ventana, voxtype, brillo, audio, CPU, batería, sysmenu |
| `dot_config/waybar/style.css` | Estilo monocromo de waybar |
| `dot_config/waybar/power_menu.xml` | Menú de energía (xml para waybar) |
| `dot_config/mako/config` | Notificaciones monocromáticas |

## Terminal / lanzador / shell

| Archivo | Función |
|---|---|
| `dot_config/foot/foot.ini` | Terminal: colores mono, fuente, tamaño |
| `dot_config/fuzzel/fuzzel.ini` | Launcher (`Mod+Space`) |
| `dot_config/fish/config.fish` | Shell: sources `cachyos-config.fish`, greeting vacío que ejecuta `fastfetch`, PATH |
| `dot_config/environment.d/10-kinder.conf.tmpl` | Variables de entorno portables (systemd): TERMINAL, BROWSER, EDITOR, NOTAS_VAULT, Obsidian |

## Apps

| Archivo | Función |
|---|---|
| `dot_config/voxtype/config.toml` | Dictado por voz: motor whisper small, atajos, idioma |
| `dot_config/btop/btop.conf` + `themes/tuigreet-mono.theme` | Monitor de recursos mono |
| `dot_config/micro/settings.json` + `colorschemes/` | Editor micro: tema y ajustes |
| `dot_config/gtk-3.0/gtk.css`, `gtk-4.0/*` | Tema GTK monocromo |
| `dot_config/fastfetch/config.jsonc` + `dot_config/branding/about.txt` | Info del sistema al abrir terminal: logo ASCII + módulos compactos |
| `dot_config/mimeapps.list` | Navegador por defecto (zen-browser) |
| `dot_config/user-dirs.dirs` | Rutas XDG en español + `XDG_PROJECTS_DIR` |

## Binarios propios (`private_dot_local/bin/`)

| Archivo | Función |
|---|---|
| `executable_osd` | OSD de volumen/brillo (llamado por binds de niri) |
| `executable_sysmenu` | Menú de sistema (`Mod+S`): Wi-Fi, Bluetooth, audio… |
| `executable_calendar-menu` | Menú fuzzel mes→día; abre/crea la nota diaria de `~/Notas/journal/` en nvim. Lo lanza el clock de waybar |

## Externo

| Elemento | Función |
|---|---|
| `.chezmoiexternal.toml` → `AndreaKinder/KinderNvim` | `~/.config/nvim` se clona/actualiza solo (`refreshPeriod 168h`). Los cambios de nvim se commitean en su propio repo |

## Portapapeles (sin código custom)

`wl-clip-persist` + `cliphist` (watch en `startup.kdl`), historial con `Mod+Alt+V`, copiado global con `Super+C/V` vía keymap XKB. Sustituye al antiguo binario C `niri-clipboard` de Dotly.
