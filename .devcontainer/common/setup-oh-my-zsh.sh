#!/bin/bash
set -e

sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

cat > "$HOME/.zshrc" <<'EOF'
export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME="robbyrussell"

plugins=(git)

source $ZSH/oh-my-zsh.sh

# Fix tmux with Ghostty terminal (xterm-ghostty terminfo not available on remote)
alias tmux='TERM=xterm-256color tmux'
EOF
