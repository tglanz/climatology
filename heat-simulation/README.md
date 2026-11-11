# Heat equation demonstration

A separate NumPy FTCS demonstration of two-dimensional heat diffusion with a
fixed-temperature source. It has no dependency on the ML package.

From the repository root:

```bash
uv sync --project heat-simulation --group dev
uv run --project heat-simulation --group dev jupyter lab --notebook-dir heat-simulation/notebooks
uv run --project heat-simulation --group dev pytest heat-simulation/tests
```

Open [heat_equation_2d.ipynb](notebooks/heat_equation_2d.ipynb).
Set grid dimensions, diffusivity, time step, number of steps, and source parameters
in the configuration cell.

[solver.py](src/heat_simulation/solver.py) owns the FTCS step, boundary stencil,
source update, and simulation loop.
[visualization.py](src/heat_simulation/visualization.py) owns snapshots and animation.
The source is applied after each diffusion step. Source coordinates index the
first and second array axes in that order. Array orientation and snapshot labels
retain the original demonstration's conventions.

The demonstration uses unit grid spacing by default. Its boundary stencil uses
the neighboring interior value minus the boundary value, giving zero external
flux in this discrete scheme. The interior FTCS stability condition is
`alpha * dt * (1/dx**2 + 1/dy**2) <= 1/2`. The solver retains the original
arithmetic and does not enforce this condition.

The notebook's initial snapshot and the field after update index zero both carry
the historical label zero. Do not interpret that labeling as a corrected physical
time axis.

The placeholder command and test were removed; the notebook is the demonstration
entry point. Saved notebook outputs are historical results.

## CI checks

Every pull request to main runs separate lint and test jobs. Pushes to main
also check changes to this project and its CI workflows. CI installs the locked
development environment, runs full pylint on the package and Black on Python
files, and runs the solver tests independently.

```bash
uv run --project heat-simulation --group dev pylint --rcfile=heat-simulation/pyproject.toml heat-simulation/src
uv run --project heat-simulation --group dev black --check heat-simulation
uv run --project heat-simulation --group dev pytest heat-simulation/tests
```
