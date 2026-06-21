# sim

Barotropic vorticity equation simulations using Isca.

Run all commands from the repository root.

## Mac: prevent sleep during long runs

Wrap any command with `caffeinate -i` to keep the machine awake:

```bash
caffeinate -i parallel -j 8 conda run -n isca_env python -m sim.scanner \
    --stirring-lat0 30 37.5 45 52.5 60 \
    --index {} ::: $(seq 0 99)
```

## Parameter sweep (scanner)

`sim/scanner.py` is the main entry point. It accepts one or more values per stirring
parameter and runs all combinations. Each param combo is identified by a 6-character
hash code; simulations are named `<code>-<index>` under a shared experiment directory.

A `sweep.json` is written at the experiment root mapping each code to its param dict.

Re-runs are safe: each `(code, index)` checks for the last segment file and skips if
it already completed.

### Step 1: compile once (must be done before any parallel run)

Compilation writes shared build files and must not run in parallel.

```bash
conda run -n isca_env python -m sim.scanner --compile
```

### Step 2: sweep lat0 across 5 values, 100 replicates each

```bash
caffeinate -i parallel -j 8 conda run -n isca_env python -m sim.scanner \
    --stirring-lat0 30 37.5 45 52.5 60 \
    --index {} ::: $(seq 0 99)
```

This produces 500 simulations (5 configs x 100 replicates) under
`output/barotropic_stirring-T85/simulations/`.

### Sweeping multiple parameters

Multiple values on any stirring argument are swept as a cartesian product:

```bash
parallel -j 8 conda run -n isca_env python -m sim.scanner \
    --stirring-lat0 30 45 60 \
    --stirring-amplitude 1e-10 2e-10 \
    --index {} ::: $(seq 0 99)
```

Produces 6 configs x 100 replicates = 600 simulations.

### Single simulation (no sweep)

```bash
conda run --no-capture-output -n isca_env python -m sim.scanner \
    --stirring-lat0 45 --index 0
```
