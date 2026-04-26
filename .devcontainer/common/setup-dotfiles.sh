#!/bin/bash
set -e

git clone https://github.com/tglanz/dotfiles ~/own/dotfiles
mkdir -p ~/.config
ln -s ~/own/dotfiles/nvim ~/.config/nvim
