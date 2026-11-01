# 09. Use one plotting contract

Priority: P2. Needed by 10.

## Evidence

`ml/src/ml/visualization/evaluation.py:14` sets Agg during import.
Other plot modules call show internally while evaluation plots return figures.
Training-curve reading and plotting exist in both `visualization/evaluation.py:57-75` and `visualization/training.py:5-22`.
`visualization/meridional_profile.py:56,71` synthesizes uniform latitudes instead of using the data coordinates.

## Work

Make reusable plot functions accept real coordinates and return figure/axes.
Let the application select the backend, show, save, and close.
Give each plot and its data preparation one owner.
Move remaining reusable notebook plots here without creating a generic plotting framework.

## Verify

1. Add `test_visualization.py`. Render fixed data with nonuniform latitudes under Agg.
2. Require plotted coordinates to equal the supplied coordinates. Check one panel, two panels, and the chosen empty-input behavior.
3. In an isolated process, select a non-Agg backend or spy on backend-selection calls before importing plot modules. Assert no backend change and no show call. Testing only an existing Agg session would miss the current defect.
4. Save and inspect representative profile, convergence, spectrum, map, and training plots.
5. Check an interactive notebook or monitor when that environment is available. State when this check is skipped.
