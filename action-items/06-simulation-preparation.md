# 06. Share simulation preparation

Priority: P1. Needed by notebooks and evaluation.

## Evidence

`ml/src/ml/data/isca_preprocessing.py:69-126` and `diagnostics/evaluation.py:82-168` independently compute anchors, targets, and windows.
Preprocessing rejects missing convergence at lines 88-92.
Evaluation substitutes the final snapshot at lines 127-129.
Evaluation uses only the first target variable at line 108, while preprocessing stacks all targets.
`data/window_selector.py:51` retains the old next-step bound M-K-1.
The current climatology input needs only K snapshots, as `config.py:107` states.

## Work

Give sample preparation one data-layer owner.
Share target intervals, channel order, window selection, and failure policy.
Keep numerical diagnostics separate from file loading and orchestration.
Use M-K as the final valid start for the climatology task.
Align the validator and `docs/pre-processing.md` with the same contract.

## Verify

1. Add `test_simulation_preparation.py` using a small segmented trajectory.
2. Preprocessing and evaluation must produce identical anchors, starts, channel order, targets, and rejection reasons.
3. Force nonconvergence. Both callers must use the same explicit policy.
4. Check multiple target variables, or reject that configuration before inference if the evaluator intentionally supports one.
5. For K=3, M=3 must yield start [0], and M=4 must yield [0, 1]. Check convergence caps, stride, limit, and missing anchors.
