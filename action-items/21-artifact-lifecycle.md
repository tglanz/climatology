# 21. Give artifacts stable identities and lifecycles

Priority: P1. System design. Build on 03, 07, and 17.

## Evidence

Validation produces console findings, while split generation rescans raw directories.
Preparation writes final HDF5 paths directly and copies its split manifest last.
Training rotates named directories, and evaluation discovers data from the current raw tree.
See the stage evidence in [architecture review](architecture-review.md).

## Work

Define a validated simulation catalog and a frozen split referencing it.
Separate source/physical integrity from task-specific eligibility. Record the diagnostic-policy fingerprint for anchors and eligibility, so a changed target policy can be checked without rerunning the simulation.
Write prepared datasets as staged artifacts with a manifest and completion state.
Consume only complete, schema-compatible artifacts.
Separate dataset identity from training-run identity and evaluation identity.
Keep completed artifact contents stable. A latest reference may point to an identified run.

Derive identity from the canonical scientific specification, preparation protocol/schema version, and source manifest.
Record the producing source revision as provenance. A behavior repair can require a new preparation protocol even when TOML and raw files are unchanged.
Record source fingerprints when ingesting.
Avoid rereading all large raw files at every launch.
Use relocatable references under configured roots.
Preserve existing results through an explicit legacy import or read-only compatibility path.

## Verify

1. Prepare D1 and train R1. Add raw simulations and change preprocessing settings. R1 must still resolve D1, while the new data becomes D2.
2. Fail preparation between split writes. No consumer may accept the partial artifact as complete.
3. Relocate D1 and train from it without raw NetCDF access. Coordinates, provenance, and target meaning must remain available.
4. Launch two runs against D1. Require distinct run identities and no overwritten data or run files.
5. Change workers only. The scientific dataset identity must stay the same. Bump the preparation protocol after a behavior change and require a new dataset identity.
6. Use a source that passes structural validation but fails a different target or convergence policy. Require distinct policy decisions and clear reasons.
7. Load a supported legacy artifact explicitly. Unsupported or ambiguous artifacts must fail with a migration message.
