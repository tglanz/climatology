#!/bin/bash
set -e

bash .devcontainer/common/setup-dotfiles.sh

git submodule update --init --recursive

export PATH="/home/ubuntu/miniforge3/bin:$PATH"
conda env create -f submodules/isca/ci/environment-py3.12_frozen.yml
conda run -n isca_env pip install -e submodules/isca/src/extra/python
