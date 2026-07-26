# Stop maintaining sweep.json at simulation time

## Problem

`sim/scanner.py` currently maintains `output/<experiment>/sweep.json` (a
`code -> stirring params` mapping) live, during simulation execution:

- It reads the existing file, merges in any new codes from the current
  invocation's CLI args, and writes the merged result back
  (`sim/scanner.py:74-77`).
- It then runs its execution loop over the *merged* result, not just the
  codes this invocation was asked to run (`sim/scanner.py:80`,
  `codes = merged`).

This is fine as long as every invocation is always given the full parameter
grid (the current local `parallel` workflow does this, see `sim/README.md`).
It breaks once an invocation is given a single combo, which is exactly what
a SLURM job array wants to do (one task = one combo x replicate): the merged
read-modify-write is an unlocked race across concurrent processes (lost
updates to the file), and reassigning the execution loop to iterate over
`merged` makes a task pick up and re-run combos it was never asked to run.

## Decision

We don't need to build or maintain `sweep.json` at simulation time at all.
Every simulation's output directory is already self-describing:

- The directory name `<code>-<index>` already encodes the code
  (`sim/scanner.py:105`).
- `namelist.json`, written once per simulation before any run segment
  executes (`sim/simulation.py:40`, `sim/barotropic_stirring.py:136-137`),
  contains the full namelist dict, including the `stirring_nml` block with
  every swept parameter (`amplitude`, `lat0`, `widthy`, `decay_time`,
  `lon0`, `widthx`, `B`).

So `code -> params` can be reconstructed entirely from completed output,
after the fact, with no shared mutable state and no dependency on execution
order.

## Plan

Add a new utility to the `ml` project:

```bash
uv run ml util create-sweep-file -c <config>
```

living alongside the existing `util` command group
(`ml/src/ml/cmd/util.py`, registered in `ml/src/ml/cmd/cli.py`). It should:

1. Glob `<experiment_dir>/simulations/*/namelist.json`.
2. For each, take `code = dirname.rsplit('-', 1)[0]` and
   `params = namelist["stirring_nml"]`.
3. Rename params' keys back to the `stirring_`-prefixed form
   (`amplitude` -> `stirring_amplitude`, etc.) to match the format
   `ml/src/ml/data/sweep_file.py` already expects to read.
4. Write the resulting `{code: params}` mapping to
   `<experiment_dir>/sweep.json`.

This replaces the live-write mechanism as the sole source of truth for
`sweep.json`, without changing the format consumed by existing readers
(`ml/src/ml/data/sweep_file.py`, `ml/src/ml/cmd/util.py:251`
`summarize-simulations`, `sim/cmd/purge_sweep.py`).

## Related

`sim/scanner.py`'s execution-time sweep.json read/merge/write has been
removed (see the fix applied alongside this action item) — the run loop now
only ever executes the codes this invocation was actually given on the CLI.
