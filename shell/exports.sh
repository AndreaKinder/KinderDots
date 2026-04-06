# ------------------------------------------------------------------------------
# Codely theme config
# ------------------------------------------------------------------------------
export CODELY_THEME_MINIMAL=false
export CODELY_THEME_MODE="dark"
export CODELY_THEME_PROMPT_IN_NEW_LINE=false
export CODELY_THEME_PWD_MODE="short"

# ------------------------------------------------------------------------------
# Projects config
# ------------------------------------------------------------------------------
export PROJECTS="$HOME/Projects"
export WORK_PROJECTS="$HOME/Projects/work"
export PERSONAL_PROJECTS="$HOME/Projects/personal"

# ------------------------------------------------------------------------------
# Assets
# ------------------------------------------------------------------------------
export LOGO="$DOTFILES_PATH/doc/assets/logo"

# ------------------------------------------------------------------------------
# Languages
# ------------------------------------------------------------------------------
export JAVA_HOME='/Library/Java/JavaVirtualMachines/amazon-corretto-15.jdk/Contents/Home'
export GEM_HOME="$HOME/.gem"
export GOPATH="$HOME/.go"

# ------------------------------------------------------------------------------
# Apps
# ------------------------------------------------------------------------------
if [ "$CODELY_THEME_MODE" = "dark" ]; then
  fzf_colors="pointer:#ebdbb2,bg+:#3c3836,fg:#ebdbb2,fg+:#fbf1c7,hl:#8ec07c,info:#928374,header:#fb4934"
else
  fzf_colors="pointer:#db0f35,bg+:#d6d6d6,fg:#808080,fg+:#363636,hl:#8ec07c,info:#928374,header:#fffee3"
fi

export LS_COLORS="di=38;5;67:ow=48;5;60:ex=38;5;132:ln=38;5;144:*.tar=38;5;180:*.zip=38;5;180:*.jpg=38;5;175:*.png=38;5;175:*.mp3=38;5;175:*.wav=38;5;175:*.txt=38;5;223:*.sh=38;5;132"
export FZF_DEFAULT_OPTS="--color=$fzf_colors --reverse"
export FZF_DEFAULT_COMMAND="fd --hidden --strip-cwd-prefix --exclude .git"
export FZF_DEFAULT_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_COMMAND="fd --type=d --hidden --strip-cwd-prefix --exlude .git"

export CARAPACE_BRIDGES='zsh,fish,bash,inshellisense'

# ------------------------------------------------------------------------------
# Path - The higher it is, the more priority it has
# ------------------------------------------------------------------------------

# Environment detection
export IS_TERMUX=0
if [[ -n "$TERMUX_VERSION" ]] || [[ -d "/data/data/com.termux" ]]; then
    export IS_TERMUX=1
fi

if [[ $IS_TERMUX -eq 1 ]]; then
    path=(
      "$PREFIX/bin"
      "$HOME/.local/bin"
      "$HOME/.cargo/bin"
      "$path"
    )
else
    path=(
      "$HOME/.local/bin"
      "$HOME/.opencode/bin"
      "$HOME/.cargo/bin"
      "$HOME/.volta/bin"
      "$HOME/.bun/bin"
      "$HOME/.nix-profile/bin"
      "/nix/var/nix/profiles/default/bin"
      "/usr/local/bin"
      "$HOME/.config"
      "$HOME/.cargo/bin"
      "/usr/local/lib/*"
      "$path"
    )
fi

path=(
  "$HOME/bin"
  "$DOTLY_PATH/bin"
  "$DOTFILES_PATH/bin"
  "$JAVA_HOME/bin"
  "$GEM_HOME/bin"
  "$GOPATH/bin"
  "$HOME/.cargo/bin"
  "/usr/local/opt/ruby/bin"
  "/usr/local/opt/python/libexec/bin"
  "/opt/homebrew/bin"
  "/usr/local/bin"
  "/usr/local/sbin"
  "/bin"
  "/usr/bin"
  "/usr/sbin"
  "/sbin"
  "$path"
)

export path
