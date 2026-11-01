# 24. Make evaluation an independent scientific artifact

Priority: P1. System design. Build on 01, 02, 06, 14, and 21.

## Evidence

`ml/src/ml/cmd/evaluate.py:55-77` derives raw-data location from the training directory and scans current simulations.
Window predictions are averaged and discarded at lines 157-179. The current outputs retain reports and figures rather than reusable prediction arrays.
Inference, scoring, figures, and report assembly share the CLI implementation.
This makes it hard to rerender, audit a score, or compare heads against a frozen evaluation.

## Work

Define an evaluation specification with bundle ID, dataset/split ID, protocol version, inclusion policy, baselines, and metrics.
State whether each result weights windows, simulations, or forcing configurations.
Distinguish training's normalized objective from scores in physical units.

Persist identified predictions and truths, metric tables, and inclusion/exclusion counts.
Persist baseline predictions or their train-derived artifact and source identities so baseline scores can be recomputed without raw data.
Keep enough detail to recompute supported scores and aggregations.
Render figures and reports from that result.
A new raw population creates a new prepared evaluation dataset.
A metric change can rescore stored predictions. A plot change can rerender without inference.
Document which target population each holdout tests.

## Verify

1. Create E1, then append raw simulations. Rerendering E1 must preserve its original dataset, predictions, scores, and coverage.
2. Remove raw-data and model access. Regenerate E1's report from its stored results.
3. Recompute one score and baseline independently from persisted arrays. Require equality within the stated tolerance.
4. Check window, simulation, and configuration aggregations on a fixture with unequal group sizes. Require each declared weighting rule.
5. Force missing predictions or rejected inputs. Record exact counts and reasons, and fail if protocol coverage requirements are unmet.
6. Compare two heads. Require identical evaluation dataset and protocol IDs, with their model bundle IDs recorded separately.
