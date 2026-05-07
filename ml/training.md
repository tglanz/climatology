# Training

## Problem

Given vorticity $\omega_t$ and stirring forcing $F_t$ at time $t$, predict $\omega_{t+1}$:

$$x_i = (\omega_e(t),\ F_e(t)), \qquad y_i = \omega_e(t+1)$$

Experiments are split 80/10/10 by simulation (not by sample) so no simulation appears in
more than one split.

## Loss

- **MSE**: $\frac{1}{N}\sum\|\hat{y}_i - y_i\|_2^2$
- **Relative $L^2$** (current): $\frac{1}{N}\sum\frac{\|\hat{y}_i - y_i\|_2}{\|y_i\|_2}$

Persistence baseline (copy $\omega_t$ as prediction): ~0.947. Target: 0.1.

## Architecture

**FNO** (current): flat 2D FFT over the lat-lon grid. Correct for the zonal
(periodic) direction; approximate for latitude (Gaussian grid, non-uniform spacing,
pole boundaries).

**SFNO** (recommended next step): replaces FFT with spherical harmonic transforms.
Natural basis for fields on a sphere; correct inductive bias for this problem.
FourCastNetv2 uses SFNO for global weather prediction. Already available at
`submodules/neuraloperator/neuralop/models/sfno.py` — drop-in replacement for FNO.
Requires `torch_harmonics`.

**TFNO**: Tucker-factorized FNO. Fewer parameters for same expressiveness; useful if
overfitting persists without switching to SFNO.

## Optimizer

Adam, lr $10^{-3}$, halved every 100 epochs.

## Tuning Heuristics

| Symptom | Action |
|---|---|
| Val plateaus, train converges | Reduce hidden_channels (32->16), add weight_decay 1e-4 |
| Both plateau above 0.3 | Increase hidden_channels or n_modes |
| Train/val gap > 0.2 | Overfitting; reduce model or add weight_decay, increase batch_size |

**Data diversity**: all current simulations use identical stirring parameters. Varying
amplitude, latitude, and width across simulations would improve generalization to
unseen forcing regimes.
