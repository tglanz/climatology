# 02. Correct preparation, training, and evaluation

**Change:** fix the functional errors in the shared code left after step 01.

## Preparation

- Make preprocessing and evaluation use the same window, target, and convergence rules. Evaluation currently substitutes the final snapshot when convergence is missing, while preprocessing rejects that simulation.
- Keep the last valid input window and honor every configured target variable.
- Make the reader's cache work, stop validation from closing a caller's dataset, and reject splits with no training samples.

Start in `ml/src/ml/data/` and `ml/src/ml/diagnostics/evaluation.py`.

## Training

- Use the actual Isca latitude grid in SFNO and in calculations that depend on coordinates. The current transform defaults to an equiangular grid, while the data uses Gaussian latitudes.
- Use the same normalization during training and after loading a checkpoint. Evaluation currently omits the epsilon added during training.
- Average reported losses by sample count. A short final batch currently counts as much as a full batch.
- Reject invalid settings and stop on nonfinite losses before updating weights.

Start in `ml/src/ml/training/`, `config.py`, and the shared prediction code.

## Evaluation

- Correct latitude-weighted profile errors and the broken spectrum helper.
- Build train baselines from train data only. The current fallback can use test targets.
- Describe replicate variability accurately; it is not automatically a minimum possible prediction error.
- Make scores, plot labels, and reports agree with what was computed. Do not include figures left over from a previous evaluation.

Start in `ml/src/ml/diagnostics/` and the evaluation code extracted from `cmd/evaluate.py`.

**Why:** these errors can change which samples are used, what the model learns, and the scores used to judge it. Source inspection and small checks established the defects; their effect on overall model quality has not been measured.

**Verify:**

1. Add focused regression tests with small inputs and known answers for the defects above.
2. Require preprocessing and evaluation to produce matching windows and targets. Check short and nonconverged simulations, empty training splits, and repeated reads of the same file.
3. Check transforms and weighted metrics on known fields using the actual grid.
4. Save and reload a small model. Require the same predictions. Require the reported validation score to be independent of batch partitioning.
5. Check that baselines never use test truth and that reports contain only the current results.
6. Run one small preparation, training, reload, and evaluation experiment. Review both the fixes and their results before proceeding.
