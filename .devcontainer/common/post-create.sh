#!/bin/bash
set -e

git clone https://github.com/tglanz/dotfiles ~/own/dotfiles
mkdir -p ~/.config
ln -s ~/own/dotfiles/nvim ~/.config/nvim

# Fix tmux with Ghostty terminal (xterm-ghostty terminfo not available on remote)
echo "alias tmux='TERM=xterm-256color tmux'" >> ~/.bashrc

# Readable ls colors (bold cyan directories instead of dark blue)
cat > ~/.dircolors <<'EOF'
DIR 01;36
LINK 01;35
EXEC 01;32
FIFO 01;33
SOCK 01;35
BLK 01;33
CHR 01;33
ORPHAN 01;31
SETUID 01;31
SETGID 01;33
STICKY_OTHER_WRITABLE 01;36
OTHER_WRITABLE 01;36
STICKY 01;36
EOF
