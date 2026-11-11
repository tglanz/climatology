# 02 Correctness implementation plan

Implement [action item 02](02-correctness.md) so samples, predictions, and scores
follow explicit mathematical contracts. Status: complete; see the
[results](02-correctness-results.md) and [progress record](02-correctness-plan-progress.md). The definitions, units, numerical policies, and statistical claims form
the first acceptance gate.

## Changes

- Reconcile scientific definitions, documentation, and executable calculations.
- Unify sample selection, target construction, and simulation acceptance.
- Correct coordinates, quadrature, normalization, losses, and numerical guards.
- Correct baselines, evaluation aggregation, variability interpretation, and reports.
- Verify analytical cases and one small complete experiment.

Scope includes the shared ML code and its method documents. Preserve existing
data, checkpoints, notebook outputs, submodule pins, and Isca patches. Use fresh
output directories. Pipeline redesign and harmonic-head research remain separate.

## Work item Correct the experiment

### Procedure

Follow this order within one delivery.

1. Establish the contracts below in [preprocessing](../docs/pre-processing.md),
   [norms](../docs/norms.md), [grids](../docs/grids.md), and
   [evaluation](../docs/model-evaluation.md). Derive formulas and add analytical
   tests before changing their callers. Resolve each documentation/code conflict.
2. Add shared grid validation and quadrature in
   [spatial diagnostics](../ml/src/ml/diagnostics/spatial.py).
   Apply it to enstrophy, convergence, metrics, and latitude-averaged spectra.
   Correct SFNO construction and coordinate embedding in
   [model building](../ml/src/ml/training/model.py).
   Verify known harmonics, axis orientation, and weighted integrals.
3. Give raw preparation and evaluation one sample-construction
   owner under [data](../ml/src/ml/data/simulation_data.py).
   Update [preparation](../ml/src/ml/data/isca_preprocessing.py),
   [evaluation loading](../ml/src/ml/data/evaluation.py), and both
   [prepared-sample](../ml/src/ml/usecases/evaluate_samples.py) and
   [by-code](../ml/src/ml/usecases/evaluate_by_code.py) evaluation.
   Apply the same contract to prepared arrays.
   Repair cache ownership, validation, split checks, and detector numerical defects.
   Require matching windows, targets, coordinates, and rejection reasons.
4. Correct normalization fitting and persistence in
   [training](../ml/src/ml/training/trainer.py) and
   [inference](../ml/src/ml/inference.py).
   Correct [losses](../ml/src/ml/training/loss.py), their
   [metric implementation](../ml/src/ml/diagnostics/errors.py), and
   [baseline reductions](../ml/src/ml/training/baselines.py).
   Validate [configuration](../ml/src/ml/config.py) before training-directory rotation or writes.
   Reject nonfinite losses and gradients before optimizer updates.
5. Correct [evaluation orchestration](../ml/src/ml/usecases/evaluate.py) and
   [replicate analysis](../ml/src/ml/usecases/climatology_analysis.py).
   Generate target-specific scores and labels. Report loaded and excluded counts.
   Assemble reports from the current invocation's generated artifacts.
6. Replace compaction assertions that preserve defects with correctness regressions.
   Run the full ML test and lint gates. Execute one bounded CPU experiment on
   existing real simulations with a tiny SFNO and fixed seeds. Exercise preparation,
   training, checkpoint loading, both evaluation routes, and report regeneration.
   Select three valid configuration groups, one per split; retain at most two
   windows per simulation. Use two epochs, one layer, four hidden channels, and
   low harmonic bandwidth. Record a synthetic fallback as a real-data verification limit.
7. Record configuration, seeds, data identities, dependency versions, tolerances,
   changed sample counts, and results in a correctness results record.
   Review the implementation and scientific claims independently.
   Resolve findings before phase 03. Record unavailable checks explicitly.

Run the existing gates from the repository root during implementation:

```bash
uv run --project ml --all-groups pytest ml/tests
uv run --project ml --all-groups pylint --rcfile=ml/pyproject.toml --errors-only ml/src
uv run --project ml --all-groups black --check ml
```

### Motivation and overview

The experiment needs defensible definitions and numerical evidence before its
scores can support scientific conclusions.

### Details

The following contracts guided implementation. The results record documents review refinements.

#### Samples and finite-run targets

Let $M$ count snapshots, $K$ count snapshots per window, $H$ count latitudes,
$W$ count longitudes, and $C$ count configured targets. Use half-open intervals.
A window is $[t_0,t_0+K)$, so $t_0\leq M-K$. Retain the existing meaning of
`end_at="convergence"`: it caps the window start at $t_c$, not its final snapshot.
Stride $K$ gives adjacent disjoint windows; $K+1$ leaves one unused snapshot.

For target variable $v_c$, define

$$
Y_{c,h}=\frac{1}{(b-a)W}\sum_{t=a}^{b-1}\sum_{\ell=0}^{W-1}v_c(t,h,\ell).
$$

Require uniform snapshot cadence and equally spaced periodic longitudes for this
unweighted average. Validate time continuity, dimensions, units, and coordinates
across segments. Preserve input time-then-variable order and target configuration
order. Keep arrays shaped `x=(B,K*V,H,W)` and `y=(B,C,H)`, where $B$ counts
samples and $V$ input variables.

This target estimates a finite trajectory average. Interpreting it as a
stationary ensemble climate additionally assumes stationarity, ergodic
sampling, and a finite mean. Input and target intervals can overlap; describe the task as
finite-run climatology estimation, without claiming an independent future target.

Retain the adjacent-block spinup heuristic in
[spinup](../ml/src/ml/diagnostics/spinup.py). Replace the contradictory rolling-mean
description. Scale enstrophy by its maximum magnitude before dimensionless
comparisons; handle an all-zero series as constant. Round minimum hold durations
upward: require $\max(1,\lceil\text{stable_time}/\text{window_size}\rceil)$
consecutive stable block comparisons. These settings count saved snapshots.
A constant series passes with enough complete blocks; insufficient data cannot
establish stability.
These comparisons are heuristic stability checks, without calibrated significance.

In [convergence](../ml/src/ml/diagnostics/convergence.py), $t_c$ is the exclusive
endpoint of the first qualifying running-average prefix. Detection is retrospective.
Compare that prefix with the full available reference using the same weighted norm
as evaluation.
A finite hold period establishes this criterion only; it proves neither
stationarity nor asymptotic convergence. Missing required anchors, unsuccessful
configured detectors, and invalid target intervals exclude a simulation explicitly.
Absent detectors remain disabled. Reject empty training assignments and zero
usable training samples. Preserve configuration-group split membership.

#### Grid and area integration

For Gaussian latitudes $\phi_h$, use Gauss-Legendre nodes
$\mu_h=\sin\phi_h$, positive weights $q_h$, and $w_h=q_h/\sum_jq_j$.
Use $\sum_hw_hf_h$ for a profile area mean. Do not multiply Gaussian weights
by another cosine. See [ECMWF](https://confluence.ecmwf.int/pages/viewpage.action?pageId=50039496)
and [Gauss quadrature](https://dlmf.nist.gov/3.5#v).

Validate actual coordinates against the selected rule. Reject unsupported grids
explicitly. SFNO must use Gaussian transforms in every spherical convolution.
The pinned constructor does not expose `sht_grids`; use a project-owned adapter
through the existing convolution interface. Preserve third-party pins.
Account for north-to-south transform order and south-to-north Isca order.
Use actual coordinates for positional features and plots.

#### Metrics and aggregation

For one target profile, define $e=\hat y-y$ and

$$
\operatorname{RMSE}_w=\sqrt{\sum_hw_he_h^2},\qquad
\operatorname{relL2}_w=
\frac{\sqrt{\sum_hw_he_h^2}}{\sqrt{\sum_hw_hy_h^2}}.
$$

RMSE has the target's units. Relative L2 is dimensionless and undefined for
zero-norm truth. Report such cases and their counts; retain RMSE and exclude
undefined ratios explicitly from relative summaries, reporting the included count.
If none are defined, report the relative summary as unavailable. Reject zero-denominator
relative training objectives with an actionable error. Test finite gradients
at perfect predictions, using a zero subgradient there. Validate shapes before
broadcasting. Do not hide undefined ratios behind an unnamed epsilon.

Reduce each relative target separately, then average targets and samples.
Do not combine wind and vorticity in a dimensional vector norm.
Label unweighted relative L2 separately. Keep training objectives in normalized
coordinates, and label them accordingly; report physical-unit evaluation separately.
Aggregate epoch means as $\sum_bn_bL_b/\sum_bn_b$, with $n_b$ the batch size.
Require fixed-model validation invariance under batch partitioning.

CLI evaluation averages window predictions within each simulation before scoring.
Prepared-sample evaluation scores windows. Name both aggregation levels explicitly.
Wind-specific diagnostics apply only to zonal wind. Label the current peak detector
as the strongest absolute wind extremum.
Global and nearest-configuration baselines average training simulations equally;
nearest profiles average replicas of the selected training configuration.
Save one target per accepted simulation for the prepared-data baseline utility.
Mark unavailable baselines unavailable, including missing parameter metadata.
Never substitute test targets or label a train-mean fallback as nearest configuration.

#### Normalization and artifact identity

Fit per-channel means and population standard deviations from training samples
only, using stable streaming moments. Retain the current reduction axes.
Require agreement with a direct calculation for any batch partition.
[PyTorch's standard-deviation definition](https://docs.pytorch.org/docs/2.11/generated/torch.std.html)
makes the correction convention explicit.

Use $z=(x-\mu)/(\sigma+\epsilon)$ and
$x=z(\sigma+\epsilon)+\mu$ in training and loaded prediction.
Save both epsilons, statistics, channel and input-unit identities, grid coordinates, and a
correctness-format identifier. Preserve every target axis.
Reject incompatible or unversioned artifacts in the corrected path with regeneration
guidance. Existing artifacts remain untouched. This is the minimum metadata
needed to prevent silent reinterpretation; broader artifact redesign stays in 03.

#### Replicate variability and claims

For a configuration with $R$ replica targets, let
$\bar Y=R^{-1}\sum_rY_r$. Retain the descriptive statistic
$R^{-1}\sum_r\operatorname{relL2}_w(Y_r,\bar Y)$, with the same zero-reference policy.
Call it mean relative deviation from the replica mean. Report $R$; one replica
does not estimate variability. It is neither a standard deviation nor an
irreducible-error bound. Conditioning on an input window can explain variation
that a configuration-only mean cannot.

A conditional mean minimizes expected squared error under finite second moments.
This does not establish optimality for mean relative L2.
See [Gneiting, Making and Evaluating Point Forecasts](https://arxiv.org/html/0912.0902v2).
Keep these distinctions in plot captions and reports. Label raw FFT power as
raw Fourier power, without implying a normalized spherical energy spectrum.

#### Acceptance evidence

Planning checks confirmed batch-dependent standard deviations (2.44949 versus
2.61861), NaN gradients at zero loss, and spinup indices changing from 20 to 10
under unit rescaling. These are additional confirmed defects in the inspected paths.

Require analytical quadrature moments, constant and low-degree harmonic tests,
orientation checks, multi-target cases, zero references, and finite gradients.
For $0\leq k\leq 2H-1$, require $\sum_hq_h\mu_h^k=0$ for odd $k$ and
$2/(k+1)$ for even $k$, within declared floating-point tolerances.
Cover exact-length windows, segment boundaries, failed detectors, cache reuse,
caller-owned dataset lifetime, invalid settings, and empty splits.
Reject nonpositive epochs, batch sizes, or model dimensions; reject negative worker
counts and nonfinite scalar settings. Reject channel mismatches, invalid schedules,
unsupported mode sizes, and validation-dependent settings without validation data.
Require identical physical predictions before and after checkpoint loading
within a declared device-specific tolerance.

Inject failures to prove optimizer weights remain unchanged. Change test targets
to prove training-derived baseline predictions remain unchanged. Rerun evaluation
with sections removed and require no stale figure links. Keep old compaction
measurements historical. The small experiment establishes integration correctness,
without claiming improved full-scale model quality.
