from dataclasses import dataclass, field
from pathlib import Path
import tomllib


@dataclass
class IscaDataConfig:
    # root directory of the experiment (contains simulations/, training-data/, checkpoints/)
    experiment_dir: Path
    # glob pattern under experiment_dir to find individual simulation directories
    simulation_pattern: str
    # glob pattern within each simulation directory to find NC files
    segment_pattern: str
    # input variable names
    x_vars: list[str]
    # target variable names
    y_vars: list[str]
    # [test, val, train] fraction by simulation, must sum to 1.0.
    # Simulations are sorted numerically; test gets the lowest indices (sim 0 first),
    # then val, then train. This keeps sim 0 permanently in the test split.
    split: tuple[float, float, float]
    # number of pairs to take from each simulation after skip; None means all
    samples_per_experiment: int | None = None
    # sampling strategy when samples_per_experiment is set: 'evenly_spaced' or 'uniform'
    sampling: str = "evenly_spaced"
    # number of initial pairs to skip per simulation
    skip: int = 0

    def __post_init__(self):
        self.experiment_dir = Path(self.experiment_dir)
        assert (
            abs(sum(self.split) - 1.0) < 1e-6
        ), f"split must sum to 1.0, got {self.split}"
        assert (
            self.experiment_dir.exists()
        ), f"experiment_dir not found: {self.experiment_dir}"
        assert self.sampling in (
            "evenly_spaced",
            "uniform",
        ), f"unknown sampling: {self.sampling}"


@dataclass
class FNOModelConfig:
    # number of Fourier modes to retain per spatial dimension
    n_modes: tuple[int, int]
    # width of the FNO lifting/projection layers
    hidden_channels: int
    # number of input fields
    in_channels: int
    # number of predicted fields
    out_channels: int
    # number of FNO blocks stacked in sequence
    n_layers: int = 4


VALID_LOSSES = ("mse", "relative_l2", "lat_weighted_relative_l2")
VALID_OPTIMIZERS = ("adam", "adamw")
VALID_SCHEDULERS = ("step", "cosine", "plateau", "none")


@dataclass
class StepSchedulerConfig:
    # epochs between LR decays
    step_size: int = 100
    # multiplicative factor applied to LR at each step
    gamma: float = 0.5


@dataclass
class CosineSchedulerConfig:
    # number of epochs over which LR anneals to eta_min; None defaults to training.epochs
    t_max: int | None = None
    # minimum learning rate floor at the end of the schedule
    eta_min: float = 0.0


@dataclass
class PlateauSchedulerConfig:
    # epochs without improvement before LR is reduced
    patience: int = 15
    # multiplicative factor applied to LR when triggered
    factor: float = 0.5
    # relative improvement threshold below which a step counts as no-progress
    threshold: float = 1e-4
    # minimum learning rate floor
    eta_min: float = 0.0


@dataclass
class SchedulerConfig:
    # 'step' (StepLR), 'cosine' (CosineAnnealingLR), 'plateau' (ReduceLROnPlateau), 'none'
    kind: str = "cosine"
    step: StepSchedulerConfig = field(default_factory=StepSchedulerConfig)
    cosine: CosineSchedulerConfig = field(default_factory=CosineSchedulerConfig)
    plateau: PlateauSchedulerConfig = field(default_factory=PlateauSchedulerConfig)

    def __post_init__(self):
        assert self.kind in VALID_SCHEDULERS, (
            f"unknown scheduler kind: {self.kind} (valid: {VALID_SCHEDULERS})"
        )


@dataclass
class TrainingConfig:
    # total training epochs
    epochs: int
    # number of samples per gradient step
    batch_size: int
    # initial learning rate
    learning_rate: float = 1e-3
    # stop early when monitored loss drops below this value; None disables
    target_loss: float | None = None
    # loss function: see VALID_LOSSES
    loss: str = "lat_weighted_relative_l2"
    # optimizer: see VALID_OPTIMIZERS
    optimizer: str = "adam"
    # L2 regularization coefficient (used by adamw)
    weight_decay: float = 0.0
    # max gradient norm for clipping; None disables
    grad_clip: float | None = None
    # learning rate scheduler configuration
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)

    def __post_init__(self):
        assert self.loss in VALID_LOSSES, (
            f"unknown loss: {self.loss} (valid: {VALID_LOSSES})"
        )
        assert self.optimizer in VALID_OPTIMIZERS, (
            f"unknown optimizer: {self.optimizer} (valid: {VALID_OPTIMIZERS})"
        )
        if self.scheduler.cosine.t_max is None:
            self.scheduler.cosine.t_max = self.epochs


@dataclass
class LoggingConfig:
    # logging level: DEBUG, INFO, WARNING, ERROR
    level: str = "INFO"
    # path to log file; None disables file logging
    output_file: Path | None = None
    # whether to also emit logs to stdout
    stdout: bool = True

    def __post_init__(self):
        if self.output_file is not None:
            self.output_file = Path(self.output_file)


@dataclass
class PathsConfig:
    # directory for saving model checkpoints; derived from experiment_dir if omitted
    checkpoint_dir: Path | None = None
    # directory where preprocessed HDF5 splits are written and read from; derived if omitted
    preprocessed_dir: Path | None = None
    # directory for training outputs; derived from experiment_dir if omitted
    training_dir: Path | None = None
    # per-epoch scalar metrics CSV; derived from training_dir if omitted
    epoch_metrics_file: Path | None = None
    # run summary CSV; derived from training_dir if omitted
    runs_file: Path | None = None
    # spatial/spectral metrics HDF5; derived from training_dir if omitted
    metrics_file: Path | None = None

    def __post_init__(self):
        for field in ("checkpoint_dir", "preprocessed_dir", "training_dir",
                      "epoch_metrics_file", "runs_file", "metrics_file"):
            v = getattr(self, field)
            if v is not None:
                setattr(self, field, Path(v))


@dataclass
class ModelConfig:
    fno: FNOModelConfig


@dataclass
class Config:
    data: IscaDataConfig
    model: ModelConfig
    training: TrainingConfig
    logging: LoggingConfig
    paths: PathsConfig


def load(path: Path) -> Config:
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    d = raw["data"]
    data = IscaDataConfig(
        experiment_dir=d["experiment_dir"],
        simulation_pattern=d["simulation_pattern"],
        segment_pattern=d["segment_pattern"],
        x_vars=list(d["x_vars"]),
        y_vars=list(d["y_vars"]),
        split=tuple(d["split"]),
        samples_per_experiment=d.get("samples_per_experiment", None),
        sampling=d.get("sampling", "evenly_spaced"),
        skip=d.get("skip", 0),
    )

    m = raw["model"]["fno"]
    model = ModelConfig(
        fno=FNOModelConfig(
            n_modes=tuple(m["n_modes"]),
            hidden_channels=m["hidden_channels"],
            in_channels=m["in_channels"],
            out_channels=m["out_channels"],
            n_layers=m.get("n_layers", 4),
        )
    )

    t = raw["training"]
    s = t.get("scheduler", {})
    s_step = s.get("step", {})
    s_cosine = s.get("cosine", {})
    s_plateau = s.get("plateau", {})
    scheduler = SchedulerConfig(
        kind=s.get("kind", "cosine"),
        step=StepSchedulerConfig(
            step_size=s_step.get("step_size", 100),
            gamma=s_step.get("gamma", 0.5),
        ),
        cosine=CosineSchedulerConfig(
            t_max=s_cosine.get("t_max", None),
            eta_min=s_cosine.get("eta_min", 0.0),
        ),
        plateau=PlateauSchedulerConfig(
            patience=s_plateau.get("patience", 15),
            factor=s_plateau.get("factor", 0.5),
            threshold=s_plateau.get("threshold", 1e-4),
            eta_min=s_plateau.get("eta_min", 0.0),
        ),
    )
    training = TrainingConfig(
        epochs=t["epochs"],
        batch_size=t["batch_size"],
        learning_rate=t.get("learning_rate", 1e-3),
        target_loss=t.get("target_loss", None),
        loss=t.get("loss", "lat_weighted_relative_l2"),
        optimizer=t.get("optimizer", "adam"),
        weight_decay=t.get("weight_decay", 0.0),
        grad_clip=t.get("grad_clip", None),
        scheduler=scheduler,
    )

    lg = raw.get("logging", {})
    logging_cfg = LoggingConfig(
        level=lg.get("level", "INFO"),
        output_file=lg.get("output_file", None),
        stdout=lg.get("stdout", True),
    )

    p = raw.get("paths", {})
    paths = PathsConfig(
        checkpoint_dir=p.get("checkpoint_dir", None),
        preprocessed_dir=p.get("preprocessed_dir", None),
        metrics_file=p.get("metrics_file", None),
    )

    if paths.preprocessed_dir is None:
        paths.preprocessed_dir = data.experiment_dir / "training-data"
    if paths.training_dir is None:
        paths.training_dir = data.experiment_dir / "training"
    if paths.checkpoint_dir is None:
        paths.checkpoint_dir = paths.training_dir
    if paths.epoch_metrics_file is None:
        paths.epoch_metrics_file = paths.training_dir / "epoch-metrics.csv"
    if paths.runs_file is None:
        paths.runs_file = paths.training_dir / "runs.csv"
    if paths.metrics_file is None:
        paths.metrics_file = paths.training_dir / "metrics.h5"

    return Config(
        data=data, model=model, training=training, logging=logging_cfg, paths=paths
    )
