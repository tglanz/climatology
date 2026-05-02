from neuralop.models import FNO

from ml.config import FNOModelConfig


def build_model(cfg: FNOModelConfig) -> FNO:
    return FNO(
        n_modes=cfg.n_modes,
        hidden_channels=cfg.hidden_channels,
        in_channels=cfg.in_channels,
        out_channels=cfg.out_channels,
    )
