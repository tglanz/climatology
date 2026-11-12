# Pipeline implementation results

Implemented on `3-pipeline` on 2026-11-12. The
[pipeline architecture](../docs/pipeline.md) is the operational reference: stages,
intermediate artifact formats and schemas, a flow diagram, commands, and limits.

## Trace and decisions

The initial trace followed `ml/configs/lat0-extra-hi-hold-out.toml` through
split generation, HDF5 preparation, training, and model evaluation. Training
already obtained coordinates from prepared data after phase 02. Evaluation still
rebuilt windows from current raw trajectories and read current sweep metadata.

Preparation now publishes a completed artifact containing all three splits,
simulation/window ownership, source selection provenance, assignments, the data
recipe, optional sweep metadata, and SHA256 hashes. Model iterations reuse it.
Training saves a standalone configuration and a manifest reference in a fresh run
directory. Evaluation predicts from the exact saved inputs and retains physical
profiles, scores, figures, and input hashes. Data-only commands do not require
model or training configuration. Existing artifacts and Isca patches are preserved.

Local and Slurm runs use the same pipeline entry point. The two-job submission
helper uses `afterok` dependencies. Training failure stops evaluation. Existing
prepared and run destinations fail explicitly instead of repeating unrelated work
or rotating previous results.

## Verification

The complete ML suite passes: **55 tests**. The pipeline integration tests cover
preparation through checkpoint loading and evaluation, two models reusing one
prepared artifact, raw trajectory removal, relocated runs and prepared inputs,
changed-file rejection, existing-output preservation, failed preparation cleanup,
and excluded validation trajectories. Existing scientific correctness tests still
pass, including two-target evaluation and unequal windows per simulation.

Pylint's repository error gate, Black's Python formatting check, `git diff --check`,
and shell syntax checks pass. Black reports that notebook formatting support is
not installed; notebook sources were not changed. Pytest retains the existing
NetCDF/NumPy binary-size warning and a figure `tight_layout` warning.

A separate manual diff review checked configuration snapshots, split membership,
empty splits, failure propagation, coordinate identity, and report regeneration.
It led to reusing device preparation across simulations, retaining only prediction
profiles for reports, recording all checkpoint input hashes, and preserving custom
metrics paths when a run moves.

### Measured normal-pipeline examples

Commands use the documented recipe with `--device cpu`, two epochs, seed 17,
serial preparation, and separate output directories. Measurements use macOS
`/usr/bin/time -l`; maximum resident set size is converted from bytes to MiB.
These are single warm-environment measurements, not performance guarantees.

| Example | Stage | Wall time (s) | Maximum RSS (MiB) |
|---|---|---:|---:|
| Synthetic, three short trajectories | Preparation | 1.82 | 386.3 |
| Synthetic | Train + evaluate, width 4 | 2.66 | 478.2 |
| Synthetic | Train + evaluate, width 6 | 2.62 | 475.3 |
| Fixed three real trajectories | Preparation | 6.99 | 1513.0 |
| Real subset | Train + evaluate, width 4 | 2.83 | 567.3 |
| Real subset | Train + evaluate, width 6 | 2.85 | 600.8 |

The real subset is `10bb40-0` (train), `0f0ad6-0` (validation), and `021787-0`
(test), with two windows per trajectory on the original Gaussian grid. Default
spinup, convergence, and target averaging remain active. Both models use a
one-layer SFNO with modes `(4,4)`. The synthetic example uses eight Gaussian
latitudes, 24 longitudes, and three windows per trajectory. Neither experiment
supports a model-quality claim.

Each measured checkpoint was loaded again and evaluated with raw-sample access
replaced by a failing guard. Scores and saved physical profiles reproduced
exactly on CPU with the same batch size. Each run's saved manifest matches the
same prepared bytes before and after model iterations.

Local evidence is retained under `output/pipeline-20261112-smoke/`,
`output/pipeline-20261112-real/`, and `output/pipeline-20261112-summary.json`.
Original experiment outputs remain untouched. These ignored artifacts are not
included in Git.

## Limits

Actual Slurm jobs were not submitted: this workstation has no cluster scheduler.
Tests check argument construction, `afterok`, failed submission, and propagation
of a failing local program through the exact Slurm wrapper using controlled
command substitutes. CUDA/MPS and full-scale training were not run. Preparation
still materializes one raw trajectory per worker, so memory use scales with source
size and worker count. Hash verification adds a full sequential read per stage.
Small CPU runs provide routine workflow feedback; large-run resource sizing
remains an explicit experiment choice.

Prepared datasets are shared references, not copied into every run. Retain them
with the run and repository lockfile. Legacy artifacts without a completed
manifest require new preparation and training. Checkpoint loading remains
available independently for older compatible normalization artifacts.
