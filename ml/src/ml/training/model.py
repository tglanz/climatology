from dataclasses import asdict

from neuralop.models import FNO

from ml.config import ModelConfig


def build_model(cfg: ModelConfig, dropout: float | None = None):
    """
    Build the neural operator selected by `cfg.architecture` ("fno" or
    "sfno"). `dropout` (if provided) is forwarded as `channel_mlp_dropout`,
    which applies dropout inside the channel-mixing MLP between blocks.
    """
    sub = cfg.active_sub_config()
    kwargs = asdict(sub)
    # asdict turns the n_modes tuple into a list; restore the tuple so the
    # constructor call is byte-identical to the pre-refactor one.
    kwargs["n_modes"] = tuple(kwargs["n_modes"])
    if dropout is not None:
        kwargs["channel_mlp_dropout"] = dropout

    if cfg.architecture == "fno":
        return FNO(**kwargs)
    if cfg.architecture == "sfno":
        try:
            from neuralop.models import SFNO
        except ImportError as e:
            raise ImportError(
                "SFNO requires torch_harmonics; install it via "
                "`uv add torch_harmonics` or switch architecture to 'fno'"
            ) from e
        return SFNO(**kwargs)
    raise ValueError(f"unknown architecture: {cfg.architecture}")
