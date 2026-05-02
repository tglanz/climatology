from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass
class IscaDataConfig:
    # root directory to search for experiments
    experiments_dir: Path
    # glob pattern under experiments_dir to find experiment directories
    experiment_pattern: str
    # glob pattern within each experiment directory to find NC files
    segment_pattern: str
    # input variable names
    x_vars: list[str]
    # target variable names
    y_vars: list[str]
    # train/val/test fraction by experiment, must sum to 1.0
    split: tuple[float, float, float] = (0.8, 0.1, 0.1)
    # number of pairs to take from each experiment after skip; None means all
    samples_per_experiment: int | None = None
    # sampling strategy when samples_per_experiment is set: 'evenly_spaced' or 'uniform'
    sampling: str = "evenly_spaced"
    # number of initial pairs to skip per experiment
    skip: int = 0

    def __post_init__(self):
        self.experiments_dir = Path(self.experiments_dir)
        assert (
            abs(sum(self.split) - 1.0) < 1e-6
        ), f"split must sum to 1.0, got {self.split}"
        assert (
            self.experiments_dir.exists()
        ), f"experiments_dir not found: {self.experiments_dir}"
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


@dataclass
class TrainingConfig:
    # total training epochs
    epochs: int = 500
    # number of samples per gradient step
    batch_size: int = 16
    # initial learning rate
    learning_rate: float = 1e-3
    # multiplicative factor applied to lr every lr_decay_every epochs
    lr_decay_factor: float = 0.5
    # epoch interval for learning rate decay
    lr_decay_every: int = 100
    # loss function: 'relative_l2' or 'mse'
    loss: str = "relative_l2"
    # optimizer: 'adam' or 'adamw'
    optimizer: str = "adam"
    # L2 regularization coefficient (used by adamw)
    weight_decay: float = 0.0


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
    # directory for saving model checkpoints
    checkpoint_dir: Path = Path("checkpoints")
    # directory where preprocessed HDF5 splits are written and read from
    preprocessed_dir: Path = Path("data")

    def __post_init__(self):
        self.checkpoint_dir = Path(self.checkpoint_dir)
        self.preprocessed_dir = Path(self.preprocessed_dir)


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
        experiments_dir=d["experiments_dir"],
        experiment_pattern=d["experiment_pattern"],
        segment_pattern=d["segment_pattern"],
        x_vars=list(d["x_vars"]),
        y_vars=list(d["y_vars"]),
        split=tuple(d.get("split", [0.8, 0.1, 0.1])),
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
        )
    )

    t = raw.get("training", {})
    training = TrainingConfig(
        epochs=t.get("epochs", 500),
        batch_size=t.get("batch_size", 16),
        learning_rate=t.get("learning_rate", 1e-3),
        lr_decay_factor=t.get("lr_decay_factor", 0.5),
        lr_decay_every=t.get("lr_decay_every", 100),
        loss=t.get("loss", "relative_l2"),
        optimizer=t.get("optimizer", "adam"),
        weight_decay=t.get("weight_decay", 0.0),
    )

    lg = raw.get("logging", {})
    logging_cfg = LoggingConfig(
        level=lg.get("level", "INFO"),
        output_file=lg.get("output_file", None),
        stdout=lg.get("stdout", True),
    )

    p = raw.get("paths", {})
    paths = PathsConfig(
        checkpoint_dir=p.get("checkpoint_dir", "checkpoints"),
        preprocessed_dir=p.get("preprocessed_dir", "data"),
    )

    return Config(
        data=data, model=model, training=training, logging=logging_cfg, paths=paths
    )
