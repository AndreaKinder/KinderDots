#!/usr/bin/env bash
# ==============================================================================
# KinderDots — Bootstrap para CachyOS sin entorno de escritorio
# ==============================================================================
# Instala paquetes base/Wayland/Niri/AUR, configura greetd+tuigreet, servicios,
# grupos, shell fish y aplica los dotfiles mediante chezmoi (incl. KinderNvim).
#
# Uso:
#   ./bootstrap.sh [opciones]
#
# Opciones:
#   --dry-run           Muestra las acciones sin ejecutar cambios
#   --repo <URL>        URL git del repo de dotfiles
#   --skip-packages     No instala paquetes (pacman ni AUR)
#   --skip-aur          No instala paquetes de AUR (voxtype-bin, wvkbd)
#   --skip-greetd       No configura /etc/greetd/config.toml ni greetd.service
#   --skip-chezmoi      No ejecuta chezmoi init/apply
#   --no-optional       Omite apps opcionales (Zen, Obsidian, FirefoxPWA, voz)
#   -h, --help          Muestra esta ayuda
# ==============================================================================

set -euo pipefail

# ── Configuración por defecto ─────────────────────────────────────────────────
DEFAULT_REPO="https://github.com/AndreaKinder/KinderDots.git"
REPO_URL="${DOTFILES_REPO:-$DEFAULT_REPO}"

DRY_RUN=0
SKIP_PACKAGES=0
SKIP_AUR=0
SKIP_GREETD=0
SKIP_CHEZMOI=0
NO_OPTIONAL=0

# ── Colores y helpers de salida ───────────────────────────────────────────────
if [[ -t 1 ]]; then
    C_RESET=$'\033[0m'
    C_BOLD=$'\033[1m'
    C_DIM=$'\033[2m'
    C_RED=$'\033[31m'
    C_GREEN=$'\033[32m'
    C_YELLOW=$'\033[33m'
else
    C_RESET="" C_BOLD="" C_DIM="" C_RED="" C_GREEN="" C_YELLOW=""
fi

step() { printf '\n%s==> %s%s\n' "$C_BOLD" "$1" "$C_RESET"; }
info() { printf '  %s[ok]%s %s\n' "$C_GREEN" "$C_RESET" "$1"; }
warn() { printf '  %s[aviso]%s %s\n' "$C_YELLOW" "$C_RESET" "$1" >&2; }
err()  { printf '  %s[error]%s %s\n' "$C_RED" "$C_RESET" "$1" >&2; }
die()  { err "$1"; exit 1; }

run() {
    if (( DRY_RUN )); then
        printf '  %s[dry-run]%s %s\n' "$C_DIM" "$C_RESET" "$*"
        return 0
    fi
    "$@"
}

# ── Parseo de argumentos ──────────────────────────────────────────────────────
usage() {
    sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)       DRY_RUN=1 ;;
        --repo)
            [[ $# -ge 2 ]] || die "--repo requiere una URL"
            REPO_URL="$2"
            shift
            ;;
        --skip-packages) SKIP_PACKAGES=1 ;;
        --skip-aur)      SKIP_AUR=1 ;;
        --skip-greetd)   SKIP_GREETD=1 ;;
        --skip-chezmoi)  SKIP_CHEZMOI=1 ;;
        --no-optional)   NO_OPTIONAL=1 ;;
        -h|--help)       usage; exit 0 ;;
        *)               die "Opción desconocida: $1 (usa --help)" ;;
    esac
    shift
done

# ── Listas de paquetes ────────────────────────────────────────────────────────
# Core: todo lo necesario para pasar de CachyOS sin desktop a Niri funcional
PACMAN_CORE=(
    # Base, utilidades y gestión de dotfiles
    git
    base-devel
    chezmoi
    jq
    ripgrep
    fd
    xdg-user-dirs
    libnotify

    # Compositor Niri, XWayland, portales y Polkit
    niri
    xwayland-satellite
    xdg-desktop-portal
    xdg-desktop-portal-gtk
    xdg-desktop-portal-gnome
    polkit
    mate-polkit

    # Barra, lanzador, notificaciones, bloqueo, wallpaper, portapapeles, entrada
    waybar
    mako
    fuzzel
    swaybg
    swaylock
    swayidle
    wl-clipboard
    wl-clip-persist
    cliphist
    wtype

    # Terminal, shell, editores y monitorización
    foot
    fish
    cachyos-fish-config
    neovim
    micro
    btop
    fastfetch

    # Audio y multimedia (PipeWire + WirePlumber)
    pipewire
    pipewire-audio
    pipewire-pulse
    pipewire-alsa
    wireplumber
    gst-plugin-pipewire
    playerctl

    # Red, Bluetooth y perfiles de energía (usados por sysmenu)
    networkmanager
    bluez
    bluez-utils
    power-profiles-daemon

    # Gestor de inicio de sesión TTY (estética tuigreet)
    greetd
    greetd-tuigreet

    # Tipografías (estética TUI monocroma + iconos Nerd Font)
    ttf-dejavu
    ttf-meslo-nerd
    awesome-terminal-fonts
    noto-fonts
    noto-fonts-emoji
)

# Aplicaciones de escritorio habituales (omitibles con --no-optional)
PACMAN_OPTIONAL=(
    zen-browser-bin
    obsidian
    firefoxpwa
    espeak-ng
)

# Paquetes AUR (omitibles con --skip-aur o --no-optional)
AUR_OPTIONAL=(
    voxtype-bin
    wvkbd
)

# Paquetes que no se encuentren en repos sync de pacman se redirigen a AUR
AUR_FALLBACK=()

# ── 1. Comprobaciones previas ─────────────────────────────────────────────────
preflight_checks() {
    step "Comprobaciones previas"

    if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
        die "No ejecutes este script como root. Lánzalo con tu usuario normal (usará sudo cuando toque)."
    fi

    command -v pacman >/dev/null 2>&1 || die "No se encontró 'pacman'. Este script está pensado para CachyOS / Arch Linux."
    command -v sudo   >/dev/null 2>&1 || die "No se encontró 'sudo'."

    if [[ -r /etc/os-release ]]; then
        # shellcheck disable=SC1091
        source /etc/os-release
        info "Sistema detectado: ${PRETTY_NAME:-Arch-based}"
    fi

    if (( ! DRY_RUN )); then
        sudo -v || die "Se requieren permisos sudo para instalar paquetes y configurar el sistema."
        # Mantener vivo el timestamp de sudo mientras corre el script
        (
            while true; do
                sleep 50
                sudo -n true 2>/dev/null || exit 0
            done
        ) &
        SUDO_KEEPALIVE_PID=$!
        trap '[[ -n "${SUDO_KEEPALIVE_PID:-}" ]] && kill "$SUDO_KEEPALIVE_PID" 2>/dev/null || true' EXIT
    else
        warn "Modo --dry-run activo: no se aplicará ningún cambio."
    fi
}

# ── 2. Paquetes oficiales / repos CachyOS ─────────────────────────────────────
install_pacman_packages() {
    if (( SKIP_PACKAGES )); then
        warn "Omitiendo instalación de paquetes (--skip-packages)."
        return 0
    fi

    step "Sincronizando repositorios e instalando paquetes (pacman)"
    run sudo pacman -Sy --noconfirm

    local -a wanted=("${PACMAN_CORE[@]}")
    if (( ! NO_OPTIONAL )); then
        wanted+=("${PACMAN_OPTIONAL[@]}")
    fi

    local -a available=()
    local pkg
    for pkg in "${wanted[@]}"; do
        if pacman -Si "$pkg" >/dev/null 2>&1; then
            available+=("$pkg")
        else
            warn "Paquete '$pkg' no está en los repos de pacman; se intentará vía AUR."
            AUR_FALLBACK+=("$pkg")
        fi
    done

    if (( ${#available[@]} > 0 )); then
        run sudo pacman -S --needed --noconfirm "${available[@]}"
        info "Instalados/verificados ${#available[@]} paquetes con pacman."
    fi
}

# ── 3. Paquetes AUR (yay / paru) ──────────────────────────────────────────────
ensure_aur_helper() {
    if command -v yay >/dev/null 2>&1; then
        echo "yay"
        return 0
    fi
    if command -v paru >/dev/null 2>&1; then
        echo "paru"
        return 0
    fi

    # En CachyOS, yay/paru suelen estar en el repo oficial cachyos
    if pacman -Si yay >/dev/null 2>&1; then
        run sudo pacman -S --needed --noconfirm yay
        echo "yay"
        return 0
    fi
    if pacman -Si paru >/dev/null 2>&1; then
        run sudo pacman -S --needed --noconfirm paru
        echo "paru"
        return 0
    fi

    # Fallback: compilar yay-bin desde AUR
    if (( DRY_RUN )); then
        echo "yay"
        return 0
    fi

    local tmpdir
    tmpdir="$(mktemp -d)"
    git clone --depth=1 https://aur.archlinux.org/yay-bin.git "$tmpdir/yay-bin"
    (cd "$tmpdir/yay-bin" && makepkg -si --noconfirm)
    rm -rf "$tmpdir"
    echo "yay"
}

install_aur_packages() {
    if (( SKIP_PACKAGES || SKIP_AUR )); then
        warn "Omitiendo paquetes AUR."
        return 0
    fi

    local -a aur_pkgs=("${AUR_FALLBACK[@]}")
    if (( ! NO_OPTIONAL )); then
        aur_pkgs+=("${AUR_OPTIONAL[@]}")
    fi

    if (( ${#aur_pkgs[@]} == 0 )); then
        info "No hay paquetes AUR pendientes."
        return 0
    fi

    step "Instalando paquetes AUR (${aur_pkgs[*]})"
    local helper
    helper="$(ensure_aur_helper)"
    info "Usando AUR helper: $helper"

    run "$helper" -S --needed --noconfirm "${aur_pkgs[@]}"
    info "Paquetes AUR instalados/verificados."
}

# ── 4. Configuración de greetd + tuigreet ─────────────────────────────────────
configure_greetd() {
    if (( SKIP_GREETD )); then
        warn "Omitiendo configuración de greetd (--skip-greetd)."
        return 0
    fi

    step "Configurando greetd + tuigreet → niri-session"

    local greetd_conf="/etc/greetd/config.toml"
    local desired_conf
    desired_conf=$(cat <<'EOF'
[terminal]
# VT en el que arranca el greeter
vt = 1

[default_session]
command = "tuigreet --time --remember --cmd niri-session"
user = "greeter"
EOF
)

    if (( DRY_RUN )); then
        printf '  %s[dry-run]%s Escribir %s (tuigreet --time --remember --cmd niri-session)\n' "$C_DIM" "$C_RESET" "$greetd_conf"
        run sudo systemctl enable --force greetd.service
        return 0
    fi

    sudo mkdir -p /etc/greetd
    if [[ -f "$greetd_conf" ]] && ! diff -q <(printf '%s\n' "$desired_conf") "$greetd_conf" >/dev/null 2>&1; then
        local backup="${greetd_conf}.bak.$(date +%Y%m%d-%H%M%S)"
        sudo cp "$greetd_conf" "$backup"
        info "Copia de seguridad creada en $backup"
    fi

    printf '%s\n' "$desired_conf" | sudo tee "$greetd_conf" >/dev/null
    sudo chmod 644 "$greetd_conf"
    info "Escrito $greetd_conf"

    if [[ -L /etc/systemd/system/display-manager.service ]]; then
        local current_dm
        current_dm="$(basename "$(readlink -f /etc/systemd/system/display-manager.service)")"
        if [[ "$current_dm" != "greetd.service" ]]; then
            warn "Sustituyendo display manager previo ($current_dm) por greetd.service."
        fi
    fi

    sudo systemctl enable --force greetd.service
    info "Habilitado greetd.service"
}

# ── 5. Servicios de sistema ───────────────────────────────────────────────────
configure_system_services() {
    step "Habilitando servicios del sistema"

    local -a services=(
        NetworkManager.service
        bluetooth.service
        power-profiles-daemon.service
    )

    local svc
    for svc in "${services[@]}"; do
        if systemctl list-unit-files "$svc" --no-legend 2>/dev/null | grep -q "^${svc}"; then
            run sudo systemctl enable --now "$svc"
            info "Servicio habilitado: $svc"
        else
            warn "Unidad $svc no encontrada; se omite."
        fi
    done
}

# ── 6. Grupos de usuario y shell por defecto (fish) ───────────────────────────
configure_user_account() {
    step "Configurando grupos y shell del usuario ($USER)"

    # Grupo 'input' requerido por ~/.config/niri/scripts/trackpoint-nav.py
    if getent group input >/dev/null 2>&1; then
        if id -nG "$USER" | grep -qw input; then
            info "$USER ya pertenece al grupo 'input'."
        else
            run sudo usermod -aG input "$USER"
            info "Añadido $USER al grupo 'input' (efectivo tras reiniciar sesión)."
        fi
    fi

    # Cambiar shell por defecto a fish
    local fish_bin=""
    if [[ -x /usr/bin/fish ]] && grep -Fxq "/usr/bin/fish" /etc/shells 2>/dev/null; then
        fish_bin="/usr/bin/fish"
    elif [[ -x /bin/fish ]] && grep -Fxq "/bin/fish" /etc/shells 2>/dev/null; then
        fish_bin="/bin/fish"
    fi

    if [[ -n "$fish_bin" ]]; then
        local current_shell
        current_shell="$(getent passwd "$USER" | cut -d: -f7)"
        if [[ "$current_shell" == "$fish_bin" || "$(basename "$current_shell")" == "fish" ]]; then
            info "La shell de $USER ya es $current_shell."
        else
            run sudo chsh -s "$fish_bin" "$USER"
            info "Shell cambiada a $fish_bin"
        fi
    else
        warn "fish no está disponible en /etc/shells; se mantiene la shell actual."
    fi
}

# ── 7. Aplicar dotfiles con chezmoi (+ KinderNvim external) ───────────────────
apply_dotfiles() {
    if (( SKIP_CHEZMOI )); then
        warn "Omitiendo chezmoi (--skip-chezmoi)."
        return 0
    fi

    step "Aplicando dotfiles con chezmoi (incluye KinderNvim)"

    if (( ! DRY_RUN )) && ! command -v chezmoi >/dev/null 2>&1; then
        die "chezmoi no está instalado. Ejecuta sin --skip-packages o instálalo antes."
    fi

    # Proteger ~/.config/nvim si ya existe y no es el repo KinderNvim
    if [[ -d "$HOME/.config/nvim" ]]; then
        local nvim_remote=""
        nvim_remote="$(git -C "$HOME/.config/nvim" remote get-url origin 2>/dev/null || true)"
        if [[ "$nvim_remote" != *"KinderNvim"* ]]; then
            local nvim_bak="$HOME/.config/nvim.bak.$(date +%Y%m%d-%H%M%S)"
            warn "~/.config/nvim ya existe y no parece KinderNvim; moviendo a $nvim_bak"
            run mv "$HOME/.config/nvim" "$nvim_bak"
        fi
    fi

    # Detectar si estamos ejecutando desde una copia local del repo de dotfiles
    local script_dir=""
    if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
        script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    fi

    local default_chezmoi_dir="$HOME/.local/share/chezmoi"

    if [[ -n "$script_dir" && -d "$script_dir/dot_config" && "$script_dir" == "$default_chezmoi_dir" ]]; then
        info "Usando source local existente en $default_chezmoi_dir"
        run chezmoi apply
    elif [[ -n "$script_dir" && -d "$script_dir/dot_config" ]]; then
        info "Inicializando chezmoi desde el repositorio local ($script_dir)"
        run chezmoi init --source "$script_dir" --apply
    elif [[ -d "$default_chezmoi_dir/.git" ]]; then
        info "Repositorio chezmoi ya presente en $default_chezmoi_dir; aplicando..."
        run chezmoi apply
    else
        info "Clonando y aplicando desde $REPO_URL"
        run chezmoi init --apply "$REPO_URL"
    fi

    # Carpetas XDG y directorios esperados por los scripts
    if command -v xdg-user-dirs-update >/dev/null 2>&1; then
        run xdg-user-dirs-update
    fi
    run mkdir -p "$HOME/Imágenes/Wallpapers" "$HOME/Notas/journal" "$HOME/Notas/templates"
    info "Dotfiles y directorios base preparados."
}

# ── 8. Servicios systemd de usuario ───────────────────────────────────────────
configure_user_services() {
    step "Habilitando servicios systemd de usuario"

    local has_user_bus=0
    if systemctl --user show-environment >/dev/null 2>&1; then
        has_user_bus=1
    fi

    local -a user_units=(
        pipewire.socket
        pipewire-pulse.socket
        wireplumber.service
    )

    if (( ! NO_OPTIONAL && ! SKIP_AUR )) && command -v voxtype >/dev/null 2>&1; then
        user_units+=(voxtype.service)
    fi

    local unit
    for unit in "${user_units[@]}"; do
        if (( has_user_bus )); then
            if systemctl --user list-unit-files "$unit" --no-legend 2>/dev/null | grep -q "^${unit}"; then
                run systemctl --user enable "$unit"
                info "Unidad de usuario habilitada: $unit"
            else
                warn "Unidad de usuario '$unit' no encontrada; se omite."
            fi
        else
            warn "Sesión systemd --user no activa en este TTY; habilita '$unit' tras iniciar sesión."
        fi
    done
}

# ── 9. Resumen post-instalación ───────────────────────────────────────────────
print_post_install() {
    step "Instalación completada — pasos manuales restantes"

    cat <<EOF
  1. Reinicia el equipo para entrar por tuigreet → Niri:
       sudo reboot

  2. Instala las PWAs (los IDs cambian en cada máquina):
       firefoxpwa site install https://web.whatsapp.com
       firefoxpwa site install https://app.hey.com
     Después, actualiza el ID de WhatsApp en:
       ~/.config/niri/config.d/binds.kdl  (atajo Mod+W)

  3. Coloca tu wallpaper en:
       ~/Imágenes/Wallpapers/06-kinder-midnight-oled.png
     (o ajusta la ruta en ~/.config/niri/config.d/startup.kdl)

  4. Primer uso de Voxtype (Alt+Space):
     Descargará el modelo Whisper 'small' en ~/.local/share/voxtype/models.
EOF

    if [[ "$USER" != "andrea" ]]; then
        cat <<EOF

  [!] Tu usuario es '$USER' (distinto de 'andrea'). Revisa las rutas fijas en:
      - ~/.config/fish/config.fish
      - ~/.config/waybar/config.jsonc
      - ~/.config/niri/config.d/startup.kdl
      - ~/.local/bin/sysmenu
EOF
    fi
    printf '\n'
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
    preflight_checks
    install_pacman_packages
    install_aur_packages
    configure_greetd
    configure_system_services
    configure_user_account
    apply_dotfiles
    configure_user_services
    print_post_install
}

main "$@"
