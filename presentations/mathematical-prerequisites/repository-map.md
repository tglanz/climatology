# Repository reading map {.unnumbered #repository-map}

This map locates applications of the general theory. Paths identify source locations, not additional mathematical assumptions. It describes the inspected source tree at base commit `d4e3594`; it does not claim that an experiment or saved notebook output was rerun.

| Read in the repository | Mathematical prerequisites |
|:--|:--|
| [Simulation overview](../../sim/README.md); [model methods](../../docs/isca-barotropic-stirring.md) | Conservation and rotating vorticity: Chapters 2, 3, 6, 10 |
| [Grid conventions](../../docs/grids.md); [grid diagnostics](../../ml/src/ml/diagnostics/grid.py) | Surface measure and Gaussian quadrature: Chapters 3, 8, 9 |
| [Spectra](../../ml/src/ml/diagnostics/spectra.py); [enstrophy](../../ml/src/ml/diagnostics/enstrophy.py) | Parseval, vorticity inversion, spectra: Chapters 7-10 |
| [Norm conventions](../../docs/norms.md); [error diagnostics](../../ml/src/ml/diagnostics/errors.py) | Weighted norms and statistical objectives: Chapters 4, 9, 11 |
| [Climatological targets](../../ml/src/ml/data/climatology.py); [convergence](../../ml/src/ml/diagnostics/convergence.py) | Time means and serial dependence: Chapter 11 |
| [Model construction](../../ml/src/ml/training/model.py); [spectral adapter](../../ml/src/ml/patches/neuralop.py) | Basis choice, spectral multipliers, learned maps: Chapters 8, 9, 12 |

The general theory is also rendered in `book/` from the same chapter sources. Project-specific settings, data schemas, and implementation behavior belong in `docs/`, `sim/`, and `ml/`.
