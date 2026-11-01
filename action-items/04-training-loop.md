# 04. Make training scores reliable and cheap

Priority: P1.

## Evidence

`ml/src/ml/training/trainer.py:260-272` averages batch means equally.
`training/baselines.py:11-25` repeats that reduction.
A partial final batch changes the reported score and can change checkpoint selection.
Relative losses divide by the target norm without a zero policy.
`config.py:354-362` accepts invalid positive-range settings.
Scalar CSV history only runs under expensive field tracking at `trainer.py:165-220`, which also adds another validation pass.

## Work

Use sample-weighted epoch and baseline scores. Reject invalid settings at load.
Fail before an optimizer update on nonfinite loss.
Always save cheap scalar history. Give field diagnostics a separate cadence and subset.
Correct help text that promises artifacts the implementation does not write.

## Verify

1. Add `test_training_loop.py`. Use 65 fixed sample losses: 64 equal to 1, one equal to 9. Score must be `73/65` for batch sizes 1, 16, and 64. Check baselines too.
2. Reject epochs=0, nonpositive batch size or learning rate, and invalid gradient clipping.
3. Exercise the chosen zero-target policy. Inject NaN and assert no optimizer step or checkpoint replacement occurs.
4. Run two tiny CPU epochs with field diagnostics off. Require two scalar records and a checkpoint.
5. Enable diagnostics every two epochs. Require one diagnostic update and no unnecessary second validation pass.
