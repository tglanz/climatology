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
    result = run(args.training_dir, limit=args.limit)
    print_metrics(result)
    for name, fn in [
        ("profiles", plot_sample_profiles),
        ("errors", plot_sample_errors),
        ("scatter", plot_sample_scatter),
        ("distribution", plot_sample_distribution),
    ]:
        for target, figure in zip(result.metadata.y_vars, fn(result), strict=True):
            figure.savefig(args.output_dir / f"{target}-{name}.png")
        plt.close("all")


if __name__ == "__main__":
    main()
