#!/bin/sh
# Envía Ctrl+C / Ctrl+V en apps normales y Ctrl+Shift+C / Ctrl+Shift+V en terminales.
# Requiere `wtype` instalado (`sudo pacman -S wtype`).

action="$1"
case "$action" in
    copy)  key="c" ;;
    paste) key="v" ;;
    *)     exit 1 ;;
esac

app_id="$(niri msg -j focused-window 2>/dev/null | sed -n 's/.*"app_id":[[:space:]]*"\([^"]*\)".*/\1/p')"

case "$app_id" in
    foot|footclient|Alacritty|alacritty|kitty|org.wezfurlong.wezterm|wezterm|com.mitchellh.ghostty|ghostty|org.gnome.Console|org.gnome.Terminal|konsole|rio)
        exec wtype -M ctrl -M shift -k "$key" -m shift -m ctrl
        ;;
    *)
        exec wtype -M ctrl -k "$key" -m ctrl
        ;;
esac
