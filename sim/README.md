# sim

Barotropic vorticity equation simulations using Isca.

Run all commands from the repository root.
Set up the [Isca conda environment](../docs/conda-isca-env.md) first.
See the [model explanation](../docs/isca-barotropic-stirring.md),
[namelist reference](../docs/barotropic-namelist.md), and
[diagnostic fields](../docs/barotropic-diagnostics.md) for methods and source details.

## Mac: prevent sleep during long runs

Wrap any command with `caffeinate -i` to keep the machine awake:

```bash
caffeinate -i parallel -j 4 conda run -n isca_env python -m sim.scanner \
    --stirring-lat0 30 37.5 45 52.5 60 --cores 2 \
    --index {} ::: $(seq 0 99)
```

## Parameter sweep (scanner)

`sim/scanner.py` is the main entry point. It accepts one or more values per stirring
parameter and runs all combinations. Each param combo is identified by a 6-character
hash code; simulations are named `<code>-<index>` directly under the output directory.
The default is `./output/simulations/barotropic_stirring-T<harmonics>`.
Set `--output-dir PATH` to use a relative or absolute directory instead.
Each simulation stores its own `namelist.json` and segment files.

```bash
conda run -n isca_env python -m sim.scanner --output-dir /data/simulations --index 0
```

Output layout:

```text
<output-dir>/
  <code>-<index>/
    namelist.json
    run0001/atmos_daily.nc
    ...
  crashed-sims.txt          # Only when all retries for a simulation fail
```

Changing the default does not move existing simulation data. To resume an older
collection, pass its directory containing `<code>-<index>` folders to `--output-dir`.

Re-runs are safe: each `(code, index)` checks for the last segment file and skips if
it already completed.

**Note on parallelism:** each simulation uses `--cores` MPI processes. Keep
`--cores * -j <= ~8` on a Mac to avoid MPI oversubscription and SIGSEGV crashes.
The recommended settings are `--cores 2 -j 4`.

### Step 1: compile once (must be done before any parallel run)

Compilation writes shared build files and must not run in parallel.

```bash
conda run -n isca_env python -m sim.scanner --compile
```

### Step 2: sweep lat0 across 5 values, 100 replicates each

```bash
caffeinate -i parallel -j 4 conda run -n isca_env python -m sim.scanner \
    --stirring-lat0 30 37.5 45 52.5 60 --cores 2 \
    --index {} ::: $(seq 0 99)
```

This produces 500 simulations (5 configs x 100 replicates) under
`output/simulations/barotropic_stirring-T85/`.

### Sweeping multiple parameters

Multiple values on any stirring argument are swept as a cartesian product:

```bash
caffeinate -i parallel -j 4 conda run -n isca_env python -m sim.scanner \
    --stirring-lat0 30 45 60 \
    --stirring-amplitude 1e-10 2e-10 --cores 2 \
    --index {} ::: $(seq 0 99)
```

Produces 6 configs x 100 replicates = 600 simulations.

### Single simulation (no sweep)

```bash
conda run --no-capture-output -n isca_env python -m sim.scanner \
    --stirring-lat0 45 --index 0
```

## Tests

```bash
conda run -n isca_env python -m pytest sim/tests
```

The CLI tests use temporary directories and mock simulation execution; they do
not compile or run Isca.
