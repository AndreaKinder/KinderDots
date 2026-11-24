# Instalación en máquina nueva (CachyOS sin desktop)

## Opción recomendada: script automático (`bootstrap.sh`)

El repositorio incluye `bootstrap.sh` (excluido de `$HOME` mediante `.chezmoiignore`) para montar todo el entorno desde un **CachyOS sin entorno de escritorio**:

```bash
# Desde un TTY recién instalado:
git clone https://github.com/AndreaKinder/KinderDots.git ~/.local/share/chezmoi
~/.local/share/chezmoi/bootstrap.sh
```

También soporta simulación y banderas selectivas:

```bash
~/.local/share/chezmoi/bootstrap.sh --dry-run          # Ver qué haría sin cambiar nada
~/.local/share/chezmoi/bootstrap.sh --no-optional      # Solo escritorio base (sin Zen/Obsidian/PWA/voz)
~/.local/share/chezmoi/bootstrap.sh --skip-greetd      # No tocar /etc/greetd/config.toml
~/.local/share/chezmoi/bootstrap.sh --help             # Ver todas las opciones
```

### Qué automatiza `bootstrap.sh`
1. **Paquetes `pacman`** (repos oficiales/CachyOS): Niri, `xwayland-satellite`, portales XDG, `mate-polkit`, Waybar, Mako, Fuzzel, `swaybg`/`swaylock`/`swayidle`, `wl-clipboard`/`wl-clip-persist`/`cliphist`, `wtype`, Foot, Fish (`cachyos-fish-config`), Neovim (+ `ripgrep`/`fd`), Micro, `btop`, `fastfetch`, PipeWire + WirePlumber, `NetworkManager`, `bluez`, `power-profiles-daemon`, `greetd` + `greetd-tuigreet`, fuentes (`ttf-dejavu`, `ttf-meslo-nerd`, `awesome-terminal-fonts`, `noto-fonts*`), `jq`, `libnotify`, `xdg-user-dirs`, Zen Browser, Obsidian, FirefoxPWA y `chezmoi`.
2. **Paquetes AUR** (`yay` o `paru`): `voxtype-bin` y `wvkbd` (más cualquier paquete que no esté en los repos sync).
3. **Login TTY (`greetd` + `tuigreet`)**: crea respaldo y escribe `/etc/greetd/config.toml` con `tuigreet --time --remember --cmd niri-session`, y habilita `greetd.service`.
4. **Servicios y usuario**: habilita `NetworkManager`, `bluetooth` y `power-profiles-daemon`; añade el usuario al grupo `input` (TrackPoint) y cambia la shell a `fish`.
5. **Dotfiles**: ejecuta `chezmoi apply` (clonando `KinderNvim` en `~/.config/nvim`), actualiza directorios XDG y habilita los servicios de usuario (`pipewire`, `wireplumber`, `voxtype`).

---

## Instalación manual (paso a paso)

Si prefieres ejecutarlo a mano en lugar de usar `bootstrap.sh`:

### 1. Dependencias

Oficiales (repos CachyOS):

```bash
sudo pacman -S --needed git base-devel chezmoi jq ripgrep fd xdg-user-dirs libnotify \
  niri xwayland-satellite xdg-desktop-portal xdg-desktop-portal-gtk xdg-desktop-portal-gnome \
  polkit mate-polkit waybar mako fuzzel swaybg swaylock swayidle \
  wl-clipboard wl-clip-persist cliphist wtype \
  foot fish cachyos-fish-config neovim micro btop fastfetch \
  pipewire pipewire-audio pipewire-pulse pipewire-alsa wireplumber gst-plugin-pipewire playerctl \
  networkmanager bluez bluez-utils power-profiles-daemon \
  greetd greetd-tuigreet \
  ttf-dejavu ttf-meslo-nerd awesome-terminal-fonts noto-fonts noto-fonts-emoji \
  zen-browser-bin obsidian firefoxpwa espeak-ng
```

AUR (con `yay`):

```bash
yay -S --needed voxtype-bin wvkbd
```

### 2. Configurar `greetd` + servicios + usuario

Escribir `/etc/greetd/config.toml`:

```toml
[terminal]
vt = 1

[default_session]
command = "tuigreet --time --remember --cmd niri-session"
user = "greeter"
```

Habilitar servicios, grupo `input` y shell `fish`:

```bash
sudo systemctl enable --force greetd.service
sudo systemctl enable --now NetworkManager.service bluetooth.service power-profiles-daemon.service
sudo usermod -aG input "$USER"
sudo chsh -s /usr/bin/fish "$USER"
```

### 3. Clonar y aplicar dotfiles

```bash
chezmoi init https://github.com/AndreaKinder/KinderDots.git
chezmoi apply
```

`chezmoi apply` clona automáticamente `KinderNvim` en `~/.config/nvim` (external git-repo). Si `~/.config/nvim` ya existe con cambios locales, haz commit/push primero o mueve la carpeta.

### 4. Servicios de usuario

```bash
systemctl --user enable --now pipewire.socket pipewire-pulse.socket wireplumber.service voxtype.service
```

---

## Pasos manuales posteriores (comunes a ambos métodos)

### 1. PWAs (WhatsApp + HEY Mail)

```bash
firefoxpwa site install https://web.whatsapp.com
firefoxpwa site install https://app.hey.com
```

- Anota el **ID de WhatsApp** y ponlo en `~/.config/niri/config.d/binds.kdl` (atajo `Mod+W`).
- Los `.desktop` e iconos de las PWAs se regeneran solos en `~/.local/share/` — **no** están en el repo porque los IDs no son reproducibles.

### 2. Wallpaper

Copiar el wallpaper a `~/Imágenes/Wallpapers/06-kinder-midnight-oled.png` o ajustar la ruta en `~/.config/niri/config.d/startup.kdl` (línea `swaybg`).

### 3. Reiniciar y validar

Tras reiniciar (`sudo reboot`) e iniciar sesión en `tuigreet`:

- [ ] `niri msg` responde; waybar y mako arrancan solos (`spawn-at-startup`)
- [ ] `Mod+Space` → fuzzel; `Mod+S` → sysmenu; `Mod+Return` → foot
- [ ] Pulsar el reloj de waybar → menú mes→día → abre la nota diaria en nvim
- [ ] Terminal nueva muestra fastfetch con el logo ASCII
- [ ] `Alt+Space` → voxtype dicta (primer uso descarga Whisper `small`)
- [ ] `Mod+Alt+V` → historial cliphist
- [ ] `Mod+W` → WhatsApp PWA (tras ajustar el ID)
