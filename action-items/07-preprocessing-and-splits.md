# 07. Bound and reproduce data preparation

Priority: P2. Useful for 19.

## Evidence

`ml/src/ml/usecases/preprocess.py:34-70` writes results in completion order and submits all simulations at once.
`data/isca_preprocessing.py:110-126` materializes every selected pair per simulation.
`diagnostics/convergence.py:35-41` recomputes each prefix mean from full grids.
`data/splits.py:84-89,121-123` can leave no training groups on a small dataset.
All-skipped preprocessing writes HDF5 files without x/y.

## Work

Preserve stable row order and row provenance across worker counts.
Bound in-flight work and stream practical chunks. Compute convergence from zonal reductions and cumulative means.
Store coordinates, simulation ID, and window start with a versioned schema.
Reject impossible splits early. Define empty optional split behavior and require nonempty training data.
Keep forcing-configuration groups intact. Do not add a second data store without a measured need.

## Verify

1. Add `test_preprocessing.py` and `test_splits.py`.
2. Serial and two-worker preparation must yield identical row identities, arrays, and split membership. Do not compare raw HDF5 container bytes.
3. Compare cumulative and existing prefix calculations on a fixed small field within a stated numerical tolerance.
4. Test one, two, and three configuration groups, excessive ratios, all-skipped simulations, and empty optional splits. Require clear errors or schema-valid empties.
5. Inject a worker failure. Require cleanup and no apparently complete partial artifact.
6. Measure peak memory and time for increasing trajectory lengths. Record the fixture and confirm the implementation respects its documented bound.
