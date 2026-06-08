from dataclasses import asdict, dataclass, field, fields
from enum import StrEnum
from pathlib import Path
import tomllib


VALID_START_AT = ("beginning", "spinup")
VALID_END_AT = ("end", "convergence")

VALID_CLIMATOLOGY_START_AT = ("spinup", "convergence")
VALID_CLIMATOLOGY_END_AT = ("convergence", "end")


@dataclass
class SpinupConfig:
    """Parameters for dynamic spin-up detection on the enstrophy series.

    Consumed by `find_spinup_time` in
    `ml/src/ml/diagnostics/convergence.py`. Present only when the user
    opts into spin-up detection by declaring `[data.windows.spinup]`.
    """

    z_threshold: float
    stable_time: int
    window_size: int = 10

    def __post_init__(self):
        assert self.z_threshold > 0.0, (
            f"spinup.z_threshold must be positive, got {self.z_threshold}"
        )
        assert self.stable_time >= 1, f"spinup.stable_time must be >= 1, got {self.stable_time}"
        assert self.window_size >= 2, f"spinup.window_size must be >= 2, got {self.window_size}"

    def to_kwargs(self) -> dict:
        return asdict(self)

@dataclass
class ConvergenceConfig:
    """Parameters for dynamic convergence detection on the running
    time-mean of the diagnostic.

    Consumed by `find_convergence_time` in
    `ml/src/ml/diagnostics/convergence.py`. Present only when the user
    opts into convergence detection by declaring
    `[data.windows.convergence]`.
    """

    threshold: float
    hold: int

    def __post_init__(self):
        assert self.threshold > 0.0, (
            f"convergence.threshold must be positive, got {self.threshold}"
        )
        assert self.hold >= 1, f"convergence.hold must be >= 1, got {self.hold}"

    def to_kwargs(self):
        return asdict(self)


@dataclass
class ClimatologyConfig:
    """Window over which per-simulation climatology diagnostics are computed.

    Exactly two of (start_at, end_at, length) must be provided; the third
    is derived. start_at and end_at are symbolic anchors resolved at
    preprocessing time against the detected t_s and t_c.

    Anchor cross-section validation (e.g. start_at='convergence' requires
    [data.convergence]) lives in IscaDataConfig.__post_init__.
    """

    start_at: str | None = None
    end_at: str | None = None
    length: int | None = None

    def __post_init__(self):
        provided = sum(v is not None for v in [self.start_at, self.end_at, self.length])
        assert provided == 2, (
            f"exactly 2 of (start_at, end_at, length) must be set, got {provided}"
        )
        if self.start_at is not None:
            assert self.start_at in VALID_CLIMATOLOGY_START_AT, (
                f"unknown climatology start_at: {self.start_at!r} "
                f"(valid: {VALID_CLIMATOLOGY_START_AT})"
            )
        if self.end_at is not None:
            assert self.end_at in VALID_CLIMATOLOGY_END_AT, (
                f"unknown climatology end_at: {self.end_at!r} "
                f"(valid: {VALID_CLIMATOLOGY_END_AT})"
            )
        if self.length is not None:
            assert self.length >= 1, f"climatology length must be >= 1, got {self.length}"


@dataclass
class WindowsConfig:
    """Configuration of the input-window selector.

    A window is `length` consecutive snapshots. The selector emits
    window-start indices `t_0` stepping by `stride` from `t_0_min`
    to `t_0_max`, optionally capped by `limit`.

    Bounds:
        t_0_min = 0   if start_at == "beginning"
        t_0_min = t_s if start_at == "spinup"
        t_0_max = M - K     if end_at == "end"
        t_0_max = t_c       if end_at == "convergence"

    Cross-section validation (start_at requires [data.spinup],
    end_at requires [data.convergence]) lives in
    `IscaDataConfig.__post_init__`, where the sibling sections are
    visible.
    """

    start_at: str
    end_at: str
    length: int
    stride: int
    limit: int | None = None

    def __post_init__(self):
        assert self.start_at in VALID_START_AT, (
            f"unknown start_at: {self.start_at} (valid: {VALID_START_AT})"
        )
        assert self.end_at in VALID_END_AT, (
            f"unknown end_at: {self.end_at} (valid: {VALID_END_AT})"
        )
        assert self.length >= 1, f"length must be >= 1, got {self.length}"
        assert self.stride >= 1, f"stride must be >= 1, got {self.stride}"
        if self.limit is not None:
            assert self.limit >= 1, (
                f"limit must be >= 1 when set, got {self.limit}"
            )


@dataclass
class SplitConfig:
    """
    validation + test + train must be equal to 1.
    """
    validation: float 
    test: float 
    train: float 
    validation_limit: int | None = None
    test_limit: int | None = None
    train_limit: int | None = None

    def __post_init__(self):
        values = [self.validation, self.train, self.test]
        assert abs(sum(values) - 1.0) < 1e-6, f"split parts {values} must equal to 1"

@dataclass
class IscaDataConfig:
    # root directory of the experiment (contains simulations/, data/, training/)
    experiment_dir: Path
    # glob pattern under experiment_dir to find individual simulation directories
    simulation_pattern: str
    # glob pattern within each simulation directory to find NC files
    segment_pattern: str
    # input variable names
    x_vars: list[str]
    # target variable names
    y_vars: list[str]

    split: SplitConfig
    # window-extraction strategy: length, selection bounds, optional cap
    windows: WindowsConfig
    # optional dynamic spin-up detector; required when windows.start_at == "spinup"
    spinup: SpinupConfig | None = None
    # optional dynamic convergence detector; required when windows.end_at == "convergence"
    convergence: ConvergenceConfig | None = None
    # optional climatology window; required when any y_var is a climatology diagnostic
    climatology: ClimatologyConfig | None = None

    def __post_init__(self):
        self.experiment_dir = Path(self.experiment_dir)
        assert (
            self.experiment_dir.exists()
        ), f"experiment_dir not found: {self.experiment_dir}"
        if self.windows.start_at == "spinup":
            assert self.spinup is not None, (
                "windows.start_at = 'spinup' requires [data.spinup] section"
            )
        if self.windows.end_at == "convergence":
            assert self.convergence is not None, (
                "windows.end_at = 'convergence' requires [data.convergence] section"
            )
        if self.climatology is not None:
            if self.climatology.start_at == "spinup" or self.climatology.end_at == "spinup":
                assert self.spinup is not None, (
                    "climatology anchor 'spinup' requires [data.spinup] section"
                )
            if self.climatology.start_at == "convergence" or self.climatology.end_at == "convergence":
                assert self.convergence is not None, (
                    "climatology anchor 'convergence' requires [data.convergence] section"
                )


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


@dataclass
class SFNOModelConfig:
    # number of spherical-harmonic modes retained per spatial dimension
    n_modes: tuple[int, int]
    # width of the SFNO lifting/projection layers
    hidden_channels: int
    # number of input fields
    in_channels: int
    # number of predicted fields
    out_channels: int
    # number of SFNO blocks stacked in sequence
    n_layers: int = 4


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
    # stop when monitored loss drops at or below this value
    value: float
    # 'val' or 'train'
    monitor: str = "val"

    def __post_init__(self):
        assert self.monitor in VALID_MONITORS, (
            f"unknown monitor: {self.monitor} (valid: {VALID_MONITORS})"
        )


@dataclass
class PatienceStopConfig:
    # epochs without improvement before training stops
    patience: int = 10
    # minimum improvement required to reset the patience counter
    min_delta: float = 1e-4
    # 'val' or 'train'
    monitor: str = "val"

    def __post_init__(self):
        assert self.patience > 0, f"patience must be positive, got {self.patience}"
        assert self.min_delta >= 0, (
            f"min_delta must be non-negative, got {self.min_delta}"
        )
        assert self.monitor in VALID_MONITORS, (
            f"unknown monitor: {self.monitor} (valid: {VALID_MONITORS})"
        )


@dataclass
class EarlyStoppingConfig:
    # absent subsection (None) disables that criterion
    target_loss: TargetLossStopConfig | None = None
    patience: PatienceStopConfig | None = None


@dataclass
class RegularizationConfig:
    # AdamW weight decay coefficient; only applied when optimizer = "adamw"
    weight_decay: float | None = None
    # FNO channel_mlp_dropout; passed to neuraloperator.models.FNO
    dropout: float | None = None

    def __post_init__(self):
        if self.weight_decay is not None:
            assert self.weight_decay >= 0, (
                f"weight_decay must be non-negative, got {self.weight_decay}"
            )
        if self.dropout is not None:
            assert 0.0 <= self.dropout < 1.0, (
                f"dropout must be in [0, 1), got {self.dropout}"
            )


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
    # loss function: see VALID_LOSSES
    loss: str = "lat_weighted_relative_l2"
    # optimizer: see VALID_OPTIMIZERS
    optimizer: str = "adam"
    # max gradient norm for clipping; None disables
    grad_clip: float | None = None
    # learning rate scheduler configuration
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    # early stopping criteria; any one firing stops training
    early_stopping: EarlyStoppingConfig = field(default_factory=EarlyStoppingConfig)
    # regularization knobs; fields default to None (no implicit regularization)
    regularization: RegularizationConfig = field(default_factory=RegularizationConfig)

    def __post_init__(self):
        assert self.loss in LossKind, (
            f"unknown loss: {self.loss!r} (valid: {[e.value for e in LossKind]})"
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
    # JSON snapshot of run metadata; derived from training_dir if omitted
    training_info_file: Path | None = None

    def __post_init__(self):
        for field in ("checkpoint_dir", "preprocessed_dir", "training_dir",
                      "epoch_metrics_file", "runs_file", "metrics_file",
                      "training_info_file"):
            v = getattr(self, field)
            if v is not None:
                setattr(self, field, Path(v))


@dataclass
class ModelConfig:
    architecture: str
    fno: FNOModelConfig | None = None
    sfno: SFNOModelConfig | None = None

    def __post_init__(self):
        assert self.architecture in VALID_ARCHITECTURES, (
            f"unknown architecture: {self.architecture} "
            f"(valid: {VALID_ARCHITECTURES})"
        )
        active = self.active_sub_config()
        assert active is not None, (
            f"architecture={self.architecture} but "
            f"[model.{self.architecture}] section is missing"
        )

    def active_sub_config(self) -> FNOModelConfig | SFNOModelConfig | None:
        return self.fno if self.architecture == "fno" else self.sfno


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
    if "windows" not in d:
        raise ValueError(
            "[data.windows] section is required. See docs/pre-processing.md "
            "for the configuration surface."
        )
    data = IscaDataConfig(
        experiment_dir=d["experiment_dir"],
        simulation_pattern=d["simulation_pattern"],
        segment_pattern=d["segment_pattern"],
        x_vars=list(d["x_vars"]),
        y_vars=list(d["y_vars"]),
        split=SplitConfig(**d["split"]),
        windows=WindowsConfig(**d["windows"]),
        spinup=SpinupConfig(**d["spinup"]) if "spinup" in d else None,
        convergence=ConvergenceConfig(**d["convergence"]) if "convergence" in d else None,
        climatology=ClimatologyConfig(**d["climatology"]) if "climatology" in d else None,
    )

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
        loss=t.get("loss", "lat_weighted_relative_l2"),
        optimizer=t.get("optimizer", "adam"),
        grad_clip=t.get("grad_clip", None),
        scheduler=scheduler,
        early_stopping=early_stopping,
        regularization=regularization,
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
        training_dir=p.get("training_dir", None),
        epoch_metrics_file=p.get("epoch_metrics_file", None),
        runs_file=p.get("runs_file", None),
        metrics_file=p.get("metrics_file", None),
        training_info_file=p.get("training_info_file", None),
    )

    if paths.preprocessed_dir is None:
        paths.preprocessed_dir = data.experiment_dir / "data"
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
    if paths.training_info_file is None:
        paths.training_info_file = paths.training_dir / "training.json"

    expected_in_channels = data.windows.length * len(data.x_vars)
    active = model.active_sub_config()
    assert active.in_channels == expected_in_channels, (
        f"model.{model.architecture}.in_channels={active.in_channels} does not match "
        f"data.windows.length * len(x_vars) = "
        f"{data.windows.length} * {len(data.x_vars)} = {expected_in_channels}"
    )

    return Config(
        data=data, model=model, training=training, logging=logging_cfg, paths=paths
    )
