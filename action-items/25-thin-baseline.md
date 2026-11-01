# 25. Thin the baseline with cleanup and small refactors

Priority: P1. First implementation phase.

## Outcome

Reduce the supported surface before correctness repairs and architecture work.
Give each retained entry point and document a clear owner.

## Work

Record a keep, remove, or merge decision for each cleanup candidate.
Include caller evidence, the canonical replacement, and any unique historical content.
Start with:

- The unreferenced rollout in `ml/src/ml/inference.py:36-117`.
- Obsolete standalone commands under `ml/src/ml/cmd/`: `rotating_globe.py`, `run_convergence.py`, and `run_variance.py`.
- The old `run-sims.sh` entry point, superseded wrappers, and stale debugger targets.
- Unused imports, commented-out code, abandoned TODO prose, and incorrect implementation-history comments, including the asdict claim in `ml/src/ml/training/model.py:26`.
- Duplicate Isca setup instructions and competing presentation sources. Choose one maintained source before merging or removing redundant material.

Remove code only after checking Python imports, notebooks, scripts, package entry points, and documented use.
Migrate a useful caller to its existing supported replacement before removing the old path.
Keep helpers with live callers.

Merge exact duplicates and make small responsibility-preserving moves.
Compare dimensions, units, defaults, and failure behavior before treating code as equivalent.
If implementations disagree, record the difference and leave semantic unification to its owning correctness item.

For documents, preserve unique instructions and research evidence in the retained destination.
Delete superseded files or sections and update their links.
Keep dated experiment results as historical records.
Preserve simulation data, checkpoints, submodule pins, and local Isca changes.

Bootstrap the existing locked dependencies needed by affected checks.
The later environment item defines and validates the full supported environment set.
This phase does not require the later fixture pipeline or new model training.

## Verify

1. Before edits, record retained entry points, callers, current import/help/config checks, and known failures.
2. For every removal, retain caller-search evidence and its keep/remove/merge decision. For every merge, name and check the destination.
3. Check retained imports, CLI help, all checked-in ML configs, shell syntax, and document links after edits.
4. For moved or unified live logic, compare fixed-input outputs before and after, including shapes, units, and failure cases. Require behavior parity.
5. Search for dangling imports, command names, file references, and duplicate maintained sources. Require none introduced by cleanup.
6. Require no new failures in retained behavior. An existing failure may remain only if unchanged and linked to its later repair item.
7. Review the complete diff for accidental scientific changes or loss of unique historical material.

Completion is a smaller supported surface with explicit owners and verified retained behavior.
Do not use a line-count target.
Live-path refactoring continues in 08, operational script changes in 18, and the full document audit in 13.
