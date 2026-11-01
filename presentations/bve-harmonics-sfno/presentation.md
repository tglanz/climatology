# BVE, spherical harmonics, and SFNO

A study guide for the climatology prediction task

---

# The model and the learning question

The barotropic vorticity equation (BVE) describes one horizontal layer of fluid on a rotating sphere.

We assume constant density and zero horizontal divergence. The state has no vertical variation.

This guide connects the velocity field, its harmonic coefficients, and a learned map from short trajectories to mean wind.

After study, you should be able to recover wind from vorticity, explain a spectral solver, and assess an SFNO output head.

Source: H, R1

---

# Coordinates and physical quantities

Let a be the sphere radius, lambda the longitude, and phi the latitude. Angles use radians.

The eastward and northward velocities are u and v, in m/s. Relative vorticity zeta measures local rotation, in 1/s.

A longitude step shrinks with latitude. The geometry enters every derivative.

$$
ds_\lambda=a\cos\phi\,d\lambda,\qquad ds_\phi=a\,d\phi,\qquad dA=a^2\cos\phi\,d\phi\,d\lambda
$$

Source: H, equations 3-8

---

# One streamfunction determines the wind

For a smooth nondivergent flow, a scalar streamfunction psi determines both velocity components.

Subscripts denote partial derivatives. These formulas give psi units of m^2/s.

$$
u=-\frac{1}{a}\psi_\phi,\qquad v=\frac{1}{a\cos\phi}\psi_\lambda
$$

The spherical divergence vanishes because the mixed derivatives cancel.

$$
\nabla_S\cdot\mathbf u=\frac{u_\lambda+(v\cos\phi)_\phi}{a\cos\phi}=0
$$

Source: H, equations 3, 6, 7

---

# Vorticity is the spherical Laplacian

Taking the radial curl of the wind gives relative vorticity.

$$
\zeta=\frac{v_\lambda-(u\cos\phi)_\phi}{a\cos\phi}=\Delta_S\psi
$$

The Laplace-Beltrami operator Delta_S is the Laplacian on the radius-a sphere.

$$
\Delta_S\psi=\frac{1}{a^2\cos^2\phi}\psi_{\lambda\lambda}
+\frac{1}{a^2\cos\phi}(\cos\phi\,\psi_\phi)_\phi
$$

Thus a vorticity field determines the velocity after solving one Poisson equation.

Source: H, equations 4-7; R1

---

# The forced barotropic vorticity equation

Earth's rotation contributes planetary vorticity f. Omega is the rotation rate in radians/s.

The sum q is absolute vorticity. A parcel carries q unchanged when forcing and dissipation vanish.

$$
q=\zeta+f,\qquad f=2\Omega\sin\phi
$$

$$
\partial_t\zeta+\frac{u}{a\cos\phi}q_\lambda+\frac{v}{a}q_\phi
=S-r\zeta-\nu(-\Delta_S)^p\zeta
$$

S has units 1/s^2. The drag rate r has units 1/s and is nonnegative. The diffusion coefficient nu has units m^(2p)/s and is nonnegative. The integer p is at least 1. Higher p damps small scales more selectively.

Source: H, equations 8-12; R1, R2

---

# Stirring supplies random, correlated forcing

Isca adds random forcing in selected spectral modes and localizes it in space.

Its temporal recurrence keeps part of the previous forcing. The field eta is a new random spatial innovation in units of 1/s^2.

$$
S_{n+1}=\rho S_n+\sqrt{1-\rho^2}\,\eta_n,\qquad
\rho=\exp(-\Delta t/\tau)
$$

Delta t is the numerical time step. The time scale tau controls how long the forcing remembers its past.

The forcing makes future trajectories random. A finite time average can also vary between realizations.

Source: R2, stirring.F90:130-160, 203-226

---

# Spherical harmonics form a basis

Spherical harmonics represent a scalar field using patterns adapted to the sphere.

Degree ell controls spatial scale. Order m counts longitude oscillations. Each degree admits m from -ell to ell.

$$
Y_\ell^m(\lambda,\phi)=N_{\ell m}P_\ell^m(\sin\phi)e^{im\lambda},
\qquad -\ell\le m\le\ell
$$

P is an associated Legendre function, the latitude shape. N normalizes the basis under angular area, dOmega.

$$
d\Omega=\cos\phi\,d\phi\,d\lambda,\qquad
\int_{S^2}Y_\ell^m\overline{Y_{\ell'}^{m'}}\,d\Omega
=\delta_{\ell\ell'}\delta_{mm'}
$$

The overbar means complex conjugation. The delta is 1 for equal indices and 0 otherwise.

Source: T, B, appendix A

---

# Coefficients specify amplitude and phase

A scalar field is a sum of harmonics. Each complex coefficient sets a pattern's amplitude and longitude phase.

$$
\zeta(\lambda,\phi)=\sum_{\ell=0}^{\infty}\sum_{m=-\ell}^{\ell}
\widehat\zeta_{\ell m}Y_\ell^m(\lambda,\phi)
$$

Degree 0 is constant. Degree 1 contains patterns proportional to sin(phi), cos(phi) cos(lambda), and cos(phi) sin(lambda).

Real fields combine conjugate modes. With the standard harmonic phase convention:

$$
\widehat\zeta_{\ell,-m}=(-1)^m\overline{\widehat\zeta_{\ell m}}
$$

Larger ell gives smaller spatial scales. Truncation keeps a finite range of degrees.

Source: T; B, appendix A

---

# Projection computes the coefficients

Orthonormality makes each coefficient an inner product of the field with its basis pattern.

$$
\widehat\zeta_{\ell m}=\int_{S^2}
\zeta(\lambda,\phi)\overline{Y_\ell^m(\lambda,\phi)}\,d\Omega
$$

A sampled transform approximates the integral with a weighted sum over latitude rows j and longitude columns k.

$$
\widehat\zeta_{\ell m}\approx
\sum_{j,k}w_j\,\Delta\lambda\,
\zeta_{jk}\overline{Y_\ell^m(\lambda_k,\phi_j)}
$$

The weights w_j integrate in sin(phi), and Delta lambda is the uniform longitude spacing. The grid determines the weights.

A spherical harmonic transform performs this projection using a longitude Fourier transform and a latitude Legendre transform.

Source: T; B, appendix A

---

# The Laplacian becomes a multiplier

Each harmonic is an eigenfunction of the spherical Laplacian. Differentiation becomes multiplication of coefficients.

$$
\Delta_SY_\ell^m=-\frac{\ell(\ell+1)}{a^2}Y_\ell^m
$$

The Poisson solve is therefore a division for every nonconstant mode.

$$
\widehat\psi_{\ell m}
=-\frac{a^2}{\ell(\ell+1)}\widehat\zeta_{\ell m},
\qquad \ell\ge1
$$

For ell=0, the eigenvalue is zero. A smooth flow on the closed sphere has zero area-mean relative vorticity. Set the constant psi coefficient to zero as a gauge. It cannot affect wind.

Source: H, spectral representation; R1; T

---

# Worked example: a zonal wind

Take an eastward wind with maximum speed U at the equator.

$$
u=U\cos\phi,\qquad v=0
$$

The streamfunction formula gives psi. Applying the degree-1 eigenvalue gives zeta.

$$
\psi=-aU\sin\phi,\qquad
\zeta=-\frac{2}{a^2}\psi=\frac{2U}{a}\sin\phi
$$

This is an ell=1, m=0 mode. The signs and units agree: psi has units m^2/s and zeta has units 1/s.

Recovering psi from zeta returns the original wind. No longitude dependence enters.

Source: streamfunction, Laplacian, and spectral inversion sections

---

# A spectral BVE step still uses the grid

The solver stores retained vorticity coefficients. It inverts the Laplacian to recover psi, then computes wind and derivatives.

The advection term multiplies fields. The solver evaluates these products on a spatial grid and transforms the tendency back to coefficients.

$$
J(\psi,q)=\frac{\psi_\lambda q_\phi-\psi_\phi q_\lambda}
{a^2\cos\phi},\qquad
\partial_t\zeta=-J(\psi,q)+S+D
$$

Here D groups the drag and diffusion terms from slide 6. A time integrator advances the coefficients.

Products couple modes. For example, nonzonal patterns can create a zonal contribution:

$$
\cos^2\lambda=\tfrac12+\tfrac12\cos(2\lambda)
$$

Source: H, equations 10-12; R1

---

# Truncation, sampling, and quadrature

Triangular cutoff L keeps degrees 0 through L and all their orders. This gives (L+1)^2 scalar modes before real-field symmetry.

Quadratic products reach higher modes. A finer grid prevents those modes from folding into the retained band when projecting products back.

$$
N_\lambda\ge3L+1,\qquad
N_\phi\ge\left\lceil\frac{3L+1}{2}\right\rceil
$$

These are standard quadratic dealiasing bounds for this Gaussian spectral setup. The repository rounds latitude count to even and longitude count for efficient Fourier transforms. T21 gives 32 by 64 points.

Gaussian latitude nodes are nonuniform. Their quadrature weights approximate area integrals in sin(phi). Uniform-latitude cosine weights are a different rule.

Source: R3, barotropic_stirring.py:20-27; H; T

---

# The zonal mean selects order zero

The zonal mean averages a field around each latitude circle.

$$
[g](\phi)=\frac{1}{2\pi}\int_0^{2\pi}g(\lambda,\phi)\,d\lambda
$$

Every nonzero longitude mode integrates to zero.

$$
\frac{1}{2\pi}\int_0^{2\pi}e^{im\lambda}\,d\lambda
=\begin{cases}1&m=0\\0&m\ne0\end{cases},
\qquad
[g](\phi)=\sum_\ell\widehat g_{\ell0}Y_\ell^0(\phi)
$$

On a uniform longitude grid, the arithmetic mean exactly selects the discrete Fourier order m=0.

A spectral output head changes how the profile is represented. It gains no automatic exactness over that discrete mean.

Source: derivation from slides 8-9; R4, model.py:14-15

---

# The target is a finite climatology

This project's target is the time mean of the zonal-mean eastward wind. M is the number of snapshots in the chosen averaging interval.

$$
y(\phi)=\frac{1}{M}\sum_{j=1}^{M}[u(t_j)](\phi)
$$

The input contains K consecutive vorticity snapshots, with K much smaller than M.

$$
X=(\zeta_{t_1},\ldots,\zeta_{t_K}),\qquad
F_\theta(X)\approx y
$$

Theta denotes learned parameters. A short random context need not identify the target uniquely. Finite target averages retain sampling uncertainty.

Predicting this mean profile does not identify the full probability distribution of the flow.

Source: R4; R5, climatology.py:72-85; R6, default.toml

---

# Self-check A

1. Why does psi have units m^2/s?

2. Why can the ell=0 vorticity coefficient not be inverted? What freedom remains in psi?

3. A vorticity field contains only ell=2, m=1 and its real-field partner. What are its streamfunction and zonal mean?

Try the questions before reading Answers A.

Source: streamfunction, spectral inversion, and zonal mean sections

---

# One SFNO spectral layer

A Spherical Fourier Neural Operator (SFNO) learns transformations of fields on a sphere.

Its spherical harmonic transform, S, converts hidden feature channels h into coefficients. A learned channel matrix R_ell mixes them at each degree.

$$
h^{(k+1)}
=\sigma\!\left(W_kh^{(k)}
+\mathcal S^{-1}\!\left(R_{k,\ell}\,\mathcal S h^{(k)}\right)
+b_k\right)
$$

k indexes layers. W mixes channels at each grid point, b is a bias, and sigma is a pointwise nonlinear function.

The displayed form is the basic layer. Implementations can add further pointwise channel mixing and scaling.

Source: B, sections 3-4; R7, spherical_convolution.py

---

# Known dynamics and learned filters

The spectral BVE solver uses known physical rules. Its Laplacian multiplier and advection determine a time derivative.

SFNO uses trainable channel matrices. Training chooses their entries to fit the requested input-to-output map.

$$
\text{BVE inversion: }\ -\frac{a^2}{\ell(\ell+1)}
\qquad\qquad
\text{SFNO filter: }\ R_{k,\ell}
$$

Both use a harmonic basis. An SFNO layer is not a prescribed BVE time step and need not conserve BVE invariants.

A degree-only filter supports rotation equivariance for scalar fields under suitable layer assumptions. Coordinates, nonlinear choices, and forcing can restrict the full model's symmetry.

Source: B; R7; R8, fno.py:179, 238-244

---

# The current network predicts a profile

The default configuration uses K=10 vorticity snapshots on an H=128, W=256 grid. Each time slice becomes an input channel.

The factory builds an SFNO or FNO that returns a spatial field. The wrapper then averages its output over longitude.

$$
\mathbb R^{K\times H\times W}
\quad\xrightarrow{\text{SFNO}}\quad
\mathbb R^{1\times H\times W}
\quad\xrightarrow{\text{longitude mean}}\quad
\mathbb R^{1\times H}
$$

A batch adds a leading sample dimension. The output represents the finite climatology defined earlier, not the next vorticity snapshot.

The default selects SFNO. The same output wrapper currently applies to both architectures.

Source: R4, model.py:9-46; R6, default.toml

---

# The transform must match the coordinates

A spherical transform assumes specific latitude nodes, row order, normalization, and mode limits.

Isca uses Gaussian latitudes. The pinned SphericalConv implementation defaults to an equiangular grid, while the current factory does not override that default.

Selecting the correct transform grid and row order is a correctness requirement. The same coordinate contract must reach preprocessing, loss weights, checkpoints, and plots.

A useful check samples one known harmonic on the data grid. Transforming and reconstructing it should preserve its mode and physical orientation.

Source: R1; R3; R4; R7, spherical_convolution.py:292, 324; T

---

# Three output representations

The current head projects to a full field and averages longitude. This leaves the SFNO trunk free to use all longitude modes.

A direct profile head predicts H latitude values. A coefficient head predicts only R retained basis coefficients.

$$
\widehat y(\phi)=\sum_{\ell=0}^{R-1}c_\ell P_\ell(\sin\phi)
$$

Here P_ell is an ordinary Legendre polynomial and c_ell is a learned output coefficient. This scalar expansion compresses the profile.

The cutoff controls approximation error and output size. Removing nonzero longitude modes throughout the trunk could discard information that helps predict the zonal target.

Source: R4; proposed experiment; spectral stepping and zonal mean sections

---

# A streamfunction head respects wind geometry

The target is a tangent velocity component. A proposed head predicts a smooth axisymmetric mean streamfunction, then derives its wind.

$$
\widehat\psi_0(\phi)=\sum_{\ell=1}^{R}c_\ell P_\ell(\sin\phi)
$$

$$
\widehat u_0(\phi)
=-\frac{\cos\phi}{a}\sum_{\ell=1}^{R}c_\ell P'_\ell(\sin\phi)
$$

The prime differentiates the polynomial's argument. The cosine factor makes this smooth axisymmetric wind vanish at each pole.

The constant streamfunction mode changes no wind, so the sum starts at ell=1.

Source: streamfunction derivation; T, vector harmonic transforms

---

# A controlled head experiment

Compare the current head, a direct profile head, and coefficient heads using the same data, splits, normalization, and loss.

First project true target profiles onto each basis. This measures truncation error before any model learns.

Then report prediction error, jet position, runtime, memory, and parameter count. Use several seeds and the same held-out forcing regimes.

Include a parameter-only baseline. A better head should improve a stated tradeoff, not merely add capacity.

Test longitude shifts explicitly. Order-zero output alone does not guarantee invariance to shifts of the input. The current coordinate embedding and localized forcing need attention.

Source: proposed experiment; R4; R6; R8

---

# Self-check B

4. Why can nonzonal input modes matter when the output has only m=0?

5. What does an SFNO learn that a spectral BVE solver already knows?

6. Why is a coefficient head not automatically more exact or more invariant than the current head?

Try the questions before reading Answers B.

Source: spectral stepping, zonal mean, SFNO, and output head sections

---

# Answers A

1. Wind is a streamfunction derivative divided by radius. Angles are dimensionless. Thus psi/a has units m/s, so psi has units m^2/s.

2. The constant harmonic has zero Laplacian. Valid closed-sphere relative vorticity has zero global integral. Adding a constant to psi changes no wind, so choose its value as a gauge.

3. The eigenvalue is -6/a^2. Thus psi=-a^2 zeta/6. Both zonal means vanish because m=1 and m=-1 average to zero.

Source: streamfunction, spectral inversion, and zonal mean sections

---

# Answers B

4. Nonlinear products couple modes. Opposite longitude orders can produce m=0. The mean flow can therefore depend on nonzonal structure.

5. SFNO learns the input-to-output transformation through spectral channel weights and nonlinear layers. A BVE solver applies specified tendencies and a time integrator.

6. The discrete longitude mean already selects m=0 exactly. A coefficient cutoff introduces truncation error. Input invariance also depends on the trunk and physical symmetries.

Review again by deriving the wind example without notes. Retry any missed question, then test it with a changed mode or cutoff.

Source: worked wind example, spectral stepping, SFNO, and output heads

---

# References: theory

H: Isaac Held. The barotropic vorticity equation. GFDL lecture notes. Geometry, streamfunction, spectral inversion, and numerical stepping.

https://www.gfdl.noaa.gov/wp-content/uploads/files/user_files/pjp/barotropic.pdf

B: Bonev et al. Spherical Fourier Neural Operators: Learning Stable Dynamics on the Sphere. ICML 2023. Sections 3-4 and appendix A.

https://proceedings.mlr.press/v202/bonev23a.html

T: NVIDIA. torch-harmonics. Scalar and vector harmonic transforms, Legendre functions, and quadrature. This project pins version 0.7.4.

https://github.com/NVIDIA/torch-harmonics

Source: primary sources

---

# References: simulator

R1: Isca, src/atmos_spectral_barotropic/barotropic_dynamics.F90. The BVE dynamics and spectral setup.

R2: Isca, src/atmos_spectral_barotropic/stirring.F90. Spectral forcing, spatial localization, and temporal recurrence.

Isca pin: a290bc376d84d0ee83adbb80eb374b9f629c3534

https://github.com/ExeClim/Isca

R3: This repository, sim/barotropic_stirring.py. Grid construction and simulation settings.

Repository pin: 51782c6a1b5fff2b40a981945cd7e05d70ae0321

https://github.com/tglanz/climatology

Source: pinned source files inspected on 2026-11-01

---

# References: machine learning

R4: ml/src/ml/training/model.py. Model factory and longitude-mean wrapper.

R5: ml/src/ml/data/climatology.py. Target computation. R6: ml/configs/default.toml. Input variables and default settings.

These refer to repository pin 51782c6a1b5fff2b40a981945cd7e05d70ae0321.

R7: neuralop/layers/spherical_convolution.py. Spherical transforms and learned filters. R8: neuralop/models/fno.py. Input coordinates and full architecture.

NeuralOperator pin: 98cd305099f4a2b232ed85773984f3e5991f9b1a

https://github.com/NeuralOperator/neuraloperator

Source: pinned source files inspected on 2026-11-01
