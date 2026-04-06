#!/usr/bin/env zsh
# Uncomment for debuf with `zprof`
# zmodload zsh/zprof

# ZSH Ops
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_FCNTL_LOCK
setopt +o nomatch
# setopt autopushd

ZSH_HIGHLIGHT_HIGHLIGHTERS=(main brackets)

# Start Zim
source "$ZIM_HOME/init.zsh"

# Async mode for autocompletion
ZSH_AUTOSUGGEST_USE_ASYNC=true
ZSH_HIGHLIGHT_MAXLENGTH=300

source "$DOTFILES_PATH/shell/init.sh"

fpath=("$DOTFILES_PATH/shell/zsh/themes" "$DOTFILES_PATH/shell/zsh/completions" "$DOTLY_PATH/shell/zsh/themes" "$DOTLY_PATH/shell/zsh/completions" $fpath)

autoload -Uz promptinit && promptinit
prompt ${DOTLY_THEME:-codely}

source "$DOTLY_PATH/shell/zsh/bindings/dot.zsh"
source "$DOTLY_PATH/shell/zsh/bindings/reverse_search.zsh"
source "$DOTFILES_PATH/shell/zsh/key-bindings.zsh"

if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

if [[ $- == *i* ]]; then
    # Commands to run in interactive sessions can go here
fi

if [[ "$(uname)" == "Darwin" ]]; then
  alias ls='ls --color=auto'
else
  alias ls='gls --color=auto'
fi

if [[ $IS_TERMUX -eq 0 ]]; then
    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS - check for Apple Silicon vs Intel
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            # Apple Silicon (M1/M2/M3)
            BREW_BIN="/opt/homebrew/bin"
        elif [[ -f "/usr/local/bin/brew" ]]; then
            # Intel Mac
            BREW_BIN="/usr/local/bin"
        fi
    else
        BREW_BIN="/home/linuxbrew/.linuxbrew/bin"
    fi

    # Only eval brew shellenv if brew is installed
    if [[ -n "$BREW_BIN" && -f "$BREW_BIN/brew" ]]; then
        eval "$($BREW_BIN/brew shellenv)"
    fi
fi

if [[ $IS_TERMUX -eq 1 ]]; then
    # Termux - plugins installed via pkg
    [[ -f "$PREFIX/share/zsh-autocomplete/zsh-autocomplete.plugin.zsh" ]] && source "$PREFIX/share/zsh-autocomplete/zsh-autocomplete.plugin.zsh"
    [[ -f "$PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ]] && source "$PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
    [[ -f "$PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ]] && source "$PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
    # Powerlevel10k on Termux - may need manual install
    [[ -f "$PREFIX/share/powerlevel10k/powerlevel10k.zsh-theme" ]] && source "$PREFIX/share/powerlevel10k/powerlevel10k.zsh-theme"
else
    source $(dirname $BREW_BIN)/share/zsh-autocomplete/zsh-autocomplete.plugin.zsh
    source $(dirname $BREW_BIN)/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
    source $(dirname $BREW_BIN)/share/zsh-autosuggestions/zsh-autosuggestions.zsh
    source $(dirname $BREW_BIN)/share/powerlevel10k/powerlevel10k.zsh-theme
fi

WM_VAR="/$TMUX"
# change with ZELLIJ
WM_CMD="tmux"
# change with zellij

function start_if_needed() {
    if [[ $- == *i* ]] && [[ -z "${WM_VAR#/}" ]] && [[ -t 1 ]]; then
        exec $WM_CMD
    fi
}

# alias
alias fzfbat='fzf --preview="bat --theme=gruvbox-dark --color=always {}"'
alias fzfnvim='nvim $(fzf --preview="bat --theme=gruvbox-dark --color=always {}")'

plugins=(
  command-not-found
)

zstyle ':completion:*' format $'\e[2;37mCompleting %d\e[m'
source <(carapace _carapace)

eval "$(fzf --zsh)"
eval "$(zoxide init zsh)"
eval "$(atuin init zsh)"

[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# Custom greeting
kinder_greeting

start_if_needed
