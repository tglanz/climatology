# Model Evaluation Plan

The model maps K vorticity snapshots to the long-run climatological zonal-mean zonal wind.
Each experiment defines its own forcing parameter space. Forcing configurations are
identified by their code (a hash of the parameter dict). The evaluation is generic over
whatever parameters the experiment uses; no parameter names are hardcoded.

Examples in this document use the current experiment's parameter space
(lat0, amplitude, widthy) for concreteness. These are illustrations only.

---

## Norms

See [docs/norms.md](norms.md) for definitions of relL2, RMSE, and normalized parameter distance.

---

## 1. Baselines

**Goal**: establish what the model needs to beat, and whether it actually beats it.

Four predictors, evaluated on the held-out test split:

| predictor               | description                                                       |
|-------------------------|-------------------------------------------------------------------|
| zero                    | predict zero everywhere; relL2 = 1 by construction               |
| global train mean       | predict the mean target profile across the entire train set       |
| nearest training config | predict the mean climatology of the closest training config in    |
|                         | parameter space, using no vorticity                               |
| model                   | trained SFNO                                                      |

The global train mean tests whether the model beats complete ignorance. It is a weak baseline and deliberately so.

The nearest-training-config baseline is the critical one. It uses only the forcing parameters, which are known at evaluation time, and no vorticity. If the model does not beat it, it is not extracting genuine information from the vorticity windows; it is effectively doing parameter-space lookup implicitly.

Distance is Euclidean over the normalized parameter vector. Each parameter is normalized by its observed range across all configurations so that no single parameter dominates by scale.

Plots:
- Bar chart: relL2 for each predictor
- Profile overlays: mean truth and each predictor's mean prediction over the test split

---

## 2. Noise floor

**Goal**: quantify the irreducible error from stochastic forcing variability, per configuration.

For each forcing configuration, the across-replicate std of the climatology profile sets the minimum achievable error. A perfect model that has learned the operator exactly would still incur this error because the stochastic seed shifts the climatology slightly between replicates. Expressed in relL2 units so it is directly comparable to model error.

Plots:
- Bar chart: noise floor per config code (sorted ascending), with model relL2 overlaid
- Scatter: model relL2 vs noise floor relL2, one point per config, colored by split. The diagonal is the theoretical limit; points above it have room to improve.

---

## 3. Generalization across the forcing parameter space

**Goal**: determine whether the model learned the operator or memorized training configurations.

Evaluate on every available forcing configuration. The key question: does error increase with distance from training configurations in parameter space? A memorizing model fails on configurations far from training; a generalizing model does not.

For each forcing parameter, produce a marginal scatter: relL2 vs that parameter value, colored by split. This reveals which parameters drive error without assuming a fixed parameter space.

Example: for the current experiment this produces three marginal plots: relL2 vs stirring_lat0, relL2 vs stirring_amplitude, and relL2 vs stirring_widthy.

Plots:
- One marginal scatter per varying parameter: relL2 vs parameter value, colored by split
- Profile overlays for the 6 worst-scoring config codes

---

## 4. Error structure

**Goal**: characterize how the model fails, not just how much.

relL2 is a scalar and masks the failure mode. Decompose error into:

- **Bias by latitude**: mean of (pred - truth) across test sims at each latitude. Systematic bias at a latitude band means the model consistently misplaces or misshapes the jet there.
- **Jet position error**: latitude of the predicted wind maximum vs truth. Getting the position wrong is physically distinct from blurring the amplitude.
- **Amplitude error**: peak magnitude of the predicted jet vs truth, independent of position.

Plots:
- Mean bias profile with per-sample error fan
- Histogram of per-sample relL2
- Scatter: predicted jet latitude vs true jet latitude
- Scatter: predicted jet amplitude vs true jet amplitude

---

## 5. Model error vs noise floor

**Goal**: identify which regimes the model handles well and which approach the noise floor.

A single summary scatter (one point per config code, colored by split) places model relL2 on the y-axis and noise floor relL2 on the x-axis. The diagonal is the theoretical limit. Points on or below the diagonal are near the best achievable by any model; points above still have room to improve. Split-level patterns are immediately visible (e.g., test configs clustering above the diagonal signals extrapolation difficulty).

Plots:
- Scatter: model relL2 vs noise floor relL2, colored by split

---

## Summary

Outputs are written to `<training-dir>/evaluation/`: a `report.md` embedding all figures and a `figures/` directory with one PNG per plot.

To convert to PDF:

```bash
pandoc <training-dir>/evaluation/report.md -o <training-dir>/evaluation/report.pdf
```
