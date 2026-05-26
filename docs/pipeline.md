# Pipeline

End-to-end flow for training and rolling out the FNO emulator of the Isca
barotropic vorticity equation.

## Simulation

- Isca barotropic dynamical core, Vallis-style stochastic vorticity stirring.
- T85 spectral truncation, alias-free Gaussian grid (128 lat x 256 lon).
- 15 daily-output segments per sim (7 days each, 105 days total).
- Single forcing distribution across all sims; only the random seed of the
  stirring varies between runs.
- One sim per CLI invocation: `python sim/barotropic_stirring.py --index N`.
- Skip-if-exists: invocations whose `simulations/N/run0015/atmos_daily.nc`
  already exists exit immediately, so `seq 0 999 | parallel ...` is idempotent
  under crashes.
- `Settings.Cores = 1` to avoid concurrent `mpirun` collisions on macOS;
  parallelism between sims handled by GNU parallel.

## Raw outputs

- `output/<experiment>/simulations/<index>/run<NNNN>/atmos_daily.nc`.
- Variables written: vor, stirring, ucomp, vcomp, pv, stream, eddy_vor,
  delta_u, stirring_amp, stirring_sqr, etc.
- Time step: 1 day per record (daily averages).

## Preprocessing

- Command: `ml preprocess training-data -c ml/config.toml`.
- Concatenates segments per simulation into a flat chronological timeline.
- Builds (input, target) pairs:
  - Input: `K = data.lag_steps` consecutive timesteps of `data.x_vars`.
  - Target: `data.y_vars` at the timestep immediately after the input window.
- Channel order in input: oldest to newest, x_vars-major within each timestep.
  For x_vars = [vor, stirring] and K = 5, channels are
  [vor_-4, stirring_-4, vor_-3, stirring_-3, ..., vor_0, stirring_0].
- Sampling per simulation: `samples_per_experiment = 1`, `sampling = "latest"`.
  Takes the most recent valid window, guaranteeing past-spinup state without
  needing manual `skip`.
- Split by simulation index: 10 percent test, 10 percent val, 80 percent
  train. Lowest indices go to test (so sim 0 is always held out).
- Outputs to `output/<experiment>/data/`:
  - `train.h5`, `val.h5`, `test.h5` (HDF5 with datasets `x`, `y`).
  - `splits.json` listing which simulations went to which split.

## Validation tooling

- `ml preprocess validate-simulations -c ml/config.toml` walks every sim and
  emits a parseable `<sim_dir> -- runs=...; samples=...; valid=...` line.
- `--invalid-only` filters to broken sims; `--analyze` adds a mean enstrophy
  field for spotting numerical outliers.
- Run before preprocessing whenever the simulation set changes.

## Normalization

- `UnitGaussianNormalizer` fit once at the start of training on the entire
  train split, per-channel reduction over batch and spatial dims.
- Stats saved to `<training_dir>/normalization.pt` so inference can apply
  the identical transform.
- Training-time loss runs on normalized tensors (well-scaled gradients).
- Validation-time loss runs on inverse-normalized predictions vs unnormalized
  targets, so the reported number is in physical units.

## Model

- Stock FNO from `neuralop.models.FNO`.
- Configurable: `n_modes`, `hidden_channels`, `n_layers`, `in_channels`,
  `out_channels`.
- `in_channels` is enforced to equal `lag_steps * len(x_vars)` at config
  load time.
- Optional dropout passed to FNO as `channel_mlp_dropout`
  (`training.regularization.dropout`).

## Loss

- Selected via `training.loss`:
  - `mse`: standard MSE.
  - `relative_l2`: per-sample relative L2, scale invariant.
  - `lat_weighted_relative_l2` (default): same as relative_l2, but each
    spatial squared term multiplied by cos(lat) area weights normalized
    to mean 1. Removes the polar-overweighting bias of unweighted L2 on
    a lat-lon grid.
- Latitudes for the weighted variant are read from the first netCDF
  in the train split via `load_latitudes`.

## Optimizer

- Selected via `training.optimizer`: `adam` or `adamw`.
- AdamW honors `training.regularization.weight_decay`; Adam ignores it
  and warns at trainer init if a non-zero value is set.
- Optional `training.grad_clip` clips global gradient norm before each
  optimizer step.

## Learning rate schedule

- Configured under `[training.scheduler]` with a `kind` field selecting
  one of: `step`, `cosine`, `plateau`, `none`.
- Each kind has its own subsection with kind-specific options
  (`[training.scheduler.cosine]`, etc.). Subsections that do not match
  the active `kind` are ignored.
- Cosine is the default; smooth monotone decay over `t_max` epochs
  (defaults to `training.epochs`).

## Early stopping

- Composite of independent criteria; any one firing ends training.
- Configured under `[training.early_stopping]`. Subsections that are
  present are enabled; absent subsections disable that criterion.
- Available criteria:
  - `target_loss`: stop when the monitored loss drops at or below `value`.
    Useful when the goal is to clear an a-priori benchmark.
  - `patience`: stop when the monitored loss has not improved by
    `min_delta` for `patience` epochs. Catches plateaus and overfitting.
- Both criteria can pick `monitor = "val"` or `"train"`.
- The trainer always wraps a `CompositeEarlyStopper` (possibly empty)
  so the per-epoch check is uniform.

## Training loop

- Command: `ml train -c ml/config.toml [--track-metrics]`.
- On start:
  - Rotate previous `training/` to `training-N` (next free index).
  - Snapshot `config.toml` into the new `training/`.
  - Build `TrainingInfo` (run_id, env, config, paths, data stats) and
    write `training.json`.
- Per epoch:
  - Forward pass on normalized inputs.
  - Loss against normalized target.
  - Backward, optional grad clip, optimizer step.
  - Validate on inverse-normalized predictions and unnormalized targets.
  - Save `parameters.pt` if val loss improved.
  - Step the scheduler (per-epoch or per-val-loss depending on kind).
  - Append a row to `epoch-metrics.csv`.
  - Query the composite early stopper.
- On finish:
  - Append a row to `runs.csv` summarizing the run.
  - Update `training.json` with end_time, total_epochs, best_val_loss,
    and stopped_early.

## Run artifacts

- `<experiment>/training/`:
  - `config.toml`: the snapshot of the config used for this run.
  - `parameters.pt`: model state at the best validation epoch.
  - `normalization.pt`: input/output normalizer stats.
  - `epoch-metrics.csv`: per-epoch loss, learning rate, timestamps.
  - `runs.csv`: one row per `fit` call.
  - `training.json`: rich run metadata (env, splits, model size, etc.).
  - `metrics.h5` (with `--track-metrics`): per-epoch spatial error, zonal
    mean error, error/signal power spectra.
- Previous runs preserved as `training-1`, `training-2`, ...; custom-named
  directories (`training-300-53`) are ignored by the rotation logic.

## Inference and rollout

- `Autoregressor` (in `ml/inference.py`) loads `parameters.pt` and
  `normalization.pt` from a checkpoint directory.
- Rollout signature: `rollout(vor_history, stirring_seq)`.
  - `vor_history` shape `(K, lat, lon)`: the K most recent known vorticity
    snapshots in chronological order. Required because the model's input
    is a K-step window.
  - `stirring_seq` shape `(K + T - 1, lat, lon)`: stirring covering all
    input windows used during the rollout. T predictions are inferred
    from the length.
- Each step:
  - Build the K-step input window with the same channel ordering as
    preprocessing.
  - Normalize, forward, inverse-normalize.
  - Append the prediction; slide the window by one.
- Returns `(K + T, lat, lon)`: the input echo followed by T predictions.

## Evaluation command

- `ml evaluate autoregression -c ml/config.toml --input <nc> --start t0 --timesteps T`.
- Refuses to evaluate on simulations not in the test split.
- Slices the netCDF to provide K-1 leading timesteps of history before t0.
- Writes `vor_pred` and `vor_pred_err` alongside ground truth into a new
  netCDF for inspection or notebook visualization.

## Health and reporting commands

- `ml util model-info -c <cfg>`: architecture summary and params/sample
  ratios per split.
- `ml util persistence-score -c <cfg>`: persistence and zero baselines on
  the val split, in the configured loss. Confirms the model is doing real
  work above persistence.
- `ml util summarize-trainings -d <experiment>` [--limit N]: rich table of
  past training runs (start time, duration, epochs, best val, params, etc.),
  newest first; reads `training.json` and falls back to `runs.csv` for
  legacy runs.

## Key design decisions

- Same forcing distribution across all sims: scope is to emulate one specific
  forcing configuration, not to learn an operator that generalizes across
  forcings.
- One independent (input, target) pair per simulation: matches the FNO
  paper's i.i.d. recipe and avoids correlated samples within a single
  trajectory.
- Lag-stacked input (`lag_steps > 1`): a single instantaneous (vor, stirring)
  pair does not fully determine vor at t+1 day; stacking K snapshots gives
  the model velocity and recent stirring trend.
- Cosine LR schedule and patience early stopping by default: smooth decay,
  with patience as the actual stop signal so wasted compute on plateaus is
  caught early.
- AdamW with optional `weight_decay`: decoupled L2 regularization that does
  not interact with the adaptive learning rate.
- Latitude-weighted loss: errors near the poles are weighted by their actual
  area, not the number of grid cells they occupy.
- Run rotation and per-run artifacts: every run is fully self-documenting
  via its own `config.toml`, `training.json`, and metric CSVs; no in-place
  overwriting.
