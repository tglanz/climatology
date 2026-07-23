#!/bin/bash

script_dir=$(realpath $(dirname $0))
cd $script_dir

pandoc index.md \
  --lua-filter ../pandoc-resources/include.lua \
  --filter pandoc-crossref \
  --pdf-engine=xelatex \
  -o executive-summary.pdf