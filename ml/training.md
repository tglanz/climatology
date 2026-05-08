# Training

This document is a procedural reference for the training pipeline of the
FNO emulator of the Isca barotropic vorticity equation. It covers the
problem statement, the data flow, the configurable knobs, the failure
modes (over and underfitting) with their typical remedies, and the
utilities exposed by `ml util` for inspecting models and runs.

## 1. Problem

Given vorticity $\omega_t$ and stirring forcing $F_t$ at time $t$,
predict $\omega_{t+1}$:

$$x_i = (\omega_e(t),\ F_e(t)), \qquad y_i = \omega_e(t+1)$$

Experiments are split 80/10/10 by simulation (not by sample) so that no
simulation appears in more than one split. The default split assignment
in `IscaDataPreprocessor` puts the lowest numbered simulations in the
test split, so simulation 0 is always held out.

## 2. Pipeline overview

The end to end pipeline has four stages.

1. **Simulation.** Run Isca to produce one experiment per parameter
   setting under
   `output/<experiment>/simulations/<id>/run<NNNN>/atmos_daily.nc`.
2. **Preprocessing.** Read `vor` and `stirring` fields from the
   simulation netCDF segments, build (input, target) pairs of
   consecutive time snapshots, and write them as three HDF5 splits
   (`train.h5`, `val.h5`, `test.h5`) plus a `splits.json` manifest.
3. **Training.** Fit input and target normalizers on the training
   split, then run gradient based optimization for a fixed number of
   epochs, saving the parameters that achieve the lowest validation
   loss.
4. **Evaluation.** Run autoregressive rollouts against held out
   simulations and compare predicted trajectories to the truth.

Stage three is the focus of this document.

## 3. Data flow during training

For each epoch:

1. Iterate the `train.h5` DataLoader. Each batch produces a tensor pair
   `(x, y)` of shape `(B, C_in, lat, lon)` and `(B, C_out, lat, lon)`.
2. Move the batch to the active device (CUDA, MPS, or CPU, in that
   priority order).
3. Apply the precomputed `UnitGaussianNormalizer` to both `x` and `y`.
   The normalizer subtracts a per channel mean and divides by a per
   channel standard deviation that was fit on the entire training split
   before the first epoch.
4. Forward pass through the model on normalized inputs.
5. Compute the configured loss between the model output and the
   normalized target.
6. Backpropagate, optionally clip gradient norm, then call
   `optimizer.step()`.
7. After the epoch, run the validation loop on the un normalized scale
   (the predictions are inverse transformed before the loss is applied),
   advance the LR scheduler, and persist the checkpoint if the
   validation loss improved.

The asymmetry in step 7 is deliberate: training loss is computed in
normalized space because that is where the gradients are well scaled,
while the reported validation loss is in physical units so it is
comparable across different normalization fits and across runs.

## 4. Configuration

All knobs live in `ml/config.toml`. Validation of the values is
performed at config load time in `ml/src/ml/config.py`. Unknown values
for `loss`, `optimizer`, or `scheduler.kind` raise an assertion error.

### 4.1 Top level training section

```toml
[training]
epochs = 300
target_loss = 0.1                   # early stop monitored loss <= target_loss
batch_size = 64
learning_rate = 1e-3
loss = "lat_weighted_relative_l2"   # mse | relative_l2 | lat_weighted_relative_l2
optimizer = "adam"                  # adam | adamw
weight_decay = 0.0                  # used by adamw
# grad_clip = 1.0                   # max gradient norm; uncomment to enable
```

### 4.2 Scheduler section

The scheduler is configured by selecting a `kind` and providing options
under the matching subsection. Subsections that do not match the active
`kind` are ignored. This keeps each scheduler isolated from the others
and avoids overloading the same field name across different schedulers.

```toml
[training.scheduler]
kind = "cosine"                     # step | cosine | plateau | none

[training.scheduler.step]
step_size = 100
gamma = 0.5

[training.scheduler.cosine]
# t_max defaults to training.epochs when omitted
eta_min = 0.0

[training.scheduler.plateau]
patience = 15
factor = 0.5
threshold = 1e-4
eta_min = 0.0
```

## 5. Loss functions

The loss is selected by `training.loss`.

### 5.1 `mse`

Standard mean squared error. Useful as a sanity check baseline.
Sensitive to the absolute scale of the target field.

### 5.2 `relative_l2`

$$\text{loss} = \frac{1}{N} \sum_{i=1}^{N} \frac{\|\hat{y}_i - y_i\|_2}{\|y_i\|_2}$$

Norms are computed over the spatial dimensions. Scale invariant per
sample, so it behaves well across simulations with different vorticity
amplitudes. Treats every grid cell equally, which over weights the
polar cells on a spherical grid.

### 5.3 `lat_weighted_relative_l2` (default)

Same as `relative_l2`, but each spatial squared term is multiplied by
$\cos(\text{lat})$ area weights normalized so that their mean is 1:

$$w(j) = \cos(\text{lat}_j), \qquad w \leftarrow w / \overline{w}$$

$$\text{loss} = \frac{1}{B C} \sum_{b,c} \frac{\sqrt{\sum_{i,j} w(j)\,(\hat{y} - y)^2}}{\sqrt{\sum_{i,j} w(j)\,y^2}}$$

Latitudes are read once at startup from the first netCDF file
referenced in the train split of `splits.json` (see `load_latitudes`
in `ml/src/ml/isca_dataset.py`). The mean normalization keeps the loss
scale roughly comparable to the unweighted relative L2.

This is the right default for fields on the lat lon grid: errors near
the poles contribute proportionally to the area they cover, not the
number of grid cells they occupy.

### 5.4 Adding a new loss

Add the kind to `VALID_LOSSES` in `config.py`, extend `create_loss_fn`
in `training.py`. If the new loss needs auxiliary tensors (lat weights,
spectral filters, etc.) pass them through the optional argument added
in the same shape as `lat_weights`.

## 6. Optimizers

Selected by `training.optimizer`.

### 6.1 `adam`

Default. Diagonal adaptive moments. Good first choice for most tasks.
`weight_decay` is ignored.

### 6.2 `adamw`

Adam with decoupled weight decay. Use this when you want $L^2$
regularization that does not interact with the adaptive learning rate.
Set `training.weight_decay` to a small positive value, typically
`1e-5` to `1e-4`.

### 6.3 Gradient clipping

Independent of the optimizer choice. Set `training.grad_clip` to a
positive float to clip the global gradient norm to that value before
each `optimizer.step()` call. Useful when training is unstable, in
particular for higher learning rates or longer rollouts.

## 7. Learning rate schedulers

The scheduler kind is selected by `training.scheduler.kind`. The
trainer distinguishes between schedulers that step on epoch boundaries
and those that step on a monitored validation metric.

### 7.1 `none`

Constant learning rate. Useful as a baseline and for short experiments.
No options.

### 7.2 `step`

`torch.optim.lr_scheduler.StepLR`. Multiplies the learning rate by
`gamma` every `step_size` epochs. Simple but blunt: it cuts the LR on
a fixed schedule regardless of whether the loss is still descending.
The previous default of `step_size = 100, gamma = 0.5` was the cause
of the visible plateau in the legacy run, because the LR was halved
while the loss was still actively descending.

Options under `[training.scheduler.step]`:

- `step_size` (int): epochs between LR decays.
- `gamma` (float): multiplicative factor at each step.

### 7.3 `cosine` (default)

`torch.optim.lr_scheduler.CosineAnnealingLR` over `t_max` epochs
(defaults to `training.epochs`). The LR follows a half cosine from the
initial value down to `eta_min`. Smooth, monotone, and has no manual
cliffs. This is the right default when you do not have a specific
reason to prefer another schedule.

Options under `[training.scheduler.cosine]`:

- `t_max` (int, optional): annealing horizon. Defaults to
  `training.epochs`.
- `eta_min` (float): final learning rate.

### 7.4 `plateau`

`torch.optim.lr_scheduler.ReduceLROnPlateau`. The LR is multiplied by
`factor` whenever the validation loss has not improved by more than
`threshold` for `patience` epochs. The trainer feeds the validation
loss into `scheduler.step(val_loss)` automatically. Requires a non
empty validation loader.

Use this when you do not know a priori how long the model will keep
improving and you want the schedule to adapt. In particular, switching
from `step` to `plateau` is a low risk way to address premature LR
decay.

Options under `[training.scheduler.plateau]`:

- `patience` (int): epochs without improvement before the LR is
  reduced.
- `factor` (float): multiplicative factor when triggered.
- `threshold` (float): relative improvement threshold below which a
  step counts as no progress.
- `eta_min` (float): minimum learning rate floor.

### 7.5 Adding a new scheduler

Steps to add a new scheduler `foo`:

1. Add the kind to `VALID_SCHEDULERS` in `config.py`.
2. Add a `FooSchedulerConfig` dataclass with the new options.
3. Add a field `foo: FooSchedulerConfig` to `SchedulerConfig`.
4. Read the subsection in `load(...)` in `config.py`.
5. Extend `build_scheduler` in `training.py` with a branch for the new
   kind. Return the right mode: `epoch` for time based schedulers,
   `plateau` for monitored ones.

## 8. Architecture options

The model factory in `ml/src/ml/model.py` currently builds a stock FNO.
Recommended next steps when moving past underfitting:

- **SFNO** (`neuralop.models.SFNO`). Replaces the 2D FFT with spherical
  harmonic transforms. Correct basis for fields on a sphere, no
  artifacts at the poles. Requires `torch_harmonics`. The model file
  in this repository at
  `submodules/neuraloperator/neuralop/models/sfno.py` is a drop in
  replacement for FNO.
- **TFNO** (Tucker factorized FNO). Fewer parameters for the same
  expressiveness. Worth trying when overfitting persists at fixed
  data size.

## 9. Normalization

`UnitGaussianNormalizer` is fit before the first epoch on the entire
training split (one full pass through `train_loader`). The fit produces
a mean and standard deviation per input channel and per output channel
(reduction over the batch and spatial dims). The fit statistics are
written to `<checkpoint_dir>/normalization.pt` so that inference and
evaluation can apply the exact same transform.

The training loss operates on normalized tensors. The validation loss
operates on inverse transformed predictions and original targets, so
the reported number is in physical units.

## 10. Overfitting and underfitting

A run is healthy when train and validation loss both decrease and stay
within a reasonable gap of each other. Two failure modes show up as
distinct shapes in `epoch-metrics.csv`.

### 10.1 Underfitting

Symptoms: train loss and validation loss both plateau at a high value,
with a small gap between them. The model is not extracting enough
signal from the data.

Common causes and remedies:

- **Model capacity too small.** Increase `model.fno.hidden_channels`,
  `model.fno.n_layers`, or `model.fno.n_modes`. For a dataset of shape
  `(lat, lon) = (128, 256)`, modes below `[32, 64]` discard most of
  the small scale information that drives the dynamics.
- **Insufficient data.** Increase `data.samples_per_experiment`. With
  `samples_per_experiment = 5` and roughly 270 train simulations the
  dataset is around 1350 pairs, which is small for an operator
  learning task.
- **Learning rate too small or scheduler decays too aggressively.**
  Check the `learning_rate` column in `epoch-metrics.csv`. If the LR
  has collapsed while loss was still descending, switch the scheduler
  to `cosine` or `plateau`.
- **Loss is dominated by the wrong scales.** On lat lon grids,
  unweighted relative L2 over weights polar cells. Switch to
  `lat_weighted_relative_l2`.
- **Wrong inductive bias.** Stock FNO assumes a periodic torus, but
  latitude is not periodic. For spherical data, consider switching to
  SFNO.
- **Irreducible floor.** If the prediction problem is partially
  stochastic at the chosen time step (for example, predicting one day
  ahead given an instantaneous stirring snapshot when the relevant
  signal is the time integral of stirring), there is a noise floor
  below which one step training cannot go. Lower the time step in the
  preprocessing source or include a stirring statistic that better
  summarizes the interval.
- **Lack of forcing diversity.** All current simulations may share
  identical stirring parameters; varying amplitude, latitude band, and
  width across simulations improves generalization to unseen forcing
  regimes and makes the operator easier to learn.

### 10.2 Overfitting

Symptoms: train loss continues to decrease while validation loss
flattens or increases. The model is memorizing training pairs.

Common causes and remedies:

- **Model too large for the dataset.** Reduce capacity, or increase
  data with more samples per simulation.
- **Insufficient regularization.** Switch optimizer to `adamw` and
  set a small `weight_decay` (1e-5 to 1e-4).
- **Run length too long.** Pick the checkpoint at the best validation
  epoch, or use the `target_loss` early stopping field.
- **Train and validation distributions differ.** Inspect `data.split`
  and the manifest. Validate that the simulations in each split are
  representative of the full parameter range.

### 10.3 Diagnosing from artifacts

After every run, the following artifacts are written under the
checkpoint directory:

- `epoch-metrics.csv`: one row per epoch with timestamp, elapsed
  seconds, learning rate, training loss, and validation loss.
- `runs.csv`: one row per fit call summarizing best validation loss
  and the epoch at which it occurred.
- `parameters.pt`: model state dict at the best validation epoch.
- `normalization.pt`: input and output normalizer statistics.
- `metrics.h5` (only when `ml train` is invoked with the
  `track-metrics` flag): per epoch spatial error, zonal mean error,
  and zonal power spectra of the error and the target signal.
  Required for spectral diagnostics in the monitor.

## 11. The `ml util` command

`ml util` is a click group of inspection commands that do not modify
any training state. They are meant to be run before or after a
training run. All commands take `-c <config>` and operate on the
resolved `PathsConfig`.

### 11.1 Existing commands

- `ml util model-info -c <config>`. Prints the FNO architecture
  summary, total and trainable parameter counts, and the parameters
  per sample ratio for each split. The ratio is a quick capacity to
  data sanity check: a ratio above one million should be treated as a
  strong underdetermined warning unless the operator structure
  compensates.
- `ml util persistence-score -c <config>`. Computes the validation
  loss for two trivial baselines: the persistence prediction
  $\hat{y} = x_{\text{vor}}$ (copy current vorticity) and the zero
  prediction. Any model that is not doing better than persistence is
  not learning useful dynamics. The command uses the loss function
  specified in the config, so the baselines are directly comparable
  to training and validation loss.

### 11.2 Suggested additions

The following commands are obvious next additions and would each be a
small wrapper around existing code.

- `ml util data-stats -c <config>`. Per channel mean, standard
  deviation, min, max for `x` and `y` across all three splits. Reads
  directly from the HDF5 files. Catches normalization surprises and
  channel mis alignments before training.
- `ml util eval-checkpoint -c <config> [--split val|test]`. Loads
  `parameters.pt` and `normalization.pt`, runs one pass over the
  chosen split, and prints the loss. Useful for ad hoc comparison of
  checkpoints across training directories.
- `ml util lr-range-test -c <config>`. Runs a Smith style LR range
  test on a small number of batches, sweeping the learning rate
  exponentially and recording the loss. The output is a recommended
  LR roughly a factor of three below the value where the loss starts
  to diverge.
- `ml util grad-norms -c <config>`. Reports per parameter group
  gradient norms over a handful of training batches. Detects
  exploding or vanishing gradients before they manifest as NaN.
- `ml util compare-runs <run_dir1> <run_dir2> ...`. Aligns
  `epoch-metrics.csv` files by epoch and prints best validation loss
  and the epoch at which it occurred for each run. A more visual
  alternative is to plot them in `notebooks/`.
- `ml util predictability-floor -c <config>`. Computes the relative
  L2 loss between consecutive snapshots in the validation set,
  broken out by zonal wavenumber. The high wavenumber portion is an
  estimate of the irreducible noise floor at the current time step.
- `ml util config-summary -c <config>`. Pretty prints the resolved
  config, including the default cosine `t_max`, default checkpoint
  paths, and the resolved `experiment_dir`. Avoids surprises from
  precedence rules in `load`.
- `ml util flops -c <config>`. Estimates forward FLOPs per sample for
  the configured architecture. Useful when sweeping `n_modes` and
  `hidden_channels`.

The `cmd/util.py` file is the place to add them. Each command should
follow the same shape: read the config, do read only work, print
results to stdout.

## 12. Verifying changes

After any change to `training.py`, `config.py`, or `config.toml`, run
the following checks:

1. `ml util model-info -c ml/config.toml` should succeed and report
   the intended architecture.
2. `ml util persistence-score -c ml/config.toml` should succeed and
   produce sensible numbers (persistence between zero and two for
   relative L2 family losses).
3. A short training smoke test, for example with `epochs = 2` and
   `samples_per_experiment = 8`, should complete with both train and
   validation loss appearing in `epoch-metrics.csv`.
4. The selected scheduler name should appear in the log line emitted
   by the trainer at startup ("scheduler: <kind> (mode=<mode>)").

## 13. Reproducibility notes

- Random seeds are not currently set in the trainer. Sampling from
  `torch.utils.data.DataLoader` with `shuffle=True` is therefore
  nondeterministic across runs. If reproducibility matters, seed
  `torch`, `numpy`, and Python `random` at the top of
  `cmd/train.py`.
- The `run_id` in `epoch-metrics.csv` and `runs.csv` is a UTC
  timestamp, which is sufficient to disambiguate concurrent or
  successive runs in the same directory.
- The exact set of files used for each split is recorded in
  `splits.json`. Treat this file as the source of truth for which
  simulations were seen during training.
