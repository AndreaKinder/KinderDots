---
name: dotfiles
description: Instala, adapta y mantiene los dotfiles de Andrea (chezmoi + Niri + foot + fish + KinderNvim). Úsala cuando se pida instalar, migrar o reparar los dotfiles en un ordenador nuevo o existente, o al hablar de componentes del sistema: niri, waybar, mako, foot, fuzzel, fish, voxtype, btop, micro, fastfetch, notas diarias de Obsidian, PWAs (WhatsApp/HEY), portapapeles (cliphist), osd, sysmenu.
---

# Dotfiles de Andrea (KinderDots)

Gestionados con **chezmoi**. Repositorio fuente: `~/.local/share/chezmoi` (git).
Neovim (`~/.config/nvim`) es un **repo externo** (KinderNvim) que chezmoi clona/actualiza solo vía `.chezmoiexternal.toml`. **No duplicar su contenido en este repo.**

## Reglas críticas

1. **Nunca versionar secretos**: tokens, `.env` reales, credenciales, perfiles de navegador, datos de cuentas, `fish_variables`, `.sync_*.db` de Obsidian.
2. **No hacer push a GitHub sin permiso explícito** — Andrea sube los cambios él mismo.
3. Los **IDs de las PWAs cambian** en cada instalación (WhatsApp/HEY): adaptar en `~/.config/niri/config.d/binds.kdl`, no copiar a ciegas.
4. Los archivos live se editan en `~/...` y se sincronizan con `chezmoi add`; el source state es la verdad.
5. Binarios propios: prefijo `executable_` en el source. Nada de binarios compilados nuevos (el antiguo `niri-clipboard` en C ya no se usa: hoy es cliphist + wl-clipboard).

## Estructura del repo (source state)

```text
.chezmoiexternal.toml .......... KinderNvim como external git-repo
.chezmoiignore ................. excluye bootstrap.sh / README de $HOME
bootstrap.sh ................... instalador completo desde CachyOS sin desktop
dot_config/fish/config.fish .... greeting = fastfetch
dot_config/foot/foot.ini
dot_config/fuzzel/fuzzel.ini
dot_config/niri/ ............... config.kdl + config.d/ (binds, startup, rules, input) + scripts/
dot_config/waybar/ ............. config.jsonc, style.css, power_menu.xml
dot_config/mako/config
dot_config/voxtype/config.toml . whisper small (CPU)
dot_config/gtk-3.0/gtk.css ..... tema monocromo
dot_config/gtk-4.0/ ............ gtk.css + settings.ini
dot_config/btop/ ............... btop.conf + themes/tuigreet-mono.theme
dot_config/micro/ .............. settings.json + colorschemes/
dot_config/environment.d/ ...... 10-kinder.conf.tmpl (variables portables)
dot_config/fastfetch/ .......... config.jsonc compacto
dot_config/branding/about.txt .. logo ASCII monocromo
dot_config/mimeapps.list, user-dirs.dirs
private_dot_local/bin/ ......... executable_osd, executable_sysmenu, executable_calendar-menu
dot_agents/skills/dotfiles/ .... esta skill
```

**Excluidos a propósito**: PWAs de firefoxpwa (`.desktop` + iconos, IDs no reproducibles), `fish_variables`, `hey-cli/`, `zen/`, `mozilla/`, `Nextcloud/`, `antigravity/`, `micro/syntax/` (bundle por defecto), `gtk-3.0/bookmarks`, `pavucontrol.ini`, `QtProject.conf`, `dconf/`.

## Flujos

- Máquina nueva → `references/instalacion.md`
- Qué hace cada archivo → `references/componentes.md`
- Qué adaptar por máquina → `references/variables-a-adaptar.md`
- Operaciones diarias y troubleshooting → `references/mantenimiento.md`
