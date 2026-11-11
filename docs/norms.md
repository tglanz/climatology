# Norms

Metrics use the actual [Gaussian grid](grids.md). Let $\phi_h$ be latitude,
$q_h$ its Gauss-Legendre weight, and $w_h=q_h/\sum_jq_j$.
These weights integrate in $\mu=\sin\phi$; another cosine changes the rule.
See [ECMWF](https://confluence.ecmwf.int/pages/viewpage.action?pageId=50039496)
and [Gauss quadrature](https://dlmf.nist.gov/3.5#v).

## Profile errors

For prediction $\hat y$, truth $y$, and error $e=\hat y-y$, all shaped $(H,)$,

$$
\operatorname{RMSE}_w=\sqrt{\sum_hw_he_h^2},
\qquad
\operatorname{relL2}_w=
\frac{\sqrt{\sum_hw_he_h^2}}{\sqrt{\sum_hw_hy_h^2}}.
$$

RMSE has the target's units. Relative L2 is dimensionless. For nonzero truth, a
perfect prediction scores zero and the zero predictor scores one.
Relative L2 is undefined for zero-norm truth, including zero prediction against
zero truth. NumPy metrics return NaN for that ratio. Summaries exclude undefined
ratios and report included and undefined counts. If none are defined, the relative
summary is unavailable. RMSE remains defined.

[Metrics](../ml/src/ml/diagnostics/errors.py) require equal shapes before
broadcasting. Arrays `(B,C,H)` reduce latitude independently for each sample and
target. Relative scores can then average targets and samples.
Absolute errors with different physical units remain separate.

## Training objectives and normalization

Fit per-channel population means and standard deviations from training samples
only. Stable streaming moments make fitting independent of batch partitioning.
Input statistics reduce sample, latitude, and longitude axes; target statistics
reduce sample and latitude axes. This is a scaling convention, not an estimate
of a spherical area mean.

For mean $\mu$, population standard deviation $\sigma$, and saved positive
epsilon $\epsilon$, use

$$
z=\frac{x-\mu}{\sigma+\epsilon},
\qquad
x=z(\sigma+\epsilon)+\mu.
$$

Training and loaded inference share these operations. Standard deviation uses
population correction zero; see [PyTorch](https://docs.pytorch.org/docs/2.11/generated/torch.std.html).
The default epsilon is $10^{-7}$ in each channel's units and is saved explicitly.

MSE averages squared normalized errors. Unweighted relative L2 uses equal
latitude weights; Gaussian-weighted relative L2 uses $w_h$. Each relative loss
reduces targets separately before averaging. Relative training losses reject a
zero target norm with guidance to use MSE or change targets. Zero prediction
error uses a zero subgradient.

Epoch loss is $\sum_bn_bL_b/\sum_bn_b$, where $L_b$ is the batch mean and $n_b$
its sample count. Fixed-model validation is independent of batch partitioning
within floating-point tolerance. Training follows changing weights, so different
training batches need not produce the same trajectory.

Training curves describe normalized-target objectives. Evaluation describes
physical-unit predictions and does not equate its errors with those curves.

## Aggregation and baselines

Prepared-window evaluation weights windows equally. CLI evaluation averages window
predictions within a simulation, then scores simulations equally. Error of the
averaged prediction differs from average window error.

The global training baseline averages one profile per training simulation.
Nearest-configuration prediction averages replicas of the chosen training
configuration. Neither uses test targets.
Parameter distance is Euclidean after dividing each varying parameter by its range
among loaded training configurations. Constant ranges become one.
This is a chosen parameter scaling, not a physical distance.

## Replicate variability

For $R\geq2$ replica targets in one configuration, let $\bar Y=R^{-1}\sum_rY_r$.
The reported statistic is

$$
\frac{1}{R}\sum_r\operatorname{relL2}_w(Y_r,\bar Y),
$$

subject to the same undefined-ratio policy. It is mean relative deviation from a
finite replica mean. It is neither a standard deviation nor an estimate of an
irreducible-error bound. One replica cannot estimate variability.
An input window may explain variation that a configuration-only mean cannot.

A conditional mean minimizes expected squared error under finite second moments.
That result does not establish optimality for mean relative L2.
See [Gneiting, Making and Evaluating Point Forecasts](https://arxiv.org/html/0912.0902v2).
