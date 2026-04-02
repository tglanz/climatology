#!/bin/bash
set -e

GO_VERSION=1.24.1

curl -LO https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz
rm -rf /opt/go
mkdir -p /opt/go
tar -C /opt/go --strip-components=1 -xzf go${GO_VERSION}.linux-amd64.tar.gz
rm go${GO_VERSION}.linux-amd64.tar.gz

echo ""
echo "To add go to your path, run:"
echo ""
echo "    echo 'export PATH=$PATH:/opt/go/bin' >> ~/.bashrc"
echo ""

