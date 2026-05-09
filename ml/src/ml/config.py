from dataclasses import dataclass, field
from pathlib import Path
import tomllib


VALID_SAMPLING = ("evenly_spaced", "uniform", "latest")

@dataclass
class SplitConfig:
    """
    validation + test + train must be equal to 1.
    """
    validation: float 
    validation_limit: int | None
    test: float 
    test_limit: int | None
    train: float 
    train_limit: int | None

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

    # number of pairs to take from each simulation after skip; None means all
    samples_per_experiment: int | None = None
    # sampling strategy when samples_per_experiment is set:
    #   'evenly_spaced' - linspace over the valid range
    #   'uniform'       - uniform random over the valid range
    #   'latest'        - take the last `samples_per_experiment` valid indices
    #                     (most temporally recent; spinup-safe without `skip`)
    sampling: str = "latest"
    # number of initial pairs to skip per simulation (per-segment-flattened indexing)
    skip: int = 0
    # number of input timesteps stacked into each training pair.
    # lag_steps = 1 means just the current state (legacy behaviour).
    # lag_steps = K means (t-K+1, ..., t) -> t+1.
    lag_steps: int = 1

    def __post_init__(self):
        self.experiment_dir = Path(self.experiment_dir)
        assert (
            self.experiment_dir.exists()
        ), f"experiment_dir not found: {self.experiment_dir}"
        assert self.sampling in VALID_SAMPLING, (
            f"unknown sampling: {self.sampling} (valid: {VALID_SAMPLING})"
        )
        assert self.lag_steps >= 1, f"lag_steps must be >= 1, got {self.lag_steps}"


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
        split=SplitConfig(**d["split"]),
        samples_per_experiment=d.get("samples_per_experiment", None),
        sampling=d.get("sampling", "latest"),
        skip=d.get("skip", 0),
        lag_steps=d.get("lag_steps", 1),
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

    expected_in_channels = data.lag_steps * len(data.x_vars)
    assert model.fno.in_channels == expected_in_channels, (
        f"model.fno.in_channels={model.fno.in_channels} does not match "
        f"data.lag_steps * len(x_vars) = {data.lag_steps} * {len(data.x_vars)} "
        f"= {expected_in_channels}"
    )

    return Config(
        data=data, model=model, training=training, logging=logging_cfg, paths=paths
    )
