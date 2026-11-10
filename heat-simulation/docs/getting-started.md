# Getting started

See the [heat demonstration README](../README.md) for environment setup, the
notebook entry point, numerical assumptions, and tests.

Run formatting or lint checks from the repository root:

```bash
uv run --project heat-simulation --group dev black --check heat-simulation/src heat-simulation/tests
uv run --project heat-simulation --group dev pylint heat-simulation/src
```
