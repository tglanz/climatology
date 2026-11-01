# System architecture review

Reviewed 2026-11-01. This is a design assessment. No pipeline changes were made.

## Assessment

The repository has a sound foundation for an evolvable research system.
Its main weakness is the contract between stages: which exact data and model an experiment used, what each stage guarantees, and which result can be reused.
Fixing these boundaries will help more than adding more folders.

Keep the separate Isca and ML runtimes, current package layout, plain configuration files, pinned upstream dependencies, and forcing-group splits.
Keep numerical diagnostics independent of execution.
Existing saved configs and training metadata are useful foundations.

## Current pipeline

| Stage | Current behavior | Architectural consequence |
|---|---|---|
| Simulation | Writes segmented NetCDF and namelist metadata | A forcing code is useful, but does not establish compatible run identity |
| Validation | Prints findings and returns counts | Downstream stages do not consume a durable eligibility decision |
| Splits | Rescans directories and saves relative paths | The selected source population is not a versioned catalog |
| Preparation | Writes HDF5 splits into configured output paths | No completed immutable dataset boundary protects consumers from partial or changed data |
| Training | Loads HDF5, but reopens raw data for latitudes; rotates a named directory | The prepared artifact is not self-contained, and directory names carry run identity |
| Evaluation | Rebuilds samples from current raw simulations | Report contents can drift independently of the dataset used for training |
| Reports and notebooks | Repeat parts of loading, inference, scoring, and plotting | New features require changes in several execution paths |

Evidence: `sim/scanner.py:60-95`; `ml/src/ml/usecases/validate_simulations.py:101-145`; `usecases/generate_splits.py:17-23`; `usecases/preprocess.py:44,97-103`; `cmd/train.py:28-47`; `data/isca_dataset.py:62-69`; `cmd/evaluate.py:55-77,157-179`.

The observed normalization and target-policy differences are examples of what these loose boundaries permit.
They are covered in items 01 and 06.

## Target structure

Each stage should consume explicit completed artifacts and produce a new identified result.

| Artifact | Owner | Essential contract |
|---|---|---|
| Simulation catalog | Data ingestion, using simulation records | Source identities, forcing groups, grid, eligibility and rejection reasons |
| Frozen split | Data preparation | Catalog ID, exact membership, grouping policy |
| Prepared dataset | Data preparation | Inputs, physical targets, coordinates, row identities, preprocessing spec |
| Training run | Training use case | Dataset ID, resolved model/training spec, seed, environment, status |
| Inference bundle | Model/predictor | Weights, transforms, target/grid/head schema, version |
| Evaluation result | Evaluation use case | Bundle and dataset IDs, protocol, predictions, scores, coverage |
| Report or notebook | Visualization and user-facing adapters | Views of a specific evaluation result |

The same prepared dataset should support several seeds, backbones, and heads that share its physical target.
Changing a target, window rule, or grid requires a new compatible dataset.
Changing a plot should only require rendering a view.

Use small explicit stage interfaces in the existing packages.
A CLI, notebook, local shell wrapper, and Slurm job should invoke the same use case with the same scientific specification.
Execution settings such as workers, device, and scheduler resources belong to the execution record.
They should not silently change scientific identity.

## Extension points

The immediate extension is the output head.
Separate backbone choice from head choice and physical target semantics.
The predictor should return the same declared physical profile for the current, direct-profile, and coefficient heads.
Keep coefficient decoding inside that boundary.

Add a new target by defining its preparation and schema, then checking model compatibility.
Add a new executor by adapting an existing stage command.
Add a plot by reading persisted predictions and scores.
These changes should each have one main owner.

## Order of work

1. Fix numerical and data contracts in 01-07, then define artifact identity and stage interfaces in 21-22.
2. Prove one small complete run and independent evaluation in 19 and 24.
3. Establish the complete model bundle in 23, then run the controlled head comparison in 20.

## Architectural acceptance scenarios

- Prepare data once, train two heads, and compare them on one frozen evaluation protocol.
- Move a dataset and model bundle away from raw NetCDF. Training and prediction still have their required coordinates and transforms.
- Add raw simulations. Existing runs and reports still identify exactly their original data.
- Stop after preparation, then continue training. Completed preparation is reused.
- Change only a plot. Regenerate it without training, inference, or raw data access.
- Run the same experiment locally and through a stubbed Slurm adapter. Scientific inputs match and failures stop dependents.

Items [21](21-artifact-lifecycle.md), [22](22-stage-interfaces.md), [23](23-model-contract.md), and [24](24-evaluation-artifacts.md) define the work and verification.

## Design basis

Shared transformations and fixed-model parity checks address training/inference skew.
[Google's ML rules](https://developers.google.com/machine-learning/guides/rules-of-ml/) describe these practices in rules 5, 32, and 37.

Explicit stage ownership also addresses the configuration and pipeline coupling discussed in
[Hidden Technical Debt in Machine Learning Systems](https://proceedings.neurips.cc/paper_files/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf).

The artifact layout and migration order above are recommendations inferred from this repository's needs.
