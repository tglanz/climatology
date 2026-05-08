# Project Review

This is a constructive review of the `climatology` repository, focused
mainly on the `ml/` subproject (the FNO emulator for the Isca barotropic
vorticity equation). The goal is to highlight what works well, then
flag concrete things to improve in priority order. Nothing here is a
showstopper; the project is in good shape.

## 1. What is working well

**Clear separation of concerns.** The package layout is clean:
`config.py` for configuration, `model.py` for architecture,
`training.py` for fit/eval, `isca_preprocessing.py` for the data
pipeline, `inference.py` for autoregressive rollout, and a `cmd/`
group that exposes everything as click subcommands. Code is short
(roughly 2k lines including the monitor). It is easy to read end to
end in one sitting.

**Configuration is centralized and validated.** `config.toml` is the
single source of truth, parsed into typed dataclasses with
`__post_init__` assertions. New options consistently land in one
place. The recent split into nested scheduler subsections
(`[training.scheduler.<kind>]`) is a good pattern.

**Sensible defaults and structure for outputs.** Each experiment has a
self contained directory under `output/<experiment>/` with
simulations, preprocessed data, and training artifacts side by side.
`splits.json` makes provenance explicit. Per epoch metrics are written
to a CSV that is easy to load anywhere.

**Useful invariants are encoded.** Test simulations are pinned to the
lowest indices so simulation 0 stays held out. The autoregression
evaluator refuses to run on non test simulations. Normalization
statistics are persisted alongside the model weights so inference is
reproducible.

**Good baseline tooling.** `ml util persistence-score` is a small idea
that pays off: any future loss change is automatically benchmarked
against zero and persistence in the same units, which catches
regressions that a single number cannot.

**Documentation discipline.** `CLAUDE.md`, `ml/README.md`, and now
`ml/training.md` give a coherent set of guidelines and references.
The pyproject groups (`train`, `inference`, `vis`, `dev`) are a clean
way to keep the visualization stack out of the training environment.

## 2. Bugs and stale code (highest priority)

These are concrete defects that should be fixed before the next
training run or before sharing the repo with collaborators.

### 2.1 Monitor still reads removed fields

`ml/src/ml/common/monitor.py` references `t.lr_decay_factor` and
`t.lr_decay_every` (around line 83). Those fields were removed when
the scheduler was refactored into the nested `SchedulerConfig`. The
monitor will raise `AttributeError` the moment the LR section is
rendered.

Fix: read from `cfg.training.scheduler` and render based on
`scheduler.kind`. Each kind has its own subconfig now, so the section
can show the active settings (e.g. `cosine: t_max=300, eta_min=0.0`).

### 2.2 IscaDataset reopens the HDF5 file on every `__getitem__`

`isca_dataset.py` opens `h5py.File(self.h5_path, "r")` inside
`__getitem__`. With `batch_size=64` and `shuffle=True`, this is at
least 64 file opens per batch. On a network filesystem or a slow disk
this is noticeable; on a fast SSD it is still wasteful.

Fix: open the file once (lazily, in `__getitem__` if a worker is
present) and cache the handle. Either keep `self._f` as a thread
local, or memory map the dataset (h5py supports this with
`driver="core"` or by loading the whole tensor into RAM if it fits).
For the current dataset size (a few thousand pairs of 128x256
float32), loading into RAM at construction time is the simplest and
fastest solution.

### 2.3 DataLoader has no `num_workers` or `pin_memory`

`make_loader` constructs `DataLoader(ds, batch_size=...)` with the
defaults. On a multi core machine that means a single Python process
doing all I/O on the main thread. Combined with 2.2 this is the
likely reason each epoch takes about four seconds even though the
data is small.

Fix: expose `num_workers` and `pin_memory` in the data config. Sane
defaults: `num_workers = 4`, `pin_memory = torch.cuda.is_available()`.

### 2.4 `_fit_normalizers` silently passes `batch_size=None`

`UnitGaussianNormalizer.partial_fit(x, batch_size=batch_size)` reads
`batch_size = train_loader.batch_size`. That is the configured batch
size, not the actual batch size passed in. If `drop_last=False` (the
default) the last batch may be smaller, and the normalizer will be
fit incorrectly on that batch.

Fix: pass `batch_size=x.shape[0]` per call, not the loader attribute.

### 2.5 No tests

There are no unit or integration tests in `ml/`. With the trainer,
preprocessing, and config now non trivial, this is a real risk. A
single small smoke test that runs end to end on synthetic data
(generated in memory, two epochs, four samples) would catch most
regressions.

Fix: add `ml/tests/` with `test_smoke_train.py` and
`test_config_load.py`. `pyproject.toml` already has `pytest` in the
`dev` group.

## 3. Design improvements (medium priority)

### 3.1 Fix the loss/metric units mismatch in epoch CSV

`epoch-metrics.csv` writes `train_loss` (computed in normalized space)
and `val_loss` (computed in physical units). Plotting them on the
same axis is misleading. Two cleaner options:

- Compute training loss in physical units too, by inverse normalizing
  the prediction before the loss. This matches the validation path
  and makes the curves directly comparable.
- Or, log both flavors: `train_loss_norm`, `val_loss_norm`,
  `train_loss_phys`, `val_loss_phys`, and let the monitor render the
  right pair.

The first option is cheaper and more honest.

### 3.2 Random seeds are not set anywhere

The trainer is non deterministic across runs. There is currently no
way to compare two runs and conclude "this change moved the loss" vs
"this is sample to sample noise".

Fix: add `training.seed` (default 0) and seed `torch`, `numpy`, and
Python `random` at the top of `cmd/train.py`. Optionally also set
`torch.use_deterministic_algorithms(True)` behind a config flag.

### 3.3 The dataset assumes one global `lat` array

`load_latitudes` reads from the first netCDF in the train manifest.
It works today, but if simulations ever differ in resolution or grid
the failure mode is silent (only the first sim's grid is used).

Fix: validate that the latitude grid is the same across all
simulations during preprocessing, and persist it into each HDF5 file
alongside `x` and `y`. Then `load_latitudes(cfg)` reads from the H5
without any netCDF dependency at training time.

### 3.4 Forcing diversity in the training set

The dataset uses a single set of stirring parameters across
simulations. The model is therefore being asked to generalize across
realizations of the same forcing distribution, not across forcing
regimes. This is a useful baseline but limits the operator
interpretation.

Suggested next step: vary stirring amplitude, latitude band, and
width across simulations. A small parameter sweep already
parameterized as named variables would let the operator learn a real
input dependence and would justify the FNO framing.

### 3.5 Training writes the best checkpoint without an epoch tag

`parameters.pt` is overwritten whenever val loss improves. There is no
way to recover an earlier checkpoint, and there is no way to resume
training. Both are useful when a run is killed or when comparing
intermediate points.

Fix: add `--checkpoint-every N` to write `parameters-epoch-NNNN.pt`
periodically, and store the optimizer and scheduler state alongside
the model state in a single dict. Add a `--resume` flag to load it
back.

### 3.6 No real early stopping

`target_loss` is the only stopping criterion. In practice you want
"stop if val loss has not improved for K epochs". This is one of the
most useful defenses against wasted compute on plateaued runs.

Fix: add `[training.early_stopping]` with `patience` and
`min_improvement`. Reuse the same monitored metric the plateau
scheduler uses.

### 3.7 `IscaDataPreprocessor` is not idempotent

Re running preprocessing overwrites HDF5 files. There is no checksum
or version stamp, so two preprocessing runs with different
`samples_per_experiment` produce indistinguishable files at first
glance.

Fix: write a small `metadata.json` next to `splits.json` recording
`x_vars`, `y_vars`, `samples_per_experiment`, `sampling`, `skip`, the
git SHA, and a content hash. The trainer can warn if those drift
from the loaded config.

## 4. Smaller things (low priority but easy)

- `ml/src/ml/cmd/util.py` should grow the proposed utilities listed in
  `training.md`. `data-stats`, `eval-checkpoint`, and
  `config-summary` are each about twenty lines and would pay for
  themselves the first time they catch a misconfiguration.
- `model.py` is thirteen lines and probably wants one more option:
  pick between FNO and SFNO via `model.kind` rather than hard coding
  FNO. The plumbing is trivial since `neuraloperator` already exposes
  `SFNO`.
- `Trainer.fit` mixes concerns: optimization, logging, checkpointing,
  metrics, and early stopping. As features grow this method will
  become hard to follow. A small split into `_train_one_epoch`,
  `_validate`, `_save_checkpoint`, and `_should_stop` would help.
- `monitor.py` (in `cmd/`) and `monitor.py` (in `common/`) share a
  name. Consider renaming the inner one to `monitor_state.py`.
- `cli.py` could group commands more visibly: a top level `--version`
  flag and a single `ml --help` listing each subcommand with one
  sentence of help would make the CLI feel finished.
- `inference.py` always picks the first available device. For
  reproducibility benchmarks across machines, a `--device` override
  is useful.
- The persistence baseline implementation in
  `util.py:persistence_score` uses `x[:, 0:1, :, :]` as the
  prediction. This silently assumes that `vor` is the first input
  channel. It should look up the channel index of `vor` in
  `cfg.data.x_vars` to be robust to reordering.

## 5. Repository wide observations

### 5.1 Multi project layout is well structured

Top level directories (`ml`, `sim`, `analysis`, `book`,
`presentations`, `heat-simulation`, `isca_work`) each have their own
purpose and tooling. `CLAUDE.md` calls this out explicitly. The risk
is drift: `sim/` uses a conda environment, `ml/` uses `uv`. The pain
of switching contexts is small now but worth keeping an eye on.

### 5.2 Submodules pinning is recorded

Pinning `neuraloperator` and `isca` as submodules is the right call
for a reproducible research project. The README explains how to
clone and update them. It would help to record the exact commit SHAs
in a top level `versions.md` so the dependency state is human
readable without running git.

### 5.3 No CI

There is no `.github/workflows/` or equivalent. For a personal
research repo this is fine, but a single workflow that runs `pytest`
and a config load smoke test on push would catch the kind of issue
flagged in 2.1 in seconds rather than at the next training run.

### 5.4 Output directory will get large

`output/` is already tens of gigabytes per experiment once
simulations and preprocessed data accumulate. There is no cleanup
policy or hint that intermediate `training-data/*.h5` files are
regenerable. Adding a short `output/README.md` describing what is
safe to delete and what is not would prevent accidental loss of
trained checkpoints.

## 6. Suggested order of operations

If the next chunk of time has to be spent on infrastructure rather
than on training experiments, do these in order:

1. Fix the monitor (2.1). It is broken right now.
2. Fix the per item HDF5 reopen plus add `num_workers` and
   `pin_memory` (2.2 and 2.3). This gives an immediate speedup with
   no risk.
3. Fix the normalizer batch size bug (2.4).
4. Set seeds and add `--resume` (3.2 and 3.5). Both make iteration
   faster and more honest.
5. Add a smoke test (2.5) and wire pytest into a single CI workflow
   (5.3).
6. Add SFNO support in `model.py` and the data stats utility
   (section 4 first two bullets).

After that, the project is in a strong shape to focus on actual
modeling work: architecture choice, forcing diversity, and rollout
strategies.

## 7. Closing note

This is a clean, well organized research codebase. The pieces that
need the most attention are the ones a fast moving research project
typically neglects: tests, reproducibility (seeds and resume), and
the small monitor regression introduced by the recent refactor. None
are large; together they would significantly raise the project's
robustness and make every future experiment cheaper to interpret.
