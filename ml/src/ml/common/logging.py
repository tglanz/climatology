import logging

from ml.config import LoggingConfig


def setup_logging(cfg: LoggingConfig):
    handlers = []
    if cfg.stdout:
        handlers.append(logging.StreamHandler())
    if cfg.output_file:
        cfg.output_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(cfg.output_file))
    logging.basicConfig(
        level=cfg.level,
        handlers=handlers,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
