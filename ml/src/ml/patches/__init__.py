"""
Runtime patches for third-party libraries we depend on.

Each patch module fixes one upstream bug; see its module docstring for
the rationale. Patches are gated by the conditions that make them
necessary (device, architecture, ...), so they're no-ops elsewhere.

Call `ml.patches.apply()` once at the start of every entry point. It is
idempotent, so duplicate calls are safe.
"""

import torch


def apply() -> None:
    if torch.backends.mps.is_available():
        from ml.patches.neuralop import patch_sht_dtype_device_order
        patch_sht_dtype_device_order()
