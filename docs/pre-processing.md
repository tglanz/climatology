# Preprocessing

Preparation converts Isca trajectories into aligned float32 datasets
`x=(B,K*V,H,W)` and `y=(B,C,H)`. Here $B$ counts windows, $K$ snapshots per
window, $V$ input variables, $C$ targets, $H$ latitudes, and $W$ longitudes.
Input channels follow time order, then configured variable order. Targets follow
`data.y_vars` order and repeat for each window from the same simulation.

[Simulation loading](../ml/src/ml/data/simulation_data.py) owns validation,
detectors, intervals, windows, and targets. Preparation and exploratory by-code evaluation use this owner. Normal model
evaluation uses saved prepared arrays and validates their metadata and hashes.
The [pipeline overview](pipeline.md) specifies artifact schemas, stages, and commands.

## Coordinates and acceptance

Segments must have matching full Gaussian coordinates, declared compatible units,
chronological times, uniform snapshot cadence, and consistent averaging intervals.
Longitudes cover one period with equal spacing and no duplicate endpoint.
Fields must be finite with dimensions `(time,lat,lon)`.
See [grids](grids.md) for coordinates and quadrature.

A configured detector must succeed. Missing required anchors, invalid target
intervals, and absent complete windows exclude the simulation with a reason.
Preparation stores exclusions and counts. An empty training assignment or zero
usable training windows is an error.

All replicas of a forcing configuration belong to the same split. Assignments
must be disjoint. Preparation writes train, validation, and test into a fresh
directory. Each file stores coordinates, channel identities, settings, and a
format identifier. These must agree across splits and with the checkpoint.
Declared input units are checked across segments and stored in artifact identity.
Known unit aliases are normalized; other fields require matching declared units.
The prepared simulation table keeps one target per accepted trajectory, so baseline
fitting is independent of its number of windows.

## Spinup stability criterion

The [detector](../ml/src/ml/diagnostics/spinup.py) compares adjacent nonoverlapping
blocks of global mean enstrophy. Enstrophy density is half the squared relative
vorticity. Its global mean uses Gaussian area weights.

Normalize the diagnostic by its maximum absolute value when nonzero. Divide it
into complete blocks of `window_size` snapshots; ignore a trailing incomplete
block. For block $i$, let $m_i$ be its mean, $s_i^2$ its sample variance, and $w$
its size. With dimensionless floor $\delta=10^{-12}$, compare

$$
A_i=\frac{|m_{i+1}-m_i|}
{\sqrt{s_{i+1}^2/w}+\sqrt{s_i^2/w}+2\delta},
\qquad
B_i=|\log(s_{i+1}^2+\delta)-\log(s_i^2+\delta)|.
$$

A comparison passes when both values are below `z_threshold`. Require
$\max(1,\lceil\text{stable_time}/w\rceil)$ consecutive passing comparisons.
Both duration settings count saved snapshots. Return $t_s=(i+1)w$ for the first
qualifying sequence, where $i$ indexes its first comparison from zero.

Constant series pass once enough complete blocks exist. Insufficient data cannot
establish stability. This retrospective heuristic has no calibrated significance
level and does not prove stationarity.

## Finite-reference convergence criterion

Let $D(a,b)$ be the time-mean zonal-mean zonal wind over $[a,b)$. The reference
starts at detected spinup $t_s$, or zero when spinup detection is disabled.
For every nonempty proper prefix, compare

$$
\varepsilon_i=
\frac{\|D(t_s,t_s+i)-D(t_s,M)\|_w}{\|D(t_s,M)\|_w}.
$$

The norm uses [Gaussian weights](norms.md). A zero reference norm makes this
relative criterion undefined and excludes the simulation. Return $t_c=t_s+i$
for the first prefix followed by `hold` consecutive errors below `threshold`.

The returned index is an exclusive prefix endpoint. Detection uses later
observations and the full-run reference. Passing establishes this finite-reference
criterion only; it proves neither stationarity nor infinite-time convergence.

## Input windows and targets

An input occupies $[t_0,t_0+K)$. Complete windows satisfy $0\leq t_0\leq M-K$.
Start at zero or $t_s$, according to `windows.start_at`.
`windows.end_at="convergence"` caps the **window start** at $t_c$.
It does not require the entire window to end there. Apply stride, then the optional
first-window limit. Stride $K$ gives adjacent disjoint windows; $K+1$ leaves a gap.

Resolve exactly two of the climatology settings `start_at`, `end_at`, and `length`
to $[a,b)$, with $0\leq a<b\leq M$. For target variable $v_c$,

$$
Y_{c,h}=\frac{1}{(b-a)W}
\sum_{t=a}^{b-1}\sum_{\ell=0}^{W-1}v_c(t,h,\ell).
$$

Uniform sampling and equal longitude spacing justify these unweighted averages.
This is a finite-trajectory estimate. An ensemble interpretation needs additional
assumptions about stationarity, ergodic sampling, and finite means.
Input and target intervals may overlap. The task does not establish independent
future forecasting.

`validate-simulations` always checks structure, units, coordinates, and cadence.
Any diagnostic-validation flag additionally checks the entire sample contract.
The existing spinup, convergence, and climatology flag spellings remain available.
