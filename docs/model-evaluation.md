# Model evaluation

The current model maps windows of vorticity snapshots to climatological
zonal-mean zonal wind profiles. Forcing configurations use hash codes from the
sweep metadata. Run from the repository root:

```bash
uv run --project ml --group train --group vis ml evaluate model --training-dir <training-dir>
```

The command loads the saved configuration, parameters, normalization, and split
manifest. It then reads every simulation currently present under the training
directory's parent experiment. It rebuilds inputs from raw NetCDF data, predicts
each window, and averages predictions within each simulation.
The [norms reference](norms.md) defines the reported metrics.

## Report sections

| Section | Current calculation |
|---|---|
| Training | Training and validation losses from the saved CSV |
| Baselines | Zero prediction, mean training truth, nearest training configuration, and model, scored on test simulations |
| Replicate variability | Mean relative L2 deviation of replica targets from their configuration mean |
| Generalization | Error against each varying forcing parameter, plus profiles for the six worst configuration codes |
| Error structure | Test error profiles, relative L2 histogram, and jet latitude and amplitude comparisons |
| Model versus variability | Configuration-level model error against replicate deviation |

The nearest-configuration distance uses Euclidean distance after normalizing
parameters by their ranges among the available training configurations. Constant
parameter ranges are replaced by one. The predictor averages training target
profiles for the selected configuration.

Jet latitude uses the location of the largest absolute profile value; amplitude
uses its absolute magnitude. Error profiles are computed per simulation after
averaging its window predictions.

## Existing limitations

Compaction preserves the calculations and legacy figure labels. The sections
named "noise floor" measure replicate variability. This statistic alone does not
establish an irreducible prediction-error bound.

Preparation rejects missing convergence; CLI evaluation substitutes the final
snapshot index. CLI evaluation uses the first configured target, whereas
preparation can build several. Notebook evaluation also retains distinct window
selection and metric conventions.

Loaded-model prediction omits the epsilon used during training normalization.
Metrics and plots retain the grid and weighting behavior described in
[norms](norms.md). If no training simulations load, the global baseline can fall
back to test targets. Reports can include figures left from an earlier evaluation.
These issues remain assigned to [action item 02](../action-items/02-correctness.md).

The prepared-sample and by-code notebooks expose their original analyses through
library calls. They are not interchangeable with the CLI's selection policy.
Workflow and saved-input redesign belong to
[action item 03](../action-items/03-pipeline.md).

## Output

The command writes `<training-dir>/evaluation/report.md` and figures under
`<training-dir>/evaluation/figures/`.

To make a PDF from an existing report:

```bash
pandoc <training-dir>/evaluation/report.md -o <training-dir>/evaluation/report.pdf
```
