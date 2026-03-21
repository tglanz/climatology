# Climatology

Research repository on Global Physical Climatology and Machine Learning (PINNs, Neural Operators, Numerical Systems).

## Submodules

This repository uses Git submodules to track external dependencies at specific commits.

### Isca

[Isca](https://github.com/ExeClim/Isca) is a framework for idealized global circulation model (GCM) experiments developed at the University of Exeter.

Located at: `submodules/isca`

---

### Cloning with Submodules

When cloning this repository for the first time, initialize and fetch all submodules:

```bash
git clone --recurse-submodules https://github.com/your-org/climatology
```

If you already cloned without `--recurse-submodules`:

```bash
git submodule update --init --recursive
```

---

### Pulling Submodule Updates

To update all submodules to the commit recorded in the superproject:

```bash
git submodule update --recursive
```

To pull each submodule to the latest commit on its tracked remote branch:

```bash
git submodule update --remote --recursive
```

After running `--remote`, the superproject index will show the submodules as modified. Commit the changes to record the new commit SHAs:

```bash
git add submodules/
git commit -m "update submodules to latest"
```

---

### Pinning a Submodule to a Specific Commit

```bash
cd submodules/isca
git fetch
git checkout <commit-sha>   # or a tag/branch name
cd ../..
git add submodules/isca
git commit -m "pin isca to <commit-sha>"
```

---

### Checking Submodule Status

```bash
git submodule status
```

A leading `-` means the submodule is not yet initialized. A leading `+` means the checked-out commit differs from what the superproject recorded.