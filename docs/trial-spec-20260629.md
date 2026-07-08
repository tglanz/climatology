# Dataset Proposal: Vorticity to Climatological Jet Learning

---

# Parameter space

## Latitude (lat0)
Values: -10, 0, 30, 40, 50, 60, 70

Effect: shifts the latitude of stochastic forcing and determines where eddy momentum is injected and where jets form

ROI: highest ROI because it directly controls jet position and strongly determines the target climatology

---

## Amplitude (stirring-amplitude)
Values: 0.75e-10, 1.0e-10, 1.25e-10

Effect: controls forcing strength, modifying eddy kinetic energy, jet sharpness, and variability intensity

ROI: high ROI because it changes signal magnitude and regime strength, improving identifiability from short windows

---

## Stirring width (stirring-widthy)
Values: 8, 12, 16

Effect: controls meridional spread of forcing, affecting eddy scale, mixing efficiency, and jet width

ROI: high ROI because it changes turbulence structure rather than only shifting or scaling, increasing richness of learned dynamics

---

## Fixed parameters
stirring-decay-time 172800
stirring-lon0 180
stirring-widthx 45
stirring-B 0.4

Effect: held constant to isolate the effects of the main control parameters

ROI: low ROI for learning but essential for controlled experiments

---

# Replicates
Four per parameter combination

Effect: captures stochastic variability from random forcing realizations

ROI: medium ROI because it improves robustness but does not add new information about parameter dependence

---

# Simulation length
150 segments of 7 days each (1050 days total)

Effect: ensures full climatological convergence and stable jet statistics

---

# Window construction

## Window length
20 daily snapshots (20 days total)

Effect: captures low-frequency dynamical structure beyond short-term variability while remaining shorter than climatological averaging scales

---

## Number of windows per simulation
Six windows

## Selection method
Evenly-spread selection: windows are uniformly spaced across the valid post-spinup trajectory with minimum separation enforced between windows

Effect: reduces temporal correlation and increases diversity of sampled dynamical regimes

ROI: high ROI because it improves effective sample efficiency without increasing simulation count

---

# Target construction

For each simulation:
- compute time-mean zonal-mean u-component
- average over converged regime

Output shape: 128

All windows from same simulation share identical target

---

# Dataset scale

63 parameter combinations from full grid
252 simulations using four replicates each
1512 total samples

---

# Execution command

```bash
caffeinate -i parallel -j 3 \
  conda run -n isca_env python -m sim.scanner \
    --segments 150 \
    --stirring-lat0 -10 0 30 40 50 60 70 \
    --stirring-amplitude 0.75e-10 1.0e-10 1.25e-10 \
    --stirring-widthy 8 12 16 \
    --cores 2 \
    --index {} \
  ::: $(seq 0 3)
```

Runs 3 parallel jobs across replicate indices 0-3, each sweeping all 63 parameter combinations. At -j 3 concurrency with --cores 2 per job, peak load is 6 MPI processes.

---

# What changed

- Expanded parameter space from a sparse latitude-only sweep to a structured 3D design including latitude, forcing amplitude, and meridional forcing width.
- Reduced replicates per configuration to prioritize coverage of physical parameter space over repeated stochastic realizations.
- Increased window length from 10 daily snapshots to 20 daily snapshots to better capture low-frequency jet-relevant dynamics.
- Reduced number of windows per simulation and replaced uniform sampling with evenly-spread selection to reduce temporal correlation between samples.
- Shifted dataset design objective from prototype learning of a few climates to learning a smooth mapping across a continuous forcing manifold.
