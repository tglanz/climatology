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

## Simulation source and ML outputs

Configure these independently:

```toml
[simulations]
dir = "./output/simulations/barotropic_stirring-T85"
pattern = "*"
segment_pattern = "run*/atmos_daily.nc"

[paths]
experiment_dir = "./output/experiments/my-experiment"
```

`pattern` selects simulation directories relative to `dir`. `segment_pattern`
selects NetCDF files relative to each simulation. Both patterns are relative globs.
`[data]` specifies variables, windows, detectors, targets, and split policy.
Relative paths resolve from the repository root when running the commands here.
Prepared data, splits, and training default to `data/`, `splits/`, and `training/`
inside `experiment_dir`. Source paths are never inferred from that directory.

`[simulations]` is required. For older configs, move `data.simulation_pattern` to
`simulations.pattern` and `data.segment_pattern` to `simulations.segment_pattern`.
Set `simulations.dir` explicitly and make the pattern relative to it. For the
existing legacy layout, use `dir = "./output/barotropic_stirring-T85/simulations"`
and `pattern = "*"`. No simulation data is moved by loading a config.

## BVE presets

```text
ml/configs/
  bvet42/
    default.toml
    lat-extra-hi-hold-out.toml
    lat-intra-hold-out.toml
  bvet85/
    default.toml
    lat-extra-hi-hold-out.toml
    lat-intra-hold-out.toml
```

| Config | T42 test split | T85 test split |
|---|---|---|
| `default.toml` | 20% of configuration groups | 20% of configuration groups |
| `lat-extra-hi-hold-out.toml` | Latitude 70 | Latitude 70 |
| `lat-intra-hold-out.toml` | Latitude 60 | Latitude 40 |

Defaults reserve 5% of all configuration groups for validation. Named latitude
holdouts reserve 5% of the remaining groups, with at least one validation group.
All replicas of a configuration stay together. Ratio splits use the existing
deterministic ordering of configuration IDs.

[bvet42](configs/bvet42/) reads the [T42 narrow pool](../scripts/sim-bve-t42-2-narrow.sh).
[bvet85](configs/bvet85/) reads the [T85 standard pool](../scripts/sim-bve-t85-4-standard.sh).
Model and training defaults are shared by all variants. Each config writes its own
ML assets under `output/experiments/<pool>/<variant>/` and shares its pool's raw
simulations. Pass the selected config with `-c` for indexing, validation, splitting,
preprocessing, and training. Evaluation reads the resulting training directory.

The existing local helpers now select one config explicitly:

```bash
./scripts/create-sweep-file.sh ml/configs/bvet42/default.toml
./scripts/preprocess.sh ml/configs/bvet42/default.toml
```

The preprocessing helper validates the source, builds its sweep index, and writes
`splits/fixed.json` for that experiment. Run `preprocess training-data` explicitly
to create HDF5 data. Slurm submission wrappers accept `bvet42` or `bvet85` and
submit the three variants for that pool; omitted pool selection defaults to `bvet85`.

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
Use `ml preprocess`, `ml train`, and `ml evaluate` for the normal workflow.
Prepare once; reuse the completed artifact for each model iteration in a fresh
run directory. Evaluation reads saved windows and simulation identities.

```bash
uv run --project ml --all-groups python -m ml.usecases.experiment_example --directory output/experiment-smoke
uv run --project ml --all-groups ml preprocess training-data -c output/experiment-smoke/prepare.toml --split output/experiment-smoke/splits/fixed.json
uv run --project ml --all-groups ml train -c output/experiment-smoke/run.toml --device cpu --track-metrics
uv run --project ml --all-groups ml evaluate model --training-dir output/experiment-smoke/run --device cpu --n-workers 0
```

Preparation accepts a TOML recipe with `[simulations]`, `[data]`, and `[paths]`.
A model recipe can inherit both its simulation source and data settings with
`data_config="prepare.toml"`, then declare model/training settings and its own
`paths.training_dir`. Training saves a standalone effective configuration,
checkpoint, normalization, split snapshot, prepared-file hashes, and run metadata.
Existing prepared and run directories are rejected. Choose fresh paths to rerun.

Prepared data and checkpoints carry versioned coordinates, channel identities,
input units, and normalization conventions. The corrected loader rejects
unversioned or incompatible artifacts. Preserve saved originals; regenerate data
and retrain into fresh directories for the corrected path. Legacy source fields
must be migrated to `[simulations]` as described above.

Training and evaluation accept `--device cpu` for bounded checks. Training uses
the saved `training.seed` (default zero). Prepared splits retain one target per
simulation so baseline fitting weights simulations equally.

Create the experiment's configuration index before parameter-based splitting:

```bash
uv run --project ml --all-groups ml preprocess create-sweep-file -c prepare.toml \
  --key stirring_lat0=stirring_nml.lat0 \
  --key stirring_amplitude=stirring_nml.amplitude \
  --key stirring_widthy=stirring_nml.widthy
```

This reads selected simulations' `namelist.json` files and writes
`<experiment_dir>/sweep.json`. The explicit keys select namelist fields.
`ml util summarize-simulations -c prepare.toml --segments 150` uses that same
source and optional experiment index. It counts matching segment files; use
`preprocess validate-simulations` for full scientific validity checks.

## Output heads

Set `[model] head = "field"`, `"profile"`, or `"legendre"` in the run recipe.
The default `field` preserves existing checkpoints: predict a full field, then
average longitude. `profile` averages trunk features before the nonlinear output
projection. `legendre` projects trunk features onto Gaussian-weighted latitude
modes, predicts coefficients, then synthesizes the profile. All heads keep the
same two-dimensional trunk and output `(batch, target, latitude)`.

For `legendre`, set `[model] head_modes = 16` (at most the latitude count).
Its basis is `sqrt(2*l+1) * P_l(sin(latitude))`, orthonormal under normalized
Gaussian area weights. It represents normalized targets; the saved normalization
converts predictions back to physical units. A scalar Legendre head does not
enforce tangent-wind behavior at the poles. The streamfunction proposal is a
separate representation. Compare truncation error before interpreting learning.

Model settings, including the head and cutoff, are saved in each run's config.
Use a fresh run directory for each head and seed, with the same prepared inputs,
normalization procedure, loss, and trunk settings.

## Library ownership

| Package or module | Responsibility |
|---|---|
| `data/` | NetCDF and HDF5 readers, timelines, windows, targets, splits |
| `diagnostics/` | Physical calculations and numerical metrics |
| `inference.py` | Checkpoint loading, device preparation, batched prediction |
| `training/` | Models, losses, optimizers, stopping, run artifacts |
| `usecases/` | Preparation, evaluation, analysis, and utility workflows |
| `services/` | Filesystem operations used by use cases |
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

## Remove simulation outputs

Preview matching simulations before deleting:

```bash
uv run --project ml --all-groups ml util purge-simulations \
  --output-dir output/simulations/barotropic_stirring-T85 --lat0 30 --dry-run
```

Repeat `--lat0` to select multiple latitudes. Omit it to select all simulations.
The command reads each simulation's `namelist.json`; it does not require
`sweep.json`. Omit `--dry-run` to delete the listed simulation directories after
interactive confirmation. This utility explicitly modifies the simulation source.

The purge command follows `cmd/util.py` -> `usecases/purge_simulations.py` ->
`services/simulations.py`: CLI arguments, cleanup workflow, then filesystem access.
