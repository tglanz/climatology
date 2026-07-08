"""Remove simulation directories for sweep entries matching given parameter filters."""

import argparse
import json
import shutil
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, required=True, help="Experiment output directory containing sweep.json")
    p.add_argument("--lat0", type=float, nargs="+", metavar="LAT", help="Filter by stirring_lat0 values")
    p.add_argument("--dry-run", action="store_true", help="Print what would be deleted without deleting")
    return p.parse_args()


def main():
    args = parse_args()

    sweep_path = args.output_dir / "sweep.json"
    if not sweep_path.exists():
        raise FileNotFoundError(f"sweep.json not found in {args.output_dir}")

    with open(sweep_path) as f:
        sweep = json.load(f)

    target_lats = set(args.lat0) if args.lat0 else None

    target_codes = [
        code for code, params in sweep.items()
        if target_lats is None or params.get("stirring_lat0") in target_lats
    ]

    sims_dir = args.output_dir / "simulations"
    targets = sorted(
        d for d in sims_dir.iterdir()
        if any(d.name.startswith(c) for c in target_codes)
    )

    if not targets:
        print("No matching simulation directories found.")
        return

    total_bytes = sum(
        f.stat().st_size for d in targets for f in d.rglob("*") if f.is_file()
    )
    print(f"{'[dry-run] ' if args.dry_run else ''}Targeting {len(targets)} dirs ({total_bytes / 1e9:.2f} GB):")
    for d in targets:
        print(f"  {d.name}")

    if args.dry_run:
        return

    confirm = input(f"\nDelete {len(targets)} directories? [y/N] ")
    if confirm.lower() != "y":
        print("Aborted.")
        return

    for d in targets:
        shutil.rmtree(d)
        print(f"Deleted {d.name}")

    print(f"\nDone. Freed ~{total_bytes / 1e9:.2f} GB.")


if __name__ == "__main__":
    main()
