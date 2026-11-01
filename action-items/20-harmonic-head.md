# 20. Test a harmonic output head

Priority: Research. Fix 01-03, 06, and 14 first.

## Question

Can a head matched to the zonal climatology target improve accuracy, data use, or cost?

The current `ml/src/ml/training/model.py:9-15,46` predicts a full field and averages longitude.
For a uniformly sampled longitude grid, that mean already selects discrete Fourier mode m=0.
A harmonic head is therefore an inductive-bias and compression experiment.
It is not inherently more exact or automatically invariant to rotations of the input.

## Experiment

Compare the current field-then-mean head with a direct latitude-profile head and a truncated coefficient head.
For scalar profile compression, use a fixed m=0 spherical-harmonic/Legendre basis on the real latitude nodes.
Zonal wind is a tangent velocity component. Also consider an axisymmetric streamfunction head with the derivative relation to wind, or the corresponding vector basis.
Define radius factors, signs, normalization, regularity at poles, and zero-mode handling.
Specify whether coefficients describe physical or normalized profiles. An affine target normalization must not invalidate a physical wind constraint.

First project true target profiles into the basis at several cutoffs.
Measure reconstruction error before training. Then train heads with the same backbone family, splits, inputs, optimizer policy, and seed set.
Report parameter counts and compute differences. Compare matched budgets where possible.
Include the train-mean and nearest-training-configuration baselines.
Keep novelty claims open until a focused related-work search is complete.

## Verify

1. Add `test_harmonic_head.py`. Check known modes, coefficient reconstruction, gradients, output shape, and checkpoint reload on the true grid.
2. Check the derived streamfunction-to-wind formula against an analytic solid-rotation example if that head is used.
3. Check longitude-shift behavior of the complete model. Do not infer input invariance from m=0 extraction alone.
4. Report target projection error, held-out profile error, jet position/amplitude error, runtime, and memory over multiple seeds.
5. Use the small profile to debug, then evaluate on fixed full held-out splits. Keep validation choices separate from the final test.
6. Record an explicit decision: retain the head only if the comparison shows a useful benefit. A negative result is valid.

Sources:
[SFNO](https://proceedings.mlr.press/v202/bonev23a/bonev23a.pdf),
[Scalar and vector harmonic transforms](https://github.com/NVIDIA/torch-harmonics),
[Held's BVE notes](https://www.gfdl.noaa.gov/wp-content/uploads/files/user_files/pjp/barotropic.pdf).
