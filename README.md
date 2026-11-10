# Climatology

Research on global physical climatology, idealized simulations, and neural operators.

| Directory | Purpose |
|---|---|
| [sim](sim/README.md) | Isca barotropic simulations and parameter sweeps |
| [ml](ml/README.md) | Preparation, diagnostics, training, evaluation, and plots |
| [heat-simulation](heat-simulation/README.md) | Separate heat-equation demonstration |
| [book](book/README.md) | General mathematics, fluid dynamics, and operator learning |
| [docs](docs/workplan.md) | Project methods, operation, and maintenance phases |
| [presentations](presentations/) | Talks and study material |
| [action-items](action-items/README.md) | Maintenance scope, plans, and verification records |

Experiment data and saved runs live under `output/` and are not tracked in Git.
Run ML commands from this directory with `uv run --project ml ...`.
Use the Isca conda environment for simulation commands.

## Submodules

[Isca](https://github.com/ExeClim/Isca) and
[neuraloperator](https://github.com/neuraloperator/neuraloperator) are pinned under
`submodules/`. Keep their recorded revisions and local patches explicit.

Clone with both dependencies:

```bash
git clone --recurse-submodules git@github.com:tglanz/climatology.git
```

For an existing checkout, initialize or restore the recorded revisions:

```bash
git submodule update --init --recursive
git submodule status
```

A leading `-` means uninitialized; `+` means the checkout differs from the pin.
Check local changes inside a submodule before updating it.

To deliberately select a new revision, enter the relevant submodule, fetch and
check out that revision, then stage the submodule path in the parent repository.
`git submodule update --remote --recursive` instead selects tracked remote branch
tips. Either operation requires a parent commit to record the new pins.

The Isca patch under [patches/isca](patches/isca/) and runtime neuraloperator
patches under [ml/src/ml/patches](ml/src/ml/patches/) remain separate from upstream.
