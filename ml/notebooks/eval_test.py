"""Run the prepared-sample evaluation notebook from the repository root."""

from pathlib import Path
import argparse
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ml.usecases.evaluate_samples import run, print_metrics
from ml.visualization.model_samples import (
    plot_sample_profiles,
    plot_sample_errors,
    plot_sample_scatter,
    plot_sample_distribution,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("training_dir", type=Path)
    parser.add_argument(
        "--output-dir", type=Path, default=Path("/tmp/climatology-evaluation")
    )
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    pred, truth, lat, rmses, rels = run(args.training_dir, limit=args.limit)
    print_metrics(rmses, rels)
    for name, fn, values in [
        ("profiles", plot_sample_profiles, (pred, truth, lat)),
        ("errors", plot_sample_errors, (pred, truth, lat)),
        ("scatter", plot_sample_scatter, (pred, truth)),
        ("distribution", plot_sample_distribution, (rmses, rels)),
    ]:
        fn(*values)
        plt.gcf().savefig(args.output_dir / f"{name}.png")
        plt.close("all")


if __name__ == "__main__":
    main()
