# Spectral discretization, quadrature, and stability {#ch-numerics}

When does a finite spectral calculation approximate the continuum problem it is intended to solve? Choosing a finite basis, integrating its coefficients, and advancing them in time are separate decisions. We derive sufficient sampling bounds for scalar products and use modal amplification to check time integration.

## Projection and the method of weighted residuals

A spectral method approximates a field in a finite basis and imposes equations on its coefficients. Spatial truncation and time integration introduce different errors. Sources: [@ArfkenWeber2005, Sections 10.4, 12.3, 14.6, 17.8]; numerical bounds below are derived for the stated finite spaces.

::: {.tb-definition #obj-9-1}
**Definition 9.1 - Finite expansion and Galerkin residual**

For an evolution equation $u_t=\mathcal Lu+\mathcal N(u)+f$, let $\mathcal L$ be a linear spatial operator, $\mathcal N$ a nonlinear term, and $f$ forcing. Choose orthonormal basis functions $e_1,\ldots,e_K$ satisfying the spatial conditions, and approximate $u_K=\sum_{j=1}^Ka_j(t)e_j$. The residual is $r_K=\partial_tu_K-\mathcal Lu_K-\mathcal N(u_K)-f$.
:::

::: {.tb-result #obj-9-2}
**Result 9.2 - Galerkin coefficient equations**

For an orthonormal basis satisfying the spatial conditions and enough regularity to form the displayed inner products, requiring $\langle r_K,e_i\rangle=0$ gives

$$
a_i'=\sum_jL_{ij}a_j+\langle\mathcal N(u_K),e_i\rangle+f_i,
\quad L_{ij}=\langle\mathcal Le_j,e_i\rangle,
\quad f_i=\langle f,e_i\rangle.
\tag{9.1}
$$
:::

::: {.tb-proof}
**Proof of Result 9.2**

Insert $u_K=\sum_ja_je_j$ into the residual. Orthonormality makes $\langle\partial_tu_K,e_i\rangle=a_i\prime$. Linearity of $\mathcal L$ gives the matrix term, and moving the other terms to the right yields (9.1). $\square$
:::

::: {.tb-definition #obj-9-3}
**Definition 9.3 - Mass matrix, collocation, and pseudospectral evaluation**

If $\mathcal Le_j=\lambda_je_j$, $L_{ij}=\lambda_j\delta_{ij}$. A nonorthonormal basis instead gives a mass matrix $M_{ij}=\langle e_j,e_i\rangle$ multiplying $a_j'$. Collocation requires the PDE residual to vanish at selected nodes. A pseudospectral method evaluates products at grid points and transforms them back; with sufficiently accurate quadrature this reproduces Galerkin projection for those products.
:::

::: {.tb-remark #obj-9-4}
**Remark 9.4 - Three independent approximation choices**

Three separate approximations are present: truncating the function space, approximating its integrals, and integrating its coefficient ODEs in time. Increasing the grid alone does not increase the retained degree; decreasing the time step does not remove spatial aliasing.
:::

::: {.tb-exercise #ex-9-1}
**Exercise 9.1 - Diagonalize one linear term**

*Application.* If $\mathcal Le_j=-j^2e_j$ and forcing and nonlinearity vanish, derive the Galerkin ODE and its exact solution for $a_j(0)=A_j$.
:::

## Gauss-Legendre quadrature and a spherical grid

Gaussian quadrature integrates polynomials up to degree $2n-1$ using $n$ carefully chosen latitude nodes. It accounts for spherical area through $\mu=\sin\varphi$. Sources: Legendre orthogonality [@ArfkenWeber2005, Section 12.3]; explicit quadrature rule [@NISTDLMFQuadrature].

::: {.tb-definition #obj-9-5}
**Definition 9.5 - Gaussian nodes and polynomial degree**

For $n\ge1$, let $\mu_i$ be the distinct roots of $P_n$ in $(-1,1)$. The notation $\deg p$ means the degree of polynomial $p$.
:::

::: {.tb-result #obj-9-6}
**Result 9.6 - Gauss-Legendre weights and exactness**

The weights below integrate every polynomial of degree at most $2n-1$ exactly:

$$
\int_{-1}^1p(\mu)d\mu=\sum_{i=1}^nw_ip(\mu_i)
\quad (\deg p\le2n-1),\qquad
w_i=\frac{2}{(1-\mu_i^2)[P_n'(\mu_i)]^2},\quad \sum_iw_i=2.
\tag{9.2}
$$

The explicit weight formula is the NIST Gauss-Legendre formula [@NISTDLMFQuadrature].
:::

::: {.tb-proof}
**Proof of Result 9.6**

Here $\deg p$ is polynomial degree. To prove the exactness, divide any polynomial of degree at most $2n-1$ as $p=P_ns+r$, with $s,r$ of degree at most $n-1$. Orthogonality gives $\int P_ns=0$, and $p(\mu_i)=r(\mu_i)$. Integrating the degree-$(n-1)$ Lagrange interpolant of $r$ exactly therefore integrates $p$. The Lagrange function that is one at $\mu_i$ and zero at the other nodes is $\ell_i(\mu)=P_n(\mu)/[(\mu-\mu_i)P_n'(\mu_i)]$; hence $w_i=\int\ell_i$. Evaluating this integral with the Legendre recurrence yields the explicit weight formula in (9.2), specified by the NIST Gauss-Legendre rule. This argument explains the extra exact degrees without assuming uniform latitude spacing. $\square$
:::

::: {.tb-definition #obj-9-7}
**Definition 9.7 - Full Gaussian grid**

A full Gaussian grid combines latitudes $\varphi_i=\arcsin\mu_i$ with $M$ equally spaced longitudes $\lambda_j=2\pi j/M$. No latitude node is at a pole.
:::

::: {.tb-result #obj-9-8}
**Result 9.8 - Quadrature for the area integral and mean**

On this full grid, applying the longitude trapezoidal rule and the Gaussian latitude rule gives

$$
\int_{S^2}f\,d\Omega\approx\frac{2\pi}{M}\sum_{i,j}w_if_{ij},
\qquad \langle f\rangle_A\approx\frac1{2M}\sum_{i,j}w_if_{ij}.
\tag{9.3}
$$

The equality is exact for functions in the respective quadrature exactness classes; for general fields it is an approximation.
:::

::: {.tb-proof}
**Proof of Result 9.8**

Write the area integral as $\int_{-1}^1\int_0^{2\pi}f(\mu,\lambda)d\lambda\,d\mu$. Apply the longitude weight $2\pi/M$ and latitude weights $w_i$, then divide by the total solid angle $4\pi$ for the mean. This gives (9.3); exactness follows whenever both component rules are exact on the integrand. $\square$
:::

::: {.tb-example #obj-9-9}
**Example 9.9 - Area weights and their polynomial limit**

For a zonal profile the normalized latitude weights are $w_i/2$. Multiplying by another $\cos\varphi_i$ would count the area Jacobian twice. With $n=2$, nodes $\pm1/\sqrt3$ and weights one give the exact mean $1/3$ for $\mu^2$, but $1/9$ for $\mu^4$ instead of $1/5$; degree four exceeds the exactness guarantee.
:::

::: {.tb-exercise #ex-9-2}
**Exercise 9.2 - Choose a quadrature order**

*Application.* How many Gauss-Legendre nodes suffice to integrate every polynomial of degree $8$ exactly? Is the two-node rule sufficient for $\mu^4$?
:::

## Exact harmonic recovery and nonlinear aliasing

Recovering a degree-$L$ field needs fewer nodes than exactly projecting a quadratic product back to that degree. Dealiasing addresses this second requirement. Sources: [@ArfkenWeber2005, Sections 12.5-12.6, 14.6]; the sufficient spherical bounds follow below.

::: {.tb-definition #obj-9-10}
**Definition 9.10 - Separated spherical analysis**

For a scalar field bandlimited to degree $L$, longitude analysis forms $F_m(\mu_i)=M^{-1}\sum_jf_{ij}e^{-im\lambda_j}$. The normalization $N_{\ell m}$ is defined by (8.5).
:::

::: {.tb-result #obj-9-11}
**Result 9.11 - Exact recovery of a degree-limited scalar field**

For a scalar field bandlimited to degrees through $L$, exact arithmetic and a full Gaussian grid satisfying the displayed bounds recover its coefficients:

$$
f_\ell^m=2\pi N_{\ell m}\sum_iw_iF_m(\mu_i)P_\ell^m(\mu_i),
\qquad n\ge L+1,\quad M\ge2L+1.
\tag{9.4}
$$
:::

::: {.tb-proof}
**Proof of Result 9.11**

These bounds make (9.4) exact in exact arithmetic for the stated bandlimited field. Longitude orthogonality eliminates different orders without aliasing. For the same order, the product $P_\ell^mP_j^m$ is $(1-\mu^2)^m$ times two polynomial derivatives, with total degree at most $\ell+j\le2L$. Gaussian quadrature therefore integrates it exactly. Individual odd-order functions need not be polynomials; their same-order products are. $\square$
:::

::: {.tb-result #obj-9-12}
**Result 9.12 - Exact low-degree projection of a quadratic scalar product**

For the product of two scalar fields bandlimited to degree $L$, sufficient full Gaussian grid bounds for exact projection back through degree $L$ are

$$
M>3L,\qquad 2n-1\ge3L.
\tag{9.5}
$$
:::

::: {.tb-proof}
**Proof of Result 9.12**

The product of two degree-$L$ scalar fields can contain degree $2L$. To compute its coefficients only through degree $L$, the integrand contains three harmonics. The largest possible longitude frequency in this triple product is $3L$, so the strict inequality prevents a nonzero multiple of $M$ from masquerading as zero. After longitude selection, the sum of the three absolute orders is even, because their signed sum is zero. The factors $(1-\mu^2)^{|m|/2}$ therefore combine into an integer power. The surviving latitude integrand is a polynomial of degree at most $3L$, and (9.2) applies. This proves exact low-degree projection, not exact recovery of every degree of the product. It is the reason for padding by roughly a factor $3/2$ relative to the minimal linear-transform grid. Vector derivatives and higher nonlinearities need their own degree analysis. $\square$
:::

::: {.tb-example #obj-9-13}
**Example 9.13 - Linear recovery is weaker than nonlinear projection**

For $L=2$, linear recovery needs $n\ge3$, $M\ge5$; quadratic projection needs $n\ge4$, $M\ge7$. A solver may use larger integer-friendly sizes. A Fourier example makes the danger explicit: on eight longitude points, multiplying mode $3$ by mode $3$ produces mode $6$, which aliases to $-2$. Truncating after this aliased transform cannot identify which $-2$ contribution was physical. Filtering damps modes; dealiasing prevents an incorrect projection. They are different operations.
:::

::: {.tb-exercise #ex-9-3}
**Exercise 9.3 - A strict longitude bound**

*Application and boundary case.* At $L=4$, give sufficient $n,M$ for quadratic projection. Why is $M=12$ excluded by (9.5)?
:::

## Time stepping and numerical stability

Exact spatial modes do not guarantee stable time stepping. Each modal growth factor must fit the time integrator's stability region. Source: [@ArfkenWeber2005, Section 9.8, modal diffusion]; the discrete amplification calculation is given here explicitly.

::: {.tb-definition #obj-9-14}
**Definition 9.14 - Forward-Euler modal amplification**

For $a'=-\gamma a$ with $\gamma\ge0$, forward Euler with step $\Delta t>0$ gives $a^{r+1}=(1-\gamma\Delta t)a^r$, where $r$ is the integer time index.
:::

::: {.tb-result #obj-9-15}
**Result 9.15 - Forward-Euler bound for spherical diffusion**

For $a\prime=-\gamma a$, $\gamma\ge0$, forward Euler is nonamplifying if $0\le\gamma\Delta t\le2$. For spherical diffusion through degree $L\ge1$,

$$
\gamma_\ell=\frac{\kappa\ell(\ell+1)}{R^2},
\qquad \Delta t\le\frac{2R^2}{\kappa L(L+1)}.
\tag{9.6}
$$
:::

::: {.tb-proof}
**Proof of Result 9.15**

The amplification factor is $1-\gamma\Delta t$. Requiring its absolute value to be at most one gives the scalar interval. The largest spherical diffusive rate occurs at degree $L$, so apply the interval to $\gamma_L=\kappa L(L+1)/R^2$. $\square$
:::

::: {.tb-counterexample #obj-9-16}
**Counterexample 9.16 - A small Euler step does not stabilize pure advection**

For pure advection $a'=-i\omega a$ with real nonzero $\omega$, forward Euler instead has squared amplification $|1-i\omega\Delta t|^2=1+\omega^2\Delta t^2>1$. A small step reduces growth but does not make this scheme linearly stable for these modes. Backward Euler uses $a^{r+1}=a^r/(1+\gamma\Delta t)$ for diffusion and is stable for every positive step, while remaining inaccurate for unresolved decay times. An exact exponential update solves a constant linear modal term exactly; forcing and nonlinear coupling still require time approximation.
:::

::: {.tb-definition #obj-9-17}
**Definition 9.17 - Courant number, consistency, stability, and convergence**

The Courant number $C=U\Delta t/\Delta x$ compares motion in one step with a grid spacing. A Courant bound is scheme-dependent, not a universal theorem that $C\le1$ suffices for every method. Consistency means local discretization error vanishes as resolution increases; stability controls error amplification; convergence means the numerical solution approaches the desired continuum solution. Each is a separate claim.
:::

::: {.tb-exercise #ex-9-4}
**Exercise 9.4 - Separate stability from accuracy**

*Calculation and interpretation.* For $a\prime=-\gamma a$, compare backward Euler amplification at $\gamma\Delta t=10$ with exact amplification. Is its magnitude bounded by one?
:::

## Weighted errors and verification

A numerical norm approximates a specified continuum norm. Coordinates and weights belong to the scientific definition of an error. Sources: [@ArfkenWeber2005, Sections 10.3-10.4, 12.3]; formulas follow from (9.3).

::: {.tb-definition #obj-9-18}
**Definition 9.18 - Gaussian-weighted error measures**

Let $a_i=w_i/2$ for a zonal profile, truth $y_i$, prediction $\widehat y_i$, and error $e_i=\widehat y_i-y_i$. Then

$$
\operatorname{RMSE}_A=\left(\sum_ia_ie_i^2\right)^{1/2},
\qquad \operatorname{rel}L_A^2=\frac{(\sum_ia_ie_i^2)^{1/2}}{(\sum_ia_iy_i^2)^{1/2}}.
\tag{9.7}
$$
:::

::: {.tb-remark #obj-9-19}
**Remark 9.19 - Units, zero targets, and multiple variables**

RMSE means root-mean-square error and has the field's units; relative $L^2$ is dimensionless and undefined for zero-norm truth. An arbitrary positive denominator floor defines a different score. For a full field use weights $w_i/(2M)$. Errors of variables with different units need separate reporting or explicit scales before aggregation.
:::

::: {.tb-remark #obj-9-20}
**Remark 9.20 - A verification sequence with distinct failure modes**

Useful independent checks are a constant's area, one harmonic's coefficients, a transform round trip, discrete Parseval, and an analytic diffusion mode. The first two test normalization and phase; the round trip alone does not test continuous sampling. Convergence studies vary retained degree, quadrature density, and time step separately. Reversing latitude requires reversing both data and weights; a changed longitude origin changes Fourier phases.
:::

::: {.tb-exercise #ex-9-5}
**Exercise 9.5 - Check the zero predictor**

*Boundary case.* For nonzero-norm truth, what is weighted relative $L^2$ error of a zero prediction? What if truth also vanishes?
:::

## Chapter summary

Galerkin methods enforce residual orthogonality. Gaussian quadrature uses Legendre roots and integrates through degree $2n-1$. Spherical integration weights already include the latitude Jacobian. Linear transform recovery needs (9.4), while exact scalar quadratic projection needs (9.5). Aliasing, filtering, and truncation are distinct. Modal amplification yields the diffusion time-step bound (9.6). Weighted errors approximate a chosen physical-area norm.

::: {.tb-exercise #ex-9-6}
**Exercise 9.6 - Connect the chapter results**

*Synthesis.* Give sufficient $n,M$ for linear recovery and quadratic projection at $L=3$. Does adding latitude points change a fixed spectral cutoff? Why can a stable implicit diffusion step still be inaccurate?
:::

::: {.tb-exercise #ex-9-7}
**Exercise 9.7 - A conserved mean in exact Galerkin transport**

*Independent proof.* On a closed sphere let a prescribed smooth tangent velocity be divergence-free, and take $q_t=-\mathbf u\cdot\nabla_sq$. An exact Galerkin approximation retains the constant harmonic. Prove that its mean coefficient stays constant. Which step would require a new check with approximate quadrature?
:::
