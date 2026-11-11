"""Retained shared-mechanics checks; scientific behavior lives in correctness tests."""

import numpy as np
import torch

from ml.data.simulation_data import build_timeline, stack_input_windows
from ml.diagnostics.errors import lat_weighted_relative_l2_torch


def test_time_major_stacking_crosses_segment_boundary(simulation):
    paths, values, _ = simulation
    windows = stack_input_windows(
        build_timeline(paths, [6, 6]), [4], 3, ["vor", "vcomp"], {}
    )
    assert windows.shape == (1, 6, 4, 12)
    for offset in range(3):
        np.testing.assert_array_equal(windows[0, 2 * offset], values[4 + offset])
        np.testing.assert_array_equal(
            windows[0, 2 * offset + 1], values[4 + offset] + 4
        )


def test_weighted_field_gradient():
    pred = torch.full((1, 1, 2, 3), 2.0, requires_grad=True)
    truth = torch.ones_like(pred)
    weights = torch.tensor([1.0, 2.0])
    loss = lat_weighted_relative_l2_torch(pred, truth, weights)
    assert loss.item() == 1
    loss.backward()
    expected = weights.view(1, 1, 2, 1).expand_as(pred) / 9
    torch.testing.assert_close(pred.grad, expected, rtol=1e-7, atol=0)
