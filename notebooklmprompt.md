You are a domain expert in scientific machine learning for fluid dynamics
and climate emulation, with full access to a whitepaper corpus relevant
to this project (FNO, SFNO, PINO, neural operators, PINNs, FourCastNet,
GraphCast, Pangu, ACE, ClimaX, Fuxi, NeuralGCM, and the broader operator
learning, weather/climate ML, and PDE surrogate literature).

Your task: produce a single self contained markdown reference document
titled "Neural Operator Training: Practitioner Reference". It will serve
as my persistent reference book while I train and tune neural operator
emulators of geophysical fluid models (currently a barotropic vorticity
emulator on a lat/lon Gaussian grid; future targets include shallow
water and primitive equation systems on the sphere).

The document MUST be:

- Self contained: no links required to understand any section.
- Procedural and concrete: prefer tables, decision trees, ranges of
  values, and "if you see X, try Y" rules over abstract prose.
- Cited: every quantitative recommendation, equation, or empirical
  claim cites the originating paper inline as [Author Year] with a
  full reference list at the end (BibTeX style entries are fine).
- Honest about disagreement: when papers disagree (e.g., L2 vs H1
  loss, curriculum vs pushforward, Adam vs AdamW for FNO), say so and
  explain the tradeoffs.
- Faithful: do not invent numbers. If a default is "common practice"
  rather than from a specific paper, label it as such.
- ASCII text only. No emojis. LaTeX for math is fine. Use single
  hyphens, no em dashes, no double dashes outside code blocks.

Cover the following topics. For each, include: definition, why it
matters, how to choose, common pitfalls, and concrete numerical
defaults or ranges with citations.

1. PROBLEM FRAMING
   1.1. Operator learning vs PDE solving vs autoregressive forecasting.
   1.2. Single step vs multi step targets; time step selection; what
        determines an irreducible predictability floor.
   1.3. Input/output design: state variables, forcings, static fields
        (orography, land mask), positional encodings, time of year
        encodings.
   1.4. Train/val/test splitting strategies for chaotic systems
        (split by trajectory, by parameter, by time slice).

2. ARCHITECTURES
   For each: core idea (1 to 2 paragraph derivation), parameter count
   scaling, where it shines, where it fails, default hyperparameters,
   and key citations.
   2.1. FNO and variants (FNO2D, FNO3D, factorized FNO, TFNO).
   2.2. SFNO (spherical FNO) and when to prefer it.
   2.3. PINO (physics informed FNO).
   2.4. PINNs (vanilla and modern variants like SIREN, Fourier features).
   2.5. DeepONet and variants (POD-DeepONet, MIONet).
   2.6. Graph based neural operators (GNO, MeshGraphNet, GraphCast).
   2.7. Transformer based operators (Pangu, ClimaX, Fuxi, AFNO).
   2.8. Diffusion / generative emulators (GenCast, ACE2, residual
        diffusion on top of a deterministic backbone).
   2.9. U-Net and ConvNet baselines (and when they actually win).
   2.10. Neural ODE / latent ODE families.
   Include a comparison table: parameters, FLOPs/sample, suitable
   geometries, native handling of multiple resolutions, ease of
   training.

3. LOSS FUNCTIONS
   3.1. MSE, relative L2, area weighted (cos lat) variants.
   3.2. Spectral and gradient losses (H1, Sobolev, band weighted FFT).
   3.3. Conservation losses (mass, energy, enstrophy) and how to weight
        them.
   3.4. Probabilistic / CRPS / ensemble losses for stochastic systems.
   3.5. PDE residual losses (PINN/PINO style); collocation vs data
        weighting.
   3.6. Multi scale and multi task weighting strategies (uncertainty
        weighting, GradNorm, PCGrad).

4. OPTIMIZERS
   4.1. Adam, AdamW, Lion, Sophia. Practical differences for operator
        learning.
   4.2. Recommended betas, eps, weight decay ranges per architecture.
   4.3. Gradient clipping defaults and when they matter.
   4.4. Mixed precision (fp16 vs bf16) and loss scaling.

5. LEARNING RATE
   5.1. LR finding (Smith range test) procedure.
   5.2. Schedules: constant, step, cosine, cosine warm restarts,
        ReduceLROnPlateau, OneCycle, linear warmup. When each is right.
   5.3. Warmup length heuristics. Effective LR scaling with batch size
        (linear vs square root).

6. BATCHING AND DATA
   6.1. Batch size selection: memory limits, gradient noise,
        generalization.
   6.2. Effective batch size via accumulation.
   6.3. Sampling strategies (uniform, evenly spaced, importance,
        curriculum by Reynolds number / forcing strength).
   6.4. Augmentations safe for spherical/periodic data: rotation,
        mirror, time reversal (case by case), small additive noise.
   6.5. Normalization choices: per channel, per channel per pixel,
        cosine latitude aware, log transforms for positive variables.

7. ROLLOUT AND AUTOREGRESSIVE TRAINING
   7.1. Single step training and its instabilities.
   7.2. Pushforward trick (Brandstetter et al.).
   7.3. Multi step / scheduled rollout / curriculum from 1 step to N.
   7.4. Noise injection during training.
   7.5. Replay buffers and history conditioning.
   7.6. Stability diagnostics (energy drift, spectral blowup at high k,
        Liapunov style growth).

8. OVERFITTING AND UNDERFITTING
   8.1. Diagnostic flowchart from train/val curves.
   8.2. Underfitting remedies: capacity, modes, lr/scheduler, loss
        weighting, inductive bias swap, more data, more parameter
        sweeps.
   8.3. Overfitting remedies: weight decay, dropout, stochastic depth,
        data aug, early stopping, smaller models, ensembling.
   8.4. Distribution shift detection and mitigation.

9. HYPERPARAMETER TUNING
   9.1. What to tune first (priority list, with cost/benefit).
   9.2. Bayesian optimization (Optuna), random search, ASHA, PBT;
        when each is appropriate.
   9.3. Multi fidelity tricks for expensive runs.
   9.4. Reproducibility checklist (seeds, deterministic algorithms,
        environment capture).

10. EVALUATION AND ASSESSMENT
    10.1. Single step metrics: relative L2, RMSE, ACC, latitude
          weighted variants.
    10.2. Rollout metrics: ACC vs lead time, RMSE skill curves, blow
          up time.
    10.3. Spectral metrics: power spectrum decay, spectral bias.
    10.4. Conservation diagnostics: tracked invariants and tolerable
          drifts.
    10.5. Ensemble metrics for stochastic models: spread/skill, rank
          histograms, CRPS.
    10.6. Climatology and statistics: mean state, variance, EOFs,
          extremes, frequency of regime occupancy.
    10.7. Comparing to physical baselines (persistence, climatology,
          linear regression, IFS/ERA5 hindcast).

11. PRACTICAL RECIPES
    Provide three to five named recipes, each a concrete starting
    point: e.g. "FNO baseline for periodic 2D PDEs", "SFNO for global
    lat/lon", "PINO when sparse data and known physics", "Diffusion
    residual on deterministic backbone for skillful ensembles". Each
    recipe lists architecture, optimizer, schedule, batch size, loss,
    and rollout strategy.

12. RED FLAGS AND ANTI PATTERNS
    Things that look fine in a paper but are usually wrong in practice:
    e.g. evaluating only at one lead time, using MSE on un normalized
    fields with mixed scales, ignoring spectrum, training rollouts on
    data with leaked future info, etc.

13. REFERENCE LIST
    Full bibliography with arxiv ids and DOIs where available.

Output a single markdown document. Aim for thoroughness over brevity;
this is a reference book, not a tutorial. Length is not a concern;
clarity and citation density are.
