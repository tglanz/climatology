# Working rules

## Scope

- Follow the user's scope. Complete clear, authorized work.
- Ask only when required information or approval is missing.
- Preserve local changes, data, and experiment results.
- Read scoped guidance, project docs, and build files before edits.
- Use available tools. Do not assume a specific agent or background API.

## Projects

- `sim/`: Isca simulations. Use its conda environment.
- `ml/`: data preparation, diagnostics, training, evaluation, and plots.
- `heat-simulation/`: a separate heat equation demonstration.
- `book/`: general theory. Keep project details in project documents.
- `docs/`: project methods and operating instructions.
- `presentations/`: talks and study material.
- Check each project's `pyproject.toml` for Python, dependencies, and tools.
- From the repo root, use `uv run --project ml ...` for ML commands.
- Keep third-party changes explicit. Preserve submodule pins and local patches.

## Code and science

- Prefer correctness, then clarity, then speed.
- Give each responsibility one owner. Reuse it across callers.
- Keep notebooks to configuration, library calls, and explanation.
- Keep heat demonstration logic in its own package.
- Validate shapes, units, coordinates, grids, and boundary cases.
- State numerical and physical assumptions. Cite primary sources.
- Separate observations, hypotheses, and proposed experiments.
- Record run configuration, seeds, data sources, and model provenance.
- Use small checks first. Run heavy jobs only when the task needs them.
- Test changed behavior. Report checks run and limits.
- Delete code only after checking callers, entry points, and notebooks.

## Voice

- Use short, direct sentences and active voice.
- Use one term for each concept. Define symbols before use.
- Lead with the result. Add only details that help the reader.
- State facts and uncertainty plainly. Avoid filler and slogans.
- Explain why in comments. Omit comments that repeat the code.
- Use ASCII prose and LaTeX for mathematics.
- Keep progress updates brief. Make the final answer self-contained.
