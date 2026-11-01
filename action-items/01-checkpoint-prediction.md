# 01. Share checkpoint prediction

Priority: P1. Needed by 10, 14, and 20.

## Evidence

`ml/src/ml/training/trainer.py:110-139` fits upstream normalizers but saves only means and standard deviations.
The pinned normalizer uses `std + eps`, with `eps=1e-7`.
`ml/src/ml/cmd/evaluate.py:174-176` divides and multiplies by bare `std`.
A sampled local checkpoint has input std near `2.48e-5`, giving about 0.40% input scale drift.
This proves a parity defect, not a measured large prediction error.

## Work

Create one library predictor for checkpoint loading, device choice, normalization, inference, and inverse normalization.
Use it from the CLI and notebooks. Save the transform parameters and artifact version.
Define explicit compatibility for old checkpoints.

## Verify

1. Add `test_checkpoint_prediction.py`. Fit, save, and reload a tiny CPU model and normalizer.
2. Include ordinary, tiny-variance, and constant channels. Reloaded transforms and physical predictions must match the live path within float32 tolerance, initially `rtol=1e-6, atol=1e-7`.
3. Check that constant inputs remain finite and unsupported artifact versions fail clearly.
4. Evaluate one saved batch through the library and CLI. Require the same profiles and metrics.
