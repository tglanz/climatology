# Workplan

Complete these three phases in order.
For each phase: implement, verify, review the diff independently, resolve findings, then proceed.
Record results and any checks that could not run. Do not count skipped checks as passed.

## Phase 1. Code and document compaction

[Action item](../action-items/01-compaction.md)

Remove unneeded code and documents. Consolidate repeated functionality into library APIs and make notebooks use them. Split responsibilities sensibly and use consistent terms. Comments and documentation should describe the current state.

Keep computational logic unchanged.

**Done when:** the retained project is smaller and clearer, representative results are unchanged, and callers, notebooks, and documents have been checked.

## Phase 2. Functional correctness

[Action item](../action-items/02-correctness.md)

Fix the identified preparation, training, and evaluation errors in the shared code. Focus on changes that affect samples, targets, predictions, and scores.

**Done when:** focused regression tests and a small complete experiment demonstrate the intended behavior, and the fixes have been reviewed.

## Phase 3. Pipeline reconsideration

[Action item](../action-items/03-pipeline.md)

Reconsider stages, data passed between them, configuration, saved results, and execution together. Include small experiments through the same pipeline.

**Done when:** one documented workflow can run, reuse prepared data, save and reload a model, and reproduce evaluation. A small run provides useful feedback for routine changes.

Phase 1 is complete with recorded verification limits. Its [implementation record](../action-items/01-compaction-results.md)
tracks checks and remaining limits. Phase 2 is complete with recorded verification
limits; see its [results](../action-items/02-correctness-results.md). Phase 3 remains planned.
