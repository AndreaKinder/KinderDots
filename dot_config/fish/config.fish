source /usr/share/cachyos-fish-config/cachyos-config.fish

# fastfetch al abrir la terminal (logo: ~/.config/branding/about.txt)
function fish_greeting
    fastfetch
end


# Added by Antigravity CLI installer
fish_add_path -p "$HOME/.local/bin"
