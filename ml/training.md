# Training

# BVE + Stirring

Goal: Train a model, such that for input $(\omega_t, F_t)$ produces $\omega_{t+1}$ where

- $\omega_t$ is the vorticity field at time $t$
- $F_t$ is the forcing (stirring) field at time $t$

## Data

Each experiment $e$ is a simulation under stirring configuration $S_e$, producing vorticity snapshots $\omega_e(t)$ and forcing fields $F_e(t)$ for $t = 0, 1, \ldots, T_e$ on a fixed spatial grid $D$.

Let $\mathcal{E}$ be the set of all experiments. For each experiment $e$, let $\mathcal{S}(e) \subseteq \{0, 1, \ldots, T_e - 1\}$ be the set of sampled time indices. Index each sample by $i = (e, t)$:

$$x_i = (\omega_e(t),\ F_e(t)), \qquad y_i = \omega_e(t+1)$$

$$\mathcal{D} = \{(x_i,\ y_i) \mid e \in \mathcal{E},\ t \in \mathcal{S}(e)\}$$

where $N = \sum_{e \in \mathcal{E}} |\mathcal{S}(e)|$ is the total number of training samples.

## Training

$\mathcal{E}$ is partitioned into train/val/test splits (e.g. by 80%/10%/10% split). All pairs from each experiment belong to a single split.

**Loss**:
- MSE: $\frac{1}{N}\sum\|\hat{y}_i - y_i\|_2^2$ — simple baseline
- Relative $L^2$ (FNO): $\frac{1}{N}\sum\frac{\|\hat{y}_i - y_i\|_2}{\|y_i\|_2}$
- Geometric relative $L^2$ (SFNO): accounts for spherical geometry by weighting grid points by latitude Jacobian and quadrature weights:

$$\mathcal{L} = \frac{\left(\sum_{i,j} w_j \sin\theta_j\, |\hat{y}_{ij} - y_{ij}|^2\right)^{1/2}}{\left(\sum_{i,j} w_j \sin\theta_j\, |y_{ij}|^2\right)^{1/2}}$$

where $\theta_j$ is the colatitude and $w_j$ are quadrature weights.

**Optimizer**: Adam in both FNO and SFNO.
- FNO: lr $10^{-3}$, halved every 100 epochs, 500 epochs total
- SFNO: lr $2\times10^{-3}$ (initial), $10^{-5}$ (fine-tuning); fine-tuning uses autoregressive rollout loss accumulated across multiple forecast steps

## Inference

The simulator is replaced by an autoregressive loop:

$$\omega(t+1) = \text{FNO}(\omega(t),\ F(t))$$

$F(t)$ is sampled from an Ornstein-Uhlenbeck process.

> Note: we can use the existing implementation at `stirring.F90:222~` to generate those samples. Commented there: !This is equation A.6 in Vallis et al 2004 - DOI:10.1175/1520-0469(2004)061<0264:AMASDM>2.0.CO;2