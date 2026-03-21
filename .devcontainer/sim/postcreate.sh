#!/bin/bash
set -e

# Isca conda environment
conda env create -f ci/environment-py3.12_frozen.yml
conda run -n isca_env pip install -e src/extra/python

# Claude Code
npm install -g @anthropic-ai/claude-code

# My dotfiles
git clone https://github.com/tglanz/dotfiles ~/own/dotfiles
mkdir -p ~/.config
ln -s ~/own/dotfiles/nvim ~/.config/nvim
