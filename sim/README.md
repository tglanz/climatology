# sim

Barotropic vorticity equation simulations using Isca.

Run all commands from the repository root.

## Single run

Compile and run one simulation. The output index is auto-incremented based on
what already exists under `output/barotropic_stirring-T85/simulations/`.

```bash
conda run --no-capture-output -n isca_env python sim/barotropic_stirring.py
```

## Parallel runs

### Step 1: compile once

```bash
conda run -n isca_env python sim/barotropic_stirring.py --compile
```

### Step 2: run N simulations in parallel

The example below runs indices 0 to 99 with concurrency of 4.
Adjust `-j` and the index range as needed. Reduce `Settings.Cores` in the
script to 2 when running in parallel to avoid oversubscription.

```bash
parallel -j 4 conda run -n isca_env python sim/barotropic_stirring.py --index {} ::: $(seq 0 99)
```

## BVE without stirring (diagnostic)

Deterministic forward integration of the barotropic vorticity equation with
no stochastic forcing. Each `--index` deterministically samples its own
initial condition (`m_0`, `zeta_0`, `eddy_lat`, `eddy_width`) from a seeded
RNG and dumps the sampled values to `output/barotropic_decaying-T85/simulations/<index>/ic.json`.

Used to test whether the FNO/SFNO training pipeline can reach FNO-paper-level
loss on a deterministic problem. See `pending-tasks/bve-without-stirring.md`.

```bash
# Compile once
conda run -n isca_env python sim/barotropic_decaying.py --compile

# Single sim
conda run --no-capture-output -n isca_env python sim/barotropic_decaying.py

# Parallel sweep
parallel -j 4 conda run -n isca_env python sim/barotropic_decaying.py --index {} ::: $(seq 0 999)
```

Train against this dataset with `ml/configs/decaying.toml`.
