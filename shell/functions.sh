function cdd() {
  cd "$(ls -d -- */ | fzf)" || echo "Invalid directory"
}

function j() {
  fname=$(declare -f -F _z)

  [ -n "$fname" ] || source "$DOTLY_PATH/modules/z/z.sh"

  _z "$1"
}

function recent_dirs() {
  escaped_home=$(echo $HOME | sed 's/\//\\\//g')
  selected=$(dirs -p | sort -u | fzf)

  cd "$(echo "$selected" | sed "s/\~/$escaped_home/")" || echo "Invalid directory"
}

kinder_greeting() {
  local purple=$'\033[35m'
  local blue=$'\033[34m'
  local cyan=$'\033[36m'
  local yellow=$'\033[33m'
  local reset=$'\033[0m'

  echo "${purple}"
  cat $LOGO
  cat <<'EOF'
EOF
  echo "${reset}"
  echo "      ${blue}Welcome to Kinder.Dots Environment!${reset}"
  echo "      ${cyan}Zsh Shell with custom configuration loaded.${reset}"
  echo ""
}
