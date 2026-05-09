# Architecture decoupling and SFNO support

Pending task: make the model architecture configurable, add SFNO as a
selectable backend, and switch the active architecture in
`ml/config.toml` to `sfno` once the decoupling is in place.

## Motivation

Two reasons stacked:

- **General flexibility.** The model factory is hardcoded to FNO. We
  expect to want other architectures over time (TFNO, U-Net baseline,
  potentially RNO for autoregressive stability). Doing the decoupling
  once, cleanly, removes a recurring blocker.
- **SFNO is the right inductive bias for our data.** Our grid is
  lat-lon on the sphere. Latitude is **not** periodic; the poles are
  geometric singularities. Standard FNO assumes a periodic torus in
  both dimensions, so its 2D FFT pretends latitude wraps around. SFNO
  uses spherical harmonic transforms instead, which respect the
  spherical geometry exactly. Pangu-Weather, FourCastNet-v2, and
  GraphCast all moved to spherical harmonics for this reason and
  achieve year-scale stable rollouts. See `docs/fno.md` and
  `docs/next-steps.md`.

## Why SFNO might perform better here

- FNO's torus assumption is wrong on one of our two axes. Errors near
  the poles can leak through wraparound and contaminate the rest of
  the field.
- The natural basis for square-integrable functions on the sphere is
  the spherical harmonics, and barotropic vorticity dynamics on the
  sphere is naturally expressed in that basis (Isca itself runs in
  spherical harmonics internally; see `T85` truncation in
  `sim/example_barotropic_stirring.py`).
- The lat-weighted relative L2 loss already partially accounts for
  the spherical geometry on the loss side. SFNO does the same on the
  architecture side.

This is one of the cheapest architectural changes we can try before
moving to bigger interventions like probabilistic outputs or
multi-step output supervision.

## Goal

A single config knob `model.architecture` selects which backend is
built. Per-architecture options live in their own subsections
(`[model.fno]`, `[model.sfno]`). Only the subsection matching the
active architecture is read at training time. The user-facing CLI
(`ml train`, `ml util model-info`, `ml evaluate autoregression`)
behaves identically apart from the architecture knob.

## Proposed config layout

```toml
[model]
architecture = "sfno"   # fno | sfno

[model.fno]
n_modes = [32, 64]
hidden_channels = 64
n_layers = 4
in_channels = 10        # MUST equal data.lag_steps * len(data.x_vars)
out_channels = 1

[model.sfno]
# SFNO is a near drop-in for FNO; same constructor signature with the
# convolution module swapped (SpectralConv -> SphericalConv).
# n_modes here is interpreted on the spherical harmonic basis, not
# rectangular Fourier modes; tune separately.
n_modes = [32, 64]
hidden_channels = 64
n_layers = 4
in_channels = 10        # MUST equal data.lag_steps * len(data.x_vars)
out_channels = 1
```

Notes on the SFNO section:

- `submodules/neuraloperator/neuralop/models/sfno.py` defines SFNO as
  `partialclass("SFNO", FNO, factorization="dense", conv_module=SphericalConv)`.
  The constructor signature is therefore the same as `FNO`. The same
  field names work; the semantics of `n_modes` differs (spherical
  harmonic degree / order rather than rectangular Fourier mode counts).
- Optional knobs we deliberately defer (do **not** add now): `factorization`,
  `rank`, `domain_padding`, `fno_skip`, `channel_mlp_skip`,
  `preactivation`, `complex_data`. Add them only after a baseline SFNO
  run motivates exposing one of them.
- The dropout knob (`training.regularization.dropout`) maps to
  `channel_mlp_dropout` for both FNO and SFNO. No change in the
  regularization contract.

## Implementation steps

- **`ml/src/ml/config.py`**:
  - Introduce `SFNOModelConfig` dataclass mirroring `FNOModelConfig`.
    Same fields. Independent class so future divergence is cheap.
  - Add `VALID_ARCHITECTURES = ("fno", "sfno")`.
  - Restructure `ModelConfig` to:
    ```
    @dataclass
    class ModelConfig:
        architecture: str
        fno: FNOModelConfig | None
        sfno: SFNOModelConfig | None
    ```
    Validate in `__post_init__` that `architecture in VALID_ARCHITECTURES`
    and that the matching sub-config is not None.
  - Update `load(...)` to read the new layout. Parse `[model]` for
    `architecture`. Parse `[model.fno]` / `[model.sfno]` only if the
    section is present; sections may be absent for the inactive
    architecture.
  - Move the existing `in_channels == lag_steps * len(x_vars)`
    cross-check so it runs on the **active** sub-config only.

- **`ml/src/ml/model.py`**:
  - Refactor `build_model(...)` to take the full `ModelConfig` (not
    just `cfg.model.fno`). Dispatch on `cfg.architecture`:
    ```
    def build_model(cfg: ModelConfig, dropout: float | None = None):
        if cfg.architecture == "fno":
            kwargs = asdict(cfg.fno)
        elif cfg.architecture == "sfno":
            kwargs = asdict(cfg.sfno)
        else:
            raise ValueError(...)
        if dropout is not None:
            kwargs["channel_mlp_dropout"] = dropout
        return _ARCH_TO_CLASS[cfg.architecture](**kwargs)
    ```
  - Import `SFNO` lazily so an installation without `torch_harmonics`
    does not fail at import time when running an FNO-only config.
    Instantiation must error clearly if `architecture = "sfno"` and
    `torch_harmonics` is missing.

- **All callers** that currently pass `cfg.model.fno`:
  - `ml/src/ml/cmd/train.py`
  - `ml/src/ml/cmd/util.py` (the `model-info` command builds a model)
  - `ml/src/ml/cmd/evaluate.py`
  Change them to pass `cfg.model`.

- **`ml/src/ml/training_info.py`**:
  - Update `_collect_model(...)` to record `architecture` plus the
    active sub-config in the run snapshot. Today it hardcodes
    `"architecture": "FNO"` and reads `cfg.model.fno`. Make it dispatch.

- **`ml/src/ml/cmd/util.py:model-info`**:
  - Print `architecture: <fno|sfno>` first, then the active sub-config
    fields. The `params/sample` ratio block is unchanged.

- **`ml/config.toml`**:
  - Add the new `[model]` section with `architecture = "sfno"`.
  - Keep the existing `[model.fno]` populated as a parked example.
  - Add a populated `[model.sfno]` section (same field values as the
    existing `[model.fno]` to start; tune later).

- **Dependencies**:
  - SFNO requires `torch_harmonics`. Verify it is in the conda env or
    `uv` project. If not, add it and document the install path. Do a
    `python -c "import torch_harmonics"` smoke check during the
    implementation.

## Acceptance criteria

The implementation is done when all of these hold:

- `ml train -c ml/config.toml` works with `architecture = "fno"` and
  produces identical numbers (within float noise) to the pre-refactor
  run on the same data.
- `ml train -c ml/config.toml` works with `architecture = "sfno"` and
  completes at least one full epoch with a finite, decreasing loss.
- `ml util model-info -c ml/config.toml` prints the active
  architecture and matching sub-config.
- `ml evaluate autoregression -c ml/config.toml ...` runs on a
  checkpoint produced by either backend.
- The `in_channels` cross-check still triggers when the **active**
  sub-config has a wrong `in_channels`.
- `training.json` records the active architecture and its config.

## Open questions / decisions to defer

- **`n_modes` semantics across backends.** Same field name on both,
  different mathematical meaning (spherical harmonic degree/order vs
  rectangular Fourier mode counts). We keep the field name for parsing
  convenience and rely on doc strings; this is a soft compromise.
- **Optional SFNO knobs** (`factorization`, `rank`, `domain_padding`,
  etc.). Defer to a follow-up; baseline first, expose only what a
  diagnostic actually motivates.
- **Loss interaction.** `lat_weighted_relative_l2` is independent of
  the architecture and stays as-is. Worth noting that with SFNO the
  cosine-latitude weighting is somewhat redundant with the spherical
  basis, but it does not hurt.
- **Checkpoint compatibility.** FNO and SFNO checkpoints are not
  interchangeable. Switching architectures requires retraining from
  scratch. The `parameters.pt` file does not encode which architecture
  it belongs to; the run's `config.toml` snapshot is the source of
  truth. Document this in `docs/pipeline.md` after the refactor lands.
- **iFNO / multi-resolution.** Not in scope here. Both could later be
  added as additional architectures or as flags within an existing
  one.

## Sub-tasks

- Read `submodules/neuraloperator/neuralop/models/sfno.py` and confirm
  the constructor signature matches `FNO` exactly (it does today via
  `partialclass`).
- Verify `torch_harmonics` import works in the active environment.
- Add `SFNOModelConfig` and restructured `ModelConfig` in `config.py`.
- Update `load(...)` to parse the new TOML layout; preserve existing
  validation (split sums, sampling/loss/optimizer enums, etc.).
- Refactor `build_model(...)` to accept `ModelConfig` and dispatch.
- Update all three CLI callers to pass `cfg.model`.
- Update `training_info.py` to record architecture and active sub-config.
- Update `model-info` util output.
- Update `ml/config.toml` to the new layout, with `architecture = "sfno"`.
- Smoke test:
  - `ml util model-info -c ml/config.toml` prints SFNO info.
  - `ml train -c ml/config.toml` runs at least one epoch on real data
    without errors. Compare wall-clock and loss shape against an FNO
    run on the same preprocessed data.
- Update `docs/pipeline.md` with a one-paragraph note on the
  architecture knob and the checkpoint-compatibility caveat.
