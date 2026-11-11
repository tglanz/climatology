"""Select complete input windows; convergence bounds the window start."""

from ml.config import WindowsConfig


class WindowSelector:
    def __init__(self, cfg: WindowsConfig):
        self.cfg = cfg

    def select(
        self, timeline_length: int, t_s: int | None = None, t_c: int | None = None
    ) -> list[int]:
        if timeline_length < 0:
            raise ValueError("timeline length must be nonnegative")
        lower = 0 if self.cfg.start_at == "beginning" else t_s
        if lower is None:
            raise ValueError("start_at='spinup' requires a detected spinup")
        if lower < 0:
            raise ValueError("window start must be nonnegative")
        upper = timeline_length - self.cfg.length
        if self.cfg.end_at == "convergence":
            if t_c is None:
                raise ValueError("end_at='convergence' requires detected convergence")
            upper = min(upper, t_c)
        indices = list(range(lower, upper + 1, self.cfg.stride))
        return indices if self.cfg.limit is None else indices[: self.cfg.limit]


def build_selector(cfg: WindowsConfig) -> WindowSelector:
    return WindowSelector(cfg)
