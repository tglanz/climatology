# Analysis

Data processing, visualization, and transformation tools for simulation and ML inputs/outputs.

## Setup

```bash
cd analysis
uv sync --all-extras
source .venv/bin/activate
```

## Commands

```bash
# Rotating globe GIF from simulation output
python -m analysis.cmd.rotating_globe --help

# Formatting
black src/

# Linting
pylint src/
```
