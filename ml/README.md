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
The `inference` group supports model loading; the full CLI also needs the
training group. HDF5 is a base dependency used during preparation.

## Current commands

```bash
uv run --project ml --group train --group vis ml preprocess --help
uv run --project ml --group train --group vis ml train --help
uv run --project ml --group train --group vis ml evaluate model --help
uv run --project ml --group train --group vis ml monitor training --help
uv run --project ml --group train --group vis ml data --help
uv run --project ml --group train --group vis ml util --help
```

The [pipeline overview](../docs/pipeline.md) describes stages, intermediate artifact
formats and schemas, the flow diagram, commands, and local/Slurm execution.
Use `ml pipeline example`, `ml pipeline prepare`, and `ml pipeline run` for the
normal iteration workflow. Prepare once; reuse the completed artifact for each
model iteration in a fresh run directory. Evaluation reads the saved prepared
windows and simulation identities rather than reopening raw trajectories.

```bash
bash scripts/pipeline.sh example --directory output/pipeline-smoke
bash scripts/pipeline.sh prepare -c output/pipeline-smoke/prepare.toml \
    --split output/pipeline-smoke/splits/fixed.json
bash scripts/pipeline.sh run -c output/pipeline-smoke/run.toml --device cpu
bash scripts/pipeline.sh run -c output/pipeline-smoke/run-wide.toml --device cpu
```

Preparation accepts a data-only TOML recipe. A model recipe can reference it with
`data_config="prepare.toml"`, then declare model/training settings and its own
`paths.training_dir`. Training saves a standalone effective configuration,
checkpoint, normalization, split snapshot, prepared-file hashes, and run metadata.
Existing prepared and run directories are rejected. Choose fresh paths to rerun.

Prepared data and checkpoints carry versioned coordinates, channel identities,
input units, and normalization conventions. The corrected loader rejects
unversioned or incompatible artifacts. Preserve saved originals; regenerate data
and retrain into fresh directories for the corrected path. Old configurations
with `data.experiment_dir` also need the current `paths.experiment_dir` field.

Training and evaluation accept `--device cpu` for bounded checks. Training uses
the saved `training.seed` (default zero). Prepared splits retain one target per
simulation so baseline fitting weights simulations equally.

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

## Checks and correctness

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

[Action item 02](../action-items/02-correctness.md) tracks the correctness
implementation and its [progress](../action-items/02-correctness-plan-progress.md).
The [sample contract](../docs/pre-processing.md), [grids](../docs/grids.md), and
[norms](../docs/norms.md) define the scientific conventions.
[Action item 03](../action-items/03-pipeline.md) records the pipeline redesign
and its [verification results](../action-items/03-pipeline-results.md).
The [compaction results](../action-items/01-compaction-results.md) remain the
historical verification record for phase 01.
