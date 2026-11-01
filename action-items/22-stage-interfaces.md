# 22. Define stage interfaces and one runnable recipe

Priority: P2. System design. Coordinate with 08, 18, 19, and 21.

## Evidence

`ml/src/ml/config.py:428-433` requires data, model, and training sections together.
Its loader validates model channels even for data-only commands.
Preprocessing use cases accept config paths, while training setup lives in the CLI.
Shell and Slurm scripts encode separate parts of the pipeline.

## Work

Define stage inputs and outputs for validate/catalog, split, prepare, train, predict/score, and render.
Parse only the specification needed by a stage.
Keep one TOML file if that is easiest. Stage-local validation does not require a configuration framework.
Separate scientific settings from workers, device, and executor resources.

Make use cases return artifact references and explicit status.
Keep CLI, notebooks, and local/Slurm wrappers as adapters.
Keep the runtime boundary explicit: the recipe runs simulation commands in conda and ML commands in uv. ML consumes manifests/NetCDF without importing Isca simulation objects.
Provide one short smoke recipe, with a plan/check option that resolves prerequisites, outputs, and reuse decisions before expensive work.
Reuse completed stages and stop dependent stages on failure.

## Verify

1. Run split and preparation commands without model or training sections.
2. Change an optimizer or head. Reuse the same compatible dataset.
3. Change a target, window rule, or grid. Require a new compatible dataset.
4. Complete the tiny recipe from a clean directory. Stop after preparation and continue at training without rebuilding data.
5. Compare local and fake-Slurm plans. Scientific specs and artifact IDs must match, while execution resources may differ.
6. Inject a stage failure. No dependent stage may start.
7. Call the same use case from a notebook and CLI. Require the same artifact references, predictions, and scores.
8. Run catalog, preparation, training, and evaluation in an ML-only environment without the isca package.
