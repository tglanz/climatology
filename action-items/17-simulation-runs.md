# 17. Make simulation runs reproducible

Priority: P1.

## Evidence

`sim/scanner.py:60-68` hashes forcing parameters only.
The skip at lines 92-95 checks for one output file without checking the run settings.
`sim/simulation.py:40` overwrites metadata before running.
Pinned Isca can skip existing segments, allowing an old prefix and changed new segments under rewritten metadata.
Work paths at `simulation.py:31-32` omit the experiment name.
Exhausted FailedRunError retries at `scanner.py:104-122` are logged but do not produce a failing exit code.
Replicate indices are not explicit random seeds.

## Work

Keep forcing code as a scientific grouping key.
Add a complete run manifest and reject incompatible reuse before skips or metadata writes.
Allow a compatible segment-count extension explicitly.
Namespace work directories by experiment as well as simulation.
Record seed policy, compiler, pinned source and patch state.
Check completion from the expected valid output set.
Propagate exhausted failures to the process status without swallowing unrelated errors.

## Verify

1. Add `test_simulation_runs.py` with fake Isca experiments. No MPI required.
2. Reuse a code/index with changed dt, segment length, or resolution. Require rejection before metadata or output changes.
3. Extend an otherwise identical run. Require preserved metadata provenance and compatible segments.
4. Run the same code/index in two experiment names. Require different work paths.
5. Force all retries to fail. Require nonzero process status and a failure record.
6. Test missing, corrupt, and complete output sets.
7. Once seed control is defined, repeat one tiny real simulation twice. Check its documented reproducibility tolerance and record the environment.
