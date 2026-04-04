#!/bin/bash
set -e

sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

cat > "$HOME/.zshrc" <<'EOF'
# ==== BEGIN: by setup-oh-my-zsh.sh ========
export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME="robbyrussell"

plugins=(git)

source $ZSH/oh-my-zsh.sh
# ==== END: setup-oh-my-zsh.sh ========
EOF
