# Workplan

Implement phases in order. Finish one phase before starting the next.
All phases are planned. This document does not start implementation.

The [action items](../action-items/README.md) define scope and detailed verification.
The [architecture review](../action-items/architecture-review.md) defines the target structure.
Each action item belongs to one phase below.

## Phase gate

For each phase:

1. Implement its action items. Add regression tests with the changes and update affected documents.
2. Run every applicable verification step in those items and the integration checks below. Record commands, results, and limits.
3. Review the complete phase diff independently. Check correctness, scientific assumptions, responsibility boundaries, and scope.
4. Resolve review findings. Repeat affected checks and review the fixes.
5. Record the implementation, verification evidence, review outcome, and remaining limits here. Then mark the phase complete.

A required check that cannot run stays pending. Either run it before closure or explicitly narrow the supported scope and review that decision.
Do not treat a skipped check as a pass.
Keep earlier phase checks passing as later phases change their consumers.

## Phase 1. Supported environments

**Outcome:** the required tools and runtimes can be installed and checked.

- [11. Supported environments](../action-items/11-environments.md)

**Verification:** install each supported dependency group in a clean environment.
Check the promised commands and the SHT compatibility patch.
Verify Isca setup on each platform claimed as tested.
Keep simulation and ML runtimes separate.

**Exit:** supported environments, exact commands, and platform limits are documented and reviewed.

## Phase 2. Data and numerical correctness

**Outcome:** one reliable interpretation of coordinates, diagnostics, samples, and targets.

Implement in this order:

- [05. NetCDF cache and ownership](../action-items/05-netcdf-lifetime.md)
- [03. Spherical grid contract](../action-items/03-spherical-grid.md)
- [02. Diagnostic metrics](../action-items/02-diagnostic-metrics.md)
- [06. Shared simulation preparation](../action-items/06-simulation-preparation.md)
- [07. Deterministic preprocessing and splits](../action-items/07-preprocessing-and-splits.md)

**Verification:** use small segmented fixtures and known analytic fields.
Check ownership, harmonic reconstruction, quadrature, metric values, window bounds, target agreement, empty splits, and failure cleanup.
Serial and parallel preparation must produce the same identified samples.

Add and run regression tests now. CI integration follows in Phase 3.

**Exit:** preprocessing and evaluation agree on sample and target semantics.
Coordinates, rejection policies, and data provenance are explicit.

## Phase 3. Training and fast feedback

**Outcome:** a small complete ML run gives reliable results and quick feedback.

- [01. Shared checkpoint prediction](../action-items/01-checkpoint-prediction.md)
- [04. Reliable training loop and cheap history](../action-items/04-training-loop.md)
- [19. Fast iteration profiles](../action-items/19-fast-iteration.md)
- [12. ML tests and CI](../action-items/12-ci.md)

**Verification:** check save/reload prediction parity, constant channels, sample-weighted scores, invalid settings, and nonfinite failures.
Run the smoke profile through preparation, training, reload, and evaluation.
Record time and memory on named hardware.
Run the same checks in a clean CI checkout and prove a deliberate failure fails the job.

Complete the fixture pipeline before closing item 12.
Extend CI with the regression tests from Phase 2.

**Exit:** one documented CPU recipe completes within its measured budget, produces usable artifacts, and runs in CI.
Development outputs cannot overwrite full results.

## Phase 4. Reproducible pipeline and artifact contracts

**Outcome:** stages consume identified, complete artifacts and preserve experiment history.

- [17. Reproducible simulation runs](../action-items/17-simulation-runs.md)
- [21. Artifact identity and lifecycle](../action-items/21-artifact-lifecycle.md)
- [23. Target and model bundle](../action-items/23-model-contract.md)
- [22. Stage interfaces and runnable recipe](../action-items/22-stage-interfaces.md)
- [18. Local and Slurm entry points](../action-items/18-run-scripts.md)

**Verification:** reject incompatible simulation reuse and propagate exhausted failures.
Check policy-specific catalog decisions, incomplete dataset rejection, relocation, stable identities, and independent training runs.
Run the same scientific specification through local and stubbed Slurm adapters.
Stop after preparation, then continue without rebuilding it.
Load a moved model bundle without raw-data path assumptions.

Use tiny profile and coefficient test heads to verify the bundle interface.
The scientific head design and comparison remain in Phase 8.
Establish stable stage interfaces here. Final legacy deletion and client migration belong to Phase 6.

**Exit:** the small end-to-end recipe uses explicit artifact references.
Changes to scientific inputs invalidate the right artifacts.
Resource changes do not alter scientific identity.
Failures stop dependent stages.

## Phase 5. Scientific evaluation

**Outcome:** scores and research claims have explicit definitions and reproducible evidence.

- [14. Evaluation and research claims](../action-items/14-evaluation-and-research-claims.md)
- [24. Independent evaluation artifacts](../action-items/24-evaluation-artifacts.md)

**Verification:** test informative-input and independent-noise examples.
Require train-derived baselines, explicit coverage, and declared window, simulation, or configuration weighting.
Recompute scores from saved predictions.
Add raw simulations and rerender an old evaluation. Its original results must stay fixed.
Regenerate reports without model or raw-data access.
Check citations and remove unsupported claims.

**Exit:** a frozen protocol identifies the dataset, model, baselines, metrics, and inclusion rules.
Model comparisons use that protocol.
Stored evidence supports every reported score.

## Phase 6. Shared APIs and thin notebooks

**Outcome:** CLI commands and notebooks use the same library behavior.

- [08. Remove legacy code and clarify owners](../action-items/08-remove-legacy-code.md)
- [09. Consistent visualization API](../action-items/09-visualization-api.md)
- [10. Thin, consistent notebooks](../action-items/10-notebooks.md)

**Verification:** check all callers before deleting code.
Run import and command smoke checks.
Verify plotting backend preservation, real coordinates, and figure ownership.
Execute every retained notebook from a fresh kernel on bounded inputs.
Require agreement with CLI predictions, targets, and scores.
For the heat demonstration, verify its extracted solver and time labels or record the explicit archive decision.

**Exit:** each reusable responsibility has one owner.
Clients preserve the contracts from Phases 2-5.
No retained notebook contains copied pipeline logic, stale results, or saved exceptions.

## Phase 7. Documentation and book

**Outcome:** operating instructions describe the system, and the book teaches correct standalone theory.

- [13. Project and operating documents](../action-items/13-project-documents.md)
- [15. Implementation-independent book](../action-items/15-book-scope.md)
- [16. Book mathematics and references](../action-items/16-book-mathematics.md)

**Verification:** follow the restart instructions with the small profile.
Check commands, links, images, historical labels, equations, and citations.
Recompute the listed mathematical counterexamples.
Render the book and maintained presentations. Inspect changed pages.

Earlier phases must update their own affected instructions.
This phase completes the repository-wide audit and removes remaining duplication.

**Exit:** current instructions work, historical records remain clearly dated, and the book requires no knowledge of the implementation.

## Phase 8. Harmonic-head research

**Outcome:** a controlled experiment answers whether a different output head offers a useful benefit.

- [20. Harmonic output head](../action-items/20-harmonic-head.md)

**Verification:** measure target projection error before training.
Check known modes, gradients, physical wind reconstruction, normalization, and checkpoint reload.
Compare heads across fixed datasets, evaluation protocols, budgets, and seeds.
Report accuracy, jet errors, runtime, memory, and parameter counts.
Measure complete-model longitude-shift behavior.
Use development profiles for debugging and full held-out splits for conclusions.

**Exit:** the evidence supports an explicit decision to retain or reject each head.
A negative result is a valid completed experiment.
