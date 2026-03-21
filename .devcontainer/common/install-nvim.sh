#!/bin/bash
set -e

NVIM_VERSION=0.11.0
curl -LO https://github.com/neovim/neovim/releases/download/v${NVIM_VERSION}/nvim-linux-x86_64.tar.gz
rm -rf /opt/nvim
mkdir -p /opt/nvim
tar -C /opt/nvim --strip-components=1 -xzf nvim-linux-x86_64.tar.gz
rm nvim-linux-x86_64.tar.gz
