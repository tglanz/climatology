# Data Preparation for FNO Training

This document covers options for preparing input data before training the Fourier Neural
Operator on Isca vorticity fields. It explains what approaches exist, their tradeoffs, and
what is recommended for this project.

## The Problem with Raw Vorticity Fields

The current preprocessing pipeline (`ml/src/ml/isca_preprocessing.py`) writes raw
float32 values from the Isca NetCDF files directly into the HDF5 training archive, with
no normalization step. The trainer then loads and feeds these tensors to the FNO without
any scaling.

This has a measurable effect on training. The `relative_l2` loss is defined as:

    loss = mean( ||pred - target|| / ||target|| )

A value of 1.0 means the prediction error is as large as the target signal, which is
equivalent to predicting zero everywhere. The first training run reached a best validation
loss of 1.12 at epoch 62 and then degraded, suggesting the model learned the approximate
scale of vorticity but not its spatial structure.

Vorticity fields from T85 Isca runs typically span several orders of magnitude across
channels (`vor` and `stirring` have different physical scales). Without normalization, the
optimizer spends most of its budget on scale correction rather than learning the operator.

## What Can Be Done

### Option 1: No Normalization (Current State)

Feed raw float32 tensors to the model. The model must learn the scale of the target
distribution from scratch.

Tradeoff: slow convergence, high sensitivity to learning rate, difficult to reach low
relative L2 values. Only reasonable when fields are already physically non-dimensionalized.

### Option 2: Global Normalization

Compute a single mean and standard deviation over all samples, all spatial locations, and
all channels. Subtract and divide.

    x_norm = (x - global_mean) / global_std

Tradeoff: simple, but loses per-channel scale information. Not suitable here because `vor`
and `stirring` have different physical units and magnitude ranges.

### Option 3: Channel-wise Normalization (Recommended)

Compute mean and standard deviation separately for each input channel and each output
channel, reducing over batch, height, and width. This is z-score normalization:

    x_norm[c] = (x[c] - mean[c]) / std[c]

For data shaped `(batch, channels, height, width)` the reduction dimensions are
`[0, 2, 3]`, leaving one mean and one std per channel.

This is the approach used in the `neuraloperator` Darcy flow tutorial (see References).
It preserves relative structure within each field while putting all channels on a common
scale for the optimizer.

### Option 4: Pixel-wise Normalization

Compute mean and standard deviation per spatial location per channel, reducing only over
the batch dimension.

Tradeoff: captures spatially non-uniform climatological biases (e.g. polar vs equatorial
vorticity), but requires a large training set to estimate per-pixel statistics reliably
and can produce degenerate std values in quiescent regions. Not recommended here unless
the dataset is very large.

### Option 5: Normalize Output Only

Apply normalization to the target `vor` field but not to the inputs. Useful if the input
scale is already well-conditioned but the output distribution is skewed.

Tradeoff: asymmetric treatment can confuse the model when input and output share the same
physical variable (`vor` appears in both `x` and `y`). Not recommended.

### Option 6: Preprocessing-time vs Training-time Normalization

Normalization statistics can be computed and applied at two points:

**Preprocessing time**: compute stats from training split, write normalized values into
the HDF5 file. Simple, but requires re-running preprocessing if the training split
changes. Stats must be serialized separately for inverse transformation at inference time.

**Training time**: load raw HDF5 values, fit a normalizer on the training `DataLoader`,
then apply it as a transform in the dataset. More flexible. The `neuraloperator` library
provides ready-made classes for this approach.

## neuraloperator References

All classes below are in the `submodules/neuraloperator` git submodule.

### UnitGaussianNormalizer

`neuralop/data/transforms/normalizers.py`, class `UnitGaussianNormalizer` (line 33)

Normalizes data to zero mean and unit standard deviation. Supports:

- `fit(data_batch)`: compute mean and std from a full tensor in one pass (line 84)
- `partial_fit(data_batch, batch_size)`: incremental fitting for datasets too large to
  fit in memory (line 87)
- `transform(x)`: apply `(x - mean) / (std + eps)` (line 154)
- `inverse_transform(x)`: undo normalization (line 157)
- `dim` parameter: list of dimensions to reduce over when computing stats (line 65)

The `dim` parameter controls granularity. For channel-wise normalization of
`(batch, channels, height, width)` tensors, pass `dim=[0, 2, 3]`.

Example from the test suite (`neuralop/data/transforms/tests/test_unit_gaussian_normalizer.py`, line 24):

```python
from neuralop.data.transforms.normalizers import UnitGaussianNormalizer

normalizer = UnitGaussianNormalizer(dim=[0, 2, 3])
normalizer.fit(train_x)           # shape: (N, C, H, W)
x_norm = normalizer.transform(x)
x_reconstructed = normalizer.inverse_transform(x_norm)
```

### DefaultDataProcessor

`neuralop/data/transforms/data_processors.py`, class `DefaultDataProcessor` (line 67)

Wraps input and output normalizers into a single object with `preprocess` and
`postprocess` methods. During training, both input and output are normalized. During
evaluation, the output is inverse-transformed before the loss is computed, so validation
metrics are in the original physical units.

Key methods:
- `preprocess(data_dict, batched=True)` (line 98): normalize x and y, move to device
- `postprocess(output, data_dict)` (line 131): inverse transform output for eval
- `to(device)` (line 90): move normalizer statistics to GPU or MPS

Usage pattern from `examples/models/plot_FNO_darcy.py` (line 52):

```python
from neuralop.data.transforms.data_processors import DefaultDataProcessor
from neuralop.data.transforms.normalizers import UnitGaussianNormalizer

in_norm = UnitGaussianNormalizer(dim=[0, 2, 3])
in_norm.fit(train_x)

out_norm = UnitGaussianNormalizer(dim=[0, 2, 3])
out_norm.fit(train_y)

data_processor = DefaultDataProcessor(in_normalizer=in_norm, out_normalizer=out_norm)
data_processor = data_processor.to(device)
```

Note that `DefaultDataProcessor` computes training loss in normalized space and
validation loss in physical space. If you want both in normalized space (which makes the
target loss threshold of 0.1 directly interpretable as 10% relative error on normalized
data), the inverse transform in `postprocess` should be skipped or the loss should be
computed before calling `postprocess`.

### PTDataset

`neuralop/data/datasets/pt_dataset.py`, class `PTDataset` (line 12)

High-level dataset class that accepts `encode_input` and `encode_output` boolean flags
and automatically creates `UnitGaussianNormalizer` instances, fits them on the training
data, and wraps them in a `DefaultDataProcessor`. The `encoding` parameter selects
`"channel-wise"` or `"pixel-wise"` normalization (line 70).

This is the most convenient entry point if you restructure the data loading to use
`PTDataset` directly, but requires saving data in the format it expects.

## Recommendation

Apply channel-wise z-score normalization to both inputs and outputs using
`UnitGaussianNormalizer` with `dim=[0, 2, 3]`. Fit the normalizers on the training
split only.

The simplest integration point is in `ml/src/ml/training.py`, inside `Trainer.__init__`,
after the training `DataLoader` is available. Fit the normalizers by iterating one pass
over the training loader, then pass a `DefaultDataProcessor` into `train_epoch` and
`evaluate` to apply the transform on each batch.

Alternatively, add a normalization step at the end of `isca_preprocessing.py` after all
training pairs are written. Compute per-channel stats from the training HDF5 file, write
normalized float32 arrays back, and save the stats (mean, std per channel) as HDF5
attributes or a companion JSON file so they can be loaded at inference time.

The training-time approach is more flexible and avoids re-running the Isca preprocessing
when experimenting with normalization settings.

Expected impact: with normalized inputs and outputs the relative L2 loss for a random
model should start near 1.0 rather than near 500. Convergence to the target of 0.1
(10% relative error) becomes achievable within the configured 300 epochs.
