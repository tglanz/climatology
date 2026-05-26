# Preprocessing

The preprocessing subsystem takes a set of simulations as input and produces three HDF5 splits: `train`, `val`, and `test`. Each split holds two `f32` datasets, `x` and `y`, whose aligned rows are training pairs $(X, Y)$.

> The training pipeline fits the model on `train` pairs, monitors generalisation on `val` pairs during training, and reports held-out performance on `test` pairs after training.

At a high level, preprocessing extracts pairs from one simulation by:

1. Detecting the spinup time $t_s$.
2. Detecting the convergence time $t_c$.
3. Slicing the snapshots between $t_s$ and $t_c$ into $K$-length windows.
4. For each window $W = (S_{j_1}, \dots, S_{j_K})$:
   - Compute the input diagnostics $X_W$.
   - Compute the target diagnostic $Y_W$.
   - Write the pair $(X_W, Y_W)$ into the output HDF5.

The sections below describe each piece in turn.

## Diagnostics

A diagnostic is any quantity computed from a simulation. Three kinds appear in this pipeline.

- A **step diagnostic** is a value attached to a single snapshot. For example, vorticity $\zeta_t$ at step $t$.
- A **static diagnostic** is a value attached to the simulation as a whole, not to any individual step. For example, the stirring amplitude used to force the simulation. Static diagnostics are useful when conditioning the model on the forcing configuration.
- A **climatology diagnostic** is a statistical summary computed over a range of snapshots. For example, the time-mean zonal-mean of zonal wind $u$ over $[a, b)$.

Each training pair labels its diagnostics by role:

- An **input diagnostic** is one that contributes to $X$.
- A **target diagnostic** is one that contributes to $Y$.

A pair can carry several input diagnostics (typically a sequence of step diagnostics across the window) and a single target diagnostic (which may itself be a step or a climatology diagnostic).

## Spinup

The spinup time $t_s$ is the first snapshot index after which a chosen scalar step diagnostic stays close to its long-run mean. The canonical choice is the global mean enstrophy $\eta_t = \overline{0.5\, \zeta_t^2}^{\,\text{area}}$.

Let $\eta_0, \eta_1, \dots, \eta_{M-1}$ be the diagnostic series. The detector proceeds as follows.

1. Smooth $\eta$ with a rolling mean of size $w$:
   $$
   \bar\eta_t = \frac{1}{w} \sum_{k = 0}^{w - 1} \eta_{t - w + 1 + k},
   \qquad t = w - 1,\, w,\, \dots,\, M - 1.
   $$
2. Take the long-run reference as the average of the last $w$ smoothed values:
   $$
   \eta^* = \frac{1}{w} \sum_{t = M - w}^{M - 1} \bar\eta_t.
   $$
3. Return the smallest $t$ such that
   $$
   \frac{|\bar\eta_{t + k} - \eta^*|}{|\eta^*|} < \tau_s
   \quad\text{for every}\ k = 0, 1, \dots, h_s - 1.
   $$

The threshold $\tau_s$ and the consecutive-count $h_s$ are exposed in the configuration. If no $t$ satisfies the condition, the simulation has not spun up under this criterion; downstream, the windowing step then drops it when configured to start at $t_s$.

Spinup detection is optional. When it is omitted, no $t_s$ is computed and windowing starts at index $0$.

## Convergence

The convergence time $t_c$ is the first snapshot index at which the running time-mean of a chosen climatology diagnostic is within tolerance of the same diagnostic taken over the full reference window. The canonical choice of diagnostic is the zonal mean of the zonal wind, $\mathcal{F}(\zeta) = \overline{u(\zeta)}^{\,\text{lon}} \in \mathbb{R}^H$.

Define the running estimator
$$
D(a, b) = \frac{1}{b - a} \sum_{t = a}^{b - 1} \mathcal{F}(\zeta_t).
$$

Set the reference start to $t_{\text{ref}} = t_s$ when spinup has been detected, and to $t_{\text{ref}} = 0$ otherwise. The reference is then $D(t_{\text{ref}}, M)$. The detector proceeds as follows.

1. For each $i = 1, 2, \dots, M - t_{\text{ref}} - 1$, compute the cos-lat-weighted relative $L^2$ error between the running estimator and the reference:
   $$
   \varepsilon_i = \frac{\| D(t_{\text{ref}},\, t_{\text{ref}} + i) - D(t_{\text{ref}}, M) \|_w}
                        {\| D(t_{\text{ref}}, M) \|_w},
   \qquad
   \| f \|_w = \sqrt{\sum_j w_j\, f_j^2},
   $$
   with weights $w_j = \cos(\mathrm{lat}_j)$ normalised so their mean is one.
2. Return $t_c = t_{\text{ref}} + i^*$, where $i^*$ is the smallest $i$ such that $\varepsilon_{i + k} < \tau_c$ for every $k = 0, 1, \dots, h_c - 1$.

The threshold $\tau_c$ and the consecutive-count $h_c$ are exposed in the configuration. If no $i$ satisfies the condition, the simulation has not converged under this criterion; downstream, the windowing step then drops it when configured to cap at $t_c$.

Convergence detection is optional. When it is omitted, no $t_c$ is computed and windowing ends at the last admissible window-start index.

## Windowing

Given a trajectory of $M$ snapshots and the (possibly missing) $t_s$ and $t_c$, the windowing step emits a sorted list of window-start indices $t_0$. A window of length $K$ occupies snapshots $t_0, t_0 + 1, \dots, t_0 + K - 1$. The next-step target sits at $t_0 + K$, so admissibility requires $0 \leq t_0 \leq M - K - 1$.

The window-start range is

$$
t_0^{\min} =
\begin{cases}
0 & \text{start\_at = beginning} \\
t_s & \text{start\_at = spinup}
\end{cases},
\qquad
t_0^{\max} =
\begin{cases}
M - K - 1 & \text{end\_at = end} \\
\min(t_c,\ M - K - 1) & \text{end\_at = convergence}
\end{cases}.
$$

The selector emits

$$
t_0 \in
\big\{ t_0^{\min},\ t_0^{\min} + \sigma,\ t_0^{\min} + 2\sigma,\ \dots \big\}
\cap
[t_0^{\min},\ t_0^{\max}],
$$

stepping by the stride $\sigma$, and optionally truncates the result to its first $L$ entries when a per-simulation limit is configured. Two common stride choices: $\sigma = 1$ gives fully overlapping windows, $\sigma = K + 1$ gives disjoint tumbling windows.

If $t_0^{\min} > t_0^{\max}$ the admissible set is empty and the simulation contributes no pairs.

Each emitted $t_0$ defines a window $W$, from which $X_W$ and $Y_W$ are computed as described in the Diagnostics section.
