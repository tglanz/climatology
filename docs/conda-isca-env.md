# Setting Up and Using the Isca Conda Environment

This document describes the conda workflow for Isca without `conda init`.

## Create the Environment

```bash
conda env create -f submodules/isca/ci/environment-py.yml
```

This creates an environment named `isca_env` with all required dependencies: `gfortran`, `openmpi`, `netcdf-fortran`, `numpy`, `xarray`, `pandas`, `f90nml`, `jinja2`, `sh`, and `tqdm`.

## Install the Isca Python Package

```bash
conda run -n isca_env pip install -e ./submodules/isca/src/extra/python
```

The `-e` flag installs in editable mode: changes to the Isca source are immediately reflected without reinstalling. All dependencies install only to `isca_env`; nothing affects your global or system Python.

## Verify the Installation

```bash
conda run -n isca_env python -c "from isca import BarotropicCodeBase; print('OK')"
```

If you see `OK`, the package is installed and all dependencies are available.

## Running Commands in the Environment

To run any command in the environment, prefix it with `conda run -n isca_env`:

```bash
conda run -n isca_env python sim/barotropic_stirring.py
conda run -n isca_env python -c "import isca; print(isca.__file__)"
```

You do not need to activate the environment or use `conda init` - `conda run` handles everything.

## Set Required Environment Variables

For Isca to find the compiler and libraries, add these to your `~/.zshrc`:

```bash
export GFDL_BASE=/path/to/climatology/submodules/isca
export GFDL_ENV=ubuntu_conda
export GFDL_WORK=/path/to/isca_work
export GFDL_DATA=/path/to/isca_data
```

Replace `/path/to/climatology` with your actual path. Then reload:

```bash
source ~/.zshrc
```

These variables are required at import time by the `isca` Python package and control where compiled code and model output are stored.
