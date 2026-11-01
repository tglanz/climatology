# 18. Consolidate local and Slurm scripts

Priority: P2. Follow 11 and 17. Initial obsolete-entry-point removal belongs to 25.

## Evidence

`run-sims.sh:4-8` checks old numeric directories and invokes a module without a main.
There are two submit-sweep wrappers and four mostly copied sweep scripts.
`slurm/check.sh:17-32` submits from the root, while `preprocess.slurm:20-22` requires submission from slurm.
`train.slurm:26,40` shifts advertised extra arguments but never forwards them.
Its missing-config branch does not exit.
`.vscode/launch.json` references absent test.toml.

## Work

Choose one wrapper for each supported operation.
Use one sweep matrix and configurable replica count. Derive array bounds from that matrix.
Resolve root/config paths once. Pass arguments unchanged.
Validate required inputs and fail correctly.
Align MPI ranks and allocated resources.
Keep notification topics and cluster choices configurable.
Start from the retained entry points selected in 25. Remove replaced implementations after migrating their callers.

## Verify

1. Run `bash -n` on all shell and Slurm files.
2. Use fake sbatch, conda, and ML executables to capture commands without submitting jobs.
3. Test invocation from the root and another working directory. Check missing configs, quoted paths, extra arguments, and propagated failures.
4. Decode every array index for each supported replica count. Require exactly the intended unique combinations with no omissions.
5. Confirm chosen MPI ranks fit the requested allocation and notification jobs report actual completion status.
6. Submit one tiny real job only after stub checks pass. Record cluster-specific assumptions.
