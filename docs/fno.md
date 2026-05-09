# FNO Paper vs Our Setup

Concise reference summarizing the FNO paper (Li et al., 2021) Navier-
Stokes benchmark and contrasting it with our barotropic vorticity
emulator. Focus: explain why their FNO converges to <1 percent error
while ours plateaus at ~65 percent.

## Their problem

- 2D Navier-Stokes, vorticity form, on the unit torus [0,1]^2.
- Periodic boundary conditions in BOTH dimensions.
- Resolution 64 x 64.
- Viscosities tested: nu = 1e-3 (smooth), 1e-4 (turbulent), 1e-5 (more turbulent).
- Forcing: a single FIXED deterministic field
  f(x) = 0.1 * (sin(2*pi*(x1+x2)) + cos(2*pi*(x1+x2))).
- Initial condition only: w0 ~ N(0, 7^1.5 * (-Laplacian + 49I)^-2.5).
  Different per simulation; this is the only randomness.
- Reference solver: pseudospectral at 256 x 256, downsampled to 64 x 64.

## Their data

- N = 1000 training instances, 200 test.
- Each instance is one full trajectory: w(t=0), w(t=1), ..., w(t=T).
  - T = 50 for nu = 1e-3.
  - T = 30 for nu = 1e-4.
  - T = 20 for nu = 1e-5.
- Mapping learned: w|[0..10] -> w|(10..T].
- FNO-2D variant converts each trajectory to many (10-step input, 1-step output) pairs.

## Their training

- Optimizer: Adam.
- LR: 1e-3 initial, halved every 100 epochs (StepLR-like).
- 500 epochs.
- Loss: relative L2.
- Inside FNO blocks: ReLU activation, batch normalization.
- 4 Fourier layers, kmax_j = 12 modes per dim, dv = 32 hidden channels.
- No weight decay, no dropout, no early stopping mentioned.
- Resolution fixed across train/eval.

## Their results

| nu   | T  | N      | FNO-3D rel L2 | FNO-2D rel L2 |
|------|----|--------|---------------|---------------|
| 1e-3 | 50 | 1000   | 0.0086        | 0.0128        |
| 1e-4 | 30 | 1000   | 0.1918        | 0.1559        |
| 1e-4 | 30 | 10000  | 0.0820        | 0.0834        |
| 1e-5 | 20 | 1000   | 0.1893        | 0.1556        |

Notes:
- nu = 1e-3 (smooth) is essentially solved.
- nu = 1e-4 with N = 1000 lands at ~19 percent, the same ballpark as
  our 65 percent. Going from N = 1000 to N = 10000 cut error 2.3x.
- The truly hard turbulent regime (nu = 1e-5) stays at ~19 percent
  even for FNO with their full setup.

## Differences from our setup, ranked by impact

### 1. Forcing: deterministic vs stochastic

- Theirs: one fixed sinusoidal f(x). Same forcing for every sim, no
  time evolution.
- Ours: Vallis stochastic stirring with decay_time = 2 days. Random
  vorticity tendency, evolves stochastically each step, different
  realization per sim.

Consequence: their map is deterministic. Same input always yields
same output. Their FNO can in principle drive loss to zero. Our map
is stochastic. The unobserved stirring during the prediction window
sets an irreducible variance the model cannot explain.

This single difference explains most of our gap.

### 2. Domain: torus vs sphere

- Theirs: [0,1]^2 with periodic boundary in BOTH dimensions. FNO's
  torus assumption is exact.
- Ours: lat-lon on the sphere. Longitude is periodic; latitude is
  NOT (poles are singular). FNO's torus assumption is wrong on the
  latitude axis. SFNO is the architectural fix.

### 3. Output shape: trajectory vs single step

- Theirs (FNO-3D): predict a 40-step volume w|(10..T] from a 10-step
  input. Per-sample supervision is rich.
- Theirs (FNO-2D): trained 1-step but on hundreds of pairs per
  trajectory.
- Ours: 1-step prediction from a 5-step input window, 8 pairs per sim.

Multi-step output supervision regularizes the operator. The model
must produce a consistent trajectory, not just a consistent next
state.

### 4. Resolution

- 64 x 64 = ~4k pixels (theirs).
- 128 x 256 = ~33k pixels (ours).

We have ~8x more spatial degrees of freedom. More expressive operator
needed; per-sample loss is dominated by more spatial detail.

### 5. Training hyperparameters

| field          | FNO paper           | Ours                            |
|----------------|---------------------|---------------------------------|
| optimizer      | Adam                | AdamW                           |
| LR start       | 1e-3                | 1e-3                            |
| LR schedule    | halve every 100 ep  | cosine to 0 over 300 ep         |
| epochs         | 500                 | 300                             |
| weight_decay   | 0                   | 1e-3                            |
| dropout        | 0                   | 0.1                             |
| early stop     | none mentioned      | patience = 30 on val            |
| loss           | relative L2         | lat-weighted relative L2        |
| normalization  | not specified       | per-channel UnitGaussian        |
| n_modes        | (12, 12)            | (32, 64)                        |
| hidden_channels| 32                  | 64                              |
| n_layers       | 4                   | 4                               |
| activation     | ReLU                | GELU (neuraloperator default)   |
| in-block norm  | BatchNorm           | none                            |

Their lack of regularization is fine because their forcing is fixed,
so 1000 trajectories are 1000 i.i.d. examples of a well-defined map.
Our regularization is partially compensating for irreducible variance
from stochastic forcing, which it cannot actually fix.

## Should we try fixed forcing in Isca?

Yes, as a diagnostic. The goal is to verify the pipeline before
debugging the harder stochastic problem.

Expected result of a fixed-forcing run:
- If best val drops to <0.1 (FNO-paper territory), our pipeline is
  fine and the 0.65 ceiling on real data is irreducible noise.
- If best val stays high, something else is broken (inductive bias,
  loss, normalization, splits).

How to do it in Isca, easiest first:

1. Set `decay_time` to a huge number (e.g. 1e15) in `stirring_nml`.
   The stirring tendency becomes effectively constant in time within a
   simulation. Random pattern across sims, frozen in time per sim.
   Closest to the FNO paper without code changes.
2. Disable stirring entirely. If `barotropic_dynamics_nml` exposes a
   `do_stirring` switch, set it false. Run decaying turbulence from a
   random initial vorticity field.
3. Replace `stirring_nml` with a deterministic spatial forcing read
   from a file. Requires Isca source modification.

Recommendation: option 1. Smallest change, closest analogue to FNO paper.

## Concrete options for us

### A. Pipeline validation with frozen-in-time forcing
- Re-run sims with `stirring_nml.decay_time = 1e15` (or equivalent).
- Re-preprocess and retrain unchanged.
- Quick gate on whether the pipeline is correct.

### B. Smaller dt
- Re-preprocess from `atmos_4xdaily` (6 hour cadence).
- More of the prediction-window stirring is captured by the input
  snapshot, so the irreducible floor drops.

### C. Include future stirring in the input
- Add stirring(t+1) (and t+2) as input channels.
- Map becomes deterministic given inputs.
- Useful as a diagnostic: if val still ceilings, the bottleneck is
  architectural, not stochastic.

### D. Probabilistic outputs
- Predict mean + std (or an ensemble) for vor(t+1).
- Train with CRPS or Gaussian NLL.
- Honest treatment of the unobserved variance. Used by GenCast, ACE2.

### E. SFNO swap
- Drop-in replacement for FNO that respects spherical geometry.
- Independent of A-D; can stack.
- See docs/next-steps.md.

### F. Multi-step output supervision
- Match FNO-3D's design: predict a few-day volume from a 5-day input.
- Stronger per-sample signal, more regularization on trajectory
  consistency.

## Simplifications worth trying (closer to the paper)

- Drop `weight_decay` and `dropout` for one run. If train loss stays
  bounded and val is unchanged, the regularization was cosmetic.
- Try Adam (not AdamW). Differs only when weight_decay is set.
- Try step LR (halve every 100 epochs) instead of cosine, matching the
  paper.

## Take-away

The FNO paper's headline numbers (<1 percent on smooth NS, ~19 percent
on turbulent NS at N = 1000) are not directly comparable to our 65
percent because they ran a strictly easier problem: deterministic
forcing on a torus. Their FNO would also plateau on our problem.

Single most informative cheap experiment: run option A (frozen-in-
time forcing). It tells us whether our pipeline can reach FNO-paper
quality at all. Until that gate is passed, scaling capacity, data, or
input lag is unlikely to break the ceiling.
