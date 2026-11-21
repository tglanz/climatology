# Spectral discretization, quadrature, and stability {#ch-numerics}

## Projection and the method of weighted residuals

**Result and motivation.** A spectral method approximates a field in a finite basis and imposes equations on its coefficients. Spatial truncation and time integration introduce different errors. Sources: [@ArfkenWeber2005, Sections 10.4, 12.3, 14.6, 17.8]; numerical bounds below are derived for the stated finite spaces.

For an evolution equation $u_t=\mathcal Lu+\mathcal N(u)+f$, let $\mathcal L$ be a linear spatial operator, $\mathcal N$ a nonlinear term, and $f$ forcing. Choose orthonormal basis functions $e_1,\ldots,e_K$ satisfying the spatial conditions, and approximate $u_K=\sum_{j=1}^Ka_j(t)e_j$. The residual is $r_K=\partial_tu_K-\mathcal Lu_K-\mathcal N(u_K)-f$. Galerkin projection sets $\langle r_K,e_i\rangle=0$:

$$
a_i'=\sum_jL_{ij}a_j+\langle\mathcal N(u_K),e_i\rangle+f_i,
\quad L_{ij}=\langle\mathcal Le_j,e_i\rangle,
\quad f_i=\langle f,e_i\rangle.
\tag{9.1}
$$

If $\mathcal Le_j=\lambda_je_j$, $L_{ij}=\lambda_j\delta_{ij}$. A nonorthonormal basis instead gives a mass matrix $M_{ij}=\langle e_j,e_i\rangle$ multiplying $a_j'$. Collocation requires the PDE residual to vanish at selected nodes. A pseudospectral method evaluates products at grid points and transforms them back; with sufficiently accurate quadrature this reproduces Galerkin projection for those products.

Three separate approximations are present: truncating the function space, approximating its integrals, and integrating its coefficient ODEs in time. Increasing the grid alone does not increase the retained degree; decreasing the time step does not remove spatial aliasing.

## Gauss-Legendre quadrature and a spherical grid

**Result and motivation.** Gaussian quadrature integrates polynomials up to degree $2n-1$ using $n$ carefully chosen latitude nodes. It accounts for spherical area through $\mu=\sin\varphi$. Sources: Legendre orthogonality [@ArfkenWeber2005, Section 12.3]; explicit quadrature rule [@NISTDLMFQuadrature].

For $n\ge1$, let $\mu_i$ be the $n$ distinct roots of $P_n$ in $(-1,1)$. Define weights $w_i$ by

$$
\int_{-1}^1p(\mu)d\mu=\sum_{i=1}^nw_ip(\mu_i)
\quad (\deg p\le2n-1),\qquad
w_i=\frac{2}{(1-\mu_i^2)[P_n'(\mu_i)]^2},\quad \sum_iw_i=2.
\tag{9.2}
$$

Here $\deg p$ is polynomial degree. To prove the exactness, divide any polynomial of degree at most $2n-1$ as $p=P_ns+r$, with $s,r$ of degree at most $n-1$. Orthogonality gives $\int P_ns=0$, and $p(\mu_i)=r(\mu_i)$. Integrating the degree-$(n-1)$ Lagrange interpolant of $r$ exactly therefore integrates $p$. The Lagrange function that is one at $\mu_i$ and zero at the other nodes is $\ell_i(\mu)=P_n(\mu)/[(\mu-\mu_i)P_n'(\mu_i)]$; hence $w_i=\int\ell_i$. Evaluating this integral with the Legendre recurrence yields the explicit weight formula in (9.2), specified by the NIST Gauss-Legendre rule. This argument explains the extra exact degrees without assuming uniform latitude spacing.

A full Gaussian grid combines latitudes $\varphi_i=\arcsin\mu_i$ with $M$ equally spaced longitudes $\lambda_j=2\pi j/M$. No latitude node is at a pole. Then

$$
\int_{S^2}f\,d\Omega\approx\frac{2\pi}{M}\sum_{i,j}w_if_{ij},
\qquad \langle f\rangle_A\approx\frac1{2M}\sum_{i,j}w_if_{ij}.
\tag{9.3}
$$

For a zonal profile the normalized latitude weights are $w_i/2$. Multiplying by another $\cos\varphi_i$ would count the area Jacobian twice. With $n=2$, nodes $\pm1/\sqrt3$ and weights one give the exact mean $1/3$ for $\mu^2$, but $1/9$ for $\mu^4$ instead of $1/5$; degree four exceeds the exactness guarantee.

## Exact harmonic recovery and nonlinear aliasing

**Result and motivation.** Recovering a degree-$L$ field needs fewer nodes than exactly projecting a quadratic product back to that degree. Dealiasing addresses this second requirement. Sources: [@ArfkenWeber2005, Sections 12.5-12.6, 14.6]; the sufficient spherical bounds follow below.

For a scalar field bandlimited to degree $L$, longitude analysis forms $F_m(\mu_i)=M^{-1}\sum_jf_{ij}e^{-im\lambda_j}$. For $m\ge0$, spherical analysis then uses

$$
f_\ell^m=2\pi N_{\ell m}\sum_iw_iF_m(\mu_i)P_\ell^m(\mu_i),
\qquad n\ge L+1,\quad M\ge2L+1.
\tag{9.4}
$$

These bounds make (9.4) exact in exact arithmetic for the stated bandlimited field. Longitude orthogonality eliminates different orders without aliasing. For the same order, the product $P_\ell^mP_j^m$ is $(1-\mu^2)^m$ times two polynomial derivatives, with total degree at most $\ell+j\le2L$. Gaussian quadrature therefore integrates it exactly. Individual odd-order functions need not be polynomials; their same-order products are.

The product of two degree-$L$ scalar fields can contain degree $2L$. To compute its coefficients only through degree $L$, the integrand contains three harmonics. A sufficient grid for exact projection is

$$
M>3L,\qquad 2n-1\ge3L.
\tag{9.5}
$$

The largest possible longitude frequency in this triple product is $3L$, so the strict inequality prevents a nonzero multiple of $M$ from masquerading as zero. After longitude selection, the sum of the three absolute orders is even, because their signed sum is zero. The factors $(1-\mu^2)^{|m|/2}$ therefore combine into an integer power. The surviving latitude integrand is a polynomial of degree at most $3L$, and (9.2) applies. This proves exact low-degree projection, not exact recovery of every degree of the product. It is the reason for padding by roughly a factor $3/2$ relative to the minimal linear-transform grid. Vector derivatives and higher nonlinearities need their own degree analysis.

For $L=2$, linear recovery needs $n\ge3$, $M\ge5$; quadratic projection needs $n\ge4$, $M\ge7$. A solver may use larger integer-friendly sizes. A Fourier example makes the danger explicit: on eight longitude points, multiplying mode $3$ by mode $3$ produces mode $6$, which aliases to $-2$. Truncating after this aliased transform cannot identify which $-2$ contribution was physical. Filtering damps modes; dealiasing prevents an incorrect projection. They are different operations.

## Time stepping and numerical stability

**Result and motivation.** Exact spatial modes do not guarantee stable time stepping. Each modal growth factor must fit the time integrator's stability region. Source: [@ArfkenWeber2005, Section 9.8, modal diffusion]; the discrete amplification calculation is given here explicitly.

For $a'=-\gamma a$ with $\gamma\ge0$, forward Euler with step $\Delta t>0$ gives $a^{r+1}=(1-\gamma\Delta t)a^r$, where $r$ is the integer time index. Avoiding growth requires $|1-\gamma\Delta t|\le1$, or $0\le\gamma\Delta t\le2$. For spherical diffusion through degree $L\ge1$,

$$
\gamma_\ell=\frac{\kappa\ell(\ell+1)}{R^2},
\qquad \Delta t\le\frac{2R^2}{\kappa L(L+1)}.
\tag{9.6}
$$

For pure advection $a'=-i\omega a$ with real nonzero $\omega$, forward Euler instead has squared amplification $|1-i\omega\Delta t|^2=1+\omega^2\Delta t^2>1$. A small step reduces growth but does not make this scheme linearly stable for these modes. Backward Euler uses $a^{r+1}=a^r/(1+\gamma\Delta t)$ for diffusion and is stable for every positive step, while remaining inaccurate for unresolved decay times. An exact exponential update solves a constant linear modal term exactly; forcing and nonlinear coupling still require time approximation.

The Courant number $C=U\Delta t/\Delta x$ compares motion in one step with a grid spacing. A Courant bound is scheme-dependent, not a universal theorem that $C\le1$ suffices for every method. Consistency means local discretization error vanishes as resolution increases; stability controls error amplification; convergence means the numerical solution approaches the desired continuum solution. Each is a separate claim.

## Weighted errors and verification

**Result and motivation.** A numerical norm approximates a specified continuum norm. Coordinates and weights belong to the scientific definition of an error. Sources: [@ArfkenWeber2005, Sections 10.3-10.4, 12.3]; formulas follow from (9.3).

Let $a_i=w_i/2$ for a zonal profile, truth $y_i$, prediction $\widehat y_i$, and error $e_i=\widehat y_i-y_i$. Then

$$
\operatorname{RMSE}_A=\left(\sum_ia_ie_i^2\right)^{1/2},
\qquad \operatorname{rel}L_A^2=\frac{(\sum_ia_ie_i^2)^{1/2}}{(\sum_ia_iy_i^2)^{1/2}}.
\tag{9.7}
$$

RMSE means root-mean-square error and has the field's units; relative $L^2$ is dimensionless and undefined for zero-norm truth. An arbitrary positive denominator floor defines a different score. For a full field use weights $w_i/(2M)$. Errors of variables with different units need separate reporting or explicit scales before aggregation.

Useful independent checks are a constant's area, one harmonic's coefficients, a transform round trip, discrete Parseval, and an analytic diffusion mode. The first two test normalization and phase; the round trip alone does not test continuous sampling. Convergence studies vary retained degree, quadrature density, and time step separately. Reversing latitude requires reversing both data and weights; a changed longitude origin changes Fourier phases.

## Chapter summary and self-test

**Main results and terms.** Galerkin methods enforce residual orthogonality. Gaussian quadrature uses Legendre roots and integrates through degree $2n-1$. Spherical integration weights already include the latitude Jacobian. Linear transform recovery needs (9.4), while exact scalar quadratic projection needs (9.5). Aliasing, filtering, and truncation are distinct. Modal amplification yields the diffusion time-step bound (9.6). Weighted errors approximate a chosen physical-area norm.

**Self-test.** Give sufficient $n,M$ for linear recovery and quadratic projection at $L=3$. Does adding latitude points change a fixed spectral cutoff? Why can a stable implicit diffusion step still be inaccurate?
