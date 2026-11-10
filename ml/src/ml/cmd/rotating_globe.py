"""Generate a rotating globe GIF from a simulation directory.

Run from the repository root with:
uv run --project ml --group vis --group train python -m ml.cmd.rotating_globe --help
"""

import argparse
from pathlib import Path
from ml.data.isca_segment import read_segments
from ml.visualization.globe import (
    COMPUTED_DIAGNOSTICS,
    get_available_diagnostics,
    make_gif,
)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a rotating globe GIF from Isca simulation output.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s --input-path ../output/barotropic_stirring-T85\n"
            "  %(prog)s --input-path ../output/barotropic_stirring-T85 --time 50 --diagnostic pv\n"
            "  %(prog)s --input-path ../output/barotropic_stirring-T85 --rotations 2 --fps 12\n"
        ),
    )

    parser.add_argument(
        "--input-path",
        required=True,
        help="Path to simulator output directory containing run*/atmos_daily.nc",
    )
    parser.add_argument(
        "--output-path",
        default="globe.gif",
        help="Output GIF path (default: globe.gif)",
    )
    parser.add_argument(
        "--time",
        default="evolve",
        help=(
            "'evolve' to advance through all time steps, or an integer for a "
            "fixed time step (default: evolve)"
        ),
    )
    parser.add_argument(
        "--diagnostic",
        default="vor",
        help="Variable name from the dataset (default: vor). "
        "Use --list-diagnostics to see options.",
    )
    parser.add_argument(
        "--list-diagnostics",
        action="store_true",
        help="Print available diagnostics and exit",
    )
    parser.add_argument(
        "--list-times",
        action="store_true",
        help="Print available time steps and exit",
    )
    parser.add_argument(
        "--cmap",
        default=None,
        help="Matplotlib colormap (default: auto based on diagnostic)",
    )
    parser.add_argument(
        "--rotations",
        type=float,
        default=1.0,
        help="Number of full rotations over the animation (default: 1.0)",
    )
    parser.add_argument(
        "--n-frames",
        type=int,
        default=None,
        help="Number of frames (default: number of time steps for evolve, 90 for fixed)",
    )
    parser.add_argument(
        "--center-lat",
        type=float,
        default=30.0,
        help="Latitude of the view center in degrees (default: 30.0)",
    )
    parser.add_argument(
        "--center-lon",
        type=float,
        default=0.0,
        help="Starting longitude of the view center in degrees (default: 0.0)",
    )
    parser.add_argument(
        "--figsize",
        type=float,
        default=6.0,
        help="Figure size in inches (square) (default: 6.0)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=6,
        help="Frames per second (default: 6)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=100,
        help="Resolution in dots per inch (default: 100)",
    )
    parser.add_argument(
        "--percentile",
        type=float,
        default=98.0,
        help="Percentile for robust color scaling (default: 98.0)",
    )

    args = parser.parse_args()

    print(f"Loading data from {args.input_path}...")
    ds = read_segments(
        str(Path(args.input_path) / "run*" / "atmos_daily.nc"), decode_time=True
    )

    if args.list_diagnostics:
        raw, computed = get_available_diagnostics(ds)
        print("Available diagnostics:")
        print("  Raw (from dataset):")
        for v in raw:
            shape = ds[v].shape
            print(f"    {v:20s} {shape}")
        print("  Computed:")
        for v in computed:
            entry = COMPUTED_DIAGNOSTICS[v]
            tag = "static" if entry["static"] else "time-varying"
            print(f"    {v:20s} {entry['description']} ({tag})")
        return

    if args.list_times:
        times = ds.time.values
        print(f"Available time steps: {len(times)} (indices 0 to {len(times) - 1})")
        for i, t in enumerate(times):
            print(f"  {i:4d}  {t}")
        return

    make_gif(ds, args)


if __name__ == "__main__":
    main()
