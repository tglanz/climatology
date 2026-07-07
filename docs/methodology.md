# Project Methodology

## Problem Statement

Learn a mapping from a short window of vorticity snapshots to the long-run climatological
zonal-mean zonal wind:

    X = [vor(t), ..., vor(t+K-1)]     K = 10 consecutive daily snapshots, shape (10, 128, 256)
    Y = time-mean zonal-mean ucomp     averaged over [t_convergence, end], shape (1, 128)

This is a spatial-to-profile regression, not autoregressive rollout. Given a brief
observation window of the vorticity field, predict what the long-run jet structure will
look like.

## Data Synthesis

### Simulator

Isca barotropic dynamical core, Vallis-style stochastic vorticity stirring, T85 spectral
truncation (128 lat x 256 lon Gaussian grid). Output is daily-averaged snapshots in
`atmos_daily.nc`. Each simulation runs for 150 output segments of 7 days each = 1050
daily snapshots total (~2.9 years).

### Forcing Parameters

The forcing is a localized stochastic stirring band. Fixed across all simulations:

    stirring_amplitude  = 1e-10
    stirring_decay_time = 172800 s  (2 days)
    stirring_widthy     = 12 deg    (meridional half-width)
    stirring_lon0       = 180 deg
    stirring_widthx     = 45 deg    (zonal half-width)
    stirring_B          = 0.4

The swept parameter is `stirring_lat0` -- the central latitude of the forcing band.
9 values are defined in the sweep:

    0, 7.5, 15, 30, 37.5, 45, 60, 67.5, 75 degrees N

### Replicates

Each `stirring_lat0` value has multiple independent replicates (same parameters, different
random stirring seed). Replicate counts for each code:

    307dbd  lat0=0.0    22 replicates
    463ad3  lat0=7.5    21 replicates
    9ebe1a  lat0=15.0   19 replicates
    6cc1bd  lat0=30.0   30 replicates
    1852dc  lat0=37.5   19 replicates
    fc0e25  lat0=45.0   30 replicates
    86f0f4  lat0=60.0   30 replicates
    bdd2a5  lat0=67.5   17 replicates
    ac9f07  lat0=75.0   30 replicates

Total: 218 simulations. Simulations are run long enough (1050 snapshots) that the
climatological profiles converge well and are similar across replicates of the same
parameter set. This was validated after an earlier hypothesis that per-replicate
climatology variance (noise floor) was the training bottleneck; longer runs resolved it.

## Preprocessing

### Spinup and Convergence Detection

Per simulation, before any data is extracted:

1. **Spinup time** (`t_s`): z-score on the global mean enstrophy series
   (`diagnostics/spinup.py`, z_threshold=2.0, stable_time=3, window_size=10). Marks end
   of the initial transient.

2. **Convergence time** (`t_c`): running time-mean zonal-mean of `ucomp` must stay
   within 5% of the long-run reference for 3 consecutive snapshots
   (`diagnostics/convergence.py`, threshold=0.05, hold=3). Marks when the climatological
   average has stabilized.

### Window Selection

Input windows extracted from the post-spinup period (`data/window_selector.py`):

    start_at = "spinup"   t0_min = t_s
    end_at   = "end"      t0_max = M - K - 1
    length   = 10         K = 10 consecutive daily vorticity snapshots
    stride   = 11         non-overlapping (stride = K + 1)
    limit    = 15         cap at 15 windows per simulation

### Climatology Target

Y is computed once per simulation over `[t_c, end]`: time mean then zonal mean of
`ucomp`, shape `(128,)`. All windows from the same simulation share the same Y. The
climatology is entirely determined by the forcing parameters; across replicates it is
essentially the same profile.

### Splits

Splits are assigned by parameter code (all replicates of a given `stirring_lat0` go
entirely to one split). This tests generalization to unseen forcing latitudes.

    train:      60 sims   lat0 = 45 (fc0e25, 30 sims) + lat0 = 75 (ac9f07, 30 sims)
    validation: 29 sims   lat0 = 60 (86f0f4)
    test:       30 sims   lat0 = 30 (6cc1bd)

Val (lat0=60) sits between the two training values -- interpolation. Test (lat0=30) is
outside the training range -- extrapolation.

Only 4 of the 9 parameter values have been preprocessed into the current HDF5 dataset.
The remaining 5 values (lat0 = 0, 7.5, 15, 37.5, 67.5) are not yet in any split.

### Sample Counts

    train:      900 samples  (60 sims x 15 windows)
    validation: 435 samples  (29 sims x 15 windows)
    test:       450 samples  (30 sims x 15 windows)

## Model

SFNO (`neuralop.models.SFNO`) -- spherical harmonic transforms replace the flat 2D FFT,
giving the correct inductive bias for lat-lon grids since latitude is not periodic.

    in_channels     = 10
    out_channels    = 1
    n_modes         = [32, 64]
    hidden_channels = 16
    n_layers        = 2
    total params    = 35,425   (39 params/train sample)

## Training

- Loss: `lat_weighted_relative_l2` -- relative L2 with cosine-latitude area weights.
  Prevents polar grid cells (denser in lat-lon) from dominating the gradient signal.
- Optimizer: AdamW, lr=1e-3, weight_decay=1e-3.
- Regularization: dropout=0.1 on channel MLP.
- Scheduler: cosine annealing, lr -> eta_min=1e-5 over 100 epochs.
- Early stopping: patience=20 epochs on val loss, or val <= 0.1 (target_loss criterion).
- Normalization: per-channel UnitGaussianNormalizer fit on train split. Train loss in
  normalized space; val loss reported in physical units for comparability.

## Baselines (on validation set, lat0=60)

    zero predictor (predict 0 everywhere):      val loss = 1.000
    mean predictor (predict training-set mean):  val loss = 0.653
    persistence:                                 N/A -- target is climatology, not next step

The mean predictor (0.653) is the meaningful lower bound for a trivial model.

## Training Results and Current Problem: Overfitting

Both completed runs show the same pattern -- val loss peaks early then diverges as train
continues to drop:

| run        | best val | @ epoch | train at best epoch | stopped at |
|------------|----------|---------|---------------------|------------|
| training   | 0.458    | 6       | 0.334               | 26         |
| training-1 | 0.446    | 3       | 0.453               | 23         |

The model beats the mean baseline at its best (0.446 vs 0.653). It is unclear whether
this reflects genuine learning of the lat0 to jet structure operator, or whether it is a
proximity artifact: the val set is lat0=60, which sits between the two training values
(45 and 75), so a model that simply memorizes the two training climatologies and outputs
one of them would incidentally be close to the val target. Distinguishing the two
interpretations requires further analysis. By epoch 26 the val loss has risen back to
0.647, near the mean baseline, as the memorized outputs no longer align well with the val
distribution.

