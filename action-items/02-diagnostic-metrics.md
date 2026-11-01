# 02. Repair diagnostic metrics

Priority: P1. Keep grid policy in 03.

## Evidence

`ml/src/ml/diagnostics/errors.py:42-44` multiplies a latitude profile by `w[:, None]`.
The profile caller at `usecases/climatology_analysis.py:65-67` therefore broadcasts to H by H and loses latitude weighting.
`diagnostics/spectra.py:48` calls `cosine_latitude_weights` without importing it.
Profile metrics also exist in `diagnostics/evaluation.py:33-56`.

## Work

Give relative L2 and RMSE one owner with explicit profile, field, and batch dimensions.
Share the same definitions across training, baselines, diagnostics, and evaluation.
Define zero-reference behavior. Repair the spectrum helper and remove obsolete duplicate formulas.

## Verify

1. Add `test_diagnostic_metrics.py`. For latitudes [-80, 0, 80], truth [1, 1, 1], prediction [1, 2, 1], weighted relative L2 must be about 0.861526, not 0.577350.
2. Check profiles and H by W fields against explicit weighted sums. Check bad shapes and the chosen zero-reference policy.
3. Where both backends remain supported, require NumPy and Torch results to agree within float32 tolerance.
4. A constant longitude field must have only mode zero. A known longitude sinusoid must peak at its known wavenumber. Test a batch too.
