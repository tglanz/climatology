# BVE without stirring

Pending task: produce a parallel pipeline that runs the barotropic
vorticity equation **without stochastic stirring**, used as a diagnostic
to validate the FNO training pipeline against a deterministic-dynamics
problem.

## Motivation

Our current setup (sim/barotropic_stirring.py) uses Vallis
stochastic stirring with decay_time = 2 days. The mapping
`(vor_history, stirring_history) -> vor(t+1)` is therefore stochastic:
the unobserved future stirring during the prediction window contributes
an irreducible variance the model cannot explain.

Empirically, training plateaus at relative L2 around 0.65 across
multiple architecture and data sweeps, despite:
- 1000 simulations (8x prior count).
- 8 evenly spaced pairs per sim (8x prior count).
- 5-step input lag window.
- Bigger model (hidden_channels=64, n_layers=4).

The FNO paper (Li et al., 2021) reports relative L2 around 0.0086 on
smooth Navier-Stokes and around 0.19 on turbulent NS at N = 1000. The
critical setup difference is that they use **fixed deterministic
forcing**, so their map is deterministic and the operator is well
defined.

We want to confirm that our 0.65 floor really is the stochastic-
forcing irreducibility, and not a pipeline bug or inductive-bias
issue. The cheapest diagnostic is to run the **unforced BVE** on the
same infrastructure and check whether the FNO can drive loss to FNO-
paper-level on it.

## Goal

Run N about 1000 simulations of the BVE without any external forcing,
each starting from a different initial condition, then preprocess and
train using the existing pipeline.

Acceptance criterion for the diagnostic:

- If best val drops below 0.1 (FNO-paper territory): the pipeline is
  validated, and the 0.65 ceiling on the stirring problem is the
  irreducible-stochasticity floor.
- If best val stays high: pipeline has a structural bug. Likely
  candidates: spherical inductive bias (FNO vs SFNO), normalization,
  loss, or splits.

## Scope

- The BVE physics is already supported by Isca. Reference experiment:
  `submodules/isca/exp/test_cases/barotropic_vorticity_equation/barotropic_vor_eq_test.py`.
  No source modifications to Isca should be necessary.
- The randomness must come from the **initial condition**, not the
  forcing. Each sim should be a deterministic forward integration from
  a different random IC.
- Output cadence and segment structure should match the existing setup
  so the same preprocessing and training code paths apply unchanged.

## Differences vs current sim script

Comparing `sim/barotropic_stirring.py` (current) against
`barotropic_vor_eq_test.py` (unforced reference):

| field                               | stirring (current) | unforced (target) |
|-------------------------------------|--------------------|-------------------|
| `stirring_nml`                      | present            | absent            |
| `barotropic_dynamics_nml.damping_order`   | 2 (biharmonic)     | 4 (sharper)       |
| `barotropic_dynamics_nml.damping_coeff`   | 1.157e-4           | 1.0e-4            |
| `barotropic_dynamics_nml.damping_coeff_r` | 1.929e-6           | absent            |
| `barotropic_dynamics_nml.m_0`             | not set            | 4 (initial wave)  |
| `barotropic_dynamics_nml.zeta_0`          | not set            | 8e-5              |
| `barotropic_dynamics_nml.eddy_lat`        | not set            | 45.0              |
| `barotropic_dynamics_nml.eddy_width`      | not set            | 15.0              |
| `barotropic_dynamics_nml.robert_coeff`    | not set            | 0.04              |
| `barotropic_dynamics_nml.spec_tracer`     | not set            | True              |
| `main_nml.dt_atmos`                       | 600                | 1200              |

Source of inter-sim diversity:

- Current setup: random stirring seed.
- Target setup: vary initial-condition parameters across sims. Concrete
  knobs that already exist in `barotropic_dynamics_nml`:
  - `m_0` (zonal wavenumber of the initial perturbation): integer.
  - `zeta_0` (amplitude of the initial perturbation).
  - `eddy_lat` (latitude of the perturbation center).
  - `eddy_width` (meridional width of the perturbation).

## Implementation options (decision still pending)

### Option 1: extend the current script

Modify `sim/barotropic_stirring.py` to support a `--no-stirring`
flag (or rename the script) that:

- Drops the `stirring_nml` block from the namelist.
- Replaces the relevant `barotropic_dynamics_nml` fields with the
  unforced defaults (damping order 4, damping coeff 1e-4, no
  `damping_coeff_r`, the four IC fields).
- Per `--index`, picks a deterministic random IC from a seeded RNG.
- Bumps `dt_atmos` to 1200.
- Keeps the rest of the harness identical: same skip-if-exists logic,
  same output directory layout, same diag table.

Pros: single source of truth, easy to compare runs apples-to-apples.
Cons: branching logic inside one script can get noisy.

### Option 2: new script

Create `sim/barotropic_decaying.py` (or similar) as a sibling.
Lift the harness boilerplate (skip-if-exists, output paths, diag
table, FFT-friendly grid) into a shared module if duplication becomes
significant.

Pros: each script reads top-to-bottom; physics differs cleanly.
Cons: two parallel scripts will drift unless we extract shared code.

The decision can be made when implementing. Both are fine; the choice
depends on how aggressively we want to keep both pipelines alive.

## Sub-tasks

- Pick option 1 vs option 2.
- Implement the new sim script (or branched script).
- Decide IC sampling strategy:
  - Discrete: `m_0` in {3,4,5,6}, `eddy_lat` in {30, 45, 60}, etc.
    Combinatorial coverage of a few hundred sims.
  - Continuous: each IC parameter sampled from a documented range,
    seeded by index.
  - The continuous approach maps better onto FNO-paper's continuous IC
    distribution but is less inspectable.
- Run a small smoke test (5-10 sims) to confirm the integration
  produces sensible vorticity fields (use
  `ml preprocess validate-simulations --analyze` to spot anomalies).
- Generate the full N about 1000 sweep using the existing parallel
  command.
- Re-preprocess with `ml preprocess training-data` (no code changes
  expected here; same `x_vars`, `y_vars`, `lag_steps`).
- Train with the existing config (no architectural changes).
- Compare best val and persistence baseline against the stirring run.
- Record results in a short follow-up note alongside this task.

## Open questions

- Does the unforced BVE produce enough turbulence within 105 days of
  integration to make the operator non-trivial? With damping_order=4
  and no source, energy decays. We may need to start from a more
  energetic IC, or accept that the dynamics is closer to "smooth NS
  at low Re" than to turbulence.
- Should `lag_steps` stay at 5? Without stirring, future evolution is
  fully determined by current state; lag stacking buys nothing in
  principle. But keeping it = 5 makes the comparison cleaner. Likely
  keep at 5 for the diagnostic, then re-evaluate.
- Do the existing splits (10/10/80 by sim index) still make sense? Yes;
  randomness across sims comes from sampled ICs, so splits remain i.i.d.
