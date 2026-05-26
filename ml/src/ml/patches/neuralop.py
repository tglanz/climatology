"""
In-memory patches for neuraloperator internals. Kept in our tree (not as
a submodule edit) so the third-party source stays bit-for-bit upstream
and submodule bumps don't conflict.

SHT dtype/device ordering on MPS
--------------------------------
`neuralop.layers.spherical_convolution.SHT.sht` and `.isht` lazily build
a `RealSHT` / `InverseRealSHT` and chain `.to(device=x.device).to(dtype=
self.dtype)`. The freshly-built transform holds fp64 Legendre buffers
(precomputed via numpy in `torch_harmonics.legendre.legpoly`). On MPS,
`.to(device=mps)` rejects fp64 tensors, so the first forward pass dies
before the dtype cast is reached.

Swapping the calls -- cast to fp32 on CPU first, then move to device --
is the workaround the torch_harmonics maintainer explicitly recommends
in NVIDIA/torch-harmonics#154. The fp64 Legendre recursion still runs
on CPU during `RealSHT.__init__`; only the final cast moves from device
to CPU. Functionally identical to upstream on CUDA/CPU; unblocks MPS.

Upstream method bodies are copied verbatim aside from the swap so future
upstream bumps stay easy to merge.
"""
from neuralop.layers.spherical_convolution import SHT
from torch_harmonics import RealSHT, InverseRealSHT


_PATCH_ATTR = "_dtype_device_order_patched"


def patch_sht_dtype_device_order() -> None:
    if getattr(SHT, _PATCH_ATTR, False):
        return

    def sht(self, x, s=None, norm="ortho", grid="equiangular"):
        *_, height, width = x.shape
        if s is None:
            modes_width = height // 2 if grid == "equiangular" else height
            modes_height = height
        else:
            modes_height, modes_width = s

        cache_key = f"{height}_{width}_{modes_height}_{modes_width}_{norm}_{grid}"

        try:
            sht_mod = self._SHT_cache[cache_key]
        except KeyError:
            sht_mod = (
                RealSHT(
                    nlat=height, nlon=width,
                    lmax=modes_height, mmax=modes_width,
                    grid=grid, norm=norm,
                )
                .to(dtype=self.dtype)
                .to(device=x.device)
            )
            self._SHT_cache[cache_key] = sht_mod

        return sht_mod(x)

    def isht(self, x, s=None, norm="ortho", grid="equiangular"):
        *_, modes_height, modes_width = x.shape
        if s is None:
            width = modes_width * 2 if grid == "equiangular" else modes_width
            height = modes_height
        else:
            height, width = s

        cache_key = f"{height}_{width}_{modes_height}_{modes_width}_{norm}_{grid}"

        try:
            isht_mod = self._iSHT_cache[cache_key]
        except KeyError:
            isht_mod = (
                InverseRealSHT(
                    nlat=height, nlon=width,
                    lmax=modes_height, mmax=modes_width,
                    grid=grid, norm=norm,
                )
                .to(dtype=self.dtype)
                .to(device=x.device)
            )
            self._iSHT_cache[cache_key] = isht_mod

        return isht_mod(x)

    SHT.sht = sht
    SHT.isht = isht
    setattr(SHT, _PATCH_ATTR, True)
