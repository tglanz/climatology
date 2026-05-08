from neuralop.models import FNO

from ml.config import FNOModelConfig


def build_model(cfg: FNOModelConfig, dropout: float | None = None) -> FNO:
    """
    Build the FNO model. `dropout` (if provided) is forwarded to the
    underlying FNO as `channel_mlp_dropout`, which applies dropout inside
    the channel-mixing MLP between FNO blocks.
    """
    kwargs: dict = dict(
        n_modes=cfg.n_modes,
        hidden_channels=cfg.hidden_channels,
        in_channels=cfg.in_channels,
        out_channels=cfg.out_channels,
        n_layers=cfg.n_layers,
    )
    if dropout is not None:
        kwargs["channel_mlp_dropout"] = dropout
    return FNO(**kwargs)
