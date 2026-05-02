from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass
class DataConfig:
    # root directory containing experiment subdirectories
    experiments_dir: Path
    # train/val/test fraction by experiment, must sum to 1.0
    split: tuple[float, float, float] = (0.8, 0.1, 0.1)

    def __post_init__(self):
        self.experiments_dir = Path(self.experiments_dir)
        assert abs(sum(self.split) - 1.0) < 1e-6, f"split must sum to 1.0, got {self.split}"
        assert self.experiments_dir.exists(), f"experiments_dir not found: {self.experiments_dir}"


@dataclass
class FNOModelConfig:
    # number of Fourier modes to retain per spatial dimension
    n_modes: tuple[int, int] = (64, 64)
    # width of the FNO lifting/projection layers
    hidden_channels: int = 64
    # number of input fields (vorticity + forcing = 2)
    in_channels: int = 2
    # number of predicted fields (vorticity = 1)
    out_channels: int = 1


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

    def __post_init__(self):
        self.checkpoint_dir = Path(self.checkpoint_dir)


@dataclass
class ModelConfig:
    fno: FNOModelConfig


@dataclass
class Config:
    data: DataConfig
    model: ModelConfig
    training: TrainingConfig
    logging: LoggingConfig
    paths: PathsConfig


def load(path: Path) -> Config:
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    data = DataConfig(
        experiments_dir=raw["data"]["experiments_dir"],
        split=tuple(raw["data"].get("split", [0.8, 0.1, 0.1])),
    )

    m = raw.get("model", {}).get("fno", {})
    model = ModelConfig(
        fno=FNOModelConfig(
            n_modes=tuple(m.get("n_modes", [64, 64])),
            hidden_channels=m.get("hidden_channels", 64),
            in_channels=m.get("in_channels", 2),
            out_channels=m.get("out_channels", 1),
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
    )

    return Config(data=data, model=model, training=training, logging=logging_cfg, paths=paths)
