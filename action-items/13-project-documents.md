# 13. Refresh project and operating documents

Priority: P2. Coordinate with 14-16.

## Evidence

The root README has a placeholder clone URL and little restart guidance.
`ml/README.md` and `heat-simulation/README.md` are empty.
`sim/README.md:22` says the scanner writes sweep.json, but that responsibility moved to ML.
`docs/isca-barotropic-stirring.md` still runs a module without a main, describes automatic CPU selection, and shows monthly output paths.
The current scanner uses explicit cores and daily output under simulations.
The dated trial spec, Slurm sweep matrix, and current TOML files describe different experiments.

## Work

Create one short restart path covering simulation, validation, split creation, preprocessing, training, evaluation, and notebooks.
Name each artifact, its owner, and its directory.
Use one source for current setup and commands. Link to it from overlapping guides.
Label dated trial specifications and presentations as historical.
Keep their measurements, correct false statements, and link to the current method.
Review both AI4PDE sources and choose the maintained source so Markdown and TeX do not drift.

Check every document family in the review index.
Fix command paths, defaults, units, stale names, missing images, and duplicate explanations.
In S3 guidance, choose one working directory and check endpoint setup and sync semantics.
In spectral guidance, distinguish total degree, stored indices, grid spacing, and wavelength.

## Verify

1. Follow the restart guide in a clean supported environment using the small fixture.
2. Check each documented command against current help. Inspect resulting paths and schemas.
3. Check local links, images, bibliography links, and all maintained presentation render commands.
4. Review ncdump/h5dump examples against tiny real files. Check MPI examples against the documented implementation.
5. Review remote-storage commands without uploading, deleting, or starting jobs. Use dry-run where appropriate.
6. Require no unlabelled historical settings presented as current facts.
