# 19. Create a fast iteration profile

Priority: P1. Reuse 01-07. No new simulation campaign is needed to start.

## Recommendation

Use a small immutable dataset and smaller run configuration through the existing ML pipeline.
A separate directory such as `output/dev/` is useful for artifacts.
Keep one code path for full and small runs.

Start with two sizes:

| Profile | Proposed budget | Purpose |
|---|---|---|
| Smoke | A few tiny segmented fixtures, one or two CPU epochs, batch 2, workers 0 | Check IO, shapes, loss, checkpoint reload, and report creation |
| Development | Fixed real simulations from several forcing configurations, a few replicas and windows, small SFNO, at most a few epochs | Compare code changes and debug behavior |

Select full existing trajectories before selecting input windows.
Preserve the post-spinup and climatology target rules.
Keep whole simulations and forcing groups within their intended splits.
Do not treat short unconverged trajectories or resampled coarse fields as equivalent scientific data.

## Work

Save a subset manifest, seed, source fingerprints, config, and exact run commands.
Prepare and cache the small dataset once. Reuse it while changing the model.
Use a small width, layer count, and retained mode count supported by its grid.
Default expensive diagnostics off. Always keep scalar history.
Store full and development artifacts separately.
Avoid config inheritance machinery unless simple explicit files prove inadequate.

## Verify

1. Measure preprocessing, one training epoch, reload, and evaluation separately on named hardware.
2. Set an explicit local time and memory budget from those measurements. Initial targets: smoke under one minute and development under five minutes, to confirm or revise.
3. Run the same commands used for full data with only config/manifest changes.
4. Require repeatable splits and inputs, finite loss, a checkpoint, scalar history, reloaded prediction parity, and a valid report.
5. Change only a model parameter. Cached preprocessing must remain reusable.
6. Check that development artifacts cannot overwrite full results. Label development scores as workflow evidence, not thesis results.
