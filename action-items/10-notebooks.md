# 10. Make notebooks thin and consistent

Priority: P2. Depends on 01, 02, 05, 06, and 09.

Notebook cell numbers below start at zero.

## Work and evidence

| Notebook | Required change |
|---|---|
| `ml/notebooks/climatology_model_evaluation.ipynb` | Cell 4 passes removed zonal_mean to build_model. Cells 4/8/10 duplicate prediction and metrics. Cell 8 invents uniform latitude coordinates. Use shared APIs. |
| `climatology_model_evaluation_by_code.ipynb` | Cells 5/7/10/12 repeat model loading, sample preparation, scores, and plots. Cell 3 ignores the configuration exposed in cell 2. |
| `climatology_noise_floor.ipynb` | Cell 2 repeats loading, fallback, statistics, and plots. Use 14's replicate-variability definition. Get physical time from coordinates. |
| `enstrophy_convergence.ipynb` and `enstrophy_convergence_long_run.ipynb` | Merge into one parameterized example. They differ mainly in path and title. Cell 6 confuses absolute snapshot indices with window lengths and mislabels the reference interval. |
| `nc_processing_example.ipynb` | Cell 2 imports fix_time_units from the wrong module and reimplements loading. Cells 5-7 own reusable plots. |
| `other_visualizations.ipynb` | Cell 2 imports nonexistent ml.isca_dataset and uses undefined SIM_DIR. Cell 3 repeats time fixes. Remove or correctly derive the incomplete PDE-residual diagnostic in cell 9. |
| `barotropic_visualization.ipynb` | Cell 9 uses np without an import. Cells 9-32 own reusable calculations and plots. Label u-only energy as such or compute total kinetic energy using u and v. |
| `ml/notebooks/eval_test.py` | Uses the removed model argument and fabricated latitudes. Replace its duplicate evaluation with shared API tests. |

Use the same order: purpose, parameters, imports, library calls, interpretation.
Keep source paths configurable. Remove stale outputs and saved exceptions.

For the heat notebook, move the solver into `heat_simulation`, not into ML.
Reuse one trajectory for snapshots and animation. Correct the one-step time-label offset.
Alternatively, explicitly archive this separate demonstration.

## Verify

1. Add fixture-backed notebook checks. Execute every retained notebook from a fresh kernel with bounded inputs and a timeout.
2. Check both convergence notebook scenarios through the merged notebook's parameters.
3. Require notebook and CLI predictions, targets, and scores to agree. Use real stored coordinates.
4. Scan cells for reusable function definitions and copied IO, metric, inference, and plotting logic. Each must move to its package or have a specific justified exception.
5. For retained heat logic, test a constant solution with zero source, a stable Fourier mode's decay, and snapshot times including t=0. Confirm animation reuses the same trajectory.
6. Visually inspect figures and labels. Require no saved traceback or obsolete results.
