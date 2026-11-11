# Action items

Three work items, implemented in order:

| Item | What | Why |
|---|---|---|
| [01. Compaction](01-compaction.md) | Remove unneeded material, consolidate code, and make notebooks use library APIs. | Establish a smaller, clearer baseline without changing its logic. |
| [02. Correctness](02-correctness.md) | Fix functional errors in preparation, training, and evaluation. | Make the samples, predictions, and scores trustworthy. |
| [03. Pipeline](03-pipeline.md) | Reconsider stages, data, configuration, saved results, and small experiments together. | Make experiments straightforward to run, repeat, and extend. |

The [workplan](../docs/workplan.md) gives the phase gates.
Compaction is complete, with recorded verification limits; see its [implementation results](01-compaction-results.md).
Correctness is complete with recorded verification limits; see its [results](02-correctness-results.md).
Pipeline redesign remains planned.

Each item includes what to change, why, and verification steps.
Small setup and implementation details belong inside this work, not in separate projects.

The harmonic-head thesis idea remains separate from this maintenance plan.
The [study presentation](../presentations/bve-harmonics-sfno/README.md) remains available.
