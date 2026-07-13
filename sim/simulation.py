from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from isca import GFDL_WORK, BarotropicCodeBase, DiagTable, Experiment, Namelist


@dataclass
class ExecutionParams:
    sim_name: str
    simulations_dir: Path
    num_cores: int
    n_segments: int


class Simulation(ABC):
    @property
    @abstractmethod
    def codebase(self) -> BarotropicCodeBase: ...

    @property
    @abstractmethod
    def diag_table(self) -> DiagTable: ...

    @abstractmethod
    def build_namelist(self) -> Namelist: ...

    @abstractmethod
    def write_metadata(self, sim_dir: Path) -> None: ...

    def work_dir(self, ep: ExecutionParams) -> Path:
        return Path(GFDL_WORK) / 'experiment' / ep.sim_name

    def compile(self) -> None:
        self.codebase.compile()

    def execute(self, ep: ExecutionParams) -> None:
        sim_dir = ep.simulations_dir / ep.sim_name
        sim_dir.mkdir(parents=True, exist_ok=True)
        self.write_metadata(sim_dir)

        exp = Experiment(ep.sim_name, codebase=self.codebase, database=str(ep.simulations_dir))
        exp.diag_table = self.diag_table
        exp.clear_rundir()
        exp.namelist = self.build_namelist()

        exp.run(1, use_restart=False, num_cores=ep.num_cores)
        for i in range(2, ep.n_segments + 1):
            exp.run(i, num_cores=ep.num_cores)
