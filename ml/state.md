# ML Training State

## Task

Predict next-day vorticity `vor(t+1)` given current vorticity and stirring `(vor(t), stirring(t))`
using a Fourier Neural Operator trained on Isca barotropic model output.

---

## Data

| Property              | Value                                      |
|-----------------------|--------------------------------------------|
| Simulations           | 90 (barotropic_stirring-T85)               |
| Grid                  | 128 lat x 256 lon (T85)                    |
| Input channels        | 2: vor [1/s], stirring [1/s^2]             |
| Output channels       | 1: vor [1/s]                               |
| Pairs per simulation  | 90 total (15 runs x 6 pairs each)          |
| Spin-up skip          | 45 pairs (configured; not yet applied)     |
| Usable pairs/sim      | 45 after skip                              |
| Train / Val / Test    | 80% / 20% / 0%                             |

### Current preprocessed dataset (old config, skip=50, samples=10)

| Split | Samples |
|-------|---------|
| Train | 450     |
| Val   | 220     |

### Pending re-preprocess (skip=45, samples=all)

| Split | Simulations | Samples |
|-------|-------------|---------|
| Train | 72          | ~3,240  |
| Val   | 18          | ~810    |

---

## Baselines (val set, physical space, relative L2)

| Predictor           | Loss   | Notes                              |
|---------------------|--------|------------------------------------|
| Zero everywhere     | 1.0000 | Worst possible                     |
| Persistence vor(t)  | 0.9474 | Copy input vorticity unchanged     |
| FNO target          | 0.1    | 10% relative error                 |

The persistence baseline of 0.947 means vorticity changes substantially day-to-day.
Beating 0.947 confirms the model is learning real structure; reaching 0.1 requires
capturing the dynamics well.

---

## Model

| Parameter       | Value   |
|-----------------|---------|
| Architecture    | FNO     |
| n_modes         | [16,16] |
| hidden_channels | 32      |
| in_channels     | 2       |
| out_channels    | 1       |
| Total params    | 603,041 |

### Params per training sample

| Dataset   | Params/sample | Assessment                       |
|-----------|---------------|----------------------------------|
| Current   | 1,340         | High; overfitting likely         |
| Pending   | ~186          | Acceptable for FNO               |
| FNO paper | ~150-600      | NS benchmark: 1000 samples, 20ch |

---

## Training History

### Run 1 - large model (34.6M params, 300 epochs, normalization OFF)
- Loss oscillated 0.9 to 927 with no convergence.
- Root cause: missing normalization. Stirring (std ~2e-10) and vor (std ~2.6e-5)
  differ by 130,000x; optimizer spent all budget on scale correction.

### Run 2 - large model (34.6M params, normalization ON)
- Epoch 1 val: 0.819. Plateaued at val ~0.66 from epoch 8 onward.
- Train reached 0.03 at epoch 122 while val stayed at 0.66.
- Root cause: 34.6M params vs 450 samples (~77,000 params/sample).
  Model memorized training simulations.

### Run 3 - reduced model (603K params, normalization ON) - IN PROGRESS
- Epoch 1 val: 0.830. Train and val tracking closely in early epochs.
- ep6: train=0.750, val=0.754 (gap=0.004 vs 0.173 gap at same epoch in run 2).
- Dataset unchanged (450 train samples, old preprocess).

---

## Improvements Made

| Change                       | Impact                                              |
|------------------------------|-----------------------------------------------------|
| Channel-wise z-score norm    | Fixed loss scale (927 -> ~0.9 at epoch 1)          |
| Reduced hidden_channels 64->32 | Reduced params 34.6M -> 603K                     |
| Reduced n_modes [64,64]->[16,16] | Modes 17-64 carry no learnable signal at this scale |

---

## Pending

1. **Re-run preprocessing** with skip=45, samples_per_experiment=null
   - Increases train set from 450 to ~3,240 samples
   - Reduces params/sample from 1,340 to ~186
   - Command: `uv run --project ml ml preprocess -c ./ml/config.toml`

2. **Restart training** after preprocessing
   - Clear training/ and checkpoints/ dirs first

---

## Heuristics for Further Improvement

### If val still plateaus after more data
- Reduce hidden_channels further (32 -> 16): 603K -> 151K params
- Add weight_decay (try 1e-4) in config to regularize
- Reduce lr_decay_every (100 -> 50) for faster LR annealing

### If train and val both plateau above 0.3
- The model may be underpowered; increase hidden_channels back to 32 or 64
- Increase n_modes to [24,24] to capture more spatial structure

### If train/val gap exceeds 0.2
- Overfitting; reduce model size or add weight_decay
- Consider increasing batch_size (16 -> 32) for smoother gradients

### Architectural alternatives if FNO stalls

**SFNO (Spherical FNO)** — strongest candidate for this problem.
FNO applies a flat 2D FFT assuming periodic, uniform spacing in both dimensions.
Longitude periodicity is correct; latitude is not — the Gaussian grid has non-uniform
spacing, the poles are boundaries, and the physics (Coriolis, vorticity, divergence)
respect spherical geometry. SFNO replaces the FFT with spherical harmonic transforms
(`torch_harmonics`), the natural basis for fields on a sphere. This is the architecture
used in FourCastNetv2 for global weather prediction.
- Already implemented in `submodules/neuraloperator/neuralop/models/sfno.py`
- Drop-in replacement for FNO (same interface, same config parameters)
- Requires `torch_harmonics` as an additional dependency
- n_modes maps to spherical harmonic degrees; T85 resolves up to degree 85
- The stirring forcing is localized at lat=45 deg — SFNO represents this correctly
- The training data comes from a spectral model already using spherical harmonics;
  SFNO is arguably the correct inductive bias for this task

**TFNO (Tucker-factorized FNO)** — fewer params, same expressiveness.
Low-rank Tucker decomposition of the spectral weights. Useful if SFNO is not pursued
and overfitting remains an issue at larger hidden_channels.

Other options:
- Increase n_layers (default 4) to deepen without widening
- Add lat/lon positional encoding as additional input channels

### Data
- Varying stirring parameters (amplitude, lat0, B) across simulations would produce
  a more diverse dataset and improve generalization to unseen forcing regimes.
  Currently all 90 simulations use identical stirring parameters.
