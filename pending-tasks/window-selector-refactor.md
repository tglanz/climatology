# Windowing config refactor and non-overlapping selector

Pending task: introduce a `[data.windows]` config section, rename the
relevant fields for clarity, encapsulate the selection logic in a class
hierarchy under `ml/src/ml/data/window_selector.py`, add a
`non_overlapping` selector, and switch the default config to use it
(FNO-2D-style tiling).

## Motivation

Current state in `ml/config.toml` and `ml/src/ml/config.py`:

- Four logically-grouped fields live directly under `[data]` next to
  unrelated fields like `experiment_dir`, `simulation_pattern`, etc.:
  `lag_steps`, `sampling`, `skip`, `samples_per_experiment`.
- `sample_indices(n_available, samples, sampling)` in
  `ml/src/ml/data/isca_dataset.py` is a string-branching function. The
  proposed `non_overlapping` mode needs `lag_steps`, which the current
  signature does not carry, so adding it forces awkward parameter
  tunneling.
- Field names are imprecise: `sampling` covers deterministic modes,
  `skip` is in unclear units, `samples_per_experiment` doubly overloads
  "samples" and "experiment".
- We have no way to use **all** valid windows from a simulation, only
  cap-based subsets. This blocks an FNO-2D-style training-pair density
  experiment.

## Goal

- Move all training-pair extraction config into a dedicated
  `[data.windows]` section with explicit, unambiguous field names.
- Replace the function-with-string-branch with a small
  `WindowSelector` ABC and one concrete class per selection mode, in
  `ml/src/ml/data/window_selector.py`.
- Add `NonOverlappingSelector`, which tiles the post-spinup timeline
  into disjoint windows of length `input_length + 1` and uses every
  one (or up to a cap).
- After the refactor lands, set the default config to use
  `non_overlapping` so each simulation contributes the maximum number
  of disjoint training pairs.

## Why non-overlapping by default

- `samples_per_experiment` was an arbitrary knob (8 vs 10 vs 20 has
  no principled justification). `non_overlapping` instead uses the
  natural unit of the operator (one window = `input_length + 1`
  snapshots) and lets the pair count fall out of the timeline length.
- Closer to FNO-2D's training data structure (which uses every valid
  window) but without the heavy overlap that makes consecutive pairs
  share `K-1` of `K` input snapshots. Non-overlap means each snapshot
  belongs to at most one (input, target) pair.
- Deterministic, reproducible, no random seed.

## Proposed config layout

```toml
[data.windows]
input_length = 5
selection = "non_overlapping"     # latest | evenly_spaced | uniform | non_overlapping
spinup_timesteps = 30
# max_per_simulation = 12          # optional cap; absent or null = take all available
```

The four other names that currently sit directly under `[data]` move
into this section. Renames (old to new):

| current                  | new                  | unit / meaning                                 |
|--------------------------|----------------------|------------------------------------------------|
| `lag_steps`              | `input_length`       | snapshots in one model input window            |
| `sampling`               | `selection`          | name of the selection strategy                 |
| `skip`                   | `spinup_timesteps`   | first valid target index (target-anchored)     |
| `samples_per_experiment` | `max_per_simulation` | optional upper cap on windows kept per sim     |

### `spinup_timesteps` semantics (definition)

`spinup_timesteps = N` means: **no window has its target at a timeline
index below N**. The earliest input snapshot of the first selected
window may be at index `N - input_length + 1`, which is fine because
spinup is naturally measured from the perspective of the target we
predict against, not the inputs.

Concretely with `input_length=5`, `spinup_timesteps=30`,
`timeline_length=105`: valid target indices are `30, 31, ..., 104`,
i.e. 75 valid candidate windows. The first selected window's input
spans timesteps `26..30`, target at `30`.

This matches how a domain user thinks: "skip the first 30 days of
spinup, then start training."

## Class hierarchy

New module `ml/src/ml/data/window_selector.py`:

```python
class WindowSelector(ABC):
    @abstractmethod
    def select(self, n_valid: int) -> list[int]: ...

class EvenlySpacedSelector(WindowSelector):
    def __init__(self, count: int): ...

class UniformSelector(WindowSelector):
    def __init__(self, count: int): ...

class LatestSelector(WindowSelector):
    def __init__(self, count: int): ...

class NonOverlappingSelector(WindowSelector):
    def __init__(self, input_length: int, count: int | None = None): ...

def build_selector(cfg: WindowsConfig) -> WindowSelector: ...
```

`select(n_valid)` returns a sorted list of indices into the
`valid_target_indices` array (the same flat list the current
`sample_indices` operates on). `n_valid` is the length of that list
after `spinup_timesteps` has already been applied.

`NonOverlappingSelector.select` returns indices `[0, S, 2S, ...]` where
`S = input_length + 1`, capped at `n_valid` and (optionally) at
`count`.

`build_selector(cfg)` is the factory: dispatches on
`cfg.selection`, instantiates the right class with the args it needs,
returns a `WindowSelector` instance. Each constructor declares
exactly the fields it requires; no per-mode tunneling through a
generic signature.

## Implementation steps

### `ml/src/ml/config.py`

- Add `VALID_SELECTIONS = ("evenly_spaced", "uniform", "latest", "non_overlapping")`.
- New dataclass:
  ```
  @dataclass
  class WindowsConfig:
      input_length: int = 1
      selection: str = "evenly_spaced"
      spinup_timesteps: int = 0
      max_per_simulation: int | None = None
  ```
  Validate `input_length >= 1`, `selection in VALID_SELECTIONS`,
  `spinup_timesteps >= 0`,
  `max_per_simulation is None or max_per_simulation > 0`.
  For modes other than `non_overlapping`, require `max_per_simulation`
  to be set (since they are cap-only modes by nature).
- Restructure `IscaDataConfig` to drop the old fields and embed
  `windows: WindowsConfig`. Update `__post_init__` accordingly.
- Update `load(...)` to parse `[data.windows]`. Keep clear errors when
  the legacy keys appear at the wrong level (loud failure with a
  migration hint, not a silent skip).
- Move the cross-check `model.fno.in_channels == lag_steps * len(x_vars)`
  to use `data.windows.input_length` and the active architecture
  sub-config.

### `ml/src/ml/data/window_selector.py` (new)

- Implement `WindowSelector`, the four selectors, and `build_selector`.
- Each selector has a `reason()` or `__repr__` that prints its
  configuration (handy for logs).
- Unit-friendly: each `select` is a pure function of `n_valid` (and
  the constructor args), no I/O.

### `ml/src/ml/data/isca_preprocessing.py`

- Replace `sample_indices(...)` call with
  `selector = build_selector(cfg.data.windows)` and
  `selected = selector.select(len(valid_target_indices))`.
- Use `cfg.data.windows.input_length` and
  `cfg.data.windows.spinup_timesteps` everywhere `lag_steps` and
  `skip` were used.

### `ml/src/ml/data/isca_dataset.py`

- Delete or deprecate the existing `sample_indices` function once no
  callers remain. Keep the file otherwise unchanged.

### `ml/src/ml/training_info.py`

- Update `_collect_data(...)` to record the new structure under
  `data.windows` (input_length, selection, spinup_timesteps,
  max_per_simulation). Drop the legacy fields.

### `ml/src/ml/cmd/preprocess.py`

- Update the `validate-simulations` command to use
  `cfg.data.windows.input_length` instead of `cfg.data.lag_steps` for
  its timeline-length check.

### `ml/src/ml/inference.py` and `ml/src/ml/cmd/evaluate.py`

- These read `lag_steps` indirectly. Update any reference to use
  `cfg.data.windows.input_length`.

### `ml/config.toml`

- Move the four fields under `[data.windows]`, renamed.
- Set `selection = "non_overlapping"`.
- Drop `max_per_simulation` (or leave commented) so each sim
  contributes all available non-overlapping windows.
- Add the model `in_channels` cross-reference comment using the new
  field name.

### `docs/pipeline.md`

- Update the preprocessing section to reference the new field names
  and selection modes.

## Acceptance criteria

- `ml preprocess training-data -c ml/config.toml` runs with
  `selection = "non_overlapping"` and produces strictly more pairs per
  simulation than `samples_per_experiment = 8` did, with each pair's
  input and target snapshots used in at most one pair.
- All four selection modes have at least one passing manual
  smoke-test: `evenly_spaced`, `uniform`, `latest`, `non_overlapping`.
- `ml train -c ml/config.toml` runs end-to-end against the new
  preprocessed data.
- `ml util model-info -c ml/config.toml` shows the new pair counts.
- Loading a config that still uses the legacy field names at the old
  location fails with a clear migration message (do not silently
  succeed).
- `training.json` records the new `data.windows` structure.

## Open questions / decisions to defer

- **Configurable overlap.** A future selector could expose a `stride`
  field for partial-overlap tiling (e.g., stride = `input_length / 2`
  for half-overlap). Out of scope here; revisit if there's a measured
  reason to want it.
- **Different selection per split.** Today all three splits (train,
  val, test) share the same `[data.windows]` config. Could split into
  per-split sub-configs later. Out of scope.
- **`max_per_simulation` for non_overlapping.** Default is "all"
  (`None`). Setting a cap silently drops the latest tiles; that is the
  intended behavior. Document it.
- **Backwards compatibility.** No need to support the legacy field
  layout silently. The repo is small and the user is the only
  consumer. Failing loud with a migration hint is the right tradeoff.

## Sub-tasks

- Create `ml/src/ml/data/window_selector.py` with the ABC, four
  selectors, and `build_selector` factory.
- Add `WindowsConfig` dataclass and validation in `config.py`.
- Restructure `IscaDataConfig` and `load(...)` to nest the new section.
- Update `isca_preprocessing.py` to consume the selector instead of
  `sample_indices`.
- Update `training_info.py`, `preprocess.py`, `inference.py`,
  `evaluate.py` to use the renamed fields.
- Re-preprocess against the new config.
- Run `ml util model-info -c ml/config.toml` and confirm the new pair
  counts.
- Run `ml util persistence-score -c ml/config.toml` and record the
  baseline at the new train/val sample sizes.
- Train end-to-end and compare best val loss against the prior run
  with `samples_per_experiment = 8`.
- Update `docs/pipeline.md` to reflect the new field names.
- Delete the old `sample_indices` function once unreferenced.

## Final config snapshot (post-implementation)

```toml
[data]
experiment_dir = "./output/barotropic_stirring-T85"
simulation_pattern = "simulations/*"
segment_pattern = "run*/atmos_daily.nc"
x_vars = ["vor", "stirring"]
y_vars = ["vor"]

[data.windows]
input_length = 5
selection = "non_overlapping"
spinup_timesteps = 30
# max_per_simulation = 12         # optional cap

[data.split]
validation = 0.1
test = 0.1
train = 0.8
```
