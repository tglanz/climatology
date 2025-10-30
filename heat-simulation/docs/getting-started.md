# Getting Started

## Setup

### Create and activate virtual environment

Create
```bash
python -m venv .venv
```

Activate
```bash
source .venv/bin/activate
```

If uv is not installed globally:
```bash
pip install uv
```

### Install dependencies

```bash
uv sync --all-groups
```

## Running

```bash
python -m heat_simulation.main
```

## Testing

```bash
pytest
```

## Linting and Formatting

### Format code

```bash
black .
```

### Run linter

```bash
pylint src/
```
