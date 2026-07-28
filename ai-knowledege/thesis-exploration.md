# Thesis Exploration: Where Is the CS Novelty?

Status: exploratory synthesis, not a committed thesis framing. Written to give the
instructor conversation a concrete starting point. Claims about "no prior work" are
softened relative to `presentations/executive-summary-20260722/index.md` after a
literature pass below -- there IS adjacent work, which is good news: it means the
gap can be stated precisely instead of asserted by absence of search results.

## 1. What this project currently does (recap)

From `docs/methodology.md` and `ml/src/ml/training/model.py`:

- Input: $K=10$ consecutive daily vorticity snapshots on a lat-lon grid,
  $X \in \mathbb{R}^{10 \times 128 \times 256}$, from a barotropic vorticity equation
  (BVE) with stochastic (Vallis-style) stirring, simulated in Isca.
- Target: $Y = [\bar{u}] \in \mathbb{R}^{128}$, the time-mean zonal-mean zonal wind --
  a long-run statistical invariant of the system, computed over hundreds of snapshots
  ($M \gg K$).
- Model: SFNO (or FNO) produces a full $(128, 256)$ field, then a `ZonalMeanWrapper`
  (`ml/src/ml/training/model.py:9-15`) takes a plain `.mean(dim=-1)` over longitude to
  collapse it to the $(128,)$ profile. This is currently a bolt-on, not a designed head
  -- see section 4.
- Training/eval spans a swept forcing parameter (`stirring_lat0`, and in earlier
  experiments amplitude/width), with splits held out by parameter value to test
  interpolation and extrapolation across the forcing family, not just across
  initial conditions.

The motivating pivot (step-ahead vorticity prediction to climatology prediction) is
documented in `docs/further-work-stochastic-forcing.md` and is mathematically sound:
$\zeta(t) \to \zeta(t+1)$ is provably ill-posed under stochastic forcing (non-unique
target for a given input), while $\{\zeta_i\}_{i=1}^{K} \to [\bar u]$ is a
deterministic functional of the forcing regime (up to a shrinking noise floor as
$M \to \infty$, quantified in `docs/model-evaluation.md` section 2).

## 2. Where this sits in the literature (this is the part that determines the novelty claim)

I searched for direct precedent. There is no exact match, but there are three adjacent
bodies of work, and the thesis needs to be positioned explicitly against all three --
"nobody has done X" is a weak claim on its own; "X is close but differs in Y, which
matters because Z" is a strong one.

### 2a. Neural operators that preserve invariant statistics (closest ML precedent)

Jiang, Kovachki, et al., **"Training neural operators to preserve invariant measures of
chaotic attractors"** (NeurIPS 2023, arXiv:2306.01187). They also start from the
observation that pointwise MSE-trained autoregressive operators degrade the long-run
statistics of a chaotic rollout, and fix it with an Optimal-Transport or contrastive
loss term that pulls the *autoregressive rollout's* long-run statistics toward the
truth's.

**The key structural difference**: their operator is still function-to-function
($\zeta(t) \to \zeta(t+1)$, same type in and out); the invariant statistic enters only
through the *loss*, and is only obtained after rolling the trained operator forward for
many steps. Our operator changes the *output type itself* --
$\{\zeta_i\}_{i=1}^K \to [\bar u]$ directly, single-shot, no rollout, no compounding
autoregressive error. This is a genuinely different design point: "fix the ill-posed
target by correcting the loss on a same-type map" vs. "fix the ill-posed target by
changing the map's codomain to the well-posed quantity." Worth stating this contrast
explicitly in the thesis -- it is a real axis of variation, not just a restatement.

### 2b. Reservoir computing "climate replication" (closest dynamical-systems precedent)

Pathak, Lu, Hunt, Girvan, Ott, **"Using machine learning to replicate chaotic
attractors and calculate Lyapunov exponents from data"** (Chaos, 2017,
arXiv:1710.07313). A reservoir is trained on a long trajectory, then run
*autonomously* (no external input) to generate its own long synthetic trajectory whose
ergodic statistics ("climate") match the true attractor's. This is the origin of the
term "climate replication" in the ML-for-dynamical-systems literature and should be
cited regardless of how the thesis is framed, since a committee member in this space
will ask about it.

**Differences that matter**:
- Their model still generates a full trajectory autonomously and computes statistics
  post hoc; ours regresses directly to the statistic from a *short, non-autonomous*
  input window. We never roll our own model forward.
- Their setup learns one attractor from one long training trajectory of that same
  system. Ours is explicitly parametric: the operator must generalize the statistic
  across a *family* of forcing configurations it has not all been trained on
  (the interpolation/extrapolation splits over `stirring_lat0` etc. in
  `docs/methodology.md`). This "predict the invariant measure of an unseen member of a
  parametric family from a short glimpse of its dynamics" framing is closer to
  amortized / meta-learning over a family of dynamical systems than to single-system
  attractor reconstruction, and I did not find a direct precedent for that combination.

### 2c. Statistical / ergodic learning theory (gives the "why K << M is possible" argument)

- **"Learning Ergodic Dynamical Systems from a Finite Trajectory"** (arXiv:2607.22399)
  and **"Data-Adaptive Learning of Dynamical Systems by Matching Transfer Operators and
  Invariant Measures"** (arXiv:2607.00391) formalize sample-complexity / consistency
  guarantees for estimating invariant measures or one-step transition operators from a
  single finite trajectory of an ergodic process.
- These give a principled way to ask the question the executive summary poses
  informally in section "Currently": *is there a $K \ll M$ such that $K$ snapshots
  carry enough information to identify $[\bar u]$?* That is an empirical statement
  right now (a training curve). The learning-theory literature gives vocabulary to
  make it a formal one: a sample-complexity / identifiability claim about how much of
  the invariant measure a finite window determines, conditioned on the process being
  (geometrically) ergodic. This is a promising place to look for an actual theoretical
  contribution rather than only an empirical one -- see section 3.3.

### 2d. Equivariant operator learning (relevant to the architecture, section 4)

General result across this literature (e.g. work on Lie-symmetry / group-equivariant
PDE surrogates, and group-equivariant regularization for ill-posed inverse problems):
baking a known symmetry into the architecture as a hard constraint, rather than hoping
the network learns it from data, (a) reduces sample complexity, (b) is the standard
justification for why SFNO's spherical-harmonic transform beats flat FNO on the sphere
in the first place -- and the same argument applies one level up, to the zonal-mean
head. See section 4.

## 3. Candidate CS novelty framings, ranked by how defensible they are right now

Framed for a CS committee: the interesting question is not "did you predict climate
correctly" (that's a physics/geoscience claim) but "what does it take, computationally
and architecturally, to learn a statistical functional of a stochastic dynamical
system from short non-autonomous observations, and how does that differ from learning
the dynamics itself." Four candidate framings, from most to least ready to defend
today:

### 3.1 Problem reformulation under ill-posedness (ready now, weakest as sole contribution)

"When the natural operator-learning target is ill-posed due to stochastic forcing,
reformulate the codomain to a deterministic statistical functional of the dynamics,
rather than patching the loss or going probabilistic." This is real, it is what the
project already did, and it is contrasted well against 2a above. But framed alone it
risks reading as "we picked a different, easier target" rather than a methods
contribution. It is a good *motivating section*, not a strong enough thesis claim by
itself. Needs to be paired with 3.2 or 3.3.

### 3.2 Symmetry-informed statistical head for neural operators (concrete, buildable, currently unimplemented)

Right now `ZonalMeanWrapper` (`ml/src/ml/training/model.py:9-15`) is a naive
post-hoc `.mean(dim=-1)` over an $(H, W)$ field the base SFNO already produced. That
throws away exactly the structure that should make this problem easier than generic
function-to-function regression:

- The zonal mean of a field on the sphere is precisely its $m=0$ (zonally-symmetric)
  spherical-harmonic component. SFNO already computes a spherical-harmonic transform
  internally (that's the whole point of using SFNO over FNO here, per
  `docs/methodology.md`). A "designed" head would read off the $m=0$ coefficients
  directly from the spectral representation instead of running an inverse transform to
  physical space and then averaging over longitude -- cheaper, exact rather than
  approximate under discretization, and structurally guaranteed to be invariant to
  longitude rotation of the *input* (a symmetry the true problem actually has: shifting
  the stirring's `stirring_lon0` should not change $[\bar u]$).
- This is a testable, falsifiable claim: does a spectral $m=0$-readout head
  outperform (in relL2, sample efficiency, or generalization across the
  `stirring_lat0` splits) the current spatial-mean head? That is a clean ablation,
  small to implement, and directly buildable on the existing pipeline
  (`ml/src/ml/training/model.py`, `ml/src/ml/data/climatology.py`).
- This is the most CS-legible of the four framings: it is squarely an architecture /
  inductive-bias question (equivariance-by-construction vs. equivariance-by-hope),
  which is a live, well-understood theme in the neural-operator literature (section
  2d), and it produces a number, not just an argument.

**This is my top recommendation for the concrete thing to build next**, precisely
because it is small, falsifiable, and directly answers "what is the CS contribution"
with an artifact (a head architecture + an ablation table) rather than only a
narrative.

### 3.3 Sample complexity / identifiability of $K$ vs $M$ (highest ceiling, most work)

Formalize and empirically characterize: as a function of the ergodic mixing rate of
the stirred BVE (which is tunable via `stirring_decay_time`,
`docs/methodology.md:29`), how does the minimum $K$ needed to identify $[\bar u]$ to
within the noise floor (`docs/model-evaluation.md` section 2) scale? This connects
directly to 2c above (ergodic learning theory) and would let the thesis make a
quantitative claim ("the operator needs $K \gtrsim f(\text{mixing time})$ snapshots"),
not just a qualitative one ("a short window is enough"). This is the highest-ceiling
option intellectually -- it is closest to an actual theorem or a rigorously-designed
experiment sweep -- but it is also the most work and the most likely to require
guidance from the ergodic-theory side, which is arguably physics/math-adjacent rather
than CS. Worth raising with the instructor explicitly: is a sample-complexity result
about a physical system's ergodic properties "CS enough," or does it need to be
generalized/abstracted first (e.g., stated for a class of ergodic stochastic PDEs, with
BVE+stirring as the demonstration case)?

### 3.4 Amortized/meta operator learning across a parametric family of stochastic systems

The interpolation/extrapolation splits over forcing parameters
(`docs/methodology.md` "Splits") are already doing this implicitly: the model must
infer the invariant statistic of a *forcing regime it has only seen a short glimpse
of*, generalizing across a family of stochastic dynamical systems rather than fitting
one. This is close to meta-learning / in-context operator learning framings elsewhere
in the neural-operator literature, but usually applied to forecasting, not to
statistic-of-attractor prediction (that combination is the gap identified in 2b).
Promising as a framing for the existing generalization experiments
(`docs/model-evaluation.md` section 3), but needs the vocabulary tightened (is this
"meta-learning," "conditional operator learning," or something else) before it reads
as a CS contribution rather than an ML-application result.

## 4. Concrete near-term action that de-risks the thesis framing

Regardless of which framing above the instructor prefers, 3.2 (symmetry-informed head)
is cheap to try and produces evidence useful for all four framings:

1. Implement a head that reads the $m=0$ spherical-harmonic mode directly from SFNO's
   internal spectral representation instead of the current spatial mean.
2. Ablate against the current `ZonalMeanWrapper` on the existing train/val/test splits.
3. Report relL2, sample efficiency (does it converge with fewer training windows?),
   and generalization error vs. distance-from-training-config
   (`docs/model-evaluation.md` section 3) for both heads.

This produces a genuine, small, falsifiable CS artifact (an architecture ablation) that
can anchor whichever larger framing (3.1/3.3/3.4) the thesis proposal ultimately
builds around, and is a natural next step after the HPC migration already planned
(`presentations/executive-summary-20260722/index.md`, "Next steps").

## 5. Open questions to bring to the instructor

- Is problem reformulation under ill-posedness (3.1), on its own, judged as CS
  innovation by this committee, or does it need to be paired with an architecture
  (3.2) or theory (3.3) contribution to count?
- Does a sample-complexity argument about one physical system (3.3) need to be
  generalized to a system-agnostic statement to be "CS enough," or is a rigorous
  empirical characterization on this one system sufficient for an MSc thesis?
- Is "meta-learning across a parametric family of stochastic dynamical systems" (3.4)
  the right vocabulary, or is there a more established subfield name for this that a
  committee would recognize faster?

## 6. Sources consulted

- Jiang, R., Kovachki, N., et al., "Training neural operators to preserve invariant
  measures of chaotic attractors," NeurIPS 2023. https://arxiv.org/abs/2306.01187
- Pathak, J., Lu, Z., Hunt, B. R., Girvan, M., Ott, E., "Using machine learning to
  replicate chaotic attractors and calculate Lyapunov exponents from data," Chaos 27,
  121102 (2017). https://arxiv.org/abs/1710.07313
- "Learning Ergodic Dynamical Systems from a Finite Trajectory."
  https://arxiv.org/abs/2607.22399
- "Data-Adaptive Learning of Dynamical Systems by Matching Transfer Operators and
  Invariant Measures." https://arxiv.org/pdf/2607.00391
- Repository-internal: `docs/further-work-stochastic-forcing.md` (already contains a
  strong literature pass on the well-posedness problem and adjacent weather-emulator
  literature -- read in full before writing any related-work section, it overlaps
  heavily with section 2 above and should not be duplicated).
- Repository-internal: `docs/methodology.md`, `docs/model-evaluation.md`,
  `docs/norms.md`, `ml/src/ml/training/model.py`.

Papers already collected locally in `papers/` (fno.pdf, fno-explained.pdf,
spherical-fourier-neural-operators.pdf, no.pdf, no-regularity-spdes.pdf, renanet.pdf,
slt-zonal.pdf, barotropic.pdf, vallis-etal-2024.pdf) were not re-fetched here (git-lfs
is not installed in this environment, so contents are pointer files, not the PDFs
themselves); their titles suggest `no-regularity-spdes.pdf` and `slt-zonal.pdf` may be
directly relevant to sections 2c/3.3 and should be read before finalizing that framing.
