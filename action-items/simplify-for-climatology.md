# Simplify: Climatology-Only Prediction

## Motivation

The system currently supports two prediction modes:
- **Step prediction**: predicts per-timestep diagnostics, `y` shape `(N, V, H, W)`
- **Climatology prediction**: predicts time-mean zonal-mean diagnostics, `y` shape `(N, C, H)`

Step prediction is no longer used. Supporting both modes introduces branching on `is_climatology` / `y.ndim` throughout the stack, dual shape assumptions, and dead code paths. Dropping step support simplifies the codebase significantly.

---

## Files to Change

### `ml/src/ml/data/isca_preprocessing.py`
- Remove `step_y_vars` / `clim_y_vars` separation (lines 50-52)
- Remove step-mode validation against segment (line 62)
- Remove the `is_clim` flag; always assume climatology
- Remove the step-mode output branch (lines 126-131); always append `clim_array`

### `ml/src/ml/usecases/preprocess.py`
- Remove `step_y_vars` / `clim_y_vars` split (lines 26-29)
- Remove `kind` attribute write branching (lines 70-71); always write `kind = "climatology"`
- Remove step `y` shape path; always produce `(N, C, H)`

### `ml/src/ml/cmd/train.py`
- Remove `clim_target` flag (lines 39-40)
- Always build model with `zonal_mean=True`

### `ml/src/ml/training/model.py`
- Remove the `zonal_mean: bool` parameter from `build_model()`
- Always wrap with `ZonalMeanWrapper`; remove the conditional (line 46)

### `ml/src/ml/training/trainer.py`
- Remove `y.ndim` branching in normalizer setup (lines 116-121)
- Always use `dim=[0, 2]` for `normalizer_y`

### `ml/src/ml/common/training_metrics.py`
- Remove `is_clim = y.ndim == 3` check (line 101)
- Remove step-mode metric paths (power spectrum, zonal_mean_error, spatial_error 2D)
- Always compute `profile_pred`, `profile_pred_std`, `profile_truth`

### `ml/src/ml/common/monitor.py`
- Remove `self.is_climatology` flag (line 37) and all step-mode state fields
- Remove step-mode history fields: `zonal_mean_history`, `error_power`, `signal_power`

### `ml/src/ml/cmd/monitor.py`
- Remove `_run_gui_step()` function entirely (lines 113-234)
- Remove the `if state.is_climatology` branch (lines 318-321)
- Keep only `_run_gui_climatology()`

### `ml/src/ml/training/baselines.py`
- Remove entirely, or remove `_assert_persistence_supported()` (lines 9-13) since persistence is step-only and irrelevant

### `ml/src/ml/usecases/validate_simulations.py`
- Remove `step_y_vars` separation (line 41) if it gates any step-only logic

### `ml/src/ml/config.py`
- Remove `climatology: ClimatologyConfig | None = None` field from `IscaDataConfig` (line 176); make `ClimatologyConfig` always required
- Remove the cross-validation guard that checks whether climatology section exists only when needed (lines 188-196)
- Simplify `IscaDataConfig`: `y_vars` are always climatology vars, no need to infer mode from content

### `ml/configs/*.toml`
- The `[data.climatology]` section is currently conditional; make it always present and required
- No other config changes needed since existing configs already use climatology vars

---

## Shape Contract After Simplification

| Tensor | Shape | Notes |
|--------|-------|-------|
| `x` | `(N, C_x, K, H, W)` | unchanged |
| `y` | `(N, C_y, H)` | always 3D, no longitude |

---

## Out of Scope

- `submodules/isca/` scripts (`create_timeseries.py`, etc.) use `is_climatology` for a different purpose (time array creation). Do not touch.
- `ml/src/ml/diagnostics/evaluation.py` already assumes climatology-only; verify it stays consistent after changes.
