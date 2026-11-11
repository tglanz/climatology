# Project compaction implementation plan

Implement [action item 01](01-compaction.md) in eight small batches. The result should have one clear home for repeated work, notebooks that call library functions, and documentation that matches the retained project.

**Status:** completed on branch `compaction`, with recorded verification limits. See the
[implementation results](01-compaction-results.md) for progress and verification.

This is the original implementation plan. A later scope decision retired the
standalone heat demo and its CI; batch 6 below is historical. The retained CI
checks are ML lint and tests. See the results for the retirement and CI followup.

Read the overview first. Each batch below states what to change and how to decide whether it is complete.

## Scope and boundaries

Preserve formulas, algorithms, normalization, data selection, targets, model behavior, and saved artifact formats. Preserve operation order, array shapes, dtypes, channel order, configuration defaults, split membership, and random seeds.

Keep simulation output, prepared data, checkpoints, logs, and unique historical results. Preserve submodule pins, local patches, and unrelated changes. The Isca submodule already has local changes; record that state before implementation.

Scientific corrections belong to [action item 02](02-correctness.md). Changes to stages, configuration design, saved data, and local versus Slurm execution belong to [action item 03](03-pipeline.md).

A stale import or obsolete function argument may be repaired here when the intended replacement is unambiguous and preserves the computation. Record that repair separately from code moves. Do not use cleanup as a reason to change scientific behavior.

## Work order

| Batch | Main change | Evidence needed to finish |
|---|---|---|
| 1 | Inventory callers and capture current behavior | Retention decisions, small reference inputs, and existing failures recorded |
| 2 | Give diagnostics clear owners | Callers use the owning modules; moved calculations agree |
| 3 | Share data reading and array construction | Each caller retains its own samples, targets, and failure behavior |
| 4 | Extract prediction and evaluation from commands | CLI and library calls agree on predictions, scores, and report contents |
| 5 | Reduce ML notebooks to settings and library calls | Every notebook has a recorded disposition and execution result |
| 6 | Move the heat demonstration into its package | The notebook and package produce the same fields |
| 7 | Remove obsolete paths and finish module cleanup | Every deletion has a caller check and a retained replacement where needed |
| 8 | Consolidate documents and correct the book | Instructions, theory, links, and changed chapter renders checked |

Follow this order. After each batch, run its focused checks and review the diff before starting the next. Batch 1 chooses what to retain; batch 7 completes deletion after replacements have been verified.

## 1 Inventory the project and capture a baseline

**Purpose:** establish what must keep working before moving or deleting code.

1. Record the Git revision, dirty files, submodule state, installed Python and dependency versions, and available runtimes.
2. Trace the registered commands in `ml/src/ml/cmd/cli.py`, directly executable modules, shell and Slurm scripts, notebook imports, and documented commands. A file does not need an import caller to be a useful entry point.
3. Give each relevant script, notebook, API, and document one disposition: retain, consolidate, remove, or defer. For removal, name the replacement or explain why no unique behavior or result remains.
4. Select small inputs for before and after comparisons:
   - A deterministic synthetic simulation with multiple NetCDF segments, distinct variables, and identifiable time and spatial coordinates.
   - Short and nonconverged inputs, a window crossing a segment boundary, and one versus several target variables.
   - A fixed small subset of available real simulations and an existing checkpoint, if available.
   - A small heat grid with an off-center source and boundary cells.
5. Capture file and simulation ordering, selected window starts, targets, coordinates, shapes, dtypes, predictions, metrics, and representative figure data. Record configurations, seeds, input paths or hashes, and the device.
6. Classify checks as passing, existing failure, or unavailable. Read errors from actual small runs where practical; source inspection alone does not establish that a notebook runs.

Use one implementation record, `action-items/01-compaction-results.md`, for the inventory, baseline, differences deferred to later phases, and verification results. Create it when implementation starts. Keep large reference arrays in a separate scratch directory and record how to reproduce them.

**Complete when:** retained workflows and their reference inputs are explicit. A missing dataset or checkpoint is recorded as a verification limit, never as a pass.

### Differences that must remain visible

The current code already contains differences that block unconditional merging:

| Difference | Locations to compare | Treatment in this phase |
|---|---|---|
| Missing convergence rejects a simulation in preparation but falls back to the final index in evaluation | `data/isca_preprocessing.py`, `diagnostics/evaluation.py` | Preserve each caller's policy |
| Preparation builds all configured targets; evaluation uses the first | Same files | Preserve target count and layout per caller |
| Window bounds and limits differ between the by-code notebook and the shared selector | `climatology_model_evaluation_by_code.ipynb`, `data/window_selector.py` | Record exact selected indices before extraction |
| Training and loaded-model prediction differ in normalization epsilon | `training/trainer.py`, evaluation and prediction paths | Move existing behavior without correcting it |
| Profile metrics differ in broadcasting and denominator epsilon | `diagnostics/errors.py`, `diagnostics/evaluation.py`, evaluation notebooks | Keep distinct formulas identifiable until phase 2 |
| The reader cache and dataset validation have known defects | `data/isca_segment.py` | Preserve and record them for phase 2 |

If two paths differ, share only the identical mechanics. Keep a small named adapter for the differing behavior, with a link to the recorded difference. Avoid a general framework with many compatibility flags.

## 2 Give diagnostics clear owners

**Main files:** `ml/src/ml/diagnostics/`, `training/loss.py`, and all diagnostic callers.

1. Move the actual computations from `diagnostics/__init__.py` into the appropriate modules. Put error calculations in `errors.py`; keep spatial reductions, spectra, enstrophy, spinup, and convergence in their existing modules.
2. Replace imports from the package root with imports from the owning module. Check notebooks and directly executable modules as well as the main CLI.
3. Compare the profile metrics in evaluation and notebooks with the existing error functions. Consolidate equal formulas. Keep differing formulas as explicitly named functions in the same owning module until phase 2.
4. Review `persistence_prediction` as a deletion candidate. Keep it only if a retained workflow needs it.
5. Leave the known spectrum helper defect and metric corrections to phase 2.

**Check:** compare moved functions against the baseline on supported field and profile shapes, including zeros and batch dimensions. Require the same outputs or the same existing failure. Check imports after removing re-exports.

**Complete when:** diagnostics have identifiable owners and package initialization contains no scientific calculations.

## 3 Share data reading and array construction

**Main files:** `data/isca_segment.py`, `data/isca_preprocessing.py`, `data/climatology.py`, `data/window_selector.py`, and `diagnostics/evaluation.py`.

1. Keep low-level NetCDF reading and time decoding in `isca_segment.py`. Preserve the distinction between raw numeric time and decoded plotting time.
2. Extract repeated simulation timeline construction, field gathering, and input-channel stacking into one focused data module, proposed as `data/simulation_data.py`.
3. Make preparation and evaluation call those shared mechanics. Keep their existing convergence policy, target selection, dtype conversion, ordering, and error handling in small caller adapters.
4. Keep climatology window resolution in `climatology.py` and window selection in `window_selector.py`. Preserve their current bounds.
5. Move reusable loading from diagnostic scripts and notebooks into the data layer where behavior agrees. Library modules must not import readers from `cmd/rotating_globe.py`.
6. Keep preparation orchestration in `usecases/preprocess.py`, including current worker and output-writing behavior.

**Check:** compare exact input arrays, target arrays, selected indices, and ordering for each caller separately. Cover segment boundaries, short inputs, absent convergence, multiple variables, and target layouts. Do not require preparation and evaluation to agree where they already differ.

**Complete when:** identical array construction has one implementation, and every remaining difference has a named owner and a phase 2 note.

## 4 Extract prediction and evaluation from commands

**Main files:** `cmd/evaluate.py`, `inference.py`, `diagnostics/evaluation.py`, `visualization/evaluation.py`, and evaluation notebooks.

Use the following division of responsibilities:

| Responsibility | Proposed home |
|---|---|
| Checkpoint loading, device selection, existing device preparation, batched prediction | `ml/inference.py` |
| Evaluation orchestration, simulation results, grouping, and report assembly | `ml/usecases/evaluate.py` |
| Numerical metrics | `ml/diagnostics/` |
| Figure construction | `ml/visualization/` |
| Parsing command options and invoking evaluation | `ml/cmd/evaluate.py` |

1. Check callers of the existing `Autoregressor` before replacing or removing it. It implements a different prediction task from climatology evaluation.
2. Extract model loading and prediction. Return predictions for individual windows; keep averaging across windows as an explicit evaluation operation.
3. Preserve checkpoint keys, normalization arithmetic, output squeezing, device preference, warmup, and required third-party patches.
4. Move the report sections and orchestration out of the CLI. Preserve split labeling, simulation selection, baseline construction, figure filenames, and report contents.
5. Make notebooks call these APIs where their behavior matches. Retain small adapters for documented differences.
6. Keep test-data fallback in baselines, report figure selection defects, and scientific interpretation changes assigned to phase 2.

**Check:** compare predictions from a fixed checkpoint and fixed windows on the same device. Compare per-window and averaged predictions separately. Compare score tables, plot input arrays, figure names, and report links. Test a small batch and a short final batch without changing reduction rules.

**Complete when:** commands and notebooks can invoke evaluation without importing private command helpers.

## 5 Simplify the ML notebooks

Keep settings, library calls, brief inspection of returned results, and explanation in notebooks. Move reusable reading, calculations, evaluation loops, and plotting into the library. Small presentation choices can remain beside the call.

| Notebook or script | Planned treatment |
|---|---|
| `climatology_model_evaluation.ipynb` | Use shared checkpoint, prediction, metric, and plotting functions |
| `climatology_model_evaluation_by_code.ipynb` | Extract grouping, loading, window prediction, and plots; preserve its distinct selection rules |
| `climatology_noise_floor.ipynb` | Extract profile loading and replicate plots; defer scientific relabeling to phase 2 |
| `enstrophy_convergence.ipynb` and `enstrophy_convergence_long_run.ipynb` | Retain one configurable notebook after preserving unique outputs; their source differs only in a path and figure title |
| `barotropic_visualization.ipynb` | Retain useful views and move repeated plotting and derived fields into library functions |
| `nc_processing_example.ipynb` | Fold reusable plots into visualization APIs; remove only if the remaining example adds no distinct teaching value |
| `other_visualizations.ipynb` | Check stale imports and each unique diagnostic before deciding what to retain |
| `eval_test.py` | Replace duplicated notebook logic with a small runner using the retained evaluation API, or remove if it adds no distinct check |

First record existing failures, including stale `fix_time_units` imports and calls passing the unsupported `zonal_mean` argument to `build_model`. Repair unambiguous API wiring during migration; defer changes requiring a scientific choice.

Execute each retained notebook from a fresh kernel on bounded inputs. Use a temporary copy for overridden paths and smaller selections. Preserve original experiment settings and unique outputs unless their removal is explicitly justified in the inventory. Inspect representative figures, including axes, units, coordinates, legends, and labels.

**Complete when:** no retained notebook owns a reusable scientific implementation. Every original notebook has a disposition, and every retained notebook has a recorded check result.

## 6 Move the heat demonstration into its own package (historical)

**Main files:** `heat-simulation/notebooks/heat_equation_2d.ipynb` and `heat-simulation/src/heat_simulation/`.

1. Move the FTCS step, heat-source update, simulation loop, and frame sampling into focused package functions.
2. Move snapshot plotting and animation construction into a visualization module. Keep notebook parameters and explanations.
3. Reuse the same simulation code for snapshots and animation. Preserve source timing, boundary stencil, array indexing, buffer swaps, snapshot indices, frame intervals, and dtypes.
4. Review the placeholder `main.py` and placeholder test. Remove or replace them only after defining the retained demonstration entry point.
5. Document the numerical assumptions. Record suspected discretization or labeling errors separately; do not alter the solver while moving it.

**Check:** compare a single step, boundary cells, source cells, final fields, snapshots, and animation frames on a small grid. Include a rectangular grid and a source near an edge. Check plotted orientation.

**Complete when:** the notebook calls the heat package and reproduces its previous numerical results. The ML package does not own heat logic.

## 7 Remove obsolete paths and finish module cleanup

1. Recheck callers after migration. Candidates include `Autoregressor`, `run_convergence.py`, `run_variance.py`, `run-sims.sh`, duplicate submission wrappers, and temporary executive-figure code. These are candidates, not approved deletions.
2. Decide whether to retain the rotating-globe tool. If retained, move its reusable calculations and plotting to their owning modules and leave a thin entry point.
3. Remove a command and its registration, imports, documentation, and obsolete examples together. Preserve unique figures or historical results before removing their generator.
4. Compare shell and Slurm scripts before consolidating them. Replica counts, resource requests, submission directories, notification behavior, and argument handling can distinguish similar files.
5. Preserve working command names and options unless the inventory identifies an obsolete entry point. Document any removal and its replacement.
6. Split other modules only where responsibilities are mixed. In particular, separate computations from formatting in `cmd/util.py`. Keep configuration schemas and existing formats stable; avoid splitting files solely because they are long.
7. Use consistent terms: a simulation is one trajectory; a replica is one stochastic realization for a parameter configuration; a window is a consecutive input sequence; a target is the associated output; a split assigns simulations to train, validation, or test; a training run produces a model and its artifacts. Keep serialized names unchanged.

**Check:** search source, notebooks, scripts, entry points, and documents for removed names. Check retained command help and shell syntax. Use harmless test inputs for file-writing tools; do not submit jobs, send notifications, purge real data, or launch simulations for these checks.

**Complete when:** each deletion has evidence, retained commands resolve, and shell consolidation has preserved behavior. Execution redesign remains in phase 3.

## 8 Consolidate documents and correct the book

1. Make the root README a short project map. Fill the currently empty ML and heat READMEs with retained setup, entry points, and links.
2. Give project instructions one home: simulation operation in `sim/README.md`, ML operation in `ml/README.md`, and detailed methods in `docs/`. From the repository root, show ML commands as `uv run --project ml ...`.
3. Reconcile overlapping material in `docs/isca-barotropic-stirring.md`, `barotropic-namelist.md`, `barotropic-diagnostics.md`, and the simulation README. Retain unique source explanations and parameter references.
4. Check `pre-processing.md`, `model-evaluation.md`, and `norms.md` against retained code. Distinguish the current implementation from intended corrections. Do not imply that a documented phase 2 defect is fixed.
5. Classify `trial-spec-20260629.md`, dated presentations, and other historical material. Keep unique experiment settings and results with their historical status. Remove abandoned instructions only after checking references and preserving useful content.
6. Keep the harmonic-head thesis exploration and `presentations/bve-harmonics-sfno/` separate from this maintenance work, as required by the action-item index.
7. Apply `book/AGENTS.md`: remove project commitments such as the final GSNO training claim in the vorticity chapter; retain general theory and standalone examples. Cross-reference shared explanations instead of repeating them.
8. Check known documentation errors in equations, conventions, units, and scientific claims. Verify corrections with a derivation, simple example, or primary source. Check citation metadata. Record unresolved questions without expanding into a new theory project.

**Check:** verify local links and anchors, command examples, referenced file paths, and callers of deleted documents. Render changed book chapters and inspect equations, cross-references, and references. If Quarto is unavailable, record rendering as unavailable.

**Complete when:** instructions describe the retained project, historical material is clearly identified, and the book is useful independently of this repository.

## Verification and final review

Use small characterization tests for numerical moves: they compare current behavior before and after restructuring. Keep tests for meaningful boundaries and known answers. Scientific regression tests that change the expected behavior belong to phase 2.

Run ML checks from the repository root with the required dependency groups, for example:

```bash
uv run --project ml --group dev --group train --group vis pytest ml/tests
uv run --project ml --group train --group vis ml --help
```

Add focused tests under `ml/tests/` during implementation; that directory is not present in the current tracked tree. Select the changed tests for each batch, then run the retained suite at the end. Use the Isca conda environment for simulation-related import or help checks. Do not compile Isca or start a new simulation for compaction.

Require exact agreement for indices, ordering, shapes, dtypes, and unchanged deterministic calculations. For model predictions, first measure repeatability on the fixed device; set and record a tolerance before judging the refactor. Investigate changed values instead of loosening the tolerance.

The final reviewer should answer:

- Did any formula, normalization, grid choice, selected sample, target, split, model option, or saved format change?
- Does each repeated responsibility have one owner? Are remaining variants justified by a recorded phase 2 difference?
- Does every removed API, command, notebook, and document have a caller check and a disposition?
- Do retained workflows have no new failures? Are existing failures and unavailable checks listed separately?
- Are data, results, local changes, submodule pins, and patches preserved?
- Is the retained project smaller and easier to navigate?

Record before and after source and notebook sizes as context, excluding tests, generated files, and third-party code. Do not pursue a line-count target at the expense of clarity.

Finish with an independent diff review, resolve compaction findings, and record the results and remaining limits. Do not start phase 2 as part of completing this plan.
