# 03. Reconsider and streamline the pipeline

**Change:** review the full route from simulation output to an evaluated experiment, then simplify how its parts fit together.

Cover these decisions together:

- **Stages:** what preparation, training, and evaluation each do, and how to run or rerun them.
- **Data:** what each stage reads and writes, including coordinates, samples, targets, and split membership.
- **Configuration:** which settings belong to data, the model, training, and execution. A data-only operation should not require model settings.
- **Saved results:** what must be kept to load a model, identify its inputs, compare runs, and regenerate evaluation.
- **Execution:** how local and Slurm runs use the same program, and how failures stop dependent work.
- **Small experiments:** a tiny smoke run and a fixed subset of real simulations with a smaller model, using the normal pipeline and separate output directories.

Start by tracing one current experiment. Choose the simplest revised flow that supports these needs. Then implement it using the existing packages where practical.

Prepare data once and reuse it for model iterations. Keep the same target and split rules in small and full runs. Address setup, scripts, performance, or CI only where they help this workflow.

**Why:** the current workflow is spread across commands, scripts, and implicit directory assumptions. Training can reopen raw data for coordinates; evaluation rebuilds samples from the raw simulations currently present. This makes experiments slow to repeat and easy to run inconsistently.

**Verify:**

1. Run a small experiment through preparation, training, checkpoint loading, and evaluation using one documented recipe.
2. Change only the model settings. Require reuse of prepared data and separate results for the new run.
3. Rerun a stage and confirm that its inputs and outputs are clear and that unrelated work is not repeated.
4. Load the saved model and reproduce its evaluation from the saved inputs and settings.
5. Check local and Slurm command construction and failure handling.
6. Measure the small experiment's runtime and memory. Confirm it is useful for routine iteration.
