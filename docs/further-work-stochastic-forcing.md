# Further work: stochastic forcing

A research-oriented summary of what the literature says (or implies)
about deterministic neural operators on systems with stochastic
forcing, framed against our barotropic-vorticity-with-Vallis-stirring
setup. Not a task spec; this is for understanding.

## The problem in one line

Our map `(vor_history, stirring_history) -> vor(t+1)` is not a
function. Different realizations of the unobserved future stirring
during `(t, t+1)` can produce different `vor(t+1)` from the same
input. A deterministic point-predictor (which is what a vanilla FNO
is) cannot represent this consistently and will tend to average
across the possible outputs. That averaging shows up as our 0.65 val
ceiling.

## What our papers say

### Original FNO paper (Li et al., 2021)

Does not address stochastic forcing. All three benchmarks (Burgers,
Darcy, Navier-Stokes) use fixed deterministic forcings; randomness
across simulations comes only from initial conditions or coefficient
fields. The paper neither discusses the well-posedness assumption
explicitly nor offers a path for stochastically-forced operators.

### Practical FNO guide (Duruisseaux, Kossaifi, Anandkumar, 2026)

This one IS explicit. Two relevant passages:

- Section 2.3.1, well-posedness:
  > "For operator learning to be mathematically meaningful, the target
  > mapping must be well-posed in the following sense: each admissible
  > input function f must correspond to a unique output g. If the
  > mapping is not unique [...] a deterministic neural operator cannot
  > represent it consistently. In such cases, the model tends to
  > average across possible outputs, which often leads to blurred or
  > unstable predictions and poor generalization. When non-uniqueness
  > is inherent to the problem, alternative probabilistic formulations
  > or ensemble-based neural operators are required."

  Translation for us: our problem is fundamentally not well-posed for
  a deterministic FNO, and the practical guide says so plainly.

- Section 5.5, UQNO (Uncertainty-Quantified Neural Operator,
  Mahmood et al.):
  Train a residual operator E(a)(x) that predicts the per-pixel
  expected error magnitude of the base operator, then conformally
  calibrate a single scalar so the resulting bands cover the truth at
  a chosen rate. Heteroscedastic, distribution-free, finite-sample
  guarantees. Implementation already exists in NeuralOperator 2.0.0
  as `UQNO`. This is the paper's recommended path for our regime.

## Theoretical framing

The relevant background is classical predictability theory and
stochastic dynamical systems, not new ML literature.

- Lorenz 1963 ("Deterministic Nonperiodic Flow") and Lorenz 1969
  ("The predictability of a flow which possesses many scales of
  motion") established that even fully deterministic chaotic flows
  have a predictability horizon, and that statistical forecasts
  (distributions) are often the only meaningful objects beyond it.
  Our case adds stochastic forcing on top of chaos, which makes the
  deterministic-prediction problem strictly harder.
- Conditional variance Var[Y | X] is the loss floor for any
  point-predictor. If X does not determine Y, no model class can drive
  point-prediction loss below this floor. The only ways to lower the
  floor are to enrich X (so it determines more of Y) or to abandon
  point prediction.
- Palmer (2019), "Stochastic weather and climate models" review,
  argues that operational forecasting moved to ensembles in the 1990s
  for exactly this reason; deterministic forecasts of a stochastic
  system stop being honest beyond the predictability window.

## Solution categories

Three structural families. Each is a different answer to "what
exactly does the model output?".

### A. Reformulate the operator so it becomes well-posed

Make X determine Y by enriching the input or by defining a less
stochastic target.

- **Include the unobserved drivers in the input.** For us: feed
  stirring during the prediction window itself (`stirring(t+1)`,
  ideally the full integral). Useful as a diagnostic; only practical
  as a forecast if you already have a stirring model.
- **Predict a time-averaged or coarse-grained target.** Daily mean
  vorticity over a long window has lower variance from sub-window
  stochastic forcing. The LES / model reduction philosophy: predict
  what's predictable, project out what isn't.
- **Predict statistical moments or invariants.** Climate-mean fields,
  energy spectra, enstrophy decay rates, attractor geometry. These
  are deterministic functions of the input distribution even when
  individual trajectories are not.
- **Predict residuals against a known deterministic baseline.**
  Persistence + correction, or linear-physics + correction. The
  correction is smaller in magnitude and may have a smaller
  unobserved-variance fraction.

Tradeoff: this changes the science question. Scientifically valuable
in different ways but no longer "predict tomorrow's vorticity".

### B. Probabilistic / generative models

Output a conditional distribution `p(Y | X)` instead of a point
estimate. The model itself does not become more powerful at single-
trajectory prediction; it becomes honest about what is and isn't
determined.

- **UQNO** (Mahmood et al., per the practical guide). Lightweight:
  base operator + residual operator + conformal scalar. Gives
  calibrated uncertainty bands per pixel.
- **Conditional generative models on function space**: conditional
  GANs, normalizing flows, conditional diffusion / score-based models.
  GenCast (Price et al., DeepMind, 2024) does this for global weather
  forecasting at production scale and reports skill exceeding ECMWF's
  ensemble system. Architecture is a graph-based diffusion model
  conditioned on the previous state.
- **ACE / ACE2** (Watt-Meyer et al., Allen Institute, 2023-2024): an
  autoregressive transformer-based climate emulator that injects
  noise during training and at inference, producing physically-
  reasonable ensemble trajectories without explicit diffusion.
- **Mixture density networks / quantile regression**: predict the
  parameters of a parametric output distribution, or a finite set of
  quantiles. Cheaper than full generative modeling. Common in the
  hydrology / streamflow forecasting literature.
- **Latent stochastic neural operators**: VAE-style or flow-style
  posterior over a latent variable that explains the unobserved
  variance. A growing but less consolidated literature.

Tradeoff: requires probabilistic evaluation (CRPS, rank histograms,
ensemble spread/skill) instead of single-number relative L2. More
code, more compute, different stories told.

### C. Stability-and-realism patches to deterministic models

These do not solve the well-posedness problem but make a deterministic
model less wrong in practice.

- **Noise injection during training** (well-known in the seq2seq
  literature; used by ACE in time): perturb inputs slightly so the
  model is robust to imperfect autoregressive inputs at inference.
  Typically improves rollout stability, not single-step skill.
- **Pushforward training** (Brandstetter et al., 2022, "Message
  Passing Neural PDE Solvers"). Train on multi-step rollouts where
  gradient flows only through the last step. Aligns training with
  inference distribution. Reduces compounding error.
- **Ensemble of independent deterministic models.** Train the same
  architecture multiple times with different seeds; average at
  inference. Cheap proxy for a probabilistic model. The variance of
  the ensemble proxies the conditional variance.
- **Spectral / energy-conserving losses**. Penalize divergence from
  expected statistical invariants of the system. Does not fix the
  pointwise floor but stabilizes long rollouts.

## Adjacent literature worth knowing

Production-scale neural weather emulators that have wrestled with the
same issue:

- Pangu-Weather (Bi et al., Nature 2023): hierarchical transformer.
  Deterministic; explicitly notes ensemble fanning to address
  predictability beyond ~5 days.
- GraphCast (Lam et al., Science 2023): graph network. Deterministic
  but the team emphasizes ensembling for long horizons.
- FourCastNet (Pathak et al., 2022) and FourCastNet-v2 with SFNO
  (Bonev et al., 2023): SFNO is the closest architecture to ours;
  same forcing-stochasticity issue applies.
- GenCast (Price et al., DeepMind 2024): explicit diffusion-based
  probabilistic forecasting. Considered the current state of the art
  for medium-range global ensembles.
- AIFS (ECMWF, 2024): operational AI forecasting system; includes
  stochastic perturbation following IFS conventions.
- ClimaX (Nguyen et al., 2023): foundation-model framing for climate;
  deterministic, plus discussion of the limitations.
- FengWu (Chen et al., 2023): focused on extending lead time;
  acknowledges the conditional-variance ceiling.

There is also a growing body of work on operator learning for
stochastic PDEs specifically (the SPDE-as-operator framing) and on
neural SDEs (Liu et al.; Tzen and Raginsky), but it is less mature
than the production-scale weather literature and has not yet
consolidated around a canonical method.

## Is the problem solvable?

Two answers, both true:

- **For deterministic point prediction with the current input
  definition: no.** The conditional variance of `vor(t+1)` given our
  input set is a hard lower bound. No FNO / SFNO / Transformer
  variant tuned harder will go below it. The practical guide
  (Section 2.3.1) states this explicitly.
- **For the broader scientific question of "predict what is
  predictable about vor(t+1)": yes, multiple ways.** Reformulate the
  operator (Category A), output a distribution (Category B), or
  patch a deterministic model with stability tools (Category C).

The choice is mostly about what science question you're trying to
answer.

## Is this a good direction for our project?

Yes, with realism.

For:
- It is the live frontier of the field. GenCast, ACE2, AIFS are 2023-
  2024 work. The conceptual ground is fresh enough that contributing
  is feasible.
- The practical guide is unambiguous about the path: probabilistic
  formulations or ensemble methods. UQNO is implemented in the same
  library we already use.
- The barotropic system is small and tractable enough to iterate on
  faster than the global-weather setting.

Against:
- Different model class (probabilistic), different training pipeline
  (CRPS / NLL / ensemble loss), different evaluation suite (rank
  histograms, spread/skill, calibration). Real engineering cost.
- More compute. Diffusion-style generative models train slower than
  deterministic FNOs by 2x to 10x typically.
- The deterministic baseline is a useful object on its own
  (mean prediction, fast inference, simple debugging). Worth getting
  right first; the probabilistic version sits on top of it.

A reasonable order:

- Confirm the deterministic ceiling is real with the fixed-forcing
  diagnostic (`pending-tasks/bve-without-stirring.md`).
- Land the architecture decoupling and try SFNO (`pending-tasks/architecture-decoupling-sfno.md`),
  which addresses the spherical inductive bias gap and may move the
  ceiling somewhat without needing a new model class.
- Once the deterministic ceiling is well characterized, the natural
  next step is UQNO on top of the trained operator. It is the
  cheapest probabilistic intervention available: same backbone plus
  a residual operator plus a conformal calibration step.
- After UQNO, the bigger move is a conditional generative model
  (diffusion-based, GenCast-style). This is real work but it is the
  research-frontier-aligned direction.

## Open questions worth investigating

- What fraction of our 0.65 ceiling is actually conditional variance
  vs. inductive-bias mismatch (FNO on sphere)? The frozen-stirring
  diagnostic plus the SFNO swap together isolate this.
- For our specific stirring (Vallis, decay 2 days), what is the
  maximum-likelihood-deterministic-prediction relative L2 floor?
  Could be estimated empirically by training on a very large dataset
  and measuring where loss saturates.
- Does daily averaging of the target (predict mean over `[t, t+1]`
  instead of an instantaneous `vor(t+1)`) materially lower the floor?
  Cheap to test by changing the preprocessing target.
- Does conditional diffusion (a la GenCast) on this small barotropic
  system meaningfully outperform a UQNO + deterministic FNO combo?
  Unknown for our regime; would be informative.

## References (selected)

- Li, Z. et al. (2021). "Fourier Neural Operator for Parametric
  Partial Differential Equations." ICLR. (`output/fno.pdf`)
- Duruisseaux, V., Kossaifi, J., Anandkumar, A. (2026). "Fourier
  Neural Operators Explained: A Practical Perspective."
  (`output/fno-practical.pdf`)
- Lorenz, E. N. (1963). "Deterministic Nonperiodic Flow." J. Atmos. Sci.
- Lorenz, E. N. (1969). "The predictability of a flow which possesses
  many scales of motion." Tellus.
- Palmer, T. N. (2019). "Stochastic weather and climate models."
  Nature Reviews Physics.
- Brandstetter, J. et al. (2022). "Message Passing Neural PDE
  Solvers." ICLR.
- Bi, K. et al. (2023). "Accurate medium-range global weather
  forecasting with 3D neural networks" (Pangu-Weather). Nature.
- Lam, R. et al. (2023). "GraphCast: Learning skillful medium-range
  global weather forecasting." Science.
- Pathak, J. et al. (2022). "FourCastNet: A Global Data-driven
  High-resolution Weather Model using Adaptive Fourier Neural
  Operators."
- Bonev, B. et al. (2023). "Spherical Fourier Neural Operators:
  Learning Stable Dynamics on the Sphere."
- Price, I. et al. (2024). "GenCast: Diffusion-based ensemble
  forecasting for medium-range weather." DeepMind.
- Watt-Meyer, O. et al. (2023, 2024). "ACE / ACE2: Stable, accurate
  climate emulation with reduced model order."
- Nguyen, T. et al. (2023). "ClimaX: A foundation model for weather
  and climate."
- Mahmood, R. et al. UQNO. Cited in the practical FNO guide as [87];
  exact title and venue not specified in the guide we have.

Some entries above are cited from memory; their availability and
exact titles should be confirmed before citing in a written paper.
