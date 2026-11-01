# 23. Define the target and model bundle

Priority: P2. System design. Build on 01, 03, and 06. Enables 20.

## Evidence

The model factory always applies a longitude mean.
Model metadata records backbone channels but no head or basis contract.
Weights, configuration, and normalization are separate files with implicit relationships.
Training still opens raw simulation files to obtain latitudes.
See `ml/src/ml/training/model.py:9-15,46`, `training/info.py:219-232`, and `data/isca_dataset.py:62-69`.

## Work

Define an input signature, a physical target schema, and a model specification with separate backbone and head choices.
Together they own variables, units, dimensions, coordinates, lag offsets/channel order, and aggregation meaning.
The head owns its output representation and decoding, including any harmonic basis convention.

Create a complete inference bundle with version, weights, grid, transforms, head/target metadata, and source run identity.
The shared predictor returns physical target profiles regardless of head.
Initially keep the trainer-facing normalized-profile interface. Keep coefficient decoding inside the head and compose it with the declared target normalization, including any physical boundary constraints.
Validate compatibility before allocating a model or running inference.
Keep training-resume state separate from the inference bundle.
Add resume support only with the optimizer, scheduler, epoch, and random state required for its stated behavior.

## Verify

1. Train and reload current, direct-profile, and coefficient heads through the same prediction/evaluation interface.
2. Reject mismatched target dimensions, grids, transform versions, and basis conventions before inference. Permute input variables or lag order without changing shape. Require rejection unless an explicit compatible adapter is declared.
3. Move a bundle to a new directory and predict using a compatible prepared sample without guessing raw-data paths.
4. Compare decoded profiles to the live model path within documented numerical tolerances.
5. If resume is implemented, compare two uninterrupted deterministic CPU epochs with one epoch plus resume. Require the declared equality of state and predictions.
