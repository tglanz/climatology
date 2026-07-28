# Thesis Exploration: Where Is the CS Novelty?

Status: updated after a full literature pass (session 2, July 2026). All local papers have
been read. Web research completed. The framing is now substantially sharper than session 1.
Claims in section 3 are more specific; the competitive landscape in section 2 is complete.

## 1. What this project currently does (recap)

From `ml/src/ml/training/model.py` and the training configs under `output/`:

- Input: K=10 consecutive daily vorticity snapshots on a lat-lon grid,
  X in R^{10 x 128 x 256}, from a barotropic vorticity equation (BVE) with
  Vallis-style stochastic stirring, simulated in Isca at T85 resolution.
- Target: Y = [u_bar] in R^{128}, the time-mean zonal-mean zonal wind, a long-run
  statistical invariant of the system computed over hundreds of snapshots (M >> K).
- Model: SFNO (neuralop.models.SFNO) produces a full (128, 256) field, then a
  ZonalMeanWrapper (ml/src/ml/training/model.py:9-15) takes a plain .mean(dim=-1)
  over longitude to collapse it to the (128,) profile.
- The swept parameter is stirring_lat0 (9 values, 0-75 degrees). Splits are held
  out by parameter value. Validation is interpolation (lat0=60), test is extrapolation
  (lat0=30).

The motivating pivot from step-ahead vorticity prediction to climatology prediction is
mathematically sound: the map zeta(t) -> zeta(t+1) is provably ill-posed under stochastic
forcing (non-unique target for a given input), while {zeta_i}_{i=1}^K -> [u_bar] is a
deterministic functional of the forcing regime (up to a noise floor as M -> inf, quantified
in docs/model-evaluation.md section 2).

Physical grounding for the target: Vallis et al. 2004 (papers/vallis-etal-2024.pdf)
provides the theoretical prediction that stochastic stirring at latitude theta_0
produces a time-mean eastward jet slightly poleward of theta_0, flanked by westward
flow. This establishes [u_bar] as a physically meaningful, theoretically predictable
quantity -- not just a convenient regression target.


## 2. Where this sits in the literature

Session 2 completed a full read of all papers in papers/ and a web research pass. The
competitive landscape is now substantially larger than session 1 found. It has four
groups, ordered by relevance.

### 2a. The Shokar group -- closest work, same physical system

Three papers from Cambridge (Shokar, Kerswell, Haynes) on stochastically forced
beta-plane turbulence, which is the same physical system as the BVE used here:

**Shokar et al. (JAMES 2024), "Stochastic Latent Transformer: Efficient Modeling of
Stochastically Forced Zonal Jets"** (papers/slt-zonal.pdf).
Architecture: translation-equivariant 1D convolution autoencoder (TEPC) + stochastic
transformer with injected noise token. Target: the evolution of U(y,t), the
zonally-averaged mean flow, autoregressively. Loss: CRPS. Training: 2e6 unit time
intervals at fixed parameters (beta=90, mu=4e-2). Result: 2.13e5x speedup over DNS.
Reproduces PDFs of U, dU/dy, dU/dt over 200,000 time units. Successfully captures
transition event probabilities (coalescence, nucleation) at 10^6-member ensemble scale.
Key limitation stated explicitly in the paper (page 16): "Since the neural network is
trained in a specific parameter regime, this implemented transfer learning to enable
the model's adaptation to alternative regimes with reduced additional training
requirements." Their solution to parametric generalization was fine-tuning, not
zero-shot inference.

**Shokar, Haynes, Kerswell (ICLR 2024 workshop, AI4DiffEq),** "Extending Deep Learning
Emulation Across Parameter Regimes to Assess Stochastically Driven Spontaneous
Transition Events." OpenReview: https://openreview.net/forum?id=7a5gUX4e5q
Extends SLT to unseen beta values using explicit parameter conditioning. Recovers
coalescence and nucleation statistics at OOD beta values. Their conditioning mechanism
requires knowing beta at test time.

**Shokar, Kerswell, Haynes (arXiv:2509.09599, 2025).** Full conditioning paper.
Method: FiLM-style conditioning (adaptive layer norm scale/shift from beta). Local
attention windows for O(D*K) cost. VAE for probabilistic latent space. Fine-tuning at
a new beta requires ~1,000 snapshots. Transition PDFs match DNS at beta=1.35.

**Structural difference from this project (the primary competitive contrast):**
All three Shokar papers require the forcing parameter (beta, or by analogy stirring_lat0)
to be provided explicitly at test time. This project's model receives no such information
-- it must infer the forcing regime from the K=10 vorticity snapshots alone. Additionally,
all Shokar models produce an autoregressive emulator of the dynamics; to extract a
climatological statistic they require rollout over thousands of steps and post-hoc
averaging. This project predicts [u_bar] directly, single-shot, without rollout.
A further structural difference: the Shokar models train on 2e6 trajectory steps vs.
900 training samples here -- a sample complexity gap of more than 2,000x.

### 2b. Neural operators preserving invariant statistics (Jiang et al.)

Jiang, Kovachki et al., "Training neural operators to preserve invariant measures of
chaotic attractors" (NeurIPS 2023, arXiv:2306.01187). Same motivating observation
(pointwise MSE-trained autoregressive operators degrade long-run statistics), fixed via
an OT/contrastive loss on the rollout's statistics. Their operator is still same-type
(zeta(t) -> zeta(t+1)); the invariant statistic enters only through the loss and is
extracted after many autoregressive steps.

**Structural difference:** They fix the ill-posed target by patching the loss on a
same-type map. This project changes the map's codomain to the well-posed quantity
directly. This is a real architectural distinction, not just a restatement.

### 2c. Reservoir computing climate replication (Pathak et al.)

Pathak, Lu, Hunt, Girvan, Ott, "Using machine learning to replicate chaotic attractors
and calculate Lyapunov exponents from data" (Chaos 2017, arXiv:1710.07313). A reservoir
trained on a long trajectory runs autonomously to generate synthetic trajectories whose
ergodic statistics match the attractor. Origin of "climate replication" as a term.

**Differences:** Single system (no parametric family), requires autonomous long rollout,
and the ergodic statistics are a post-hoc result rather than the direct target.

### 2d. Neural operators for SPDEs (NORS)

Hu et al., "Neural Operator with Regularity Structure for Modeling Dynamics Driven by
SPDEs" (ICLR 2022 workshop, arXiv:2204.06255, papers/no-regularity-spdes.pdf).
Incorporates "model feature vectors" derived from the linear semigroup of the SPDE
(Chevyrev et al. 2021's regularity structure theory) as preprocessing before the FNO.
These features have better regularity than raw SPDE inputs, reducing error by ~10x over
FNO on stochastic Navier-Stokes and Phi^4_3. Requires knowing the explicit linear
differential operator L, which is available for the BVE.

**Relevance:** Confirms that standard neural operators struggle with SPDE-driven systems
and that the regularity of the input representation matters. A potential future direction
for enriching the K vorticity snapshots before SFNO processes them. Not competing --
NORS still maps to the solution path, not the statistical invariant.

### 2e. In-context operator learning

A distinct literature on operators that infer the PDE / forcing configuration from a
few context examples at inference time, without weight updates:

**ICON** (Yang et al., PNAS 2023, arXiv:2304.07993): shared linear encoder + transformer
encoder, cross-attention decoder. ~2% relative error with 5 context pairs. 1D only.
The paradigm: given a few (input, output) pairs from an unseen operator, predict outputs
at new query points without retraining.

**VICON** (Cao et al., TMLR 2024, arXiv:2411.16063): ViT-style patch tokenization extends
ICON to 2D fields. 37.9% lower rollout error than DPOT. Compatible with grid structure
of this project.

**Cautionary (Mahowald 2026, arXiv:2603.21534):** OOD errors for ICON-style models are
an order of magnitude larger than in-distribution errors. More context examples do not
help OOD. Failure modes include boundary conditions and heterogeneous context.
Implication: the error-vs-distance-from-training-config evaluation in
docs/model-evaluation.md section 3 is not optional -- it is the required honesty check.

**This project's connection to ICON:** The K=10 vorticity snapshots act as the context
window from which the model must infer the forcing regime (stirring_lat0) and predict
[u_bar]. This is in-context inference of a statistical invariant from dynamics -- neither
ICON nor VICON have been applied to stochastic systems or statistical targets.

### 2f. Ergodic learning theory

**"Learning Ergodic Dynamical Systems from a Finite Trajectory"**
(arXiv:2607.22399, Kachaiev, Villa, Rosasco 2026). Proves O(T^{-1/2}) excess error for
learning from a single correlated trajectory of an ergodic Markov chain, with mixing-time
penalty (1-rho)^{-2}. The penalty factor means learning is harder near forcing regimes
where jets form or dissolve (slow mixing). Formal vocabulary for the "K snapshots are
enough" claim.

**"Data-Adaptive Learning of Dynamical Systems by Matching Transfer Operators and
Invariant Measures"** (arXiv:2607.00391, Huang et al. 2026). Proposes replacing
trajectory-matching losses with losses based on how probability mass flows through state
space (transfer operator matching). Outperforms trajectory regression on Lorenz-63,
Lorenz-96, and NOAA SST. Directly applicable as an alternative loss function.

### 2g. Architecture context (SFNO)

Bonev et al., "Spherical Fourier Neural Operators" (ICML 2023, papers/sfno.pdf).
The SFNO backbone used in this project. Key architectural fact (from appendix A.2,
equation 24): the forward SHT computes u_hat[l, m] via a 1D DFT over longitude followed
by Legendre transform over latitude. The filter kappa_theta(l) acts only on l, not m.
The SFNO already computes all u_hat[l, m] internally. Reading off the m=0 column is
trivially available from the internal spectral representation.

Mathematical identity from barotropic.pdf (Held, GFDL -- the Isca spectral model docs):
the zonal mean is exactly the m=0 column of the SHT coefficient matrix:

    zeta_bar(theta) = sum_{l=0}^{inf} zeta_{l,0} P_{l,0}(sin(theta))

This is not an approximation -- it is a mathematical identity. The BVE simulator itself
stores and evolves spectral coefficients; [u_bar] is the m=0 slice. The current
ZonalMeanWrapper (.mean(dim=-1)) computes this in physical space (approximate under
discretization). A spectral head reading u_hat[l, 0] is exact.


## 3. Candidate CS novelty framings, ranked by defensibility

### 3.1 Problem reformulation under ill-posedness (still valid, still weakest alone)

"When the natural operator-learning target is ill-posed due to stochastic forcing,
reformulate the codomain to a deterministic statistical functional of the dynamics,
rather than patching the loss (Jiang 2023) or going probabilistic (SLT 2024)."

This is real, well-motivated, and now supported by more literature. The three-way
contrast is now precise: (a) patch the loss on a same-type map (Jiang); (b) output a
distribution over trajectories (SLT); (c) change the codomain to the well-posed
quantity (this project). But framed alone it still reads as "we picked an easier target."
Must be paired with 3.2 or 3.4.

### 3.2 Symmetry-informed statistical head for neural operators
(concrete, buildable, strongest standalone CS artifact)

ZonalMeanWrapper's .mean(dim=-1) is a naive post-hoc operation. The correct head reads
m=0 coefficients from SFNO's internal SHT -- the operation that is (a) mathematically
exact (see section 2g), (b) structurally invariant to longitude rotation of the input
by construction, and (c) consistent with the architecture's own spectral representation.

This is the most CS-legible framing: an architecture/inductive-bias question
(equivariance-by-construction vs. equivariance-by-hope), which is a live theme in the
neural-operator literature, and it produces a number from a clean ablation.

**This remains the top recommended concrete thing to build.** It is small, falsifiable,
and directly answers "what is the CS artifact" with a head architecture and an ablation
table (relL2, sample efficiency, generalization vs stirring_lat0 distance), regardless
of which broader framing the thesis ultimately takes.

### 3.3 Sample complexity of K vs M: empirical and possibly formal

The empirical contrast is now concrete: SLT requires 2e6 trajectory steps to
characterize the same system; this project uses 900 training samples (60 sims x 15
windows). If the model achieves comparable or better accuracy on [u_bar], that is a
sample complexity result with a number attached.

The formal vocabulary is now available: arXiv:2607.22399 proves O(T^{-1/2}) rates with
mixing-time penalty. The empirical counterpart is a K-sweep: sweep the number of input
snapshots from 1 to 50, measure relL2, and characterize how the rate depends on the
forcing regime (penalty should be larger near jet-formation transitions where mixing is
slow). This is a concrete, runnable experiment.

Whether to go further into formal theory (a theorem about the BVE) is the instructor's
call. It is the highest-ceiling option but the most work and possibly math-adjacent.

### 3.4 In-context inference across a parametric family of stochastic systems
(now the primary thesis claim, not just a supporting framing)

The Shokar 2025 FiLM conditioning paper (arXiv:2509.09599) defines the alternative:
given a new forcing parameter, condition the model on it explicitly and fine-tune with
~1,000 snapshots. This project's model receives no parameter value -- it must infer
the regime from K=10 observations of the dynamics alone.

This is now the clearest way to describe what is novel. The intersection of (a)
in-context operator learning (ICON/VICON line) and (b) stochastic GFD emulation
(SLT line), applied to (c) a statistical invariant rather than a next-step prediction,
is currently unoccupied in the literature.

**The thesis claim is:** A single neural operator trained on a few forcing configurations
can infer the invariant measure of an unseen member of the parametric family from K=10
vorticity snapshots, without being told the forcing parameter and without any rollout or
fine-tuning. The cautionary paper (Mahowald 2026) bounds how far this can go OOD, and
the generalization evaluation in docs/model-evaluation.md section 3 measures exactly
this.

The vocabulary question from session 1 ("is this meta-learning or in-context learning?")
is now answered: "in-context operator learning" is the established term (ICON/VICON),
and the distinction from ICON is that this project targets a statistical invariant of a
stochastic system rather than a solution value of a deterministic PDE.


## 4. Recommended goals for the thesis (ranked)

### Required (core claim)

1. **Prove genuine operator learning.** Run the nearest-training-config baseline
   (docs/model-evaluation.md section 1). If the model does not beat a predictor that
   ignores vorticity and just looks up the nearest training climatology, there is no
   CS claim.

2. **Extend preprocessing to all 9 stirring_lat0 values.** Currently only 4 of 9 are
   in the dataset. The parametric generalization claim requires testing all 9, including
   the extreme extrapolation cases (lat0=0, 7.5, 15). This is a simulation and
   preprocessing task, not an ML question.

3. **Implement and ablate the m=0 spectral head.** Replace ZonalMeanWrapper with a
   direct readout of m=0 SHT coefficients from SFNO's internal spectral representation.
   Ablate vs. current head on relL2, convergence speed, and generalization across
   stirring_lat0 splits.

### Strong additions (if time allows)

4. **FiLM conditioning comparison.** Train a version that receives stirring_lat0 as an
   explicit scalar conditioning input (FiLM-style, as in Shokar 2025). Compare against
   the in-context version. This is the primary competitive baseline and the comparison
   that gives the thesis its strongest quantitative claim.

5. **K-sweep (sample complexity experiment).** Sweep input window length K from 1 to
   ~50, measure relL2. Characterize the scaling and whether the rate is slower for
   forcing regimes near jet-formation transitions. Connects to arXiv:2607.22399 theory.

### Optional (instructor's call)

6. **Formal sample complexity argument.** Use the ergodic learning theory vocabulary
   to state a quantitative claim about K vs. the mixing time of the BVE. Highest ceiling
   but most work, possibly math-adjacent.


## 5. Open questions (updated)

Questions from session 1 that are now answered:

- "Is 'meta-learning across a parametric family' the right vocabulary?" -- Answered:
  "in-context operator learning" is the established term. ICON (Yang et al. PNAS 2023)
  is the canonical reference.

- "Are no-regularity-spdes.pdf and slt-zonal.pdf relevant?" -- Answered: Both fully
  read. SLT is now the primary competing paper. NORS is a supporting citation for why
  standard neural operators struggle with SPDE-driven systems.

Questions that remain open and require instructor input:

- Is problem reformulation (3.1) alone, without the architecture (3.2) or theory (3.3)
  contribution, judged as CS innovation by this committee? Probably not -- but 3.1 + 3.2
  together should be sufficient. Confirm.

- Is a formal sample complexity result about one physical system (framing 3.3 taken to
  its limit) "CS enough," or must it be stated for a class of ergodic SPDEs to count?
  The Mahowald 2026 cautionary paper suggests the OOD failure modes are a more pressing
  theoretical question than the in-distribution rate.

- Should the thesis compare against SLT/Shokar 2025 directly (which requires re-running
  their model or reporting from their published numbers), or is a principled qualitative
  contrast sufficient given the different scope (they target trajectory statistics,
  we target time-mean profile)?


## 6. Sources consulted

### Papers in papers/ (all read in full or in part this session)

- Vallis, Gerber, Kushner, Cash. "A Mechanism and Simple Dynamical Model of the North
  Atlantic Oscillation and Annular Modes." JAS, 2004. (papers/vallis-etal-2024.pdf)
  Origin of the Vallis-style stirring. Physical justification for [u_bar] as the target.

- Held, I.M. "The Barotropic Vorticity Equation." GFDL technical document.
  (papers/barotropic.pdf) Isca spectral model documentation. Section 3 contains the
  SHT equations for the BVE, including the proof that the zonal mean = m=0 column.

- Bonev, Kurth, Hundt, Pathak, Baust, Kashinath, Anandkumar. "Spherical Fourier Neural
  Operators." ICML 2023. (papers/sfno.pdf) Appendix A.2 contains the SHT algorithm;
  appendix A.3 contains the FNO-to-SFNO derivation.

- Shokar, Kerswell, Haynes. "Stochastic Latent Transformer." JAMES 2024.
  (papers/slt-zonal.pdf) Closest competing work. Same physical system.

- Hu, Meng, Chen, Gong, Wang, Chen, Zhu, Ma, Liu. "Neural Operator with Regularity
  Structure for Modeling Dynamics Driven by SPDEs." ICLR 2022 workshop.
  (papers/no-regularity-spdes.pdf) Adjacent work on SPDE-driven neural operators.

- Li et al. "Fourier Neural Operator." ICLR 2021. (papers/fno.pdf, papers/no.pdf)

- Duruisseaux, Kossaifi, Anandkumar. "Fourier Neural Operators Explained." 2026.
  (papers/fno-explained.pdf) Section 2.3.1 explicitly states ill-posedness of
  deterministic operators on stochastic systems.

### Papers found via web research this session

- Shokar, Haynes, Kerswell. "Extending Deep Learning Emulation Across Parameter
  Regimes..." ICLR 2024 AI4DiffEq workshop.
  https://openreview.net/forum?id=7a5gUX4e5q

- Shokar, Kerswell, Haynes. Full FiLM conditioning paper. arXiv:2509.09599.
  The FiLM conditioning baseline. Fine-tuning at new parameter requires ~1,000 snapshots.

- Jiang, Kovachki et al. "Training neural operators to preserve invariant measures of
  chaotic attractors." NeurIPS 2023. arXiv:2306.01187.

- Pathak, Lu, Hunt, Girvan, Ott. "Using machine learning to replicate chaotic
  attractors and calculate Lyapunov exponents from data." Chaos 2017. arXiv:1710.07313.

- Yang et al. "In-Context Operator Learning." PNAS 120(39), 2023. arXiv:2304.07993.
  Canonical in-context operator learning reference.

- Cao et al. "VICON." TMLR 2024. arXiv:2411.16063. 2D extension of ICON.

- Mahowald. "Generalization limits of in-context operator learning." arXiv:2603.21534
  (2026). OOD errors are 10x larger; more context does not help OOD.

- Kachaiev, Villa, Rosasco. "Learning Ergodic Dynamical Systems from a Finite
  Trajectory." arXiv:2607.22399, 2026. O(T^{-1/2}) rate with mixing-time penalty.

- Huang, Botvinick-Greenhouse, Yang. "Data-Adaptive Learning of Dynamical Systems by
  Matching Transfer Operators and Invariant Measures." arXiv:2607.00391, 2026.
  Transfer operator matching loss. Better than trajectory regression on chaotic systems.

### Repository-internal documents (all current and correct as of this writing)

- docs/model-evaluation.md: evaluation plan including nearest-training-config baseline.
- docs/norms.md: relL2, RMSE, normalized parameter distance definitions.
- ml/src/ml/training/model.py: SFNO + ZonalMeanWrapper implementation.
