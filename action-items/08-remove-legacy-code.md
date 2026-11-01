# 08. Refactor live code and clarify owners

Priority: P2. Follow 01 and 06. Initial obsolete removal belongs to 25.

## Evidence

`ml/src/ml/cmd/util.py:370-439` duplicates diagnostics.
`usecases/executive.py:28-84` repeats calculations and plots.
The evaluation CLI owns model loading, scientific evaluation, and report assembly.
These active paths need shared library owners after the numerical contracts are repaired.

## Work

Keep CLI modules to options and orchestration.
Use the shared predictor from 01, preparation from 06, and plotting contract from 09.
Put numerical calculations in diagnostics and report orchestration in use cases.
Migrate active utility and executive flows to these owners.
Remove replaced implementations after their callers use the canonical path.
Keep public interfaces consistent with the stage contracts.

Do not repeat the obsolete-code inventory from 25.
Keep baseline helpers while they have live callers.

## Verify

1. Search Python, notebook cells, scripts, package entry points, and docs for every moved or replaced symbol. Require no unresolved references.
2. Run import and CLI help smoke checks in the supported environment.
3. Run the tiny train/evaluate pipeline. Require one active implementation per migrated responsibility.
4. Compare fixed-input outputs before and after each refactor. Allow only intentional corrections from linked items.
5. Load all four checked-in TOML configs. If the parser changes, compare parsed values, including optional scheduler and early-stop sections.
