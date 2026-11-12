"""Validated configuration for the retained preparation/training/evaluation stages."""

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
import math
import tomllib
import tomli_w

from ml.data.climatology import diagnostic_for


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _integer(name: str, value: int, minimum: int = 1) -> None:
    _require(
        isinstance(value, int) and not isinstance(value, bool) and value >= minimum,
        f"{name} must be an integer >= {minimum}",
    )


def _number(name: str, value: float, minimum: float = 0, strict: bool = False) -> None:
    _require(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and (value > minimum if strict else value >= minimum),
        f"{name} must be finite and {'>' if strict else '>='} {minimum}",
    )


def _choice(name: str, value: str, choices) -> None:
    _require(value in choices, f"unknown {name}: {value!r}; expected {tuple(choices)}")


VALID_START_AT = ("beginning", "spinup")
VALID_END_AT = ("end", "convergence")
VALID_CLIMATOLOGY_START_AT = ("spinup", "convergence")
VALID_CLIMATOLOGY_END_AT = ("convergence", "end")


@dataclass
class SpinupConfig:
    z_threshold: float
    stable_time: int
    window_size: int = 10

    def __post_init__(self):
        _number("spinup.z_threshold", self.z_threshold, strict=True)
        _integer("spinup.stable_time", self.stable_time)
        _integer("spinup.window_size", self.window_size, 2)

    def to_kwargs(self) -> dict:
        return asdict(self)


@dataclass
class ConvergenceConfig:
    threshold: float
    hold: int

    def __post_init__(self):
        _number("convergence.threshold", self.threshold, strict=True)
        _integer("convergence.hold", self.hold)

    def to_kwargs(self) -> dict:
        return asdict(self)


@dataclass
class ClimatologyConfig:
    start_at: str | None = None
    end_at: str | None = None
    length: int | None = None

    def __post_init__(self):
        _require(
            sum(v is not None for v in (self.start_at, self.end_at, self.length)) == 2,
            "exactly two of climatology start_at, end_at, and length must be set",
        )
        if self.start_at is not None:
            _choice("climatology.start_at", self.start_at, VALID_CLIMATOLOGY_START_AT)
        if self.end_at is not None:
            _choice("climatology.end_at", self.end_at, VALID_CLIMATOLOGY_END_AT)
        if self.length is not None:
            _integer("climatology.length", self.length)


@dataclass
class WindowsConfig:
    """Convergence caps starts; complete windows occupy [start, start + length)."""

    start_at: str
    end_at: str
    length: int
    stride: int
    limit: int | None = None

    def __post_init__(self):
        _choice("windows.start_at", self.start_at, VALID_START_AT)
        _choice("windows.end_at", self.end_at, VALID_END_AT)
        _integer("windows.length", self.length)
        _integer("windows.stride", self.stride)
        if self.limit is not None:
            _integer("windows.limit", self.limit)


@dataclass
class SplitConfig:
    validation_ratio: float
    test_ratio: float | None = None
    test_hold_out: dict | None = None

    def __post_init__(self):
        _require(
            (self.test_ratio is None) != (self.test_hold_out is None),
            "exactly one of test_ratio or test_hold_out must be set",
        )
        _number("validation_ratio", self.validation_ratio, strict=True)
        _require(self.validation_ratio < 1, "validation_ratio must be < 1")
        if self.test_ratio is not None:
            _number("test_ratio", self.test_ratio, strict=True)
            _require(
                self.validation_ratio + self.test_ratio < 1,
                "test_ratio + validation_ratio must leave a training split",
            )
        if self.test_hold_out is not None:
            _require(
                bool(self.test_hold_out)
                and all(isinstance(v, list) and v for v in self.test_hold_out.values()),
                "test_hold_out must contain nonempty parameter lists",
            )


@dataclass
class IscaDataConfig:
    simulation_pattern: str
    segment_pattern: str
    x_vars: list[str]
    y_vars: list[str]
    split: SplitConfig
    windows: WindowsConfig
    climatology: ClimatologyConfig
    spinup: SpinupConfig | None = None
    convergence: ConvergenceConfig | None = None

    def __post_init__(self):
        for name, variables in (("x_vars", self.x_vars), ("y_vars", self.y_vars)):
            _require(
                bool(variables)
                and all(isinstance(v, str) and v for v in variables)
                and len(set(variables)) == len(variables),
                f"{name} must be a nonempty list of distinct variables",
            )
        for name in self.y_vars:
            diagnostic_for(name)
        if self.windows.start_at == "spinup" or self.climatology.start_at == "spinup":
            _require(self.spinup is not None, "spinup anchor requires [data.spinup]")
        if self.windows.end_at == "convergence" or "convergence" in (
            self.climatology.start_at,
            self.climatology.end_at,
        ):
            _require(
                self.convergence is not None,
                "convergence anchor requires [data.convergence]",
            )


@dataclass
class OperatorModelConfig:
    n_modes: tuple[int, int]
    hidden_channels: int
    in_channels: int
    out_channels: int
    n_layers: int = 4

    def __post_init__(self):
        _require(
            len(self.n_modes) == 2, "n_modes must contain latitude and longitude counts"
        )
        for name, value in (
            ("latitude modes", self.n_modes[0]),
            ("longitude modes", self.n_modes[1]),
            ("hidden_channels", self.hidden_channels),
            ("in_channels", self.in_channels),
            ("out_channels", self.out_channels),
            ("n_layers", self.n_layers),
        ):
            _integer(name, value)


@dataclass
class FNOModelConfig(OperatorModelConfig):
    pass


@dataclass
class SFNOModelConfig(OperatorModelConfig):
    pass


class LossKind(StrEnum):
    MSE = "mse"
    RELATIVE_L2 = "relative_l2"
    LAT_WEIGHTED_RELATIVE_L2 = "lat_weighted_relative_l2"


VALID_ARCHITECTURES = ("fno", "sfno")
VALID_OPTIMIZERS = ("adam", "adamw")
VALID_SCHEDULERS = ("step", "cosine", "plateau", "none")
VALID_MONITORS = ("val", "train")


@dataclass
class TargetLossStopConfig:
    value: float
    monitor: str = "val"

    def __post_init__(self):
        _number("target_loss.value", self.value)
        _choice("monitor", self.monitor, VALID_MONITORS)


@dataclass
class PatienceStopConfig:
    patience: int = 10
    min_delta: float = 1e-4
    monitor: str = "val"

    def __post_init__(self):
        _integer("patience", self.patience)
        _number("min_delta", self.min_delta)
        _choice("monitor", self.monitor, VALID_MONITORS)


@dataclass
class EarlyStoppingConfig:
    target_loss: TargetLossStopConfig | None = None
    patience: PatienceStopConfig | None = None


@dataclass
class RegularizationConfig:
    weight_decay: float | None = None
    dropout: float | None = None

    def __post_init__(self):
        if self.weight_decay is not None:
            _number("weight_decay", self.weight_decay)
        if self.dropout is not None:
            _number("dropout", self.dropout)
            _require(self.dropout < 1, "dropout must be < 1")


@dataclass
class StepSchedulerConfig:
    step_size: int = 100
    gamma: float = 0.5

    def __post_init__(self):
        _integer("scheduler.step_size", self.step_size)
        _number("scheduler.gamma", self.gamma, strict=True)


@dataclass
class CosineSchedulerConfig:
    t_max: int | None = None
    eta_min: float = 0.0

    def __post_init__(self):
        if self.t_max is not None:
            _integer("scheduler.t_max", self.t_max)
        _number("scheduler.eta_min", self.eta_min)


@dataclass
class PlateauSchedulerConfig:
    patience: int = 15
    factor: float = 0.5
    threshold: float = 1e-4
    eta_min: float = 0.0

    def __post_init__(self):
        _integer("scheduler.plateau.patience", self.patience, 0)
        _number("scheduler.factor", self.factor, strict=True)
        _require(self.factor < 1, "plateau factor must be < 1")
        _number("scheduler.threshold", self.threshold)
        _number("scheduler.eta_min", self.eta_min)


@dataclass
class SchedulerConfig:
    kind: str = "cosine"
    step: StepSchedulerConfig = field(default_factory=StepSchedulerConfig)
    cosine: CosineSchedulerConfig = field(default_factory=CosineSchedulerConfig)
    plateau: PlateauSchedulerConfig = field(default_factory=PlateauSchedulerConfig)

    def __post_init__(self):
        _choice("scheduler", self.kind, VALID_SCHEDULERS)


@dataclass
class TrainingConfig:
    epochs: int
    batch_size: int
    learning_rate: float = 1e-3
    seed: int = 0
    loss: str = "lat_weighted_relative_l2"
    optimizer: str = "adam"
    grad_clip: float | None = None
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    early_stopping: EarlyStoppingConfig = field(default_factory=EarlyStoppingConfig)
    regularization: RegularizationConfig = field(default_factory=RegularizationConfig)

    def __post_init__(self):
        _integer("seed", self.seed, 0)
        _integer("epochs", self.epochs)
        _integer("batch_size", self.batch_size)
        _number("learning_rate", self.learning_rate, strict=True)
        _choice("loss", self.loss, LossKind)
        _choice("optimizer", self.optimizer, VALID_OPTIMIZERS)
        if self.grad_clip is not None:
            _number("grad_clip", self.grad_clip, strict=True)
        if self.scheduler.cosine.t_max is None:
            self.scheduler.cosine.t_max = self.epochs
        eta_min = (
            self.scheduler.cosine.eta_min
            if self.scheduler.kind == "cosine"
            else self.scheduler.plateau.eta_min
        )
        _require(
            eta_min <= self.learning_rate,
            "scheduler minimum exceeds initial learning rate",
        )

    def validate_loaders(self, train_loader, val_loader) -> None:
        _require(
            train_loader is not None and len(train_loader.dataset) > 0,
            "training requires usable samples",
        )
        if val_loader is not None and len(val_loader.dataset) > 0:
            return
        criteria = (self.early_stopping.target_loss, self.early_stopping.patience)
        _require(
            self.scheduler.kind != "plateau"
            and not any(
                criterion is not None and criterion.monitor == "val"
                for criterion in criteria
            ),
            "validation-dependent settings require validation samples",
        )


@dataclass
class LoggingConfig:
    level: str = "INFO"
    output_file: Path | None = None
    stdout: bool = True

    def __post_init__(self):
        _choice(
            "logging.level",
            self.level.upper(),
            ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        )
        if self.output_file is not None:
            self.output_file = Path(self.output_file)


@dataclass
class PathsConfig:
    experiment_dir: Path
    preprocessed_dir: Path | None = None
    training_dir: Path | None = None
    epoch_metrics_file: Path | None = None
    metrics_file: Path | None = None
    splits_dir: Path | None = None
    checkpoint_dir: Path | None = None
    training_info_file: Path | None = None

    def __post_init__(self):
        for name in (
            "experiment_dir",
            "preprocessed_dir",
            "training_dir",
            "epoch_metrics_file",
            "metrics_file",
            "splits_dir",
        ):
            value = getattr(self, name)
            if value is not None:
                setattr(self, name, Path(value))


@dataclass
class ModelConfig:
    architecture: str
    fno: FNOModelConfig | None = None
    sfno: SFNOModelConfig | None = None

    def __post_init__(self):
        _choice("architecture", self.architecture, VALID_ARCHITECTURES)
        _require(
            self.active_sub_config() is not None, "active model section is missing"
        )

    def active_sub_config(self) -> FNOModelConfig | SFNOModelConfig:
        return self.fno if self.architecture == "fno" else self.sfno


@dataclass
class Config:
    data: IscaDataConfig
    model: ModelConfig
    training: TrainingConfig
    logging: LoggingConfig
    paths: PathsConfig

    def __post_init__(self):
        active = self.model.active_sub_config()
        _require(
            active.in_channels == self.data.windows.length * len(self.data.x_vars),
            "model input channels do not match window length * input variables",
        )
        _require(
            active.out_channels == len(self.data.y_vars),
            "model output channels do not match target variables",
        )
        if (
            self.paths.preprocessed_dir is not None
            and self.paths.training_dir is not None
        ):
            _require(
                not self.paths.preprocessed_dir.resolve().is_relative_to(
                    self.paths.training_dir.resolve()
                ),
                "training directory must not contain the prepared data directory",
            )
            _require(
                not self.paths.training_dir.resolve().is_relative_to(
                    self.paths.preprocessed_dir.resolve()
                ),
                "prepared data directory must not contain the training directory",
            )


def _parse_split_config(s: dict) -> SplitConfig:
    return SplitConfig(
        validation_ratio=s["validation_ratio"],
        test_ratio=s.get("test_ratio"),
        test_hold_out=s.get("test_hold_out"),
    )


@dataclass
class PreparationConfig:
    data: IscaDataConfig
    logging: LoggingConfig
    paths: PathsConfig


def read_raw(path: Path) -> dict:
    path = Path(path)
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    if "data_config" in raw:
        if "data" in raw:
            raise ValueError("use either data_config or [data], not both")
        with (path.parent / raw.pop("data_config")).open("rb") as handle:
            source = tomllib.load(handle)
        if "data_config" in source:
            raise ValueError(
                "data_config must reference a standalone preparation recipe"
            )
        raw["data"] = source["data"]
        raw["paths"] = source.get("paths", {}) | raw.get("paths", {})
    return raw


def save(cfg, path: Path) -> None:
    """Write a standalone snapshot with absolute artifact paths."""

    def clean(value):
        if isinstance(value, dict):
            return {k: clean(v) for k, v in value.items() if v is not None}
        if isinstance(value, (tuple, list)):
            return [clean(v) for v in value]
        if isinstance(value, Path):
            return str(value.resolve())
        return value

    path.write_text(tomli_w.dumps(clean(asdict(cfg))))


def load_data(path: Path) -> PreparationConfig:
    return load(path, data_only=True)


def load(path: Path, *, data_only: bool = False) -> Config | PreparationConfig:
    raw = read_raw(path)

    d = raw["data"]
    if "windows" not in d:
        raise ValueError(
            "[data.windows] section is required. See docs/pre-processing.md "
            "for the configuration surface."
        )
    data = IscaDataConfig(
        simulation_pattern=d["simulation_pattern"],
        segment_pattern=d["segment_pattern"],
        x_vars=list(d["x_vars"]),
        y_vars=list(d["y_vars"]),
        split=_parse_split_config(d["split"]),
        windows=WindowsConfig(**d["windows"]),
        climatology=ClimatologyConfig(**d["climatology"]),
        spinup=SpinupConfig(**d["spinup"]) if "spinup" in d else None,
        convergence=(
            ConvergenceConfig(**d["convergence"]) if "convergence" in d else None
        ),
    )

    lg = raw.get("logging", {})
    logging_cfg = LoggingConfig(
        level=lg.get("level", "INFO"),
        output_file=lg.get("output_file", None),
        stdout=lg.get("stdout", True),
    )

    p = raw.get("paths", {})
    if "experiment_dir" not in p:
        raise ValueError("[paths.experiment_dir] is required")
    paths = PathsConfig(
        experiment_dir=p["experiment_dir"],
        preprocessed_dir=p.get("preprocessed_dir"),
        training_dir=p.get("training_dir"),
        epoch_metrics_file=p.get("epoch_metrics_file"),
        metrics_file=p.get("metrics_file"),
        splits_dir=p.get("splits_dir"),
    )

    if paths.preprocessed_dir is None:
        paths.preprocessed_dir = paths.experiment_dir / "data"
    if paths.training_dir is None:
        paths.training_dir = paths.experiment_dir / "training"
    paths.checkpoint_dir = paths.training_dir
    if paths.epoch_metrics_file is None:
        paths.epoch_metrics_file = paths.training_dir / "epoch-metrics.csv"
    if paths.metrics_file is None:
        paths.metrics_file = paths.training_dir / "metrics.h5"
    paths.training_info_file = paths.training_dir / "training.json"
    if paths.splits_dir is None:
        paths.splits_dir = paths.experiment_dir / "splits"

    if data_only:
        return PreparationConfig(data, logging_cfg, paths)

    model_raw = raw["model"]
    architecture = model_raw["architecture"]
    fno_cfg = None
    if "fno" in model_raw:
        f = model_raw["fno"]
        fno_cfg = FNOModelConfig(
            n_modes=tuple(f["n_modes"]),
            hidden_channels=f["hidden_channels"],
            in_channels=f["in_channels"],
            out_channels=f["out_channels"],
            n_layers=f.get("n_layers", 4),
        )
    sfno_cfg = None
    if "sfno" in model_raw:
        s = model_raw["sfno"]
        sfno_cfg = SFNOModelConfig(
            n_modes=tuple(s["n_modes"]),
            hidden_channels=s["hidden_channels"],
            in_channels=s["in_channels"],
            out_channels=s["out_channels"],
            n_layers=s.get("n_layers", 4),
        )
    model = ModelConfig(architecture=architecture, fno=fno_cfg, sfno=sfno_cfg)

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
    es_raw = t.get("early_stopping", {})
    es_target_raw = es_raw.get("target_loss")
    es_patience_raw = es_raw.get("patience")
    early_stopping = EarlyStoppingConfig(
        target_loss=(
            TargetLossStopConfig(
                value=es_target_raw["value"],
                monitor=es_target_raw.get("monitor", "val"),
            )
            if es_target_raw is not None
            else None
        ),
        patience=(
            PatienceStopConfig(
                patience=es_patience_raw.get("patience", 10),
                min_delta=es_patience_raw.get("min_delta", 1e-4),
                monitor=es_patience_raw.get("monitor", "val"),
            )
            if es_patience_raw is not None
            else None
        ),
    )

    r_raw = t.get("regularization", {})
    regularization = RegularizationConfig(
        weight_decay=r_raw.get("weight_decay"),
        dropout=r_raw.get("dropout"),
    )

    training = TrainingConfig(
        epochs=t["epochs"],
        batch_size=t["batch_size"],
        learning_rate=t.get("learning_rate", 1e-3),
        seed=t.get("seed", 0),
        loss=t.get("loss", "lat_weighted_relative_l2"),
        optimizer=t.get("optimizer", "adam"),
        grad_clip=t.get("grad_clip", None),
        scheduler=scheduler,
        early_stopping=early_stopping,
        regularization=regularization,
    )

    return Config(
        data=data, model=model, training=training, logging=logging_cfg, paths=paths
    )
