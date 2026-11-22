# Scope and source conventions {.unnumbered #scope}

This guide develops the mathematics needed to read spherical fluid simulations, their diagnostics, and spectral operator models. It starts with definitions and builds to partial differential equations, Fourier analysis, spherical harmonics, numerical projection, and physical applications. This is a compact graduate introduction. It uses elementary algebra from the outset and introduces the calculus, complex notation, and functional language needed for the later derivations.

The main source is George B. Arfken and Hans J. Weber, *Mathematical Methods for Physicists*, sixth edition (2005), abbreviated **AW** [@ArfkenWeber2005]. The supplied file is [the local textbook](../../papers/methods-of-mathemacial-for-physicists.pdf). Section numbers in citations refer to this edition. Its printed Arabic page $p$ is PDF page $p+13$ (one-based), which helps locate the original treatment. Derivations below reconstruct the selected results with their assumptions.

Supplementary sources are identified where used. **V** denotes the supplied 2006 first edition of Vallis [@Vallis2006], [local PDF](../../papers/atmospheric-and-oceanic-fluid-dymamics.pdf), for fluid mechanics and averaging. **F** and **S** denote the original Fourier and spherical Fourier neural-operator papers [@Li2021fno; @Bonev2023sfno], [F local PDF](../../papers/fno.pdf), [S local PDF](../../papers/sfno.pdf). The local F paper is arXiv version 3 (2021); the local S paper is version 1 (2023). Hunter supplies the Sobolev-space definitions [@HunterPDE, Chapter 3], and NIST supplies the explicit Gaussian quadrature rule [@NISTDLMFQuadrature]. These extensions are not attributed to AW when its coverage is insufficient.

| Guide chapters | Principal AW sections |
|:--|:--|
| 1. Language and linear algebra | 1.1-1.5; 3.2-3.6; 6.1 |
| 2-3. Calculus and spherical geometry | 1.6-1.12, 1.16; 2.1-2.2, 2.5 |
| 4-6. Spaces and differential equations | 1.15; 5.5-5.7; 9.1-9.8; 10.1-10.5; 17.4 |
| 7. Fourier analysis | 14.1-14.6; 15.1-15.5 |
| 8-9. Harmonics and discretization | 12.1-12.6, 12.8, 12.11; 14.6; 17.8 |
| 10. Fluid applications | Vector and harmonic identities above; physical model from V |
| 11. Probability and averages | 19.1-19.2, 19.5-19.6; correlation interpretation from V |
| 12. Integral and learned operators | 10.5; 12.8; 15.5; 16.1-16.4; learned maps from F and S |

Read Chapters 1-8 in order. Chapter 9 adds discretization, Chapter 10 fluid applications, Chapter 11 statistics, and Chapter 12 operator maps. Teaching objects share one counter per chapter; equations and exercises have separate counters. Definitions have a left rule, results a frame, and examples a top rule. Proofs and derivations identify their target result. Exercises close sections; checked solutions are supplied in a separate instructor key.
