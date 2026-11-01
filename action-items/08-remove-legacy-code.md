# 08. Remove old paths and clarify owners

Priority: P2. Follow 01 and 06.

## Evidence

`ml/src/ml/inference.py:36-117` implements an unreferenced vorticity/stirring rollout.
The current factory always returns a latitude profile.
`cmd/rotating_globe.py:26`, `cmd/run_convergence.py:20-25`, and `cmd/run_variance.py:19-23` import APIs that no longer exist.
`cmd/util.py:370-439` duplicates diagnostics and describes the diagnostics module as future work.
`usecases/executive.py:28-84` repeats calculations and plots.
`training/model.py:26` falsely says asdict changes tuples to lists.

## Work

Remove obsolete rollout and standalone commands after checking callers, or migrate useful commands to shared APIs.
Keep CLI modules to options and orchestration.
Put inference in 01, data preparation in 06, math in diagnostics, report orchestration in use cases, and plotting in 09.
Remove unused imports, obsolete comments, commented-out code, and abandoned TODO prose.
Check low-confidence dead-code candidates before deleting them.
Keep baseline helpers still called by `cmd/util.py`.

## Verify

1. Search Python, notebook cells, scripts, package entry points, and docs for every removed symbol. Require no unresolved references.
2. Run `python -m compileall -q ml/src` and CLI help/import smoke checks in the supported environment.
3. Run the tiny train/evaluate pipeline. Require one active implementation per migrated responsibility.
4. For moved logic, compare fixed inputs before and after. Allow only intentional corrections from linked items.
5. Load all four checked-in TOML configs. If the parser changes, compare the parsed values, including optional scheduler and early-stop sections.
