import logging
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

log = logging.getLogger(__name__)


class Autoregressor:
    def __init__(self, model: nn.Module, checkpoint_dir: Path):
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        normalization_path = checkpoint_dir / "normalization.pt"
        assert normalization_path.exists(), f"normalization stats not found: {normalization_path}"
        stats = torch.load(normalization_path, map_location="cpu", weights_only=True)
        self.x_mean = stats["x_mean"].to(self.device)
        self.x_std = stats["x_std"].to(self.device)
        self.y_mean = stats["y_mean"].to(self.device)
        self.y_std = stats["y_std"].to(self.device)

        parameters_path = checkpoint_dir / "parameters.pt"
        assert parameters_path.exists(), f"model parameters not found: {parameters_path}"
        model.load_state_dict(torch.load(parameters_path, map_location=self.device, weights_only=False))
        self.model = model.to(self.device)
        self.model.eval()

        log.info("loaded model from %s (device: %s)", checkpoint_dir, self.device)

    def rollout(self, vor0: np.ndarray, stirring_seq: np.ndarray) -> np.ndarray:
        """
        Autoregressively predict vorticity for T steps.

        Parameters
        ----------
        vor0 : (lat, lon) initial vorticity field at t_0
        stirring_seq : (T, lat, lon) stirring forcing for steps t_0 .. t_0+T-1

        Returns
        -------
        vor_pred : (T+1, lat, lon) predicted vorticity at t_0 .. t_0+T
        """
        T = stirring_seq.shape[0]
        lat, lon = vor0.shape
        vor_pred = np.empty((T + 1, lat, lon), dtype=np.float32)
        vor_pred[0] = vor0

        vor_t = torch.from_numpy(vor0.astype(np.float32)).to(self.device)

        with torch.no_grad():
            for t in range(T):
                stirring_t = torch.from_numpy(stirring_seq[t].astype(np.float32)).to(self.device)

                # x shape: (1, 2, lat, lon)
                x = torch.stack([vor_t, stirring_t], dim=0).unsqueeze(0)

                x_norm = (x - self.x_mean) / self.x_std
                y_norm = self.model(x_norm)
                y = y_norm * self.y_std + self.y_mean

                vor_t = y.squeeze(0).squeeze(0)

                assert not torch.isnan(vor_t).any(), f"NaN in model output at step {t}"

                vor_pred[t + 1] = vor_t.cpu().numpy()

        return vor_pred
