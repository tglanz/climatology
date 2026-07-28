# Handoff prompt: continue MSc thesis CS-novelty exploration

Paste everything below this line as the opening message to a fresh agent session in
this repo (on any machine that has it checked out).

---

You're picking up work on an MSc thesis exploration in this repository (Global
Physical Climatology + Machine Learning). Read `CLAUDE.md` at the repo root first and
follow it exactly -- in particular: this is an exploration phase, ask before
implementing any feature/experiment/algorithm, and don't lecture on basics.

## Context you need before doing anything

The thesis must be in **computer science**, not climate/physics. The instructor is
explicitly looking for CS innovation. The user (Tal) believes the overall project
direction is plausibly novel but needs help articulating *why*, precisely, in CS
terms rather than physics terms.

A prior session already did a first pass on this. Read these two documents in full
before responding to anything else:

1. `ai-knowledege/thesis-exploration.md` -- the synthesis. It documents:
   - What the project currently does: an SFNO-based neural operator maps a short
     window of $K=10$ vorticity snapshots from a stochastically-stirred barotropic
     vorticity equation (BVE) simulation to the long-run time-mean zonal-mean zonal
     wind $[\bar u]$ (a statistical invariant, not a forecast).
   - Why this reformulation exists: step-ahead vorticity prediction is provably
     ill-posed under stochastic forcing (one input maps to many valid outputs); the
     climatology target is the well-posed alternative. See
     `docs/further-work-stochastic-forcing.md` for the literature backing this.
   - A literature pass positioning the project against the three closest bodies of
     work found: (a) Jiang et al. NeurIPS 2023, "Training neural operators to
     preserve invariant measures of chaotic attractors" (arXiv:2306.01187) -- same
     motivating problem, different solution shape (loss correction on a same-type
     map vs. changing the map's codomain); (b) Pathak/Lu/Ott 2017 reservoir-computing
     "climate replication" (arXiv:1710.07313) -- closest dynamical-systems precedent,
     but single-system and requires autonomous rollout, whereas this project is
     single-shot and generalizes across a *family* of forcing configurations; (c)
     ergodic learning theory on invariant-measure identifiability from finite
     trajectories (arXiv:2607.22399, arXiv:2607.00391).
   - Four ranked candidate CS-novelty framings (section 3): problem reformulation
     under ill-posedness (weakest alone); a symmetry-informed statistical head for
     the neural operator (concrete, buildable, currently unimplemented -- top
     recommendation); sample-complexity/identifiability of $K$ vs $M$ (highest
     ceiling, most work, possibly math-adjacent rather than CS); amortized/
     meta-learning across a parametric family of stochastic systems.
   - Open questions the instructor still needs to weigh in on (section 5).

2. `docs/methodology.md` and `docs/model-evaluation.md` -- ground truth on the
   current data pipeline, model config, splits, baselines, and evaluation metrics.
   Don't re-derive these; they're current and correct as of this writing.

## The most concrete unfinished thread

The top-recommended next action (section 4 of the exploration doc) is a small,
falsifiable architecture ablation:

- `ZonalMeanWrapper` in `ml/src/ml/training/model.py:9-15` currently collapses
  SFNO's $(H, W)$ output to the zonal-mean profile with a naive
  `.mean(dim=-1)` in physical space.
- The zonal mean is exactly the $m=0$ (zonally-symmetric) spherical-harmonic
  coefficient. SFNO already computes a spherical-harmonic transform internally.
  A head that reads $m=0$ directly from the spectral representation, instead of
  inverse-transforming to physical space and averaging, is (a) exact rather than a
  discretized approximation, (b) structurally invariant to longitude shifts of the
  input by construction rather than by hoping the network learns it, and (c) a
  standard "equivariance-by-construction vs. equivariance-by-hope" argument that
  is well understood and citable in the neural-operator literature.
- This has NOT been implemented or ablated yet. It was proposed, not built.

This is a good candidate to actually build and ablate against the current
`ZonalMeanWrapper` baseline (same train/val/test splits, same relL2 metric from
`docs/norms.md`), because it produces a real number for the thesis regardless of
which of the four framings ends up being the headline contribution.

## What's unresolved / needs the user's input, not yours to decide

- Which of the four framings (or combination) to commit to -- this is the user's
  and their instructor's call, not something to pick unilaterally.
- `papers/no-regularity-spdes.pdf` and `papers/slt-zonal.pdf` were never actually
  read -- the machine that produced the exploration doc didn't have `git-lfs`
  installed, so these are still LFS pointer files, not real PDF content. If this
  machine has `git lfs` available, run `git lfs pull` and actually read those two;
  their titles suggest they're directly relevant to the sample-complexity framing
  (candidate 3.3) and might change how strongly that option should be recommended.
- Whether "meta-learning across a parametric family of stochastic dynamical
  systems" is the right established vocabulary for framing 3.4, or whether there's
  a better-known subfield name -- worth a literature check if the user leans toward
  that framing.

## How to proceed

Don't jump straight to implementing the ablation. Per `CLAUDE.md`'s workflow, surface
where things stand, ask the user which framing(s) they want to pursue (or whether they
want you to read the two unread papers first, or want to just get instructor feedback
on the current doc before more exploration), and only start writing code once that's
decided.
