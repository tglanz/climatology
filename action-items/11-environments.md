# 11. Define supported environments

Priority: P2. Needed for repeatable verification.

## Evidence

`ml/src/ml/cmd/cli.py:3-10` eagerly imports optional training, monitor, and plotting dependencies.
The base and inference groups in `ml/pyproject.toml` do not provide all those imports.
The existing lockfile metadata matches the current ML project metadata.
The Isca setup guides and devcontainer select different environment files.
Local Isca modifications include six tracked files and an untracked entry.

## Work

Choose the smallest useful supported ML environment set.
Either simplify dependency groups or load optional commands lazily.
Declare direct dependencies used by each supported path. Remove dependencies only after checking source and notebooks.
Keep the pinned torch-harmonics compatibility patch until tested evidence supports removal.
Document Linux/HPC and Mac Isca setup, compiler selection, and patch application.
Inspect the untracked Isca entry before deciding whether it is needed. Preserve current work.
Keep personal editor/bootstrap conveniences optional.

## Verify

1. In clean temporary environments, sync each documented group with the lockfile.
2. Run help and the promised preprocess, train, evaluate, and visualization smoke paths. A lightweight command must not fail because an unrelated optional group is absent.
3. Confirm `uv lock --check` and a locked sync succeed.
4. In an isolated CPU process, call patch_sht_dtype_device_order directly. Compare SHT forward/inverse outputs before and after within float32 tolerance. Call the patch twice and require unchanged installed function identity and outputs. patches.apply alone is insufficient on CPU. Test MPS if Mac support is claimed.
5. Validate the documented Isca patch against the pinned revision in a disposable checkout. Compile one tiny case on each platform actually claimed as tested.
