# Climatology ML

FNO-based emulator for the Isca barotropic vorticity equation. Given vorticity and
stirring forcing at time $t$, predicts vorticity at $t+1$. Autoregressive rollout
compares model trajectories against held-out simulations.

## Setup

```bash
uv sync --group train      # training + preprocessing + inference
uv sync --group vis        # visualization notebooks (no torch)
uv sync --all-groups       # everything
```

## Pipeline

```bash
# 1. Preprocess simulations into HDF5 splits + splits.json manifest
ml preprocess training-data -c ml/config.toml

# 2. Train (saves parameters.pt + normalization.pt to checkpoints/)
ml train -c ml/config.toml --track-metrics

# 3. Monitor training in real time
ml monitor training -c ml/config.toml

# 4. Evaluate autoregressive rollout on a test simulation
#    Output defaults to output/barotropic_stirring-T85/eval/autoregression.nc
ml evaluate autoregression \
    -c ml/config.toml \
    --input output/barotropic_stirring-T85/simulations/73/run0001/atmos_daily.nc \
    --start 50 --timesteps 100
```

## Notebooks

All notebooks are in `notebooks/`. Run jupyter from `ml/`:

| Notebook | Contents |
|---|---|
| `model_evaluation.ipynb` | Side-by-side rotating globes (vor vs vor_pred), relative error maps |
| `barotropic_visualization.ipynb` | Full diagnostic suite for simulation output |
| `other_visualizations.ipynb` | Additional diagnostics |

## Dependency Groups

| Group | Contents |
|---|---|
| `train` | torch, neuraloperator, h5py, rich, plotext |
| `inference` | torch, neuraloperator |
| `vis` | cartopy, matplotlib, jupyter, dask |
| `dev` | black, pylint, pytest |

Base (always): numpy, xarray, netCDF4, click, tqdm.

## Training outputs

All training artifacts go to `output/<experiment>/training/`:
- `parameters.pt` — model weights (best val loss)
- `normalization.pt` — normalizer mean/std (required for inference)
- `epoch-metrics.csv` — per-epoch loss and learning rate
- `runs.csv` — per-run summary
- `metrics.h5` — spatial/spectral error per epoch (with `--track-metrics`)
