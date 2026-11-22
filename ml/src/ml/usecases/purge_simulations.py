"""Preview simulation cleanup and require confirmation before deletion."""

from collections.abc import Callable
from pathlib import Path

from ml.services.simulations import find_simulations, delete_simulation


def run(
    output_dir: Path,
    latitudes: tuple[float, ...],
    dry_run: bool,
    *,
    confirm: Callable[[str], bool],
    emit: Callable[[str], None],
) -> None:
    simulations = find_simulations(output_dir, latitudes)
    if not simulations:
        emit("No matching simulation directories found.")
        return

    total_bytes = sum(simulation.size_bytes for simulation in simulations)
    emit(
        f"{'[dry-run] ' if dry_run else ''}Targeting {len(simulations)} dirs "
        f"({total_bytes / 1e9:.2f} GB):"
    )
    for simulation in simulations:
        emit(f"  {simulation.path.name}")
    if dry_run:
        return
    if not confirm(f"Delete {len(simulations)} directories?"):
        emit("Aborted.")
        return

    for simulation in simulations:
        delete_simulation(simulation)
        emit(f"Deleted {simulation.path.name}")
    emit(f"Done. Freed ~{total_bytes / 1e9:.2f} GB.")
