# Diagnostics module extraction

Pending task: introduce `ml/src/ml/diagnostics/__init__.py` as the
single home for all "semanticful" computations on physical fields
(area-weighted means, errors, spectra, invariants, persistence
baselines), and migrate the existing inline implementations to use it.

## Motivation

Today the same primitives are re-implemented in multiple places, and
in some cases multiple times in the same file. A non-exhaustive list:

### Cosine-latitude area weights

Implemented at least four times:

- `ml/src/ml/training.py:_cosine_lat_weights` (numpy + torch tensor).
- `ml/src/ml/cmd/preprocess.py:mean_enstrophy` (numpy, inlined as
  `w = np.cos(np.deg2rad(lat)); w = w / w.mean()`).
- `ml/notebooks/*.ipynb` `def area_mean(...)` (numpy, several copies).
- `ml/notebooks/*.ipynb` direct inline `np.cos(np.deg2rad(lat))` calls.

### Power spectrum

Re-implemented at least three times:

- `ml/src/ml/common/training_metrics.py:update` (torch:
  `torch.fft.rfft(error, dim=-1).abs().pow(2).sum(dim=(0, 1))`).
- `ml/notebooks/*.ipynb` `def power_spectrum(...)` (numpy).
- `ml/notebooks/*.ipynb` direct `np.fft.rfft(field, axis=1)` calls
  used for filtering / spectrum diagnostics.

### Errors

Inline everywhere, never a single named function:

- `np.abs(VOR_PRED - VOR_TRUE)` (notebooks, several places).
- `np.sqrt(np.mean(vor_err**2))` (`cmd/evaluate.py:79`, also
  notebooks).
- `pred - target` (residual, notebooks).
- `signed_error`, `abs_error`, `residual` as one-off variable names
  in notebooks.

### Other

- Enstrophy: `cmd/preprocess.py:mean_enstrophy` is the only
  implementation, but it inlines the area-weight primitive instead of
  consuming a shared one.
- Persistence baseline: `cmd/util.py:persistence-score` constructs
  the persistence prediction inline (slice the right vor channel from
  the lag-stacked input). Used only there today, but the same logic
  is conceptually a diagnostic.
- Zonal mean / zonal anomaly: `common/training_metrics.py` writes
  `zonal_mean_error = spatial_error.mean(axis=1)` inline; notebooks
  also compute zonal means by hand.

The cost of this duplication is mostly correctness drift (one site
clips at zero, another doesn't; one normalizes to mean 1, another to
sum 1, another not at all) and the maintenance tax of touching
multiple files when a single primitive needs a fix.

## Goal

A flat module at `ml/src/ml/diagnostics/__init__.py` containing all
semantic computations on physical fields. No submodules, no public
API curation. The module is a single file with simple, well-named
functions. Existing call sites migrate to consume it; inline
duplicates are removed.

The module accepts numpy arrays by default. Functions consumed by
the training loss path additionally have a torch-tensor variant when
needed (the loss runs on GPU tensors). Where the math is identical
in both, a single function with type-dispatched implementation is
fine.

## Documentation contract

The module is library code that must read cleanly months from now,
including by people who do not know the project. The following
applies to `diagnostics/__init__.py` only:

- **Module docstring at the top of the file.** Describes the goal of
  the module ("the single home for semantic computations on physical
  fields used elsewhere in the codebase: area-weighted means, error
  metrics, spectra, invariants, baselines"), and states the
  invariants the module guarantees:
  - All functions are pure: a function's output depends only on its
    arguments. No reading from disk, no global state, no caching, no
    side effects.
  - All functions are stateless. No classes with internal state. No
    closures over module-level mutables.
  - Numpy-first; torch variants only where strictly required by a
    consumer.
  - Each function operates on the spatial dimensions implied by its
    arguments and broadcasts cleanly over leading batch / channel
    dims when applicable.

- **Per-function docstring for every function.** Required content:
  - **What it computes.** A one-sentence definition. Not the formula;
    the meaning.
  - **Why it is meaningful.** A one-sentence physical or statistical
    rationale. Why a practitioner would compute this quantity.
  - **Reference link** when the quantity has an established name. Most
    of these are well-known concepts; cite Wikipedia or a canonical
    reference. Cite a specific page, not the encyclopedia root.
  - Argument and return shapes, briefly.
  - **Not** required: how it is implemented, derivation of the
    formula, edge-case handling discussion (those belong in inline
    comments next to the relevant lines).

- **Reference links to include.** Most of the entries below have a
  Wikipedia page. Use these unless a better canonical reference
  exists:

  | function | reference |
  |---|---|
  | `cosine_latitude_weights` | https://en.wikipedia.org/wiki/Spherical_coordinate_system (surface element on the unit sphere is `cos(lat) dlat dlon`) |
  | `area_mean`, `area_l2_norm` | same as above |
  | `zonal_mean`, `zonal_anomaly` | https://en.wikipedia.org/wiki/Zonal_and_meridional_flow |
  | `signed_error`, `absolute_error`, `relative_error` | https://en.wikipedia.org/wiki/Approximation_error |
  | `rms_error` | https://en.wikipedia.org/wiki/Root_mean_square |
  | `relative_l2`, `lat_weighted_relative_l2` | https://en.wikipedia.org/wiki/Lp_space |
  | `zonal_power_spectrum`, `error_power_spectrum`, `signal_power_spectrum` | https://en.wikipedia.org/wiki/Spectral_density |
  | `spectrum_residual` | https://en.wikipedia.org/wiki/Spectral_density (no separate page; explain the distinction from error spectrum in the docstring) |
  | `enstrophy_density`, `mean_enstrophy` | https://en.wikipedia.org/wiki/Enstrophy |
  | `kinetic_energy_density` | https://en.wikipedia.org/wiki/Kinetic_energy |
  | `persistence_prediction` | https://en.wikipedia.org/wiki/Persistence_forecasting |

  When adding a new function later that does not correspond to a
  recognized concept (something genuinely project-specific), the
  docstring should call that out explicitly rather than pointing at
  a loosely-related reference.

## Contents

The module is a flat list of functions. No internal sectioning of
the file is required; just keep related functions adjacent (errors
near errors, spectra near spectra) and let order tell the story.
Use comment headers only if a future reader would otherwise be lost
at a glance. Do not split into submodules.

The list below is grouped only for the readability of this doc, not
as a directive about the source file layout. Argument and return
shapes are described in each function's docstring per the
documentation contract above.

- `cosine_latitude_weights(latitudes_deg, normalize="mean1")`. Returns
  numpy array. `normalize` in {"mean1", "sum1", "none"}.
- `area_mean(field, latitudes_deg, axis=(-2, -1))`. Cos-lat-weighted
  spatial mean over the trailing two dims.
- `area_l2_norm(field, latitudes_deg)`. `sqrt(area_mean(field**2))`.
- `zonal_mean(field, axis=-1)`. Mean over the longitude axis.
- `zonal_anomaly(field, axis=-1)`. `field - zonal_mean(field)`.
- `signed_error(pred, truth)`: `pred - truth`.
- `absolute_error(pred, truth)`: `|pred - truth|`.
- `relative_error(pred, truth, eps=1e-12)`: `|pred - truth| / (|truth| + eps)`.
  Pointwise; not the same as relative L2.
- `rms_error(pred, truth)`: `sqrt(mean((pred - truth)**2))` over all
  spatial dims.
- `relative_l2(pred, truth, eps=1e-12)`: `||pred - truth||_2 / (||truth||_2 + eps)`,
  per sample.
- `lat_weighted_relative_l2(pred, truth, latitudes_deg, eps=1e-12)`:
  same with cosine-latitude area weights.
- `zonal_power_spectrum(field, axis=-1)`. `|rfft(field)|**2` along
  the longitude axis. Returns the per-wavenumber power.
- `error_power_spectrum(pred, truth)`. Power spectrum of
  `pred - truth`. (Currently `error_power` in `training_metrics.py`.)
- `signal_power_spectrum(truth)`. Power spectrum of the target.
  (Currently `signal_power` in `training_metrics.py`.)
- `spectrum_residual(pred, truth)`. Difference of the two power
  spectra: `signal_power_spectrum(pred) - signal_power_spectrum(truth)`.
  Distinct from `error_power_spectrum`; measures whether the model
  reproduces the right energy distribution across scales,
  irrespective of phase.
- `enstrophy_density(vor)`. `0.5 * vor**2` (per-pixel; no reduction).
- `mean_enstrophy(vor, latitudes_deg)`. Area-weighted spatial mean of
  enstrophy density. Currently in `cmd/preprocess.py`.
- `kinetic_energy_density(u, v)`. `0.5 * (u**2 + v**2)`. Optional;
  add when first consumer appears.
- `persistence_prediction(input, vor_channel_index)`. Slice the
  most-recent vor snapshot out of a lag-stacked input. Used by the
  persistence baseline.

A note on error functions: all operate on aligned `(pred, truth)`
arrays and broadcast over batch / channel dims.

## Sweep: where each function would replace inline code

| current site | inline code | replaced by |
|---|---|---|
| `training.py:_cosine_lat_weights` | builds w from cos(deg2rad(lat)), clips, mean-normalizes | `cosine_latitude_weights(...)` |
| `training.py:lat_weighted_relative_l2` | inline cos-weighted sum-of-squares quotient | could call `lat_weighted_relative_l2` directly (loss function = thin wrapper that converts numpy weights to torch once at construction) |
| `cmd/preprocess.py:mean_enstrophy` | inline cos-lat weights + 0.5*vor**2 mean | `mean_enstrophy(vor, lat)` |
| `cmd/util.py:persistence_score` | hand-built channel slice | `persistence_prediction(...)` |
| `cmd/evaluate.py:79` | `np.sqrt(np.mean(vor_err**2))` | `rms_error(...)` |
| `common/training_metrics.py:update` | inline accumulator for L1 spatial map, zonal mean, FFT power | several calls into diagnostics; the class keeps only the per-batch accumulation and h5 write logic |
| notebooks `area_mean` | inline cos-lat weighting | `area_mean(...)` |
| notebooks `power_spectrum` | inline rfft + abs.pow(2) | `zonal_power_spectrum(...)` |
| notebooks `np.abs(VOR_PRED - VOR_TRUE)` | inline | `absolute_error(...)` |
| notebooks `pred - truth` for residual heatmaps | inline | `signed_error(...)` |
| notebooks `np.sqrt(np.mean(...**2))` for RMS | inline | `rms_error(...)` |

## Implementation steps

- Create `ml/src/ml/diagnostics/__init__.py` with all functions
  listed above. Pure functions where possible. Numpy is the default
  backend; functions called from training loss accept a torch tensor
  alternatively.
- Migrate `training.py`:
  - `_cosine_lat_weights` becomes a one-liner that calls
    `diagnostics.cosine_latitude_weights` and converts to torch.
  - `create_loss_fn` for `lat_weighted_relative_l2` becomes a thin
    closure around `diagnostics.lat_weighted_relative_l2` (or stays
    as-is and consumes the diagnostics primitives only at the math
    level; either is fine).
- Migrate `cmd/preprocess.py:mean_enstrophy` to call
  `diagnostics.mean_enstrophy`. Remove the inline cos-lat weight
  computation.
- Migrate `cmd/util.py:persistence_score` to use
  `diagnostics.persistence_prediction` and one of the relative-L2
  functions, instead of constructing the prediction inline.
- Migrate `cmd/evaluate.py` rollout-RMS line to `diagnostics.rms_error`.
- Migrate `common/training_metrics.py:update` to use
  `diagnostics.absolute_error` (or signed, depending on what we
  actually want to track), `diagnostics.zonal_power_spectrum` for
  both error and signal, and `diagnostics.zonal_mean`. The class is
  reduced to per-batch accumulation and h5 I/O.
- Update notebooks to import from the new module instead of
  re-defining `area_mean`, `power_spectrum`, etc. Notebooks that
  have working visualization code stay otherwise unchanged.
- Cross-check all uses of `np.cos(np.deg2rad(lat))` across the repo
  (both `ml/src` and notebooks). None should remain after the
  migration.

## Acceptance criteria

- `grep -rE "np\.cos\(np\.deg2rad" ml/src ml/notebooks` returns no
  hits outside `diagnostics/__init__.py`.
- `grep -rnE "torch\.fft\.rfft|np\.fft\.rfft" ml/src` returns hits
  only inside `diagnostics/__init__.py`.
- `grep -rnE "np\.sqrt\(np\.mean\([^)]*\*\*2" ml/src` returns no
  hits.
- All callers compile and tests / smoke runs still pass:
  - `ml preprocess validate-simulations -c ml/config.toml --analyze`
    produces the same enstrophy values as before.
  - `ml util persistence-score -c ml/config.toml` produces the same
    persistence and zero baselines as before.
  - `ml train -c ml/config.toml` produces an unchanged train/val
    loss curve when run on the same preprocessed data and seed.
  - `ml evaluate autoregression ...` reports the same RMS as before.
- `metrics.h5` contents match (within float rounding) what
  `training_metrics.py` currently writes.
- `diagnostics/__init__.py` has the module-level docstring described
  in the "Documentation contract" section, and every function in the
  file has a docstring explaining what it computes, why it is
  meaningful, and (where applicable) a reference link. No function
  has internal state, reads from disk, or has side effects.

## Open questions / decisions to defer

- **Numpy vs torch dispatch.** Keep simple: numpy primary, torch
  versions where strictly needed (loss path). Do not introduce a
  generic dispatch layer.
- **Function signature for spectrum functions.** Decide once whether
  spectra are returned as 1D (sum over batch and lat) or as full 3D
  (per-batch, per-lat). The current `training_metrics.py` returns
  the summed 1D version; keep that as the default.
- **Where does the latitude grid come from?** Today
  `load_latitudes(cfg)` reads it from the first netCDF in the train
  split. Diagnostics functions accept lat as an argument so they
  remain pure; the caller is responsible for getting it. No change
  here.
- **Persistence baseline signature.** Today the persistence baseline
  is written for the lag-stacked layout and assumes `vor` is in
  `x_vars`. Keep the signature explicit (channel index as a param)
  rather than coupling to config.

## Sub-tasks

- Draft the function list and signatures in
  `diagnostics/__init__.py`. No tests, no I/O.
- Move enstrophy into the module; migrate `cmd/preprocess.py`.
- Move cos-lat weights into the module; migrate `training.py`.
- Move RMS, relative L2, lat-weighted relative L2 into the module;
  migrate `cmd/evaluate.py`.
- Move zonal mean and power spectrum into the module; migrate
  `common/training_metrics.py`.
- Move persistence prediction into the module; migrate
  `cmd/util.py`.
- Update notebooks. Each notebook gets a single
  `from ml.diagnostics import area_mean, power_spectrum, ...`
  cell near the top, and inline definitions are deleted.
- Run the smoke checks from the acceptance criteria.
- Sanity-check that `ml/src/ml/common/training_metrics.py` is now
  small enough that it might warrant renaming to something like
  `metrics_writer.py` (writer of metrics.h5; not actually computing
  metrics anymore). Defer the rename if scope creeps.
