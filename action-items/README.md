# Repository review

Reviewed 2026-11-01 at `51782c6`. These are work items, not implemented fixes.

Only the three `CLAUDE.md` guidance files were replaced with `AGENTS.md`.
The BVE study presentation was added later at the user's request.
Existing Isca submodule changes were preserved.

## Start here

Read the [system architecture review](architecture-review.md) for the end-to-end assessment and target structure.

Fix numerical contracts before comparing models. Build the small iteration profile early.
Use each item as a separate change where practical.

| Item | Priority | Work |
|---|---|---|
| [01](01-checkpoint-prediction.md) | P1 | Checkpoint prediction and normalization |
| [02](02-diagnostic-metrics.md) | P1 | Profile metrics and spectrum failure |
| [03](03-spherical-grid.md) | P1 | Gaussian grid and SFNO transforms |
| [04](04-training-loop.md) | P1 | Training scores, validation, and cheap history |
| [05](05-netcdf-lifetime.md) | P1 | NetCDF cache and ownership |
| [06](06-simulation-preparation.md) | P1 | One sample and target preparation path |
| [07](07-preprocessing-and-splits.md) | P2 | Deterministic, bounded data preparation |
| [08](08-remove-legacy-code.md) | P2 | Remove old paths and split responsibilities |
| [09](09-visualization-api.md) | P2 | One plotting contract |
| [10](10-notebooks.md) | P2 | Thin, consistent notebooks |
| [11](11-environments.md) | P2 | Supported dependencies and setup |
| [12](12-ci.md) | P1 | ML checks and useful CI |
| [13](13-project-documents.md) | P2 | Current project and operating documents |
| [14](14-evaluation-and-research-claims.md) | P1 | Honest evaluation and research claims |
| [15](15-book-scope.md) | P2 | Implementation-independent book |
| [16](16-book-mathematics.md) | P1 | Book errata and citations |
| [17](17-simulation-runs.md) | P1 | Simulation identity, completion, and failures |
| [18](18-run-scripts.md) | P2 | Local and Slurm entry points |
| [19](19-fast-iteration.md) | P1 | Small runs through the same pipeline |
| [20](20-harmonic-head.md) | Research | Controlled output-head experiment |
| [21](21-artifact-lifecycle.md) | P1 | Artifact identity, completion, and lineage |
| [22](22-stage-interfaces.md) | P2 | Stage interfaces and one runnable recipe |
| [23](23-model-contract.md) | P2 | Complete target and model bundle |
| [24](24-evaluation-artifacts.md) | P1 | Frozen evaluation protocols and reusable results |

P1 means address before trusting a new scientific comparison. P2 means simplify or repair the workflow.
These priorities describe review risk, not a measured model quality result.

## Verification convention

Each code logic item includes regression cases and expected outcomes.
Named tests below are proposed tests to add, not existing tests or completed checks.
After item 11 defines the environment, run focused tests from the repo root:

```bash
uv run --project ml --all-groups --locked pytest ml/tests/<test-file>.py
```

Simulation tests in 17 should use fake Isca adapters in the unit suite. Run real Isca checks in its conda environment. Keep heat tests in the heat package.
Use the tiny fixture in item 19 for integration checks.
Use CPU for routine checks. Compare numerical results with stated tolerances.
Use real data and accelerators only where a test requires them.

## Review coverage and limits

- Read all first-party ML source, all eight ML notebooks, and the heat demonstration.
- Reviewed all book source, project docs, simulation code, shell scripts, CI, and presentation sources.
- Read pinned upstream code where it defines behavior. This is not a full review of either upstream submodule.
- Inspected selected NetCDF coordinates, HDF5 schemas, and checkpoint metadata. Did not scan all raw output or reproduce past results.
- Parsed 66 first-party Python files and checked Bash syntax in 29 scripts. Both passed.
- Small isolated probes reproduced the cache, metric, spectrum, window-boundary, batch-reduction, and small-split defects.
- PyTorch integration, notebooks, model jobs, MPI, Slurm, and Quarto builds were not run during the review. The read-only review environment had no writable temporary directory for PyTorch.
- Peer reviewers challenged findings before inclusion. The work items preserve relevant caveats.
- No lockfile drift was found between the ML project metadata and its lockfile.
- No automatic dead-code deletion is proposed. Public APIs and notebook callers need a final check.

## Document coverage

The documentation work is split by ownership. Check every listed family when closing its item.

| Documents | Item |
|---|---|
| Root README, ML README, sim README, heat README and getting-started | 13 |
| `docs/pre-processing.md` | 06, 13 |
| `docs/model-evaluation.md`, `docs/norms.md`, `docs/notations.md` | 02, 03, 14 |
| `docs/barotropic-namelist.md`, `docs/barotropic-diagnostics.md`, `docs/isca-barotropic-stirring.md`, `docs/spectral-truncation.md` | 13, 14 |
| `docs/conda-isca-env.md`, `docs/mpi-cheatsheet.md`, `docs/ncdump-cheatsheet.md`, `docs/h5dump-cheatsheet.md`, `docs/s3-atmos-cheatsheet.md` | 13 |
| `docs/references.md`, `docs/trial-spec-20260629.md` | 13, 14 |
| All book QMD files, book README, bibliography, Quarto configuration | 15, 16 |
| All notebook Markdown, labels, and saved results | 10, 14 |
| All existing `presentations/` Markdown, TeX, references, and render instructions | 13, 14 |
| `ai-knowledege/thesis-exploration.md` | 14, 20 |

Keep dated experiment records as dated records. Correct errors and link to the current method.
Do not rewrite historical measurements as if they came from today's code.
