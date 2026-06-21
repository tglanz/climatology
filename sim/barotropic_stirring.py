import json
import math
from dataclasses import dataclass
from pathlib import Path

from isca import BarotropicCodeBase, DiagTable, Namelist, GFDL_BASE

from sim.simulation import Simulation


def _is_fft_friendly(n: int) -> bool:
    if n == 0:
        return False
    for p in [2, 3, 5]:
        while n % p == 0:
            n //= p
    return n == 1


def _alias_free_grid(num_fourier: int) -> tuple[int, int]:
    min_lat = math.ceil((3 * num_fourier + 1) / 2)
    min_lon = 3 * num_fourier + 1
    num_lat = min_lat if min_lat % 2 == 0 else min_lat + 1
    num_lon = min_lon
    while not _is_fft_friendly(num_lon):
        num_lon += 1
    return num_lat, num_lon


@dataclass
class BarotropicStirringParams:
    fourier_harmonics:  int   = 85
    dt_atmos:           int   = 600
    segment_days:       int   = 7
    stirring_amplitude: float = 1.0e-10
    stirring_decay_time:float = 172800.0
    stirring_lat0:      float = 45.0
    stirring_widthy:    float = 12.0
    stirring_lon0:      float = 180.0
    stirring_widthx:    float = 45.0
    stirring_B:         float = 0.4


_cb = BarotropicCodeBase.from_directory(GFDL_BASE)

_diag = DiagTable()
_diag.add_file('atmos_daily', 1, 'days', time_units='days')
_diag.add_field('barotropic_diagnostics', 'ucomp',       time_avg=True)
_diag.add_field('barotropic_diagnostics', 'vcomp',       time_avg=True)
_diag.add_field('barotropic_diagnostics', 'vor',         time_avg=True)
_diag.add_field('barotropic_diagnostics', 'pv',          time_avg=True)
_diag.add_field('barotropic_diagnostics', 'stream',      time_avg=True)
_diag.add_field('barotropic_diagnostics', 'trs',         time_avg=True)
_diag.add_field('barotropic_diagnostics', 'tr',          time_avg=True)
_diag.add_field('barotropic_diagnostics', 'eddy_vor',    time_avg=True)
_diag.add_field('barotropic_diagnostics', 'delta_u',     time_avg=True)
_diag.add_field('stirring_mod',           'stirring',     time_avg=True)
_diag.add_field('stirring_mod',           'stirring_amp', time_avg=True)
_diag.add_field('stirring_mod',           'stirring_sqr', time_avg=True)


class BarotropicStirring(Simulation):
    def __init__(self, params: BarotropicStirringParams):
        self.params = params

    @property
    def codebase(self) -> BarotropicCodeBase:
        return _cb

    @property
    def diag_table(self) -> DiagTable:
        return _diag

    def _namelist_dict(self) -> dict:
        p = self.params
        num_lat, num_lon = _alias_free_grid(p.fourier_harmonics)
        return {
            'main_nml': {
                'days'    : p.segment_days,
                'hours'   : 0,
                'minutes' : 0,
                'seconds' : 0,
                'dt_atmos': p.dt_atmos,
                'calendar': 'no_calendar',
            },
            'atmosphere_nml': {
                'print_interval': 86400,
            },
            'fms_io_nml': {
                'threading_write': 'single',
                'fileset_write'  : 'single',
            },
            'fms_nml': {
                'print_memory_usage': True,
                'domains_stack_size': 200000,
            },
            'barotropic_dynamics_nml': {
                'triang_trunc'      : True,
                'num_fourier'       : p.fourier_harmonics,
                'num_spherical'     : p.fourier_harmonics + 1,
                'num_lat'           : num_lat,
                'num_lon'           : num_lon,
                'fourier_inc'       : 1,
                'damping_option'    : 'resolution_dependent',
                'damping_order'     : 2,
                'damping_coeff'     : 1.157e-4,
                'damping_coeff_r'   : 1.929e-6,
                'grid_tracer'       : True,
                'spec_tracer'       : True,
                'm_0'               : 6,
                'zeta_0'            : 0.0,
                'eddy_lat'          : 45.0,
                'eddy_width'        : 10.0,
                'robert_coeff'      : 0.04,
                'initial_zonal_wind': 'zero',
            },
            'barotropic_physics_nml': {},
            'stirring_nml': {
                'amplitude' : p.stirring_amplitude,
                'decay_time': p.stirring_decay_time,
                'lat0'      : p.stirring_lat0,
                'widthy'    : p.stirring_widthy,
                'lon0'      : p.stirring_lon0,
                'widthx'    : p.stirring_widthx,
                'B'         : p.stirring_B,
            },
        }

    def build_namelist(self) -> Namelist:
        return Namelist(self._namelist_dict())

    def write_metadata(self, sim_dir: Path) -> None:
        (sim_dir / 'namelist.json').write_text(json.dumps(self._namelist_dict(), indent=2))
