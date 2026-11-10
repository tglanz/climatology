# Compaction implementation results

Completed [action item 01](01-compaction.md) on branch `compaction`, with the
verification limits below. Computational behavior and saved artifact formats are
unchanged. Correctness and pipeline redesign remain separate phases.

## Missing import followup

The missing `cosine_latitude_weights` import in `diagnostics/spectra.py` is now
repaired. This restores the intended function call without changing the spectrum
formula. Deferring this wiring repair was unnecessary.

The ML suite now has 19 passing tests. A new regression checks a known Fourier
mode and batch scaling against analytical power values. Both previously blocked
notebooks, barotropic visualization and other visualizations, now pass fresh
kernel execution on the same bounded fixtures. All nine notebooks have therefore
passed bounded checks across the original run and this followup. Saved notebook
outputs remain unchanged. The spectrum module's undefined-name check passes.

The tables below retain the original compaction measurements and historical
failures; their equivalence results predate this intentional failure-to-success
repair. GPU, full real-data, scheduler, and native Quarto verification limits
remain unchanged.

## Completed batches

| Batch | Result |
|---|---|
| 1 Baseline and inventory | Captured original source, configurations, numerical outputs, failures, and Isca patch state |
| 2 Diagnostics | Calculations live in owning modules; package-root re-exports and unused APIs removed |
| 3 Shared data mechanics | Timeline and channel stacking shared; preparation and evaluation retain distinct policies |
| 4 Prediction and evaluation | Shared checkpoint and prediction API; evaluation orchestration and reports extracted from CLI |
| 5 ML notebooks | All reusable functions moved into the library; original settings and saved outputs preserved |
| 6 Heat demonstration | Solver and visualization moved into its own package; placeholder entry point and test replaced |
| 7 Obsolete paths | Callerless paths removed; utility collection separated from printing; distinct wrappers retained |
| 8 Documents and book | Setup and parameter references consolidated; current methods documented; verified theory errors corrected |
| Independent review | One introduced plot dependency found, fixed, and independently verified; zero open findings |

## Baseline and provenance

- Baseline revision: `911c6d0f27c8a07b8f13956afe721ab4708a82e0`.
- Initial changes: the compaction plan and its action-item link, plus six modified
  Isca files. Those Isca changes remain byte-for-byte unchanged.
- Isca pin: `a290bc376d84d0ee83adbb80eb374b9f629c3534`.
- Neuraloperator pin: `98cd305099f4a2b232ed85773984f3e5991f9b1a`.
- ML runtime: Python 3.13.13, NumPy 2.4.4, xarray 2026.4.0, Torch 2.11.0,
  neuraloperator 2.0.0, pytest 9.0.3, nbconvert 7.17.1, Matplotlib 3.10.9.
- The heat environment was installed from its existing lockfile. Dependency
  declarations, lockfiles, third-party pins, and runtime patches were preserved.

Numerical fixtures use 12 snapshots across two NetCDF segments, four latitudes
`[-65, -20, 20, 65]`, and 12 longitudes. Values are
`arange(12*4*12).reshape(12,4,12)/100 + 1`, converted to float32, with offsets
0, 2, and 4 for vorticity, zonal wind, and meridional wind.
Input variables are vorticity and meridional wind, with window length 3, stride 2,
and limit 4. Targets use the final two snapshots. Separate cases cover short
input, multiple targets, and missing convergence.

Real prediction comparisons use the existing `training-inter-hold-out`
checkpoint and the first two input samples from the existing `data/test.h5`,
shape `(2, 10, 128, 256)`. The saved configuration uses the old location for
`experiment_dir`. Only a temporary copy gained the required `[paths]` section;
the original configuration and weights were not changed. SHA256 hashes of the
saved configuration, parameters, normalization, and selected inputs are in the
review evidence's `provenance.json`.

CPU repeat predictions had maximum absolute difference 0. The comparison
tolerance was therefore 0, with exact shape and dtype agreement required.
All 19 captured arrays matched exactly.

Tiny-model tests use seed 17 for checkpoint reloading and seed 23 for notebook
and CLI fixtures. The heat comparison uses seed 31 and a rectangular 5 by 8
initial field. No model was trained and no new Isca simulation was launched.

## Retention and deletion decisions

Caller checks covered source, notebook source cells, scripts, command
registrations, and documentation. Directly executable files were treated as
entry points even if they had no import callers.

| Material | Decision and evidence |
|---|---|
| Scanner, simulation runner, purge tool | Retained distinct operations; no experiment data was purged |
| Preparation, training, monitoring, analysis, evaluation, utilities | Retained command names and options |
| Diagnostic root module | Retained as a package marker; calculations and callers moved to owners |
| Autoregressor and persistence helper | Removed; no retained callers, and both served the retired next-step forecasting path |
| Old convergence and variance scripts | Removed; no retained entry-point references; shared convergence and replicate analyses replace them |
| `run-sims.sh` | Removed; obsolete numeric-directory loop and obsolete simulation entry point |
| Unused spectrum APIs | Removed `zonal_power_spectrum_torch`, `error_power_spectrum`, `signal_power_spectrum`, and `spectrum_residual`; no retained callers |
| Unused plotting APIs | Removed `plot_meridional_profile`, `plot_noise_floor_code`, and `plot_per_config`; no retained callers |
| Rotating globe and executive talk generator | Retained; reading, calculations, and rendering now have separate owners |
| `eval_test.py` | Retained as a small runner for the shared sample-evaluation APIs |
| Both convergence notebooks | Retained as thin examples with distinct paths and historical outputs; their shared analysis has one implementation |
| NetCDF and other visualization notebooks | Retained for distinct field views, errors, spectra, and the exploratory advection residual |
| Submission wrappers and replica-specific Slurm jobs | Retained: path handling, environment export, replica counts, and resources differ |
| Shell ML invocations | Updated to select `--project ml` from the repository root; scheduler and notification behavior unchanged |
| Heat placeholders | Removed unused greeting command and no-op test; the notebook is the demonstration entry point |
| Dated trial proposal and talks | Retained historical settings and results; proposal gains an explicit history marker |
| Harmonic-head exploration and study presentation | Preserved separately from maintenance |

No raw data, prepared experiment data, saved model, log, historical notebook
output, or unique research result was deleted.

## Original numerical and command verification

| Check | Result |
|---|---|
| ML tests | 18 passed, including weighted gradients, checkpoint reload, and ten independently rendered field views |
| Heat tests in its own environment | 3 passed |
| Before and after calculations | 19 arrays exactly equal, including real checkpoint predictions |
| Original heat functions versus package | Four rectangular-grid snapshots exactly equal |
| Report sections and utility output | 15 files byte-identical: report, tables, two fingerprints, and 11 PNG figures |
| Retained command help | All 24 command and group help paths passed |
| Actual CLI operations | Preparation, model information, preprocessing fingerprints, and complete CPU evaluation passed |
| Prepared CLI fixture | Train, validation, and test each contain `x=(2,10,4,16)`, `y=(2,1,4)`, float32 |
| Simulation entry point | `conda run -n isca_env python -m sim.scanner --help` passed; no compilation or run |
| Shell syntax | All 20 retained shell and Slurm files passed `bash -n` |
| Explicit scan of all retained modules | Only the existing weighted-spectrum undefined name remains |
| Stored notebook results | Outputs in all nine notebooks exactly match the baseline |
| Notebook structure | Code lines reduced from 1594 to 271; no notebook function definitions remain |
| Source plus notebook code | 8345 to 8164 lines, excluding tests, docs, generated files, and third-party code |
| Isca local patch | Exact diff preserved; both submodule pins unchanged |
| Diff formatting | `git diff --check` passed |

The CLI smoke run used isolated temporary files, a tiny FNO, one evaluation
worker, batch size 2, and an explicit CPU device override. It did not write to
the repository's `output/` directory or submit jobs.

The ML run emits a NumPy/netCDF import warning. The original wind-direction
layout also emits a Matplotlib tight-layout warning. Neither was counted as a
failed test or silently suppressed in the recorded suite.

## Original fresh kernel notebook checks

Every notebook ran in a separate kernel. Temporary copies selected synthetic
simulation directories and a tiny FNO checkpoint. CPU selection was explicit.
Simulation fixtures contain 40 time samples on a 4 by 16 grid. The heat check
used an 8 by 10 grid and 12 steps. Original notebook files and their saved outputs
were not overwritten by these executions.

| Notebook | Original source on bounded fixtures | Compacted source |
|---|---|---|
| Barotropic visualization | Missing `np` import | Reaches existing spectrum failure |
| Prepared-sample model evaluation | Unsupported `zonal_mean` argument | Passed |
| By-code model evaluation | Unsupported `zonal_mean` argument | Passed |
| Replicate variability | Passed | Passed |
| Convergence | Passed | Passed |
| Long-run convergence | Passed | Passed |
| NetCDF processing example | Stale `fix_time_units` import | Passed |
| Other visualizations | Stale `ml.isca_dataset` import | Reaches existing spectrum failure |
| Heat equation demonstration | Passed | Passed |

Seven notebooks pass. Two fail at the known
`lat_weighted_zonal_power_spectrum` missing import. That defect is also
reproduced by calling the original function directly. The late field views
beyond that failure are independently rendered in the test suite, so an early
notebook failure does not hide their extraction errors.

## Documentation verification

Changed relative document links resolve. All six citation keys used by the book
exist in its bibliography. Primary arXiv metadata was checked for the cited SFNO,
GSNO, and practical FNO papers; bibliography URLs were added.

The book corrections cover polynomial-space dimension, normalized Fourier
coefficients, square-wave continuity and Gibbs overshoot units, the distinction
between spherical separation and a regular interval Sturm-Liouville problem,
and architecture commitments in general theory. The coefficient normalization
follows directly by substituting
`phi_n = exp(i*n*x)/sqrt(2*pi)` into the stated inner product. A degree-n
polynomial space has the basis `1,x,...,x**n`. These corrections affect prose
and equations only.

Eight changed chapters rendered together with Pandoc, citation processing, and
native MathML. The HTML contains 264 mathematical expressions, a bibliography,
no MathML error nodes, and no unresolved-citation marker. Quarto is not installed.
Full Quarto navigation, chapter cross-references, and native preview inspection
remain unverified; the Pandoc render is not counted as a Quarto render.

## Differences reserved for later phases

Phase 2 still owns the convergence fallback difference, first-target evaluation,
last-window omission, notebook selection variants, metric broadcasting and
epsilon differences, loaded-model normalization epsilon, cache truthiness,
dataset-closing validation, actual grid handling, loss aggregation, baseline
fallback, scientific figure labels, and stale report-figure selection.

Phase 3 still owns configuration, prepared-data reuse, saved artifact design,
and local versus Slurm execution. Neither phase was started.

## Independent review and reproducible evidence

The `tg-cr` review used separate correctness, tests, and scope reviewers, followed
by an adversarial pass. It found one introduced issue: the extracted globe
evolution plot lacked its formerly notebook-global coordinate transform. The
function now creates that transform locally. Its direct rendering check and
the ten-view test suite pass. The adversary verified the fix and the subsequent
callerless-API removals. Final open findings: 0.

An initial external comparison harness could select the archived package during
an after run. Its import precedence was corrected, module paths were recorded,
and numerical, report, and CLI checks were rerun against the actual current
source. The adversary independently checked the corrected import provenance and
exact comparisons. Earlier ambiguous comparisons are superseded.

Durable evidence and review files are stored locally at:

`/Users/tal.glanzman/obsidian/reviews/1011-climatology-compaction/`

The `evidence/` directory contains original source, executable comparison
scripts, arrays, notes, module import paths, model hashes, report artifacts,
notebook outcomes, CLI output, and the chapter render. Executed notebook copies
and initial scratch files remain at:

`/var/folders/4p/1s3ml81d7sx9zjdx06ttqs8r0000gp/T/climatology-compaction-l3spzfu9/`

Run durable suites from the repository root:

```bash
uv run --project ml --group dev --group train --group vis pytest ml/tests
uv run --frozen --project heat-simulation --group dev pytest heat-simulation/tests
```

To regenerate the comparison evidence with the original local data still present:

```bash
EVIDENCE=/Users/tal.glanzman/obsidian/reviews/1011-climatology-compaction/evidence
uv run --no-sync --project ml python "$EVIDENCE/compare.py" "$EVIDENCE/before"
uv run --no-sync --project ml python "$EVIDENCE/compare.py" "$EVIDENCE/after-final"
uv run --no-sync --project ml python "$EVIDENCE/check_report.py" "$EVIDENCE" before
uv run --no-sync --project ml python "$EVIDENCE/check_report.py" "$EVIDENCE" after
uv run --no-sync --project ml python "$EVIDENCE/final_checks.py" "$EVIDENCE"
```

GPU execution, a full real-data notebook run, a fresh simulation, and scheduler
execution were not performed. Native Quarto checks remain unavailable. The
historical spectrum failures listed above are resolved by the import followup.
