# Experiment pipeline

## Purpose

The pipeline turns simulation trajectories into a reusable dataset, a fitted
model, and an evaluation. Preparation fixes the samples and targets once. Model
iterations share that artifact and write separate run directories. Evaluation
uses the saved samples, so changes to raw simulation directories cannot change
an existing experiment's inputs.

The implementation lives in [preprocessing commands](../ml/src/ml/cmd/preprocess.py),
[preparation](../ml/src/ml/usecases/preprocess.py),
[training](../ml/src/ml/cmd/train.py), and
[evaluation](../ml/src/ml/usecases/evaluate.py).
The [sample contract](pre-processing.md), [grid](grids.md), and [norms](norms.md)
define the scientific calculations.

## Stages and artifacts

```mermaid
flowchart LR
    S[Simulation: Isca] --> N[NetCDF trajectories]
    N --> P[Preparation: validate, split, sample]
    C[Data recipe + assignments] --> P
    P --> D[Prepared HDF5 + manifest]
    D --> T[Training: normalize and fit]
    M[Model + training recipe] --> T
    T --> R[Run: weights, normalization, config, input reference]
    D --> E[Evaluation: predict and aggregate]
    R --> E
    E --> O[Profiles, scores, report, figures]
```

| Conventional stage | Reads | Writes | Rerun rule |
|---|---|---|---|
| Simulation | Namelist, Isca code, forcing, replica index | NetCDF segments, namelist, code provenance | Use the simulation's existing segment resume behavior |
| Preparation | Raw segments, data recipe, split assignments, optional sweep metadata | One completed prepared directory | Choose a fresh directory when samples or splits change |
| Training | Completed prepared directory, model and training recipe | One run directory | Choose a fresh run; reuse prepared data |
| Evaluation | Run checkpoint and its exact prepared artifact | Profiles, scores, report, figures under that run | Recompute evaluation without preparing or fitting again |

### 1. Simulation output

NetCDF segments contain fields with dimensions `(time, lat, lon)`. Coordinates
carry units; time carries a CF reference epoch and calendar. Examples are
relative vorticity `vor` in `1/s` and wind `ucomp` in `m/s`. Latitude is a full
Gaussian grid. Longitude is uniform over one period without a duplicate endpoint.
Segments must form one chronological, uniformly sampled trajectory.

`<simulations.dir>/<configuration-code>-<replica>/` identifies one trajectory
when `simulations.pattern="*"`. Raw output is shared independently of ML experiments.
The experiment-owned `sweep.json` maps configuration codes to parameter objects,
for example
`{"021787": {"stirring_lat0": 30.0}}`. All replicas of one configuration stay in
one split. [Simulation operation](../sim/README.md) describes compilation and runs.

### 2. Preparation recipe and assignments

`prepare.toml` contains `[simulations]`, `[data]`, `[paths]`, and optional `[logging]`.
`[simulations]` declares `dir`, `pattern`, and `segment_pattern`. The directory is
independent of ML outputs. Patterns select simulation folders under that directory
and segment files under each simulation, respectively.
`[data]` declares input/target variables, windows, optional detectors, target
averaging, and split policy. `[paths]` selects the ML `experiment_dir`,
`preprocessed_dir`, and `splits_dir`. Prepared/training/split paths default under
`experiment_dir`. Preparation does not require model or training settings.

`preprocess create-sweep-file -c prepare.toml --key alias=nml.path` reads selected
simulations' namelists and writes `<experiment_dir>/sweep.json`. Repeat `--key` to
select each parameter explicitly. Parameter-based splitting reads this index;
preprocessing copies it into the prepared artifact for later evaluation.

A split JSON contains `train`, `validation`, and `test` arrays of simulation paths
relative to the JSON's directory. `meta` records description, timestamp, and split
policy. Assignments must be disjoint, including configuration replicas. `preprocess generate-splits` creates assignments using the configured policy.
`preprocess training-data --split PATH` uses those assignments or an explicit
fixed subset of the configured simulation source. Stale assignments that point
outside that selection fail before preparation. Ratio assignment sorts
configuration codes deterministically. It does not randomize individual windows.

### 3. Prepared dataset

Preparation builds a temporary sibling directory and publishes it by rename only
after all splits and the manifest are complete. Existing output directories are
rejected. Failed staging directories are removed; source data remain untouched.

Let `N` count windows in a split, `S` accepted simulations, `K` snapshots per
window, `V` input variables, `C` target channels, `H` latitudes, and `W` longitudes.
Each of `train.h5`, `val.h5`, and `test.h5` has this HDF5 schema:

| Dataset or attribute | Type / shape | Meaning |
|---|---|---|
| `x` | float32 `(N, K*V, H, W)` | Physical inputs; channels ordered by time, then variable |
| `y` | float32 `(N, C, H)` | Finite-run time-mean zonal-mean profiles, repeated per window |
| `window_baselines` | float32 `(N, C, H)` | Target-field mean over each input window; optional for older artifacts, used only as an evaluation reference |
| `simulation_targets` | float32 `(S, C, H)` | One profile per accepted simulation; supports equal simulation weighting |
| `simulation_paths` | UTF-8 `(S,)` | Stable source identities; downstream stages do not open these paths |
| `simulation_offsets` | int64 `(S+1,)` | Simulation `i` owns rows `[offsets[i], offsets[i+1])`; starts at zero, ends at `N` |
| `window_starts` | int64 `(N,)` | Zero-based snapshot indices in the original trajectory |
| `simulation_provenance` | JSON attribute, `S` objects | Detected spinup/convergence indices, target interval `[a,b)`, timeline length |
| `metadata` | JSON attribute | Versioned coordinates, variable order, input units, window settings, detectors, target rules |
| `exclusions` | JSON attribute | Rejected source identities and reasons |
| `simulations_requested`, `simulations_loaded` | integer attributes | Coverage counts |

An empty validation or test split retains zero-length arrays and the common
metadata. Training must contain usable windows. Nonfinite fields, inconsistent
units, grids, cadence, or unsuccessful required detectors exclude a simulation.
The existing acceptance rules remain the same for small and full runs.

The directory also contains:

| File | Format and important fields |
|---|---|
| `splits.json` | Requested assignments, including sources later excluded |
| `preparation.toml` | Standalone data configuration snapshot with resolved absolute paths |
| `sweep.json` | Optional parameter snapshot for nearest-configuration baselines and plots |
| `manifest.json` | JSON `format="climatology-prepared-v1"`, `files={filename: SHA256}` for all artifact inputs |

The manifest hashes the full file bytes, including saved arrays and source
membership. Training and evaluation verify them. Editing a prepared file requires
a new prepared artifact. Verification reads the files once per stage and costs
I/O proportional to artifact size.

### 4. Training recipe and run

`run.toml` can reference a preparation recipe through the top-level
`data_config="prepare.toml"`; this reference resolves beside the run recipe.
It inherits `[simulations]`, `[data]`, and preparation paths, then supplies
`[model]`, `[training]`, optional `[logging]`, and
`[paths.training_dir]`. A combined standalone configuration remains supported.
Relative paths in `[simulations]` and `[paths]` resolve against the invocation's
working directory, so
commands and wrappers run from the repository root. Saved snapshots use absolute
paths. Referenced preparation recipes cannot chain other references.

| Run artifact | Format and important fields |
|---|---|
| `config.toml` | Standalone effective configuration; includes model architecture, channels, modes, training seed and settings, data contract, and simulation source |
| `prepared.json` | JSON `directory` and complete `manifest`; binds this run to exact prepared bytes |
| `splits.json` | Training assignment snapshot with paths relative to this file |
| `parameters.pt` | PyTorch state dictionary; best validation checkpoint, or latest epoch when no validation split exists |
| `normalization.pt` | Versioned PyTorch dictionary; `x_mean`, `x_std` shaped `(1,K*V,1,1)`, `y_mean`, `y_std` shaped `(1,C,1)`; epsilon values and versioned metadata |
| `training.json` | JSON run ID, start/end times, epochs, best validation result, data/model/training settings, environment and Git revision |
| `epoch-metrics.csv` | With metrics tracking: run ID, epoch, timestamp, duration, learning rate, train/validation objective |
| `metrics.h5` | With metrics tracking: per-target diagnostics across epochs |

Normalization fits only training windows. Baseline targets retain one row per
training simulation. Model construction gets coordinates from prepared metadata.
The training command rejects an existing run directory instead of moving an old
run. A failed run remains inspectable; retry with a new directory.

Keep the full run and its prepared artifact. Raw trajectories are needed to
change the sample recipe, but not to load the checkpoint or reproduce evaluation.
Training provenance records the current Git revision and whether the checkout
has tracked edits. Use a committed checkout and retain the repository lockfile
for an archived scientific experiment. A training seed controls initialization
and loading order; identical results across devices are not guaranteed.

### 5. Evaluation outputs

Evaluation checks the saved prepared manifest, loads one simulation's windows at
a time, predicts in batches, and averages its window predictions. It then scores
simulations equally in physical units. It uses the saved sweep metadata for
baselines, never the current raw experiment directory.

| File | Format and important fields |
|---|---|
| `evaluation/profiles.npz` | NumPy archive: `simulation_paths (S,)`, `target_names (C,)`, `latitudes (H,)`, `truth` and `predictions (S,C,H)` |
| `evaluation/scores.json` | JSON `targets` keyed by target name: units, aggregation, predictor scores, replica variability, nearest matches; also exclusions and generated figure paths |
| `evaluation/inputs.json` | JSON prepared reference, parameter/normalization/configuration SHA256 values, execution device and batch size |
| `evaluation/report.md` | Markdown numerical tables, coverage, exclusions, and links to figures generated by that invocation |
| `evaluation/figures/` | PNG diagnostics; physical target units and saved coordinates |

A score summary has `mean`, `count`, and `undefined`. A missing baseline records
its reason. Relative errors with a zero reference norm are undefined and counted;
RMSE remains available. The separate prepared-window evaluation API scores
windows individually, so it answers a different aggregation question.

## Command reference

Run from the repository root after `uv sync --project ml --all-groups`.
The flow is `preprocess`, `train`, then `evaluate`. Each command owns one stage.

```bash
uv run --project ml --all-groups ml preprocess create-sweep-file -c prepare.toml --key stirring_lat0=stirring_nml.lat0
uv run --project ml --all-groups ml preprocess generate-splits -c prepare.toml --name fixed
uv run --project ml --all-groups ml preprocess training-data -c prepare.toml --split PATH/TO/splits/fixed.json
uv run --project ml --all-groups ml train -c run.toml --device cpu --track-metrics
uv run --project ml --all-groups ml evaluate model --training-dir PATH/TO/run --device cpu --n-workers 0
```

For another model, change its model settings and `paths.training_dir`, then run
`train` and `evaluate` again. Reuse the same prepared directory. To regenerate
figures, run only `evaluate`. After relocating prepared data, pass
`--prepared-dir PATH`; saved checksums must still match.

`--workers` controls preprocessing processes or training DataLoader workers.
Prepared evaluation is serial over simulations and batches predictions;
`--n-workers` remains accepted for caller compatibility.

### Small experiments

Create a bounded recipe with the example module, then use the same stage commands:

```bash
uv run --project ml --all-groups python -m ml.usecases.experiment_example --directory output/experiment-smoke
uv run --project ml --all-groups ml preprocess training-data -c output/experiment-smoke/prepare.toml --split output/experiment-smoke/splits/fixed.json
uv run --project ml --all-groups ml train -c output/experiment-smoke/run.toml --device cpu --track-metrics
uv run --project ml --all-groups ml evaluate model --training-dir output/experiment-smoke/run --device cpu --n-workers 0
```

The synthetic example writes raw fixtures to a sibling `<directory>-simulations/`
directory. Its ML directory contains only configuration and derived assets.
Add `--real-root output/simulations/barotropic_stirring-T85` to the example module invocation
for a fixed real subset. Use a fresh destination. Its trajectories are
`10bb40-0` (train), `0f0ad6-0` (validation), and `021787-0` (test).
The real recipe retains the default detectors, target rules, and window length,
caps windows at two per trajectory, and uses a one-layer, four-channel SFNO for
two epochs. The synthetic recipe writes three short Gaussian-grid trajectories
with seed 17. These examples check software behavior, not model quality.
`run-wide.toml` changes only model width and the run destination.

### Slurm

The individual stage scripts call the same `preprocess`, `train`, and `evaluate`
commands. Existing scripts under `slurm/` document their submission directories
and resource requests. Submit dependent jobs using `sbatch --dependency=afterok:ID`
so failed preparation or training prevents dependent work from running. Set
resources explicitly for the actual experiment. A cluster needs the same
checkout, locked environment, and shared artifact paths.

## Decisions and limits

The original flow was traced through `lat0-extra-hi-hold-out.toml`:
preparation wrote arrays, training read them, and evaluation reopened assigned raw
simulations and the current `sweep.json`. Saving window ownership and sweep
metadata closes that second raw-data dependency without replacing the scientific
sample construction or report calculations.

Prepared artifacts are referenced rather than copied into each run. This avoids
large duplicate datasets but means they must be retained. Runs can move within
the same source-path layout; evaluation uses the run directory passed explicitly.
Relocated prepared artifacts require `--prepared-dir` and byte-identical contents.
Moving source identities across filesystems does not rewrite their saved paths.
No automatic stage cache, checkpoint resume, distributed training, or experiment
database is introduced. Old artifacts without the pipeline manifest need fresh
preparation and training; saved originals are preserved.
