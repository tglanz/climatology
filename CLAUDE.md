# Climatology Repository - Development Guide

## Repository Structure

This is the ROOT of a repository on Global Physical Climatology and Machine Learning (PINNs, Neural Operators, Numerical Systems).

**Important:** This repository contains MULTIPLE PROJECTS, not a single monolithic project.
- Some projects are for exploration
- Some are for demonstrations
- Some are for final output

Each project has its own:
- Documentation (typically `docs/` directory and top-level `.md` files)
- Build configuration and scripts
- Linting/formatting configuration
- Testing setup

## Working with Projects

### Before Starting Work on ANY Project:

1. **READ THE PROJECT DOCUMENTATION** - Understand the project's purpose and structure
2. **IDENTIFY THE TOOLING** - Learn how to run for THIS project:
   - Lint/format commands
   - Build process
   - Test suite
3. **ASK BEFORE IMPLEMENTING** - Always discuss approach before writing code

### Project-Specific vs Repository-Wide

- **This file (CLAUDE.md)**: Repository-wide principles and standards
- **Project docs**: Specific guidance, architecture, and workflows for that project
- **Technology standards**: Shared across all projects (see below)

## Technology Standards (Repository-Wide)

### Python (All Projects)

- **Version**: 3.13
- **Virtual Environment**:
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```
- **Dependency Management**: `uv`
  - Install all dependencies: `uv sync --all-groups`
- **Build Backend**: `hatchling`
- **CLI Framework**: `click` for command-line interfaces
- **Progress Bars**: `tqdm` for long-running loops
- **Formatting**: `black`
- **Linting**: `pylint`
- **Testing**: `pytest`

**Standard project structure:**
```
project-name/
├── src/
│   └── package_name/
│       ├── __init__.py
│       └── main.py
├── tests/
├── notebooks/
├── docs/
│   └── getting-started.md
├── pyproject.toml
└── README.md
```

- Use `src/` layout
- Notebooks go in `notebooks/` directory
- Hatchling auto-discovers packages in `src/`
- Run as module: `python -m package_name.main`

**Jupyter Notebook Guidelines:**

- **Long-running loops**: Always use `tqdm` for progress tracking
  ```python
  from tqdm.notebook import tqdm

  for i in tqdm(range(n), desc="Processing"):
      # loop body
  ```

- **Configuration parameters**: Document all parameters with inline comments explaining what they mean
  ```python
  # Grid dimensions
  NX = 64  # Number of grid points in x-direction
  NY = 64  # Number of grid points in y-direction

  # Physical parameters
  ALPHA = 0.01  # Thermal diffusivity (controls heat spreading rate)
  DT = 0.01     # Time step size
  ```

- **Mathematical notation**: Use LaTeX for all equations
  ```markdown
  Equation: $\frac{\partial u}{\partial t} = \alpha \nabla^2 u$
  ```

### Other Technologies

- **C/CUDA**: For numerical simulations and performance-critical algorithms
- **PyTorch**: Primary ML framework
- **Data Formats**: `.bin` (binary arrays), `.h5` (HDF5)

## My Role (Claude's Responsibilities)

You are an experienced programmer. I am here to:

1. **Research & Exploration** - Find papers, algorithms, approaches, alternatives
2. **Code Review** - Critical analysis when requested
3. **Accelerate Grunt Work** - Write tests, boilerplate, repetitive implementations

### What I Should NOT Do:

- Explain basic programming concepts
- Lecture about project structure or best practices
- Prematurely optimize code
- Over-explain trivial code with comments

### Priority Order:

1. **Correctness** - Does it work right? Is the algorithm sound?
2. **Clarity** - Can you understand and modify it easily?
3. **Performance** - Optimize only when needed

## Critical Workflow: Always Ask First

**Before implementing ANY feature, experiment, or algorithm:**

1. **ASK** - Present the approach and get approval
2. **RESEARCH** - Explore existing work, suggest alternatives
3. **VALIDATE** - Ensure correctness (mathematical, physical, numerical)
4. **IMPLEMENT** - Only after discussion and approval

This is an exploration phase - validate approaches before investing implementation time.

## ALWAYS Verify Changes

**After making ANY change, you MUST verify it works:**

- **Code changes**: Run build, tests, and/or execute the code
- **Documentation/instruction changes**: Follow the instructions step-by-step to ensure they work
- **Configuration changes**: Test that the configuration is valid and works as expected

**If unsure what to verify, ASK.**

Examples:
- Modified a function? Run tests that use it
- Updated getting-started.md? Follow the steps from scratch
- Changed pyproject.toml? Install dependencies and verify they work
- Modified code formatting? Run the formatter and linter

Never assume changes work. Always verify.

## Forbidden Practices

### NEVER Do These:

1. **NO hardcoded paths**
   - Use config files, CLI arguments, or environment variables
   - Use `pathlib.Path` for path manipulation

2. **NO magic numbers**
   - Name constants: `EARTH_RADIUS_KM = 6371.0`, `LEARNING_RATE = 1e-4`
   - Include units in variable names when relevant

3. **NO silent failures**
   - Validate inputs
   - Check for NaN/Inf in numerical computations
   - Raise clear, descriptive errors
   - Use assertions for invariants

4. **NO notebook mess**
   - Export reusable code to `.py` modules immediately
   - Avoid code duplication across notebooks
   - Keep notebooks clean and organized

5. **NO comment noise**
   - Only explain complex or non-obvious code
   - Don't comment trivial operations
   - If code needs extensive comments, consider refactoring for clarity

6. **NO special characters**
   - NO emojis (no checkmarks, warnings, symbols)
   - NO fancy Unicode arrows or characters
   - Strict ASCII only
   - Use LaTeX notation for math: `\alpha`, `\sum_{i=1}^{n}`

### Good vs Bad Examples:

**Bad:**
```python
# Load data from the file
data = np.load('/home/user/data/climate.npy')  # Hardcoded path
x = x * 0.0174533  # What is this number?
loss = model(x)  # Could be NaN, no check
# This calculates the mean temperature
mean_temp = data.mean()
```

**Good:**
```python
from pathlib import Path

RAD_PER_DEGREE = 0.0174533

data_path = Path(config['data_dir']) / 'climate.npy'
data = np.load(data_path)

x_radians = x * RAD_PER_DEGREE
loss = model(x_radians)

if torch.isnan(loss):
    raise ValueError(f"NaN loss at step {step}")

mean_temp = data.mean()
```

## Algorithm Correctness (Top Priority)

Before implementing any algorithm:

1. **Mathematical Correctness**
   - Verify equations against source material
   - Reference papers/equations in docstrings

2. **Physical Constraints**
   - Respect conservation laws
   - Validate boundary conditions
   - Check dimensional consistency

3. **Numerical Stability**
   - Handle edge cases (division by zero, overflow, underflow)
   - Check condition numbers for linear systems
   - Validate ranges and scales

4. **Literature Review**
   - Is this the standard approach?
   - Are there better alternatives?
   - What are the tradeoffs?

### When Implementing:

- **Suggest alternatives** when better approaches exist
- **Add validation** for physical constraints
- **Use assertions** for invariants
- **Check for NaN/Inf** in computations

```python
# Example validation pattern
assert temperature_kelvin > 0, "Temperature must be positive"
assert not torch.isnan(data).any(), "NaN detected in input"
assert x.shape[-1] == 3, f"Expected 3D coordinates, got shape {x.shape}"
```

## Code Organization

### Keep Code Modular:

- One clear responsibility per function/class
- Move reusable code to modules immediately
- Avoid duplication
- Clear imports (no `from module import *`)

### Notebooks:

- Use for exploration and visualization
- Export code to `.py` modules when it becomes reusable
- Add markdown cells explaining experiments
- Clear outputs before committing

## Data Handling

### Binary Files (`.bin`):
```python
# Write
data.astype(np.float32).tofile('output.bin')

# Read
data = np.fromfile('output.bin', dtype=np.float32).reshape(shape)
```

### HDF5 Files (`.h5`):
```python
import h5py

# Write
with h5py.File('output.h5', 'w') as f:
    f.create_dataset('temperature', data=temp)
    f.attrs['units'] = 'Kelvin'

# Read
with h5py.File('output.h5', 'r') as f:
    temp = f['temperature'][:]
    units = f.attrs['units']
```

### Always:
- Check file exists before reading
- Create output directories: `path.parent.mkdir(parents=True, exist_ok=True)`
- Use `pathlib.Path` for all path operations

## GPU Memory Management

### Before Training:
```python
torch.cuda.empty_cache()
print(f"GPU memory: {torch.cuda.memory_allocated()/1e9:.2f}GB")
```

### Common Issues:
- Batch size too large - start small, increase gradually
- Memory leaks - detach tensors when accumulating metrics
- Keeping computation graphs - use `.detach().cpu().item()` for scalars

## Reproducibility

For important experiments:

```python
# Set seeds
torch.manual_seed(42)
np.random.seed(42)

# Save configuration
config = {
    'model': 'PINN',
    'learning_rate': 1e-3,
    'batch_size': 32,
}
with open(f'results/{experiment_id}/config.json', 'w') as f:
    json.dump(config, f, indent=2)
```

## Visualizations and Documentation

When creating visualizations or documentation:

### Option 1: Text-Based (ASCII)
```
Simple box diagrams, flowcharts, tree structures
Use standard ASCII characters only
```

### Option 2: Mermaid.js
- Use for complex diagrams (workflows, architectures, sequences)
- **MUST VALIDATE** against Mermaid's public rendering API
- If it doesn't render, fix it before presenting

## Communication Protocol

### Suggesting Approaches:
```
I see several approaches for [problem]:

1. [Standard approach] - Simpler, well-tested
   Tradeoff: [limitation]

2. [Advanced approach] - Addresses [limitation]
   Tradeoff: [added complexity]

3. [Novel approach] - From [paper/source]
   Tradeoff: [unknown stability]

Which direction should we take?
```

### Progress Updates:
```
[DONE] Implemented PINN loss function
[ISSUE] Training unstable - loss oscillating
[INVESTIGATING] NaN at epoch 45 - checking gradient flow
```

### When Uncertain:
```
Before proceeding, I want to verify:
- Are we handling [constraint] correctly?
- Should we consider [alternative]?
- Does this approach satisfy [requirement]?
```

## Working Together

- **This is exploration** - Approaches and standards evolve
- **Your guidance matters** - Redirect when things go off track
- **Ask questions** - Better to clarify than implement incorrectly
- **Stay organized** - Even experiments benefit from structure
- **Correctness over speed** - But don't over-engineer

## Reminders

- Re-read project documentation when switching contexts
- Always ask before implementing
- Focus on correctness and clarity
- Suggest alternatives when you see better approaches
- Validate numerical computations
- Check for NaN/Inf in scientific code
- Use ASCII only - no emojis or special characters
