# Legendre polynomials and spherical harmonics {#ch-harmonics}

What replaces periodic plane waves on a sphere? Separation in longitude produces integer orders, while regularity at the poles selects discrete degrees. We use that eigenproblem to fix the Legendre normalization, construct spherical harmonics, and distinguish scalar profiles from tangent vector fields.

## Angular separation and Legendre's equation

Spherical harmonics are the globally regular eigenfunctions of the spherical Laplacian. Longitude periodicity and pole regularity quantize their two indices. Sources: [@ArfkenWeber2005, Sections 9.3-9.5, 12.1-12.6].

::: {.tb-assumption #obj-8-1}
**Assumption 8.1 - A globally regular angular eigenfunction**

Seek $\Delta_\Omega Y=-\Lambda Y$ on the unit sphere, where $\Lambda$ is dimensionless and $Y(\theta,\lambda)=\Theta(\theta)\Phi(\lambda)$.
:::

::: {.tb-result #obj-8-2}
**Result 8.2 - Angular separation produces an associated Legendre equation**

For a separated angular eigenfunction with $2\pi$-periodic longitude factor, the order $m$ is an integer, and its latitude factor obeys

$$
\frac{d}{d\mu}\left[(1-\mu^2)\frac{d\Theta}{d\mu}\right]
+\left[\Lambda-\frac{m^2}{1-\mu^2}\right]\Theta=0.
\tag{8.1}
$$
:::

::: {.tb-proof}
**Proof of Result 8.2**

Insert $Y=\Theta(\theta)\Phi(\lambda)$ into (3.5), multiply by $\sin^2\theta$, and separate the two variable dependences. The longitude equation is $\Phi\prime\prime+m^2\Phi=0$, whose single-valued periodic solutions require integer $m$. Choose $\Phi=e^{im\lambda}$ and set $\mu=\cos\theta$. $\square$
:::

::: {.tb-result #obj-8-3}
**Result 8.3 - Power-series recurrence at order zero**

For $m=0$ and a power-series solution $\Theta=\sum_{j\ge0}a_j\mu^j$ near zero,

$$
a_{j+2}=\frac{j(j+1)-\Lambda}{(j+2)(j+1)}a_j.
\tag{8.2}
$$
:::

::: {.tb-proof}
**Proof of Result 8.3**

The coefficient of $\mu^j$ in $(1-\mu^2)\Theta\prime\prime-2\mu\Theta\prime+\Lambda\Theta$ is $(j+2)(j+1)a_{j+2}+[\Lambda-j(j+1)]a_j$. Set it to zero. $\square$
:::

::: {.tb-result #obj-8-4}
**Result 8.4 - Regular degrees and polynomial solutions (quoted)**

If $\Lambda=\ell(\ell+1)$ for $\ell\in\mathbb N_0$, one parity branch terminates at degree $\ell$. Its normalization $P_\ell(1)=1$ defines the Legendre polynomial $P_\ell$. The other independent solution is singular at an endpoint. The global regularity theorem for (8.1) selects these discrete eigenvalues; the recurrence exhibits the regular polynomial solutions but is not by itself a proof that all other $\Lambda$ fail both endpoint conditions. For integer $m\ne0$, admissible degrees satisfy $\ell\ge|m|$. [@ArfkenWeber2005, Sections 9.5 and 12.5-12.6].
:::

::: {.tb-remark #obj-8-5}
**Remark 8.5 - Pole conditions are endpoint regularity**

For $m=0$ the Legendre equation has singular Sturm-Liouville endpoints because $p=1-\mu^2$ vanishes at $\pm1$. The boundary condition is regularity of the scalar on the sphere, rather than arbitrary Dirichlet data at coordinate poles.
:::

::: {.tb-exercise #ex-8-1}
**Exercise 8.1 - Terminate a recurrence**

*Application.* At $m=0$ and $\Lambda=2$, use (8.2) to obtain the odd regular polynomial with $P(1)=1$.
:::

## Polynomial normalization and associated functions

Explicit normalization and phase conventions make coefficients comparable. Associated Legendre functions supply the latitude dependence for nonzero longitude order. Sources: [@ArfkenWeber2005, Sections 12.2-12.5].

::: {.tb-result #obj-8-6}
**Result 8.6 - Rodrigues representation and Legendre orthogonality**

For the regular degree-$\ell$ solution normalized by $P_\ell(1)=1$, Rodrigues' representation and orthogonality are

$$
\begin{aligned}
P_\ell(\mu)&=\frac1{2^\ell\ell!}\frac{d^\ell}{d\mu^\ell}(\mu^2-1)^\ell,\\
P_0&=1,\quad P_1=\mu,\quad P_2=\tfrac12(3\mu^2-1),\\
\int_{-1}^1P_\ell(\mu)P_j(\mu)d\mu&=\frac2{2\ell+1}\delta_{\ell j}.
\end{aligned}
\tag{8.3}
$$

Rodrigues' representation is quoted from AW, Section 12.4; the norm and orthogonality can be derived from it.
:::

::: {.tb-proof}
**Proof of Result 8.6**

Orthogonality for different degrees follows by multiplying their differential equations, subtracting, and integrating; the boundary factor $1-\mu^2$ makes the regular polynomial boundary terms zero. The norm can also be derived from Rodrigues. The leading coefficient of $P_\ell$ is $a_\ell=(2\ell)!/[2^\ell(\ell!)^2]$. Since $P_\ell-a_\ell\mu^\ell$ has lower degree, orthogonality gives $\int P_\ell^2=a_\ell\int P_\ell\mu^\ell$. Define $I_\ell=\int_{-1}^1(1-\mu^2)^\ell d\mu$. Integrating Rodrigues by parts $\ell$ times gives $\int P_\ell\mu^\ell=2^{-\ell}I_\ell$: all endpoint terms vanish and $d^\ell\mu^\ell/d\mu^\ell=\ell!$.

For $\ell\ge1$, integrate the derivative of $\mu(1-\mu^2)^\ell$ over $[-1,1]$ to get $0=I_\ell-2\ell(I_{\ell-1}-I_\ell)$. Thus $I_\ell=2\ell I_{\ell-1}/(2\ell+1)$ with $I_0=2$. Iterating gives $I_\ell=2^{2\ell+1}(\ell!)^2/(2\ell+1)!$, and the norm is $a_\ell2^{-\ell}I_\ell=2/(2\ell+1)$. $\square$
:::

::: {.tb-definition #obj-8-7}
**Definition 8.7 - Associated functions and the Condon-Shortley phase**

For integer $0\le m\le\ell$, choose the Condon-Shortley phase by defining

$$
P_\ell^m(\mu)=(-1)^m(1-\mu^2)^{m/2}\frac{d^mP_\ell}{d\mu^m},
\qquad
\int_{-1}^1(P_\ell^m)^2d\mu
=\frac2{2\ell+1}\frac{(\ell+m)!}{(\ell-m)!}.
\tag{8.4}
$$

The second identity is a quoted normalization result [@ArfkenWeber2005, Section 12.5].
:::

::: {.tb-remark #obj-8-8}
**Remark 8.8 - Pole factors and the quoted associated norm**

Differentiating Legendre's equation $m$ times and multiplying by $(1-\mu^2)^{m/2}$ gives (8.1). The associated-function norm in (8.4) is quoted from AW, Section 12.5; its repeated-integration proof is not reproduced here. The factor $(1-\mu^2)^{m/2}=\sin^m\theta$ enforces the required vanishing of a regular scalar's nonzero longitude order at the poles. Odd-$m$ associated functions are not polynomials in $\mu$.
:::

::: {.tb-result #obj-8-9}
**Result 8.9 - Degree recurrence (quoted)**

A stable degree recurrence follows from Rodrigues or the generating function:
$(\ell+1)P_{\ell+1}=(2\ell+1)\mu P_\ell-\ell P_{\ell-1}$. It constructs all degrees from $P_0,P_1$; high-degree numerical algorithms still need controlled normalization to avoid overflow. [@ArfkenWeber2005, Section 12.2].
:::

::: {.tb-exercise #ex-8-2}
**Exercise 8.2 - Generate the next degree**

*Application.* Use the degree recurrence and $P_1=\mu$, $P_2=(3\mu^2-1)/2$ to obtain $P_3$.
:::

## Spherical harmonic expansion and Parseval

The spherical harmonic transform is longitude Fourier analysis coupled to weighted latitude analysis. Degree measures total angular scale; order measures longitude variation. Sources: [@ArfkenWeber2005, Sections 12.5-12.6].

::: {.tb-definition #obj-8-10}
**Definition 8.10 - Normalized complex spherical harmonics**

For $m\ge0$, define

$$
Y_\ell^m(\theta,\lambda)=N_{\ell m}P_\ell^m(\cos\theta)e^{im\lambda},
\qquad N_{\ell m}=\left[\frac{2\ell+1}{4\pi}\frac{(\ell-m)!}{(\ell+m)!}\right]^{1/2},
\qquad Y_\ell^{-m}=(-1)^m\overline{Y_\ell^m}.
\tag{8.5}
$$

Degree $\ell$ is nonnegative, and order satisfies $-\ell\le m\le\ell$.
:::

::: {.tb-result #obj-8-11}
**Result 8.11 - Angular orthonormality and the physical eigenvalue**

For the convention (8.5),

$$
\int_{S^2}Y_\ell^m\overline{Y_j^n}d\Omega=\delta_{\ell j}\delta_{mn},
\qquad \Delta_sY_\ell^m=-\frac{\ell(\ell+1)}{R^2}Y_\ell^m.
\tag{8.6}
$$
:::

::: {.tb-proof}
**Proof of Result 8.11**

Longitude integration removes unequal orders. For equal nonnegative order $m$ but unequal degrees $\ell,j$, multiply the two associated Legendre equations by the other function, subtract, and integrate. The $m^2/(1-\mu^2)$ terms cancel, giving

$$
[\ell(\ell+1)-j(j+1)]\int_{-1}^1 P_\ell^mP_j^m\,d\mu
=\left[(1-\mu^2)\left(P_\ell^m(P_j^m)\prime-(P_\ell^m)\prime P_j^m\right)\right]_{-1}^1=0.
$$

Regularity makes the endpoint bracket zero: for $m=0$ the polynomial factors are finite, and for $m>0$ the pole factors in (8.4) make the product vanish. Distinct degrees have different $\ell(\ell+1)$, proving the cross integral is zero. For equal degrees use (8.4), whose factorials cancel $N_{\ell m}^2$. The eigenvalue follows by substituting the separated equations into $\Delta_s=R^{-2}\Delta_\Omega$. Negative orders follow by conjugation. $\square$
:::

::: {.tb-remark #obj-8-12}
**Remark 8.12 - The measure belongs to the normalization**

The symbol $S^2$ denotes the unit sphere; these angular functions are also evaluated on $S_R^2$. They are normalized under $d\Omega$, not physical area $dA$. In particular $Y_0^0=1/\sqrt{4\pi}$ and $Y_1^0=\sqrt{3/(4\pi)}\cos\theta$.
:::

::: {.tb-result #obj-8-13}
**Result 8.13 - Spherical harmonic expansion and Parseval**

The harmonics form a complete orthonormal system in $L^2(S^2,d\Omega)$. For any $f$ in that space,

$$
\begin{aligned}
f&=\sum_{\ell=0}^{\infty}\sum_{m=-\ell}^{\ell}f_\ell^mY_\ell^m,
& f_\ell^m&=\int_{S^2}f\overline{Y_\ell^m}d\Omega,\\
\int_{S^2}|f|^2d\Omega&=\sum_{\ell,m}|f_\ell^m|^2,
& \langle f\rangle_A&=f_0^0/\sqrt{4\pi}.
\end{aligned}
\tag{8.7}
$$

The expansion converges in norm; completeness is quoted from AW, Section 12.6. Parseval follows from Chapter 4.
:::

::: {.tb-proof}
**Proof of Result 8.13**

The completeness assertion is the cited spherical harmonic theorem. Apply the Hilbert-space projection and Parseval results of Chapter 4 with the double index $(\ell,m)$ to obtain the norm limit and squared-coefficient sum. Only the constant harmonic has nonzero area integral, so $\langle f\rangle_A=f_0^0/\sqrt{4\pi}$. $\square$
:::

::: {.tb-remark #obj-8-14}
**Remark 8.14 - Real fields and a degree cutoff**

The expansion converges in $L^2$; smooth fields admit stronger convergence. Real $f$ obeys $f_\ell^{-m}=(-1)^m\overline{f_\ell^m}$. A cutoff $0\le\ell\le L$ retains $(L+1)^2$ basis functions, or the same number of independent real coefficients for a real field. The physical inverse length is approximately $\sqrt{\ell(\ell+1)}/R$; degree zero is the mean, not a finite wavelength.
:::

::: {.tb-example #obj-8-15}
**Example 8.15 - Expanding squared sine of latitude**

For $f=\mu^2$, equation (8.3) gives $\mu^2=P_0/3+2P_2/3$. Hence $f_0^0=\sqrt{4\pi}/3$, $f_2^0=(2/3)\sqrt{4\pi/5}$, and all other coefficients vanish. The area mean is $1/3$. Parseval gives $\int\mu^4d\Omega=4\pi/5$, agreeing with direct integration.
:::

::: {.tb-exercise #ex-8-3}
**Exercise 8.3 - Recover a constant mode**

*Application.* For $f(\mathbf n)=C$, find $f_0^0$ and verify the area mean using (8.7).
:::

## Zonal means, tangent vectors, and isotropy

Longitude averaging keeps only order zero. Tangent vectors need geometric basis functions, while rotationally invariant scalar filters must act identically on all orders of a degree. Sources: [@ArfkenWeber2005, Sections 12.6, 12.8, 12.11].

::: {.tb-definition #obj-8-16}
**Definition 8.16 - Zonal mean and normalized latitude basis**

The zonal mean is $\overline f(\mu)=(2\pi)^{-1}\int_0^{2\pi}f(\mu,\lambda)d\lambda$. Because the average of $e^{im\lambda}$ is zero for $m\ne0$, only $m=0$ survives. For a profile use $b_\ell(\mu)=\sqrt{2\ell+1}P_\ell(\mu)$, orthonormal under $d\mu/2$. Then $\overline f=\sum_\ell a_\ell b_\ell$ with $a_\ell=\frac12\int_{-1}^1\overline f b_\ell d\mu$. A scalar profile and an eastward velocity component have different pole regularity: an arbitrary scalar Legendre expansion of speed does not by itself define a smooth tangent vector field.
:::

::: {.tb-definition #obj-8-17}
**Definition 8.17 - Tangent gradient and rotated-gradient harmonics**

For $\ell\ge1$, dimensionless tangent vector harmonics are

$$
\mathbf E_\ell^m=\frac{R\nabla_sY_\ell^m}{\sqrt{\ell(\ell+1)}},
\qquad
\mathbf B_\ell^m=\mathbf e_r\times\mathbf E_\ell^m.
\tag{8.8}
$$
:::

::: {.tb-result #obj-8-18}
**Result 8.18 - Tangent harmonic normalization and differential type**

For each $\ell\ge1$ and $|m|\le\ell$, the tangent harmonics (8.8) both have unit norm under $d\Omega$. The gradient family is surface-curl-free; the rotated-gradient family is divergence-free. The convention here is the tangent gradient/rotated-gradient convention, whereas AW also uses coupled vector harmonics with radial components.
:::

::: {.tb-proof}
**Proof of Result 8.18**

Integration by parts gives $\int R^2|\nabla_sY_\ell^m|^2d\Omega=-R^2\int\overline{Y_\ell^m}\Delta_sY_\ell^m d\Omega=\ell(\ell+1)$. Divide by the squared normalizing factor in (8.8). Rotation by $\mathbf e_r\times$ preserves tangent length, so the rotated family has the same norm. The curl of a gradient and the divergence of its rotated gradient vanish by cancellation of mixed derivatives in (3.4). $\square$
:::

::: {.tb-definition #obj-8-19}
**Definition 8.19 - A harmonic tangent field**

A smooth tangent field with zero surface divergence and zero radial curl is called a harmonic tangent field.
:::

::: {.tb-result #obj-8-20}
**Result 8.20 - Smooth tangent decomposition on the sphere**

Every smooth tangent field on the whole sphere can be written $\mathbf v=\nabla_s\chi+\mathbf e_r\times\nabla_s\psi$, with scalar potentials unique up to constants. A smooth divergence-free field therefore has a streamfunction.
:::

::: {.tb-proof}
**Proof of Result 8.20**

For a smooth tangent field $\mathbf v$, let $\delta=\nabla_s\cdot\mathbf v$ and $\zeta=(\nabla\times\mathbf v)\cdot\mathbf e_r$. Both have zero area integral by the surface divergence and Stokes identities. Scalar harmonic inversion therefore supplies zero-mean potentials $\chi,\psi$ with $\Delta_s\chi=\delta$ and $\Delta_s\psi=\zeta$, by dividing each degree-$\ell\ge1$ coefficient by $-\ell(\ell+1)/R^2$. Then $\mathbf w=\mathbf v-\nabla_s\chi-\mathbf e_r\times\nabla_s\psi$ has zero divergence and radial curl. Such a field is called a harmonic tangent field.

The sphere is simply connected: every closed loop can be continuously shrunk to a point. Stokes' theorem therefore makes the integral of a curl-free smooth tangent field around every loop zero. Its line integral from a reference point is path-independent and defines a scalar $h$ with $\mathbf w=\nabla_sh$ (the potential-field argument of AW, Section 1.13). Since $\Delta_sh=0$, (3.8) gives $\int|\nabla_sh|^2dA=0$, hence $\mathbf w=0$. This proves the smooth decomposition $\mathbf v=\nabla_s\chi+\mathbf e_r\times\nabla_s\psi$. In particular, a divergence-free smooth field has the streamfunction representation. Expanding these potentials gives the $\mathbf E/\mathbf B$ modes; the construction here only needs smooth fields. A velocity generated from a streamfunction uses the latter family; treating its coordinate components as unrelated scalars does not encode that constraint. $\square$
:::

::: {.tb-result #obj-8-21}
**Result 8.21 - Spherical addition theorem (quoted)**

For unit vectors $\mathbf n,\mathbf n'$ separated by angle $\gamma$, with $\cos\gamma=\mathbf n\cdot\mathbf n'$, the addition theorem is

$$
P_\ell(\mathbf n\cdot\mathbf n')
=\frac{4\pi}{2\ell+1}\sum_{m=-\ell}^{\ell}Y_\ell^m(\mathbf n)\overline{Y_\ell^m(\mathbf n')}.
\tag{8.9}
$$

This theorem uses the normalization (8.5) [@ArfkenWeber2005, Section 12.8].
:::

::: {.tb-remark #obj-8-22}
**Remark 8.22 - Why all orders of a degree belong together**

This theorem is quoted from AW, Section 12.8. It shows why an isotropic kernel, depending only on angular separation, multiplies every order at fixed degree by the same scalar. Chapter 12 derives the multiplier. Keeping all orders through a degree gives a rotation-invariant subspace (triangular truncation). Selecting unrelated orders can break that property.
:::

::: {.tb-exercise #ex-8-4}
**Exercise 8.4 - Apply zonal averaging**

*Application.* What is the zonal mean of $Y_\ell^m$ when $m\ne0$? What happens for $m=0$?
:::

## Chapter summary

Longitude periodicity selects integer order $m$; global regularity selects integer degree $\ell\ge|m|$. Rodrigues' formula defines $P_\ell$, and the Condon-Shortley choice fixes the phase of $P_\ell^m$. Equations (8.5)-(8.7) define the normalized spherical harmonic transform, eigenvalues, and Parseval identity. Zonal means keep $m=0$. Vector harmonics separate gradient and nondivergent tangent fields. The addition theorem underlies isotropic spherical kernels.

::: {.tb-exercise #ex-8-5}
**Exercise 8.5 - Connect the chapter results**

*Synthesis.* Expand $\mu^2-1/3$ and solve $\Delta_s\psi=A(\mu^2-1/3)$ with zero mean. How many independent real degrees of freedom remain at cutoff $L=2$? Why is a two-dimensional periodic FFT on latitude-longitude coordinates not spherical harmonic analysis?
:::
