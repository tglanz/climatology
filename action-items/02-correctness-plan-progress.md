# 02 Correctness implementation progress

Plan: [Correctness implementation plan](02-correctness-plan.md).
Status: complete on branch `correctness`.
Results: [implementation and verification record](02-correctness-results.md).

## Procedure progress

- Complete: scientific contracts and analytical tests.
- Complete: shared Gaussian geometry, quadrature, coordinates, and transforms.
- Complete: canonical samples, detectors, units, cache ownership, and split checks.
- Complete: normalization, checkpoint identity, losses, and numerical safeguards.
- Complete: training-only baselines, per-target evaluation, and current-result reports.
- Complete: final tests, lint, formatting, and the real-data CPU experiment.
- Complete: independent review, adversarial follow-up, and results record.

## Verification

49 tests pass. Error-level pylint, Black, documentation links, and whitespace pass.
Existing notebook outputs remain unchanged. The final real-data experiment has exact
raw/prepared sample agreement and exact same-partition reload predictions.
Two pre-existing warnings remain. See the results for commands, measurements,
provenance, review dispositions, compatibility requirements, and skipped checks.

## Refinements

Review added CF calendar coverage, explicit input-unit identity, and one saved
target per simulation. Convergence figures now use the detector reference and
prefix indices. Shared operator construction preserves configuration-only
parameter inspection. These close phase 02 contracts without broader pipeline redesign.

## Next action

No required phase 02 implementation work remains. Phase 03 remains separate.
