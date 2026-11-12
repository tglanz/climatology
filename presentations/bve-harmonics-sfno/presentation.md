# BVE, spherical harmonics, and SFNO

A lecture and study guide for the climatology prediction task

---

# The model and the learning question

The barotropic vorticity equation (BVE) describes one horizontal layer of fluid on a rotating sphere.

We assume constant density and zero horizontal divergence. The state has no vertical variation.

Chapter 1 develops the fluid equations. Chapter 2 defines the SHT and its Gaussian grid. Chapter 3 connects spectral dynamics to the learned map and its output head.

After study, you should be able to recover wind from vorticity, explain a spectral solver, and assess an SFNO output head.

Source: H, R1

---

# Chapter 1: coordinates and physical quantities

Let $a$ be the sphere radius, $\lambda$ the longitude, and $\phi$ the latitude. Angles use radians.

The eastward and northward velocities are $u$ and $v$, in $\mathrm{m\,s^{-1}}$. Relative vorticity $\zeta$ measures local rotation, in $\mathrm{s^{-1}}$.

A longitude step shrinks with latitude. The geometry enters every derivative.

$$
ds_\lambda=a\cos\phi\,d\lambda,\qquad ds_\phi=a\,d\phi,\qquad dA=a^2\cos\phi\,d\phi\,d\lambda
$$

Source: H, equations 3-8

---

# One streamfunction determines the wind

For a smooth nondivergent flow, a scalar streamfunction $\psi$ determines both velocity components.

Subscripts denote partial derivatives. These formulas give $\psi$ units of $\mathrm{m^2\,s^{-1}}$.

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

The Laplace-Beltrami operator $\Delta_S$ is the Laplacian on the sphere of radius $a$.

$$
\Delta_S\psi=\frac{1}{a^2\cos^2\phi}\psi_{\lambda\lambda}
+\frac{1}{a^2\cos\phi}(\cos\phi\,\psi_\phi)_\phi
$$

Thus a vorticity field determines the velocity after solving one Poisson equation.

Source: H, equations 4-7; R1

---

# The forced barotropic vorticity equation

Earth's rotation contributes planetary vorticity $f$. $\Omega$ is the rotation rate in $\mathrm{rad\,s^{-1}}$.

The sum $q$ is absolute vorticity. A parcel carries $q$ unchanged when forcing and dissipation vanish.

$$
q=\zeta+f,\qquad f=2\Omega\sin\phi
$$

$$
\partial_t\zeta+\frac{u}{a\cos\phi}q_\lambda+\frac{v}{a}q_\phi
=S-r\zeta-\nu(-\Delta_S)^p\zeta
$$

$S$ has units $\mathrm{s^{-2}}$. The drag rate $r$ has units $\mathrm{s^{-1}}$ and is nonnegative. The diffusion coefficient $\nu$ has units $\mathrm{m^{2p}\,s^{-1}}$ and is nonnegative. The integer $p$ is at least 1. Higher $p$ damps small scales more selectively.

Source: H, equations 8-12; R1, R2

---

# Stirring supplies random, correlated forcing

Isca adds random forcing in selected spectral modes and localizes it in space.

Its temporal recurrence keeps part of the previous forcing. The field $\eta$ is a new random spatial innovation in units of $\mathrm{s^{-2}}$.

$$
S_{n+1}=\rho S_n+\sqrt{1-\rho^2}\,\eta_n,\qquad
\rho=\exp(-\Delta t/\tau)
$$

$\Delta t$ is the numerical time step. The time scale $\tau$ controls how long the forcing remembers its past.

The forcing makes future trajectories random. A finite time average can also vary between realizations.

Source: R2, stirring.F90:130-160, 203-226

---

# Chapter 2: spherical harmonic transform

The spherical harmonic transform (SHT) converts a field on a sphere into coefficients of known basis functions.

We will separate the two coordinates: Fourier analysis along longitude, then Legendre projection in latitude.

Longitude runs around a latitude circle. Latitude runs from the south pole to the north pole. Keep this distinction in mind at every step.

The goal is to understand the transform, its inverse, and why a Gaussian grid makes the numerical projection accurate.

Source: T; C

---

# Spherical harmonics form a basis

Spherical harmonics represent a scalar field using patterns adapted to the sphere.

Degree $\ell$ controls spatial scale. Order $m$ counts longitude oscillations. Each degree admits $m$ from $-\ell$ to $\ell$.

$$
Y_\ell^m(\lambda,\phi)=N_{\ell m}P_\ell^m(\sin\phi)e^{im\lambda},
\qquad -\ell\le m\le\ell
$$

$P_\ell^m$ is an associated Legendre function, the latitude shape. $N_{\ell m}$ normalizes the basis under angular area, $d\Omega$.

$$
d\Omega=\cos\phi\,d\phi\,d\lambda,\qquad
\int_{S^2}Y_\ell^m\overline{Y_{\ell'}^{m'}}\,d\Omega
=\delta_{\ell\ell'}\delta_{mm'}
$$

The overbar means complex conjugation. The Kronecker symbol $\delta$ equals $1$ for equal indices and $0$ otherwise.

Source: T, B, appendix A

---

# Coefficients specify amplitude and phase

A scalar field is a sum of harmonics. Each complex coefficient sets a pattern's amplitude and longitude phase.

$$
\zeta(\lambda,\phi)=\sum_{\ell=0}^{\infty}\sum_{m=-\ell}^{\ell}
\widehat\zeta_{\ell m}Y_\ell^m(\lambda,\phi)
$$

Degree $0$ is constant. Degree $1$ contains patterns proportional to $\sin\phi$, $\cos\phi\cos\lambda$, and $\cos\phi\sin\lambda$.

Real fields combine conjugate modes. With the standard harmonic phase convention:

$$
\widehat\zeta_{\ell,-m}=(-1)^m\overline{\widehat\zeta_{\ell m}}
$$

Larger $\ell$ gives smaller spatial scales. Truncation keeps a finite range of degrees.

Source: T; B, appendix A

---

# Latitude, colatitude, and angular area

Let $\mu$ be the sine of latitude. Many references instead use colatitude $\vartheta$, measured from the north pole.

$$
\mu=\sin\phi=\cos\vartheta,\qquad
\vartheta=\frac{\pi}{2}-\phi,\qquad -1\le\mu\le1
$$

This change of variable absorbs the area factor. The sphere's angular integral becomes an ordinary integral on a rectangle.

$$
d\Omega=\cos\phi\,d\phi\,d\lambda=d\mu\,d\lambda,
\qquad \int_{S^2}g\,d\Omega=\int_{-1}^{1}\int_0^{2\pi}g(\lambda,\arcsin\mu)\,d\lambda\,d\mu
$$

Physical area adds $a^2$. We use angular area to normalize the harmonics, so a transform preserves the field's units.

Source: Y; H

---

# Basis normalization and Legendre functions

Let $P_\ell$ be the ordinary Legendre polynomial with $P_\ell(1)=1$. For nonnegative order, define the associated function with the Condon-Shortley phase.

$$
P_\ell^m(\mu)=(-1)^m(1-\mu^2)^{m/2}\frac{d^mP_\ell}{d\mu^m},
\qquad 0\le m\le\ell
$$

Our orthonormal convention fixes the scale of every coefficient.

$$
N_{\ell m}=\sqrt{\frac{2\ell+1}{4\pi}\frac{(\ell-m)!}{(\ell+m)!}},
\qquad Y_\ell^{-m}=(-1)^m\overline{Y_\ell^m}
$$

For $m=0$, the latitude basis is an ordinary Legendre polynomial. For nonzero order, its latitude shape changes with $m$.

Source: Y, equations 14.30.1 and 14.30.6

---

# SHT definition: analysis and synthesis

Let $g$ be a square-integrable scalar field. Analysis finds its inner products with the orthonormal harmonics.

$$
(\mathcal Sg)_{\ell m}=\widehat g_{\ell m}
=\int_{-1}^{1}\int_0^{2\pi}g(\lambda,\arcsin\mu)
\overline{Y_\ell^m(\lambda,\arcsin\mu)}\,d\lambda\,d\mu
$$

Synthesis rebuilds the field. A triangular cutoff $L$ keeps every order through degree $L$.

$$
(\mathcal S_L^{-1}\widehat g)(\lambda,\phi)
=\sum_{\ell=0}^{L}\sum_{m=-\ell}^{\ell}\widehat g_{\ell m}Y_\ell^m(\lambda,\phi)
$$

For a field bandlimited to $L$, synthesis recovers the field exactly. For a general field, it returns its orthogonal projection onto the retained modes.

Source: Y; C

---

# Step 1: Fourier analysis along longitude

Hold latitude fixed and travel around its circle. Longitude is periodic, so ordinary Fourier modes are the natural basis.

$$
G_m(\mu)=\frac{1}{2\pi}\int_0^{2\pi}
 g(\lambda,\arcsin\mu)e^{-im\lambda}\,d\lambda
$$

Let $N_\lambda$ count longitude columns. A discrete Fourier transform acts on each row; the FFT computes it efficiently.

$$
\lambda_k=\frac{2\pi k}{N_\lambda},\qquad
G_m(\mu_j)\approx\frac{1}{N_\lambda}\sum_{k=0}^{N_\lambda-1}g_{jk}e^{-im\lambda_k}
$$

The result still varies with latitude. Only the longitude coordinate has become an order index $m$.

Source: T, v0.7.4 RealSHT.forward; C

---

# Step 2: Legendre projection in latitude

Insert the separated harmonic into the SHT definition. The longitude integral is exactly the Fourier coefficient we just computed.

$$
\widehat g_{\ell m}=2\pi N_{\ell m}\int_{-1}^{1}G_m(\mu)P_\ell^m(\mu)\,d\mu,
\qquad 0\le m\le\ell
$$

For each fixed order $m$, project the remaining latitude dependence onto associated Legendre functions of degree $\ell$.

The factor $2\pi$ follows from our normalized Fourier coefficient. A library may distribute this factor differently; analysis and synthesis must use the same convention.

This is the separation: Fourier in longitude, Legendre in latitude. It is not a two-dimensional FFT on a flat rectangle.

Source: T; C; derivation from the SHT definition

---

# Gaussian quadrature: nodes and weights

Quadrature approximates an integral by a weighted sum. Let $N_\phi$ count latitude nodes. Gauss-Legendre nodes are roots of $P_{N_\phi}$.

$$
P_{N_\phi}(\mu_j)=0,\qquad
w_j=\frac{2}{(1-\mu_j^2)[P'_{N_\phi}(\mu_j)]^2},\qquad
\sum_{j=1}^{N_\phi}w_j=2
$$

With $N_\phi$ nodes, it integrates every polynomial of degree at most $2N_\phi-1$ exactly, in exact arithmetic.

$$
\int_{-1}^{1}p(\mu)\,d\mu
=\sum_{j=1}^{N_\phi}w_jp(\mu_j),\qquad \deg p\le2N_\phi-1
$$

For nonpolynomial integrands, the rule generally has an integration error.

Source: Q, Gauss quadrature and Gauss-Legendre formula

---

# Why Gauss quadrature reaches that degree

Take any polynomial $p$ of degree at most $2N_\phi-1$. Polynomial division gives a quotient $q$ and remainder $r$.

$$
p=P_{N_\phi}q+r,\qquad \deg q\le N_\phi-1,\qquad \deg r\le N_\phi-1
$$

Legendre orthogonality makes the integral of $P_{N_\phi}q$ vanish. At the chosen nodes, this product also vanishes pointwise.

$$
\int_{-1}^{1}p\,d\mu=\int_{-1}^{1}r\,d\mu
=\sum_j w_jr(\mu_j)=\sum_jw_jp(\mu_j)
$$

The weights integrate the interpolating remainder exactly. Choosing the roots removes the higher-degree part from both the integral and the sum.

Source: Q; polynomial division and Legendre orthogonality

---

# The Gaussian grid on the sphere

Convert the Gauss-Legendre nodes to latitude. Pair each row with equally spaced longitudes to form a full Gaussian grid.

$$
\phi_j=\arcsin\mu_j,\qquad
\lambda_k=\frac{2\pi k}{N_\lambda},\qquad g_{jk}=g(\lambda_k,\phi_j)
$$

The latitude rows are symmetric about the equator and exclude the poles. They are nonuniform in latitude and in its sine. They are not equal-area rows.

The name refers to Gauss's integration rule, not a Gaussian probability distribution. The node locations and weights are a matched pair.

A reduced Gaussian grid uses fewer longitudes near the poles. Here we use the full grid, with the same longitude count on every row.

Source: E; Q; R3

---

# The discrete SHT combines both rules

First apply the longitude FFT to each latitude row. Then contract each order with the weighted Legendre functions.

$$
g_{jk}\ \xrightarrow{\mathrm{FFT\ in}\ \lambda}\ G_m(\mu_j)
\ \xrightarrow{\mathrm{weighted\ Legendre\ in}\ \mu}\ \widehat g_{\ell m}
$$

$$
\widehat g_{\ell m}\approx2\pi N_{\ell m}
\sum_{j=1}^{N_\phi}w_jG_m(\mu_j)P_\ell^m(\mu_j),\qquad m\ge0
$$

For a real field, negative orders follow by conjugate symmetry. Inverse synthesis evaluates the Legendre sums at the latitude nodes, then applies an inverse longitude FFT.

No extra cosine weight belongs in this sum: the substitution $\mu=\sin\phi$ already absorbed the spherical area factor.

Source: T, v0.7.4 RealSHT and InverseRealSHT

---

# When the sampled transform is exact

Assume a scalar field is bandlimited to degree $L$. To distinguish longitude orders through $L$, use at least $2L+1$ columns.

For a fixed order, the latitude integrands are products of associated Legendre functions. The square-root factors combine into an ordinary polynomial.

$$
P_\ell^m(\mu)P_{\ell'}^m(\mu)
\text{ has degree at most }\ell+\ell'\le2L
$$

Gauss-Legendre quadrature therefore gives sufficient sampling bounds for an exact analysis-synthesis round trip.

$$
N_\lambda\ge2L+1,\qquad N_\phi\ge L+1
$$

Exactness assumes matching normalization and coordinates, and exact arithmetic. Unresolved structure aliases into the retained modes.

Source: C, Gaussian sampling; Q; derivation for a triangular scalar bandlimit

---

# Worked example: two Gaussian latitude rows

With two latitude nodes, the ordinary Legendre polynomial and its roots give the grid and weights.

$$
P_2(\mu)=\tfrac12(3\mu^2-1),\qquad
\mu_\pm=\pm\frac{1}{\sqrt3},\qquad w_\pm=1
$$

The latitudes are approximately $\pm35.264^\circ$. The rule integrates a quadratic exactly.

$$
\int_{-1}^{1}\mu^2\,d\mu=\frac23
=1\!\left(-\frac{1}{\sqrt3}\right)^2+1\!\left(\frac{1}{\sqrt3}\right)^2
$$

It fails for the fourth power: the integral is $2/5$, but the weighted sum is $2/9$. The degree limit is a real constraint.

Source: Q; direct calculation

---

# Worked example: transform a latitude pattern

Take the dimensionless field $g(\lambda,\phi)=\sin\phi=\mu$. Its longitude Fourier transform has only order zero.

$$
G_0(\mu)=\mu,\qquad G_m(\mu)=0\quad(m\ne0)
$$

Use the two Gaussian rows and at least three longitude columns. Since $P_1(\mu)=\mu$, the coefficient is

$$
\widehat g_{10}=2\pi\sqrt{\frac{3}{4\pi}}
\sum_{j=\pm}w_j\mu_j^2=\sqrt{\frac{4\pi}{3}},
\qquad \widehat g_{00}=0
$$

Synthesis gives $\widehat g_{10}Y_1^0=\mu$. Within the degree-one band, this reconstructs the original field exactly.

Source: Y; Q; direct calculation with the stated normalization

---

# Area means on the Gaussian grid

For a sampled scalar field, a global area mean uses longitude averaging followed by the Gaussian latitude weights.

$$
\langle g\rangle=\frac{1}{4\pi}\int_{S^2}g\,d\Omega
\approx\frac12\sum_jw_j\left(\frac{1}{N_\lambda}\sum_kg_{jk}\right)
$$

The weights sum to $2$, so a constant field is unchanged. Multiplying the Gaussian weights by another cosine changes the measure.

A zonal mean is different: it averages around one latitude circle and needs no latitude weights. Latitude weights enter global means and area-weighted errors.

The grid is therefore part of the numerical method. Array dimensions alone do not specify a valid transform or integral.

Source: E; T; R4, Gaussian coordinate contract

---

# Self-check: SHT and the Gaussian grid

1. At fixed latitude, which coordinate does the FFT vary? What index replaces it?

2. Why do the Gaussian weights need no extra factor of $\cos\phi$?

3. For a field bandlimited to $L=3$, how many Gaussian latitude rows and longitude columns suffice for an exact linear transform?

4. Why does the two-node rule integrate $\mu^3$ exactly but fail for $\mu^4$?

Write the two-stage transform before reading the answers. Use our normalization to check the factor $2\pi$.

Source: SHT chapter

---

# Answers: SHT and the Gaussian grid

1. The FFT varies longitude $\lambda$ around a fixed latitude circle. Its output is indexed by longitude order $m$ and still depends on latitude.

2. The change of variable gives $d\mu=\cos\phi\,d\phi$. The weights already approximate integration in $\mu$.

3. Four Gaussian latitude rows and seven longitude columns suffice: $N_\phi\ge L+1$ and $N_\lambda\ge2L+1$.

4. Two-node Gauss-Legendre quadrature is exact through degree three. Odd symmetry makes both the cubic integral and its sum zero. For the fourth power they give $2/5$ and $2/9$.

These are linear transform bounds. Projecting nonlinear products requires a finer grid, as we will see in the spectral solver.

Source: SHT chapter and worked quadrature example

---

# Chapter 3: spectral dynamics and SFNO

We now have a map between grid values and harmonic coefficients, with a numerical integration rule that respects the sphere.

The BVE solver uses this map to apply known differential operators and evaluate nonlinear products.

SFNO uses the same representation to learn transformations of hidden feature channels.

We will distinguish the physical time step, the learned spectral layer, and the final representation of the mean-wind target.

Source: H; B; R1; R4

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

For $\ell=0$, the eigenvalue is zero. A smooth flow on the closed sphere has zero area-mean relative vorticity. Set the constant $\psi$ coefficient to zero as a gauge. It cannot affect wind.

Source: H, spectral representation; R1; T

---

# Worked example: a zonal wind

Take an eastward wind with maximum speed $U$ at the equator.

$$
u=U\cos\phi,\qquad v=0
$$

The streamfunction formula gives $\psi$. Applying the degree-1 eigenvalue gives $\zeta$.

$$
\psi=-aU\sin\phi,\qquad
\zeta=-\frac{2}{a^2}\psi=\frac{2U}{a}\sin\phi
$$

This is an $\ell=1$, $m=0$ mode. The signs and units agree: $\psi$ has units $\mathrm{m^2\,s^{-1}}$ and $\zeta$ has units $\mathrm{s^{-1}}$.

Recovering $\psi$ from $\zeta$ returns the original wind. No longitude dependence enters.

Source: streamfunction, Laplacian, and spectral inversion sections

---

# A spectral BVE step still uses the grid

The solver stores retained vorticity coefficients. It inverts the Laplacian to recover $\psi$, then computes wind and derivatives.

The advection term multiplies fields. The solver evaluates these products on a spatial grid and transforms the tendency back to coefficients.

$$
J(\psi,q)=\frac{\psi_\lambda q_\phi-\psi_\phi q_\lambda}
{a^2\cos\phi},\qquad
\partial_t\zeta=-J(\psi,q)+S+D
$$

Here $D$ groups the drag and diffusion terms from the forced BVE equation. A time integrator advances the coefficients.

Products couple modes. For example, nonzonal patterns can create a zonal contribution:

$$
\cos^2\lambda=\tfrac12+\tfrac12\cos(2\lambda)
$$

Source: H, equations 10-12; R1

---

# Truncation, sampling, and quadrature

Triangular cutoff $L$ keeps degrees 0 through $L$ and all their orders. This gives $(L+1)^2$ scalar modes before real-field symmetry.

Quadratic products reach higher modes. A finer grid prevents those modes from folding into the retained band when projecting products back.

$$
N_\lambda\ge3L+1,\qquad
N_\phi\ge\left\lceil\frac{3L+1}{2}\right\rceil
$$

These are standard quadratic dealiasing bounds for this Gaussian spectral setup. The repository rounds latitude count to even and longitude count for efficient Fourier transforms. T21 gives 32 by 64 points.

Gaussian latitude nodes are nonuniform. Their quadrature weights approximate area integrals in $\sin\phi$. Uniform-latitude cosine weights are a different rule.

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

On a uniform longitude grid, an arithmetic mean exactly selects order $m=0$.

A spectral output head changes how the profile is represented. It gains no automatic exactness over that discrete mean.

Source: harmonic expansion and longitude orthogonality; R4, ZonalMeanWrapper

---

# The target is a finite climatology

This project's default target is the time mean of the zonal-mean eastward wind. $M$ is the number of snapshots in the chosen averaging interval.

$$
y(\phi)=\frac{1}{M}\sum_{j=1}^{M}[u(t_j)](\phi)
$$

The input contains $K$ consecutive vorticity snapshots, with $K$ much smaller than $M$.

$$
X=(\zeta_{t_1},\ldots,\zeta_{t_K}),\qquad
F_\theta(X)\approx y
$$

$\theta$ denotes learned parameters. A short random context need not identify the target uniquely. Finite target averages retain sampling uncertainty.

Predicting this mean profile does not identify the full probability distribution of the flow.

Source: R4; R5, compute_climatology and compute_time_mean_zonal_mean; R6, default.toml

---

# Self-check A

1. Why does $\psi$ have units $\mathrm{m^2\,s^{-1}}$?

2. Why can the $\ell=0$ vorticity coefficient not be inverted? What freedom remains in $\psi$?

3. A vorticity field contains only $\ell=2$, $m=1$ and its real-field partner. What are its streamfunction and zonal mean?

Try the questions before reading Answers A.

Source: streamfunction, spectral inversion, and zonal mean sections

---

# One SFNO spectral layer

A Spherical Fourier Neural Operator (SFNO) learns transformations of fields on a sphere.

Its spherical harmonic transform, $\mathcal S$, converts hidden feature channels $h^{(k)}$ into coefficients. A learned channel matrix $R_{k,\ell}$ mixes them at each degree $\ell$.

$$
h^{(k+1)}
=\sigma\!\left(W_kh^{(k)}
+\mathcal S^{-1}\!\left(R_{k,\ell}\,\mathcal S h^{(k)}\right)
+b_k\right)
$$

$k$ indexes layers. $W_k$ mixes channels at each grid point, $b_k$ is a bias, and $\sigma$ is a pointwise nonlinear function.

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

Source: B; R7; R8, input coordinates and architecture

---

# The current network predicts a profile

The default uses $K=10$ vorticity snapshots. A T85 Isca run supplies an $H=128$, $W=256$ Gaussian grid; the model reads its physical coordinates. Each time slice becomes an input channel.

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

Source: R4, model factory and wrapper; R6, default.toml

---

# The transform must match the coordinates

A spherical transform assumes specific latitude nodes, row order, normalization, and mode limits. Grid shape alone does not specify them.

Isca uses Gaussian latitudes. The current model explicitly selects Gauss-Legendre transforms and reverses south-to-north input rows for the transform, then restores the original row order.

The model uses the physical coordinates for positional features. Preprocessing, area-weighted errors, checkpoints, and plots share the same coordinate contract.

A useful check samples one known harmonic on the data grid. Transforming and reconstructing it should preserve its mode, amplitude, and physical orientation.

Source: R4, GaussianSphericalConv and CoordinateEmbedding; docs/grids.md; T

---

# Three output representations

The current head projects to a full field and averages longitude. This leaves the SFNO trunk free to use all longitude modes.

A direct profile head predicts $H$ latitude values. A coefficient head predicts only $R$ retained basis coefficients.

$$
\widehat y(\phi)=\sum_{\ell=0}^{R-1}c_\ell P_\ell(\sin\phi)
$$

Here $P_\ell$ is an ordinary Legendre polynomial and $c_\ell$ is a learned output coefficient. This scalar expansion compresses the profile.

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

The constant streamfunction mode changes no wind, so the sum starts at $\ell=1$.

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

4. Why can nonzonal input modes matter when the output has only $m=0$?

5. What does an SFNO learn that a spectral BVE solver already knows?

6. Why is a coefficient head not automatically more exact or more invariant than the current head?

Try the questions before reading Answers B.

Source: spectral stepping, zonal mean, SFNO, and output head sections

---

# Answers A

1. Wind is a streamfunction derivative divided by radius. Angles are dimensionless. Thus $\psi/a$ has units $\mathrm{m\,s^{-1}}$, so $\psi$ has units $\mathrm{m^2\,s^{-1}}$.

2. The constant harmonic has zero Laplacian. Valid closed-sphere relative vorticity has zero global integral. Adding a constant to $\psi$ changes no wind, so choose its value as a gauge.

3. The eigenvalue is $-6/a^2$. Thus $\psi=-a^2\zeta/6$. Both zonal means vanish because $m=1$ and $m=-1$ average to zero.

Source: streamfunction, spectral inversion, and zonal mean sections

---

# Answers B

4. Nonlinear products couple modes. Opposite longitude orders can produce $m=0$. The mean flow can therefore depend on nonzonal structure.

5. SFNO learns the input-to-output transformation through spectral channel weights and nonlinear layers. A BVE solver applies specified tendencies and a time integrator.

6. The discrete longitude mean already selects $m=0$ exactly. A coefficient cutoff introduces truncation error. Input invariance also depends on the trunk and physical symmetries.

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

# References: SHT and Gaussian quadrature

Y: NIST Digital Library of Mathematical Functions, section 14.30. Harmonic normalization, conjugate symmetry, and orthogonality.

https://dlmf.nist.gov/14.30

Q: NIST DLMF, section 3.5(v). Gaussian quadrature, polynomial exactness, and Gauss-Legendre nodes and weights.

https://dlmf.nist.gov/3.5

C: Nathanael Schaeffer. Efficient spherical harmonic transforms aimed at pseudospectral numerical simulations (2013). SHTns documentation and Gaussian sampling.

https://nschaeff.bitbucket.io/shtns/spat.html

Source: primary mathematical and numerical sources

---

# References: grid and transform implementation

E: ECMWF. Gaussian grids. Full and reduced longitude layouts and Gaussian latitude placement.

https://confluence.ecmwf.int/spaces/FCST/pages/49415103/Gaussian%2Bgrids

T: NVIDIA torch-harmonics, version 0.7.4. RealSHT and InverseRealSHT: longitude FFT, weighted Legendre contraction, grid selection, and normalization.

https://github.com/NVIDIA/torch-harmonics/blob/v0.7.4/torch_harmonics/sht.py

The derivations and worked examples use the orthonormal convention stated in this lecture. Check conventions before comparing coefficients from another library.

Source: primary implementation sources inspected on 2026-11-11

---

# References: simulator

R1: Isca, src/atmos_spectral_barotropic/barotropic_dynamics.F90. The BVE dynamics and spectral setup.

R2: Isca, src/atmos_spectral_barotropic/stirring.F90. Spectral forcing, spatial localization, and temporal recurrence.

Isca pin: a290bc376d84d0ee83adbb80eb374b9f629c3534

https://github.com/ExeClim/Isca

R3: This repository, sim/barotropic_stirring.py. Grid construction and simulation settings.

Repository pin: 185e086fed79420544a1f06485f7fedf425ec100

https://github.com/tglanz/climatology

Source: pinned source files inspected on 2026-11-11

---

# References: machine learning

R4: ml/src/ml/training/model.py. Model factory and longitude-mean wrapper.

R5: ml/src/ml/data/climatology.py and diagnostics/convergence.py. Target computation. R6: ml/configs/default.toml. Input variables and default settings.

These refer to repository pin 185e086fed79420544a1f06485f7fedf425ec100.

R7: neuralop/layers/spherical_convolution.py. Spherical transforms and learned filters. R8: neuralop/models/fno.py. Input coordinates and full architecture.

NeuralOperator pin: 98cd305099f4a2b232ed85773984f3e5991f9b1a

https://github.com/NeuralOperator/neuraloperator

Source: pinned source files inspected on 2026-11-11
