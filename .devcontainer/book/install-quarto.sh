#!/usr/bin/env bash
set -e

QUARTO_VERSION="1.6.42"
curl -LO "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.deb"
dpkg -i "quarto-${QUARTO_VERSION}-linux-amd64.deb"
rm "quarto-${QUARTO_VERSION}-linux-amd64.deb"
