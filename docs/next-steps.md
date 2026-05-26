# Next steps

Distilled from `output/fno-practical.pdf` (Duruisseaux et al., 2026)
applied to the current state of this project. Ordered by expected impact
and cost.

## Where we are

- 1000 simulations, 5-day input window (lag_steps=5).
- Default config now: 8 evenly-spaced pairs per sim, hidden_channels=64,
  n_layers=4, AdamW with weight_decay=1e-3, dropout=0.1, cosine LR over
  300 epochs, patience=30 on val.
- Previous baseline: best val 0.649 with 1 pair per sim. Persistence
  baseline: 0.94. Reduction-vs-persistence: about 31 percent. Same regime
  whether K=1 or K=5.

## Step 1: small-overfitting diagnostic (do this first)

Section 4.6 of the paper. The cheapest experiment that resolves "is the
model big enough?" before any more full runs.

- Subset the train data to 20-50 pairs.
- Disable patience (or set it to thousands).
- Run with the cosine schedule disabled or very long.
- Goal: drive **train loss to near zero**. We do not care about val.

Outcomes:

- Train loss goes to near zero -> capacity is sufficient. Your val
  ceiling is data/regularization, not model size.
- Train loss plateaus high (e.g. 0.4) -> model is under-capacity for the
  operator at this resolution. Bump `hidden_channels` to 96-128 or
  `n_layers` to 5 before scaling further.

Concrete way to run it without disturbing the canonical config: a
`config-small.toml` override with `samples_per_experiment=...` set such
that train ends up around 30 pairs, `epochs=5000`, and the
`[training.early_stopping.patience]` subsection removed.

## Step 2: try SFNO

Section 6.3.2. Latitude is **not** periodic (poles). Standard FNO assumes
a periodic torus in both directions, so it is fighting the wrong inductive
bias on the lat axis. Spherical harmonics fix this. Pangu, FourCastNet-v2,
GraphCast all moved to SFNO for the same reason.

- `neuralop.models.SFNO` is a near drop-in for FNO.
- Update `model.py` to dispatch on `model.kind`, accept SFNO with the same
  `n_modes`, `hidden_channels`, `n_layers`, `in_channels`, `out_channels`.
- Same training config otherwise. Compare best val to the FNO baseline
  on the same data and splits.

This is the most likely architectural win for your spherical setup.

## Step 3: rebuild the FNO baseline against the new config

Run with the just-updated `ml/config.toml`:

- 8 pairs per sim (was 1).
- `hidden_channels=64`, `n_layers=4`.
- `patience=30` on val.
- 300-epoch budget; expect patience to fire around 60-120 epochs.

Numbers to record for comparison with everything that follows:

- best val loss and the epoch it occurred.
- final train loss at that epoch.
- train/val gap (overfitting indicator).
- run duration.
- persistence baseline reduction (best_val / persistence).

## Step 4: address rollout distribution shift

Section 5.2. Once single-step training is solid, autoregressive rollout
will have a train/inference mismatch: train sees ground-truth inputs,
rollout consumes its own predictions. Compounding errors are the typical
result.

Two complementary mitigations, in order of cost:

- **Noise injection during training.** Add small Gaussian noise to inputs
  during training so the model is robust to the imperfect state it
  feeds itself at inference. Cheap one-line change inside `train_epoch`.
- **Pushforward training.** Train on 2-3 step rollouts where the
  gradient only flows through the last step. Memory cost is manageable
  with detach() between steps. Implement as an optional
  `training.pushforward.unroll_steps` config field.

Skip both until after Step 3 establishes the single-step baseline.

## Step 5: H1 / Sobolev loss term

Section 5.1. Vorticity is oscillatory; matching gradients in addition
to values gives a stronger signal than pure relative L2.

- Add `lat_weighted_h1` as a new loss option.
- Weighted blend: total = relative_l2 + alpha * gradient_l2 with alpha
  small (0.1-0.5) to start.
- Implement gradients via `torch.gradient` on the un-normalized
  prediction and target.

Measure: best val in the relative_l2 metric still drops by a few
percent, and rollouts should look less smoothed at high wavenumbers.

## Step 6: TFNO if overfit persists

Section 6.1. Low-rank tensor decomposition of the spectral weights.
Reduces param count at the same n_modes / hidden_channels, which fights
overfitting structurally rather than via regularization. Drop-in
available as `neuralop.models.TFNO`.

Only consider after Steps 1-3 if the train/val gap is still wide.

## Things deliberately NOT on this list

- Re-tuning n_modes. Currently `[32, 64]` on `[128, 256]` is at N/4 in
  both directions, comfortably below the Nyquist limit and the
  nonlinearity-spread guidance from Section 4.2.
- Increasing batch size. With small-data regime, smaller batches add
  helpful stochasticity per Section 4.1.
- Multi-resolution / iFNO (Section 5.3). Useful for super-resolution
  generalization, but our resolution is fixed for this scope.
- Physics-informed (PINO, Section 5.4). Worth keeping in mind for the
  long term, but our data is plentiful enough that data losses are the
  right primary signal.

## Workflow note

The recurring pattern here is: paper recommends running a cheap
diagnostic before any expensive change. Specifically: small-overfit
study before scaling capacity, persistence-score before declaring a
plateau is irreducible, val-curve shape before adjusting regularization.
Build that into the loop rather than running 8-hour trainings to
diagnose model questions.

## Climatology prediction track

Generalising the pipeline so the target diagnostic can be a climatology
profile (e.g. time-mean zonal-mean of $u$) rather than only a next-step
field. Aims at predicting a statistical climatology from a finite
window of step diagnostics.

- Add a climatology target to preprocessing: per-window time-mean
  zonal-mean of $u$, shape $(C, H)$.
- Add a model head that outputs $(C, H)$ instead of $(C, H, W)$.
- Add a $(B, C, H)$ variant of `lat_weighted_relative_l2`.
- Add a baseline: in-window time-mean zonal-mean of $u$ (no model).
- Add a static-input pathway for forcing parameters (stirring
  amplitude, latitude band, decorrelation time).
- Eval against per-sim reference $D(t_s, M)$ and against the
  ensemble-mean climatology across realizations of the same forcing.
- Sweep $K$; plot model error and baseline error against $K$ to
  characterise the informative regime.
- Notebook with predicted vs reference profile per simulation, against
  the variance envelope from `notebook_2`.
- Decide single-forcing vs multi-forcing scope before the static-input
  pathway is wired.
