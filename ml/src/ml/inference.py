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

    def rollout(
        self, vor_history: np.ndarray, stirring_seq: np.ndarray
    ) -> np.ndarray:
        """
        Autoregressively predict vorticity.

        Parameters
        ----------
        vor_history : (K, lat, lon)
            Vorticity at the K most recent known timesteps, in chronological
            order. K must equal the lag_steps the model was trained with.
            For K=1 this is a single (1, lat, lon) snapshot, equivalent to
            the previous (lat, lon) `vor0` argument.
        stirring_seq : (K + T - 1, lat, lon)
            Stirring at all timesteps used in any input window:
            the K history timesteps plus T - 1 additional steps for the
            future predictions. T is inferred as
                T = stirring_seq.shape[0] - K + 1
            and must be >= 1.

        Returns
        -------
        vor : (K + T, lat, lon)
            Vorticity at the union of history and prediction times. The
            first K rows echo `vor_history`; rows K..K+T-1 are predicted
            one step ahead each.

        The model input for prediction step s (s = 0, ..., T - 1) uses
        the K-step window
            (vor_t-K+1, stirring_t-K+1, vor_t-K+2, stirring_t-K+2, ...,
             vor_t,     stirring_t)
        flattened along the channel axis (oldest-to-newest, x_vars-major
        within each step). This must match the convention used by
        `extract_pairs` in `ml.isca_preprocessing`.
        """
        assert vor_history.ndim == 3, (
            f"vor_history must be (K, lat, lon), got {vor_history.shape}"
        )
        assert stirring_seq.ndim == 3, (
            f"stirring_seq must be (L, lat, lon), got {stirring_seq.shape}"
        )
        K, lat, lon = vor_history.shape
        L = stirring_seq.shape[0]
        assert L >= K, (
            f"stirring_seq length {L} must be >= K={K} (history coverage)"
        )
        T = L - K + 1
        assert T >= 1, "no predictions: stirring_seq too short"

        out = np.empty((K + T, lat, lon), dtype=np.float32)
        out[:K] = vor_history.astype(np.float32)

        vor_window = torch.from_numpy(vor_history.astype(np.float32)).to(self.device)
        stirring_t = torch.from_numpy(stirring_seq.astype(np.float32)).to(self.device)

        with torch.no_grad():
            for s in range(T):
                stirring_window = stirring_t[s : s + K]  # (K, lat, lon)

                # Interleave channels [vor_k, stirring_k] for k = 0..K-1
                channels = []
                for k in range(K):
                    channels.append(vor_window[k])
                    channels.append(stirring_window[k])
                x = torch.stack(channels, dim=0).unsqueeze(0)  # (1, 2K, lat, lon)

                x_norm = (x - self.x_mean) / self.x_std
                y_norm = self.model(x_norm)
                y = y_norm * self.y_std + self.y_mean
                next_vor = y.squeeze(0).squeeze(0)  # (lat, lon)

                assert not torch.isnan(next_vor).any(), (
                    f"NaN in model output at rollout step {s}"
                )

                out[K + s] = next_vor.cpu().numpy()
                # Slide window: drop oldest, append the new prediction.
                vor_window = torch.cat(
                    [vor_window[1:], next_vor.unsqueeze(0)], dim=0
                )

        return out
