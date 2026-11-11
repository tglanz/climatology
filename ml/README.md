# ML experiments

Prepare Isca output, train a neural operator, and evaluate climatology predictions.
Run commands from the repository root.

## Environment

Python 3.13 or later is required. Install the development, training, and plotting
groups for the complete local workflow:

```bash
uv sync --project ml --group dev --group train --group vis
uv run --project ml --group train --group vis ml --help
```

The training group uses the pinned, editable neuraloperator submodule.
The `inference` group supports model loading; HDF5 evaluation and the full CLI
also need the training group.

## Current commands

```bash
uv run --project ml --group train --group vis ml preprocess --help
uv run --project ml --group train --group vis ml train --help
uv run --project ml --group train --group vis ml evaluate model --help
uv run --project ml --group train --group vis ml monitor training --help
uv run --project ml --group train --group vis ml data --help
uv run --project ml --group train --group vis ml util --help
```

Preparation validates simulations, creates sweep metadata, generates splits, and
writes training data. See [preprocessing](../docs/pre-processing.md).
Training reads the configured prepared splits and writes parameters, normalization
statistics, metrics, a configuration copy, split metadata, and run information.
Evaluation takes a training directory and reads raw simulations again. See
[evaluation](../docs/model-evaluation.md) and the
[default configuration](configs/default.toml).

These stages retain their existing configuration and directory assumptions.
Older saved configurations with `data.experiment_dir` instead of
`paths.experiment_dir` are incompatible with the current loader. Preserve the
saved originals; any explicit compatibility copy should keep the original model
and data settings.

## Library ownership

| Package or module | Responsibility |
|---|---|
| `data/` | NetCDF and HDF5 readers, timelines, windows, targets, splits |
| `diagnostics/` | Physical calculations and numerical metrics |
| `inference.py` | Checkpoint loading, device preparation, batched prediction |
| `training/` | Models, losses, optimizers, stopping, run artifacts |
| `usecases/` | Preparation, evaluation, analysis, and read-only summaries |
| `visualization/` | Figures and animation |
| `cmd/` | Command arguments and output presentation |

Import diagnostics from their owning modules, such as
`ml.diagnostics.errors` or `ml.diagnostics.enstrophy`.
Notebooks configure and call these APIs. Their saved outputs are historical
results; a changed source cell does not establish that an old output was
regenerated. The two convergence notebooks retain distinct example paths and
historical outputs while calling the same implementation.

Launch notebooks from `ml/notebooks/`:

```bash
uv run --project ml --group train --group vis jupyter lab --notebook-dir ml/notebooks
```

The rotating-globe entry point remains available:

```bash
uv run --project ml --group train --group vis python -m ml.cmd.rotating_globe --help
```

## Checks and remaining corrections

Every pull request to main runs separate ML lint and test jobs. Pushes to main
also check changes to ML, its neuraloperator pin, and the shared CI workflow.
CI initializes the pinned neuraloperator submodule and installs all dependency
groups from the lockfile. Tests run from the repository root.

The ML lint gate checks pylint errors and Black formatting. Existing pylint
style and refactoring warnings remain available locally. HDF5 group inference
is excluded from member checking because dataset lookups share the same API.

```bash
uv run --project ml --all-groups pylint --rcfile=ml/pyproject.toml --errors-only ml/src
uv run --project ml --all-groups black --check ml
```

```bash
uv run --project ml --group dev --group train --group vis pytest ml/tests
```

Compaction preserves existing scientific behavior, including known differences
between preparation, CLI evaluation, and notebook evaluation.
[Action item 02](../action-items/02-correctness.md) owns those corrections;
[action item 03](../action-items/03-pipeline.md) owns workflow redesign.
The [compaction results](../action-items/01-compaction-results.md) record checks,
retention decisions, and verification limits.
