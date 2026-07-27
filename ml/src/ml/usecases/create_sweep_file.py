import json
from pathlib import Path


def run(experiment_dir: Path, key_specs: list[tuple[str, list[str]]]) -> None:
    sim_dir = experiment_dir / "simulations"
    out_path = experiment_dir / "sweep.json"

    if not sim_dir.exists():
        raise FileNotFoundError(f"simulations directory not found: {sim_dir}")

    sweep: dict[str, dict] = {}
    for namelist_path in sorted(sim_dir.glob("*/namelist.json")):
        code = namelist_path.parent.name.rsplit("-", 1)[0]
        if code in sweep:
            continue
        namelist = json.loads(namelist_path.read_text())
        entry = {}
        for alias, path in key_specs:
            node = namelist
            for part in path:
                if not isinstance(node, dict) or part not in node:
                    raise KeyError(f"{namelist_path}: path '{'.'.join(path)}' not found")
                node = node[part]
            entry[alias] = node
        sweep[code] = entry

    out_path.write_text(json.dumps(sweep, indent=2))
    print(f"wrote {len(sweep)} codes to {out_path}")
