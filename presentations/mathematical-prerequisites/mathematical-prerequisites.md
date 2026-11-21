---
title: "Mathematical prerequisites"
subtitle: "From fields and conservation to spherical analysis and operator maps"
date: "21 November 2026"
lang: en-US
documentclass: report
classoption: [oneside, openany]
fontsize: 11pt
papersize: a4
geometry: [left=23mm, right=23mm, top=26mm, bottom=24mm]
mainfont: texgyrepagella-regular.otf
mainfontoptions: [BoldFont=texgyrepagella-bold.otf, ItalicFont=texgyrepagella-italic.otf, BoldItalicFont=texgyrepagella-bolditalic.otf]
mathfont: texgyrepagella-math.otf
monofont: texgyrecursor-regular.otf
colorlinks: true
linkcolor: MidnightBlue
urlcolor: MidnightBlue
citecolor: MidnightBlue
toc-depth: 2
numbersections: true
bibliography: ../../book/references.bib
link-citations: true
header-includes:
  - \usepackage[dvipsnames]{xcolor}
---

<nav aria-label="Contents">
<ul>
<li><a href="#ch-language">Mathematical language and linear algebra</a></li>
<li><a href="#ch-calculus">Calculus, fluxes, and conservation</a></li>
<li><a href="#ch-sphere">Geometry and calculus on the sphere</a></li>
<li><a href="#ch-spaces">Function spaces, limits, and weak derivatives</a></li>
<li><a href="#ch-odes">Differential equations and eigenfunction theory</a></li>
<li><a href="#ch-pdes">Partial differential equations and physical models</a></li>
<li><a href="#ch-fourier">Fourier analysis</a></li>
<li><a href="#ch-harmonics">Legendre polynomials and spherical harmonics</a></li>
<li><a href="#ch-numerics">Spectral discretization, quadrature, and stability</a></li>
<li><a href="#ch-fluids">Rotating fluids, vorticity, and spectra</a></li>
<li><a href="#ch-statistics">Probability, averages, and climatological estimates</a></li>
<li><a href="#ch-operators">Integral operators, symmetries, and learned maps</a></li>
<li><a href="#answers">Self-test answers</a></li>
<li><a href="#references">References</a></li>
</ul>
</nav>

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

Read Chapters 1-8 in order for the analytic foundations. Chapter 9 uses both Fourier and spherical analysis. Chapter 10 adds physical models, Chapter 11 adds statistical interpretation, and Chapter 12 connects them to integral and learned operators. Each subchapter starts with its result and purpose. Each chapter ends with a compact summary and retrieval questions; answers are separated at the end.

# Mathematical language and linear algebra {#ch-language}

## Scalars, functions, and dimensions

**Result and motivation.** A field assigns a value to each position and time. Its domain, units, and type determine which equations and averages are meaningful. This is the starting point for interpreting either a PDE or an array of samples. Sources: [@ArfkenWeber2005, Sections 1.1-1.4, 2.6, 6.1].

The sets $\mathbb R$, $\mathbb C$, $\mathbb Z$, and $\mathbb N_0$ denote real numbers, complex numbers, integers, and nonnegative integers. The notation $x\in D$ means that $x$ belongs to the set $D$; $f:D\to V$ assigns a unique element of $V$ to every element of $D$. The image $f(x)$ is the value at $x$. A domain is the region on which a field is defined. A scalar field takes real or complex values; a vector field takes values in a vector space. A component is a scalar coordinate in a chosen basis.

Write position as $\mathbf x=(x_1,x_2,x_3)$, time as $t$, and a real scalar field as $q(\mathbf x,t)$. A sampled array $q_{ij}$ stores values at specified positions; its indices are not physical coordinates. A continuous field and its finite sample array are different mathematical objects.

The imaginary unit $i$ satisfies $i^2=-1$. For real $a,b$, define $z=a+ib$, conjugate $\overline z=a-ib$, real part $\operatorname{Re}z=a$, and modulus $|z|=(a^2+b^2)^{1/2}$. Euler's identity connects oscillations to algebra:

$$
e^{i\alpha}=\cos\alpha+i\sin\alpha,\qquad
\overline{e^{i\alpha}}=e^{-i\alpha},\qquad |e^{i\alpha}|=1.
\tag{1.1}
$$

Here $\alpha$ is a dimensionless angle in radians. The exponential can be defined by $e^z=\sum_{n=0}^{\infty}z^n/n!$, where $n!=1\cdot2\cdots n$ and $0!=1$. A sum means repeated addition; an infinite sum denotes the limit of its finite partial sums. The sine and cosine are the imaginary and real parts of $e^{i\alpha}$.

Use $[q]$ for the physical dimensions of $q$. An equation can add only quantities with the same dimensions. If length and time have units $\mathrm m$ and $\mathrm s$, velocity has $[u]=\mathrm m\,\mathrm s^{-1}$, vorticity has $[\zeta]=\mathrm s^{-1}$, and a diffusivity has $[\kappa]=\mathrm m^2\,\mathrm s^{-1}$. Derivatives divide by the units of the independent variable. A logarithm or an exponential requires a dimensionless argument. For example, $\exp(-\kappa k^2t)$ is admissible when $k$ has units $\mathrm m^{-1}$.

## Vectors, bases, and linear maps

**Result and motivation.** A basis separates a mathematical object from the coefficients used to store it. Changing basis changes coefficients, while the underlying vector or field stays the same. Sources: [@ArfkenWeber2005, Sections 1.2-1.5, 3.2-3.4].

A vector space is a set closed under addition and multiplication by scalars, with associative and commutative addition, a zero vector, additive inverses, and the distributive rules. Vectors $\mathbf e_1,\ldots,\mathbf e_n$ are linearly independent if $\sum_jc_j\mathbf e_j=0$ implies every $c_j=0$. Their span is the set of all such linear combinations. They form a basis of a space if they are independent and span it. The number $n$ of basis vectors is its dimension.

In a real orthonormal Cartesian basis, the dot product and length are

$$
\mathbf u\cdot\mathbf v=\sum_{j=1}^{n}u_jv_j,
\qquad |\mathbf u|^2=\mathbf u\cdot\mathbf u.
\tag{1.2}
$$

Orthonormal means $\mathbf e_j\cdot\mathbf e_k=\delta_{jk}$, where the Kronecker symbol $\delta_{jk}$ is one for $j=k$ and zero otherwise. In three dimensions the cross product is the vector perpendicular to its arguments with components $(\mathbf u\times\mathbf v)_i=\sum_{j,k}\epsilon_{ijk}u_jv_k$. The permutation symbol $\epsilon_{ijk}$ is zero if an index repeats, $+1$ for an even permutation of $(1,2,3)$, and $-1$ for an odd permutation. Its sign fixes a right-handed orientation.

A map $A$ is linear if $A(\alpha\mathbf u+\beta\mathbf v)=\alpha A\mathbf u+\beta A\mathbf v$. A matrix represents that map in chosen input and output bases: $(A\mathbf u)_i=\sum_jA_{ij}u_j$. Matrix multiplication represents composition. The identity matrix $I$ leaves vectors unchanged. The nullspace is $\ker A=\{\mathbf u:A\mathbf u=0\}$; the range is the set of outputs. An inverse $A^{-1}$ exists precisely when a square map has zero nullspace and full range. The determinant $\det A$ is its signed volume factor; invertibility is equivalent to $\det A\ne0$.

For complex vectors use the inner product $\langle\mathbf u,\mathbf v\rangle=\sum_j u_j\overline{v_j}$, linear in its first argument throughout this guide. The adjoint matrix $A^*=\overline A^{\mathsf T}$ is the conjugate transpose. A Hermitian matrix has $A=A^*$; a unitary matrix has $A^*A=I$. Unitary changes of coordinates preserve inner products and norms. A real unitary matrix is called orthogonal.

## Eigenvectors, projection, and conditioning

**Result and motivation.** Hermitian operators admit orthogonal modes. In those modes differentiation, diffusion, and elliptic inversion become scalar calculations. Small eigenvalues also expose unstable inversions. Sources: [@ArfkenWeber2005, Sections 3.5-3.6, 10.2-10.3].

An eigenvector is a nonzero vector $\mathbf v$ such that $A\mathbf v=\lambda\mathbf v$; $\lambda$ is its eigenvalue. If $A=A^*$, then

$$
\lambda\|\mathbf v\|^2
=\langle A\mathbf v,\mathbf v\rangle
=\langle\mathbf v,A\mathbf v\rangle
=\overline\lambda\|\mathbf v\|^2.
\tag{1.3}
$$

Thus $\lambda$ is real. Applying the same identity to eigenvectors with eigenvalues $\lambda$ and $\eta$ gives $(\lambda-\eta)\langle\mathbf v,\mathbf w\rangle=0$; distinct eigenvalues have orthogonal eigenvectors. The finite-dimensional spectral theorem states that a Hermitian $A$ has an orthonormal eigenbasis: $A=Q\Lambda Q^*$, where $\Lambda$ is diagonal and $Q$ is unitary. This theorem is used here without proof; the differential analogue needs boundary conditions (Chapter 5).

For orthonormal $\mathbf e_j$, the projection onto their span is $P\mathbf u=\sum_j\langle\mathbf u,\mathbf e_j\rangle\mathbf e_j$. The remainder is orthogonal to every retained basis vector. Hence for any vector $\mathbf v$ in that span,

$$
\|\mathbf u-\mathbf v\|^2
=\|\mathbf u-P\mathbf u\|^2+\|P\mathbf u-\mathbf v\|^2.
\tag{1.4}
$$

Projection therefore minimizes squared error. This argument will apply unchanged to functions.

For invertible $A$, define $\sup$ as the least upper bound of a set of real numbers. Its induced norm is $\|A\|=\sup_{\mathbf v\ne0}\|A\mathbf v\|/\|\mathbf v\|$ and condition number $\operatorname{cond}(A)=\|A\|\|A^{-1}\|$. If $A\mathbf u=\mathbf b$ and only the right side changes by $\delta\mathbf b$, then $A\delta\mathbf u=\delta\mathbf b$ and

$$
\frac{\|\delta\mathbf u\|}{\|\mathbf u\|}
\le\operatorname{cond}(A)\frac{\|\delta\mathbf b\|}{\|\mathbf b\|}.
\tag{1.5}
$$

For $A=\operatorname{diag}(1,\varepsilon)$ with $0<\varepsilon\ll1$, noise in the second component is amplified by $1/\varepsilon$. A zero eigenvalue requires a compatibility condition and an additional choice fixing the nullspace component; division by zero is not an inversion method.

## Chapter summary and self-test

**Main results and terms.** A field has a domain, value type, and units. A basis defines coefficients; a linear map acts on vectors; its nullspace controls uniqueness. Complex conjugation defines a positive inner product. Hermitian matrices have real eigenvalues and orthonormal eigenbases. Orthogonal projection minimizes squared error by (1.4). Conditioning measures sensitivity through (1.5).

**Self-test.** Why does multiplying a complex Fourier coefficient by $e^{i\alpha}$ preserve its squared modulus? What prevents a unique solution of $\operatorname{diag}(1,0)\mathbf u=(1,1)$? Answers appear in the separate self-test answer section.

# Calculus, fluxes, and conservation {#ch-calculus}

## Derivatives, local linearization, and transport

**Result and motivation.** A derivative is a local linear approximation. Following a moving parcel introduces advection through the chain rule. Sources: [@ArfkenWeber2005, Sections 1.6, 5.5-5.7, 9.2].

For a scalar function $f(x)$, $f'(x)=\lim_{h\to0}[f(x+h)-f(x)]/h$ when this limit exists. A partial derivative $\partial_jf=\partial f/\partial x_j$ holds all other variables fixed. Write $f\in C^k$ if its derivatives through order $k$ exist and are continuous. The notation $r(h)=O(h^p)$ means $|r(h)|\le C|h|^p$ for a constant $C$ and sufficiently small $|h|$; $r(h)=o(h)$ means $r(h)/h\to0$.

A differentiable map $\mathbf F:\mathbb R^n\to\mathbb R^m$ has a Jacobian matrix $(D\mathbf F)_{ij}=\partial_jF_i$ satisfying $\mathbf F(\mathbf x+\mathbf h)=\mathbf F(\mathbf x)+D\mathbf F(\mathbf x)\mathbf h+o(|\mathbf h|)$. A scalar's gradient is the vector $\nabla f=(\partial_1f,\ldots,\partial_nf)$. Its Hessian $H_f$ is the matrix $(\partial_i\partial_jf)$. Taylor's theorem for $C^3$ functions gives

$$
f(\mathbf x+\mathbf h)=f(\mathbf x)+\nabla f\cdot\mathbf h
+\tfrac12\mathbf h^{\mathsf T}H_f\mathbf h+O(|\mathbf h|^3).
\tag{2.1}
$$

The Hessian is symmetric for $C^2$ functions because mixed partial derivatives commute. A critical point has $\nabla f=0$; a positive-definite Hessian at a critical point, meaning $\mathbf h^{\mathsf T}H_f\mathbf h>0$ for every nonzero $\mathbf h$, implies a strict local minimum.

For differentiable one-variable functions, the product rule is $(fg)'=f'g+fg'$ and the chain rule is $(f\circ g)'(x)=f'(g(x))g'(x)$, where $f\circ g$ means composition. The familiar derivatives $(e^x)'=e^x$, $(\sin x)'=\cos x$, and $(\cos x)'=-\sin x$ follow from their defining series. A definite integral $\int_a^b f(x)dx$ is the limit of sums $\sum_j f(\xi_j)\Delta x_j$ as the largest partition width tends to zero, for continuous $f$; $\xi_j$ is a point in the $j$th subinterval. The fundamental theorem of calculus and the product rule give

$$
F'(x)=f(x)\ \Longrightarrow\ \int_a^b f(x)dx=F(b)-F(a),
\qquad
\int_a^b f g'\,dx=[fg]_a^b-\int_a^b f'g\,dx.
\tag{2.2}
$$

Here $[h]_a^b=h(b)-h(a)$; the second identity is integration by parts. For example, take $f=x$, $g'=e^x$, $g=e^x$ to obtain $\int_0^1xe^x dx=[xe^x]_0^1-\int_0^1e^x dx=e-(e-1)=1$. The multivariable chain rule is the same local-linearization rule applied to a trajectory.

Let $\mathbf X(t)$ be a parcel trajectory with $d\mathbf X/dt=\mathbf u(\mathbf X,t)$. Applying the chain rule to $q(\mathbf X(t),t)$ gives the material derivative

$$
\frac{Dq}{Dt}:=\frac{d}{dt}q(\mathbf X(t),t)
=\partial_tq+\mathbf u\cdot\nabla q.
\tag{2.3}
$$

The symbol $:=$ means "is defined as." Local change $\partial_tq$ is measured at a fixed location; advection $\mathbf u\cdot\nabla q$ measures motion across spatial gradients. For constant speed $c$, $q(x,t)=q_0(x-ct)$ satisfies $\partial_tq+c\partial_xq=0$ even while a fixed sensor sees a changing signal.

## Gradient, divergence, curl, and Laplacian

**Result and motivation.** Gradient measures directional change, divergence measures outward flux density, and curl measures circulation density. The scalar Laplacian is the divergence of a gradient. Sources: [@ArfkenWeber2005, Sections 1.6-1.9].

In right-handed Cartesian coordinates and for a $C^1$ vector field $\mathbf F=(F_1,F_2,F_3)$, define

$$
\nabla\cdot\mathbf F=\sum_i\partial_iF_i,
\qquad (\nabla\times\mathbf F)_i=\sum_{j,k}\epsilon_{ijk}\partial_jF_k,
\qquad \Delta q=\nabla\cdot\nabla q=\sum_i\partial_i^2q.
\tag{2.4}
$$

For a unit direction $\mathbf n$, $\mathbf n\cdot\nabla q$ is change per unit distance along $\mathbf n$. For velocity, $\nabla\cdot\mathbf u>0$ means a small parcel expands. The vorticity $\boldsymbol\omega=\nabla\times\mathbf u$ measures twice the local rigid rotation rate. Solid-body planar rotation $\mathbf u=(-\Omega y,\Omega x,0)$ has $\nabla\cdot\mathbf u=0$ and $\boldsymbol\omega=(0,0,2\Omega)$; circulation is not the same as speed.

Product differentiation and commuting mixed derivatives give

$$
\begin{aligned}
\nabla\cdot(q\mathbf F)&=\nabla q\cdot\mathbf F+q\nabla\cdot\mathbf F,\\
\nabla\times\nabla q&=0,\qquad \nabla\cdot(\nabla\times\mathbf F)=0,\\
\nabla\times(\nabla\times\mathbf F)&=\nabla(\nabla\cdot\mathbf F)-\Delta\mathbf F.
\end{aligned}
\tag{2.5}
$$

The vector Laplacian in the last line acts on Cartesian components. These identities assume enough continuous derivatives. Curvilinear components require basis-variation terms; differentiating each spherical component as a Cartesian scalar is generally incorrect.

## Integration, Jacobians, and integral theorems

**Result and motivation.** Conservation laws relate what crosses a boundary to what changes inside. Correct integration also fixes the weights in global means. Sources: [@ArfkenWeber2005, Sections 1.10-1.12, 2.1-2.2].

An integral sums a density over lengths, areas, or volumes. Write $dV$ for volume, $dA$ for surface area, and $d\mathbf l$ for an oriented tangent line element. Let $V\subset\mathbb R^3$ have a piecewise smooth closed boundary $\partial V$ with outward unit normal $\mathbf n$. The divergence theorem is

$$
\int_V\nabla\cdot\mathbf F\,dV
=\int_{\partial V}\mathbf F\cdot\mathbf n\,dA.
\tag{2.6}
$$

For an oriented smooth surface $S$ with boundary curve $\partial S$, oriented by the right-hand rule, Stokes' theorem is

$$
\int_S(\nabla\times\mathbf F)\cdot\mathbf n\,dA
=\oint_{\partial S}\mathbf F\cdot d\mathbf l.
\tag{2.7}
$$

The circle on $\oint$ denotes integration around a closed curve. These identities require fields regular on the integration region; a singular vortex cannot be ignored inside it.

A smooth invertible coordinate map $\mathbf x=\mathbf X(\mathbf q)$ changes volume by

$$
dV=\left|\det D\mathbf X(\mathbf q)\right|\,dq_1dq_2dq_3.
\tag{2.8}
$$

The determinant is the Jacobian factor: a small coordinate box maps to a parallelepiped spanned by $\partial_{q_i}\mathbf X\,dq_i$. On a surface parametrized by $(a,b)$, its area factor is $|\partial_a\mathbf X\times\partial_b\mathbf X|$. Coordinates are labels; these factors convert labels into physical measure.

Substitute $\mathbf F=f\nabla g$ in (2.6), with real $C^2$ functions $f,g$, to obtain Green's first identity,

$$
\int_V f\Delta g\,dV
=\int_{\partial V}f\partial_ng\,dA-\int_V\nabla f\cdot\nabla g\,dV,
\qquad \partial_ng=\mathbf n\cdot\nabla g.
\tag{2.9}
$$

This is multidimensional integration by parts. For complex $f$, replace $f$ by $\overline f$ when constructing energy or adjoint identities. A boundary condition determines whether the boundary term vanishes.

## From a balance law to a PDE

**Result and motivation.** A local conservation PDE is the differential form of a balance for every fixed control volume. It distinguishes transport from sources. Sources: [@ArfkenWeber2005, Sections 1.7, 1.11, 9.8]; fluid interpretation: [@Vallis2006, Sections 1.2, 1.7].

Let $q$ be amount per unit volume, $\mathbf J$ its flux (amount per area per time), and $s$ its production per volume per time. For a fixed $V$,

$$
\frac{d}{dt}\int_Vq\,dV=-\int_{\partial V}\mathbf J\cdot\mathbf n\,dA+\int_Vs\,dV
\quad\Longrightarrow\quad
\partial_tq+\nabla\cdot\mathbf J=s.
\tag{2.10}
$$

The implication uses (2.6) and the fact that the integral of a continuous function over every small volume vanishes only if that function is zero. For an advected concentration with diffusion, $\mathbf J=q\mathbf u-\kappa\nabla q$. Constant $\kappa$ gives

$$
\partial_tq+\mathbf u\cdot\nabla q+q\nabla\cdot\mathbf u
=\kappa\Delta q+s.
\tag{2.11}
$$

When $\nabla\cdot\mathbf u=0$, conservative and advective forms agree. Otherwise the compression term matters. A concentration per volume differs from a mixing ratio per unit mass; the latter uses mass continuity in its transport equation.

## Chapter summary and self-test

**Main results and terms.** The Jacobian is the local derivative map and its determinant changes volume. The gradient, divergence, curl, and Laplacian have the meanings in (2.4). The material derivative (2.3) follows parcels. Divergence and Stokes' theorems convert volume or surface integrals to boundary flux or circulation. Green's identity (2.9) controls energy and adjoints. Equation (2.10) connects integral conservation with a local PDE.

**Self-test.** Derive $\partial_t\rho+\nabla\cdot(\rho\mathbf u)=0$ for mass density $\rho$. Under what condition does it imply $D\rho/Dt=0$? Why is no source needed for the translating-profile example above?

# Geometry and calculus on the sphere {#ch-sphere}

## Coordinates, metric factors, and area

**Result and motivation.** Spherical coordinates have unequal physical scale factors. The area measure becomes uniform in sine of latitude, which explains Gaussian latitude weights. Sources: [@ArfkenWeber2005, Sections 2.1-2.2, 2.5].

Let $r>0$ be radius, $\theta\in[0,\pi]$ colatitude measured from the north pole, and $\lambda\in[0,2\pi)$ east longitude. Latitude is $\varphi=\pi/2-\theta$. Write

$$
\mathbf x=r(\sin\theta\cos\lambda,\sin\theta\sin\lambda,\cos\theta),
\qquad \mu=\cos\theta=\sin\varphi.
\tag{3.1}
$$

The unit vectors $\mathbf e_r,\mathbf e_\theta,\mathbf e_\lambda$ point toward increasing coordinates. Differentiating (3.1) gives mutually perpendicular vectors of lengths $1,r,r\sin\theta$. These are scale factors $h_i=|\partial_{q_i}\mathbf x|$. The metric is the rule for squared distance:

$$
ds^2=dr^2+r^2d\theta^2+r^2\sin^2\theta\,d\lambda^2,
\qquad dV=r^2\sin\theta\,dr\,d\theta\,d\lambda.
\tag{3.2}
$$

On the radius-$R$ sphere $S_R^2=\{\mathbf x:|\mathbf x|=R\}$, use solid angle $d\Omega=dA/R^2$. Then

$$
dA=R^2\sin\theta\,d\theta\,d\lambda
=R^2\cos\varphi\,d\varphi\,d\lambda,
\qquad
\int_{S_R^2}q\,dA=R^2\int_{-1}^1\int_0^{2\pi}q(\mu,\lambda)\,d\lambda\,d\mu.
\tag{3.3}
$$

The last equality reverses the $\mu$ bounds to absorb $d\mu=-\sin\theta\,d\theta$. It uses a positive area measure, not an oriented two-form. The total area is $4\pi R^2$. For $q=\mu^2$, its global area mean is $\frac12\int_{-1}^1\mu^2\,d\mu=1/3$; equal weights on equally spaced latitudes would give a different average.

## Tangent differential operators

**Result and motivation.** Physical derivatives divide coordinate derivatives by arc lengths. These scale factors determine the spherical Laplacian and the correct signs of wind and vorticity. Sources: [@ArfkenWeber2005, Sections 2.2, 2.5].

The surface gradient $\nabla_s q$ is tangent to the sphere and satisfies $dq=\nabla_s q\cdot d\mathbf x$ for tangent displacements. For $\mathbf F=F_\theta\mathbf e_\theta+F_\lambda\mathbf e_\lambda$, where $F_\theta,F_\lambda$ are physical components, one obtains

$$
\begin{aligned}
\nabla_s q&=\frac{\mathbf e_\theta}{R}\partial_\theta q
+\frac{\mathbf e_\lambda}{R\sin\theta}\partial_\lambda q,\\
\nabla_s\cdot\mathbf F&=\frac{1}{R\sin\theta}
\left[\partial_\theta(\sin\theta F_\theta)+\partial_\lambda F_\lambda\right],\\
(\nabla\times\mathbf F)\cdot\mathbf e_r&=\frac{1}{R\sin\theta}
\left[\partial_\theta(\sin\theta F_\lambda)-\partial_\lambda F_\theta\right].
\end{aligned}
\tag{3.4}
$$

For the divergence formula, consider a small patch with sides $R\,d\theta$ and $R\sin\theta\,d\lambda$. The difference of meridional fluxes through its latitude edges is $R\partial_\theta(\sin\theta F_\theta)d\theta d\lambda$; the longitude edges contribute $R\partial_\lambda F_\lambda d\theta d\lambda$. Divide by patch area. Applying Stokes' theorem to the same patch yields the curl formula, with counterclockwise orientation viewed from outside.

The Laplace-Beltrami operator is the surface divergence of the surface gradient:

$$
\Delta_s q:=\nabla_s\cdot\nabla_s q
=\frac1{R^2}\left[\frac1{\sin\theta}\partial_\theta(\sin\theta\partial_\theta q)
+\frac1{\sin^2\theta}\partial_\lambda^2q\right].
\tag{3.5}
$$

Define the dimensionless angular operator $\Delta_\Omega=R^2\Delta_s$. In latitude and in $\mu$,

$$
\Delta_s q=\frac1{R^2\cos\varphi}\partial_\varphi(\cos\varphi\partial_\varphi q)
+\frac1{R^2\cos^2\varphi}\partial_\lambda^2q
=\frac1{R^2}\left[\partial_\mu((1-\mu^2)\partial_\mu q)
+\frac{\partial_\lambda^2q}{1-\mu^2}\right].
\tag{3.6}
$$

In three-dimensional space, the full scalar Laplacian is $\Delta q=r^{-2}\partial_r(r^2\partial_rq)+r^{-2}\Delta_\Omega q$. Restricting to a surface and assuming radial independence are distinct operations; (3.5) is intrinsic to the surface. Its units are field units divided by $\mathrm m^2$.

## Regularity, streamfunction, and the closed surface

**Result and motivation.** Poles are coordinate singularities, not physical edges. A smooth nondivergent tangent velocity on the sphere has a streamfunction whose mean is arbitrary. Sources: [@ArfkenWeber2005, Sections 1.16, 2.5, 12.11]; fluid application: [@Vallis2006, Sections 2.2, 4.5].

All longitudes at a pole describe one point. A smooth scalar has a unique value there; nonzero longitude Fourier orders must vanish at the poles with the behavior derived in Chapter 8. The local tangent basis itself depends on longitude, so smooth vector components need not be longitude-independent at a pole. Smoothness is a geometric condition, not a command to set all derivatives to zero.

For a smooth real streamfunction $\psi$ with units $\mathrm m^2\,\mathrm s^{-1}$, set $\mathbf u=\mathbf e_r\times\nabla_s\psi$. Let $u$ be eastward speed and $v$ northward speed, so $F_\lambda=u$ and $F_\theta=-v$. Equation (3.4) gives

$$
u=-\frac1R\partial_\varphi\psi,
\qquad v=\frac1{R\cos\varphi}\partial_\lambda\psi,
\qquad \nabla_s\cdot\mathbf u=0,
\qquad \zeta:=(\nabla\times\mathbf u)\cdot\mathbf e_r=\Delta_s\psi.
\tag{3.7}
$$

To check divergence, substitute the first two expressions into $[\partial_\lambda u+\partial_\varphi(v\cos\varphi)]/(R\cos\varphi)$; the mixed partials cancel. Substituting into the radial curl yields (3.6). Adding a spatial constant to $\psi$ changes neither speed nor vorticity. The converse for every smooth divergence-free tangent field on the whole sphere is justified by the potential decomposition in Section 8.4. Until then, (3.7) defines the velocity class considered. Domains with holes can require additional circulation modes.

Surface integration by parts has no external boundary term:

$$
\int_{S_R^2}f\Delta_sg\,dA=-\int_{S_R^2}\nabla_sf\cdot\nabla_sg\,dA,
\qquad \int_{S_R^2}\Delta_sg\,dA=0.
\tag{3.8}
$$

Here $f,g$ are smooth real scalars. The second identity uses $f=1$. Thus $\Delta_sg=h$ requires zero area integral of $h$. The coordinate cuts at longitude $0$ and the poles are not physical boundaries; periodicity and regularity cancel their apparent terms.

## Chapter summary and self-test

**Main results and terms.** Colatitude $\theta$, latitude $\varphi$, and longitude $\lambda$ follow (3.1); $\mu=\sin\varphi$. Scale factors define distance, area, and differential operators. Area is uniform in $(\mu,\lambda)$, not $(\varphi,\lambda)$. The physical Laplace-Beltrami operator is $\Delta_s=R^{-2}\Delta_\Omega$. With the convention $\mathbf u=\mathbf e_r\times\nabla_s\psi$, vorticity is $\zeta=\Delta_s\psi$. The Laplacian has zero integral and a constant nullspace.

**Self-test.** Verify $\Delta_s\mu=-2\mu/R^2$. If $\psi=A\sin\varphi$, find $u$, $v$, and $\zeta$, including their units.

# Function spaces, limits, and weak derivatives {#ch-spaces}

## Norms, inner products, and convergence

**Result and motivation.** A function expansion is meaningful only after specifying the measure and the kind of convergence. Mean-square accuracy does not imply accuracy at every point or of every derivative. Sources: [@ArfkenWeber2005, Sections 5.5, 10.2-10.4, 14.1, 14.4].

Let $D$ be an interval, a spatial region, or a sphere, with positive integration measure $d\nu$ (for example $dx$, $dV$, or $d\Omega$). A norm $\|\cdot\|$ is nonnegative, zero only on the zero element, homogeneous ($\|af\|=|a|\|f\|$), and obeys the triangle inequality. For $1\le p<\infty$, define

$$
L^p(D,d\nu)=\left\{f:\int_D|f|^p\,d\nu<\infty\right\},
\qquad \|f\|_p=\left(\int_D|f|^p\,d\nu\right)^{1/p}.
\tag{4.1}
$$

Functions here are measurable, meaning their level sets can be assigned the chosen measure. Functions that differ only on a set of measure zero are identified. "Almost everywhere" means except on such a set. For $L^\infty$, the norm is the essential supremum: the smallest bound valid almost everywhere. These identifications make the integral norms genuine norms. We use the standard completeness of $L^p$ without a measure-theoretic proof.

For complex functions choose

$$
\langle f,g\rangle=\int_D f\overline g\,d\nu,
\qquad \|f\|_2^2=\langle f,f\rangle,
\qquad |\langle f,g\rangle|\le\|f\|_2\|g\|_2.
\tag{4.2}
$$

The final statement is Cauchy-Schwarz. To derive it when $g\ne0$, set $a=\langle f,g\rangle/\|g\|_2^2$ and expand $0\le\|f-ag\|_2^2=\|f\|_2^2-|\langle f,g\rangle|^2/\|g\|_2^2$. A positive weight $w(x)$ defines $d\nu=w(x)dx$; changing $w$ changes orthogonality, projections, and losses.

A sequence $f_n$ converges in $L^2$ to $f$ if $\|f_n-f\|_2\to0$. It converges pointwise if $f_n(x)\to f(x)$ at each $x$, and uniformly if $\sup_x|f_n(x)-f(x)|\to0$. On a finite-measure domain, uniform convergence implies $L^2$ convergence because $\|f_n-f\|_2^2\le\nu(D)\sup|f_n-f|^2$. The reverse fails: a triangular pulse of height one and width $1/n$ has vanishing $L^2$ norm but no vanishing maximum.

A sequence is Cauchy if $\|f_n-f_m\|\to0$ as both indices grow. A space is complete when every Cauchy sequence has a limit in it. A Hilbert space is a complete inner product space. $L^2$ is Hilbert; continuous functions with the $L^2$ norm are not complete, because increasingly sharp continuous transitions can converge in that norm to a step.

## Orthogonal expansions and approximation

**Result and motivation.** An orthonormal basis converts squared function error into a sum of squared coefficient errors. Truncation is the best approximation in the chosen norm, rather than a claim of pointwise exactness. Sources: [@ArfkenWeber2005, Sections 10.3-10.4].

Functions $e_j$ are orthonormal if $\langle e_j,e_k\rangle=\delta_{jk}$. A complete orthonormal system has no nonzero function orthogonal to all its members. For such a system in a Hilbert space, define coefficients $c_j=\langle f,e_j\rangle$ and projection $P_Nf=\sum_{j=1}^Nc_je_j$. Orthogonality gives

$$
\|f-P_Nf\|_2^2=\|f\|_2^2-\sum_{j=1}^N|c_j|^2,
\qquad \|f\|_2^2=\sum_{j=1}^{\infty}|c_j|^2.
\tag{4.3}
$$

The first identity implies Bessel's inequality $\sum_j|c_j|^2\le\|f\|_2^2$ even for an incomplete orthonormal system. Completeness makes the remainder converge to zero and yields the second identity, Parseval's identity. Applying the Pythagorean argument (1.4) shows that $P_Nf$ minimizes error over the retained span. Completeness of Fourier and spherical harmonic systems is a theorem, used below rather than inferred from orthogonality alone.

For independent functions $f_j$, Gram-Schmidt constructs an orthonormal system by

$$
g_n=f_n-\sum_{j<n}\langle f_n,e_j\rangle e_j,
\qquad e_n=g_n/\|g_n\|_2.
\tag{4.4}
$$

For example, with normalized measure $d\mu/2$ on $[-1,1]$, the functions $1$, $\sqrt3\mu$, and $\frac{\sqrt5}{2}(3\mu^2-1)$ are orthonormal. Their normalization differs from that under $d\mu$. This distinction explains factors of $2$ and $4\pi$ in latitude and spherical expansions.

## Distributions, weak derivatives, and energy spaces

**Result and motivation.** Weak derivatives transfer differentiation to smooth test functions. They describe finite-energy fields and point sources without pretending that every solution is classically smooth. Sources: [@ArfkenWeber2005, Sections 1.15, 9.7, 10.5]; the $H^1$ definition follows [@HunterPDE, Sections 3.5 and 3.9].

A test function $\eta\in C_c^\infty(D)$ is infinitely differentiable and zero outside a closed bounded subset lying inside $D$ (compact support). A distribution $T$ is a linear rule assigning a scalar $T[\eta]$ to each test function, continuous in the following sense: if all test functions have support in one fixed compact subset and every derivative converges uniformly to zero, their values under $T$ tend to zero. A locally integrable function (one integrable on every compact subset of $D$) defines $T_f[\eta]=\int_D f\eta$. The Dirac delta at $x_0$ is the distribution $\delta_{x_0}[\eta]=\eta(x_0)$; it is not an ordinary function of infinite height. In one dimension,

$$
T_f'[\eta]=-T_f[\eta'],\qquad
\int f\eta'=-\int g\eta\ \Longrightarrow\ g=\partial_x f
\text{ in the weak sense}.
\tag{4.5}
$$

The integral equality must hold for every test function $\eta$. There is no boundary term because the test function vanishes near the boundary. For the step $H(x)=0$ for $x<0$, $H(x)=1$ for $x>0$,
$T_H'[\eta]=-\int_0^\infty\eta'(x)dx=\eta(0)$, so $H'=\delta_0$ as distributions. Values at $x=0$ do not affect this identity.

The Sobolev space $H^1(D)$ consists of $L^2$ functions whose first weak partial derivatives are also in $L^2$. With dimensionless coordinates, its norm is $\|f\|_{H^1}^2=\|f\|_2^2+\sum_j\|\partial_jf\|_2^2$. With dimensional coordinates one can insert a reference length squared on the derivative terms; otherwise the displayed sum mixes units. $H_0^1(D)$ consists of all limits in the $H^1$ norm of sequences of compactly supported smooth functions. On a sufficiently regular bounded domain it encodes zero boundary values. This functional-analytic notation is an explicit extension of AW's energy and integration-by-parts methods; no general Sobolev embedding theorem is needed here.

On the dimensionless $2\pi$-periodic coordinate $x$, $f_n(x)=\sin(nx)/n$ tends uniformly to zero, but $f_n'(x)=\cos(nx)$ does not tend to zero in $L^2$. An $L^2$ approximation to a field does not by itself control gradients, wind inferred from a streamfunction, or vorticity inferred from wind.

## Chapter summary and self-test

**Main results and terms.** The measure belongs to the definition of an $L^p$ norm. A Hilbert space is complete with an inner product. Pointwise, uniform, and norm convergence are distinct. Projection, Bessel's inequality, and Parseval follow from orthogonality plus the appropriate completeness assumption. A distribution acts on test functions; a weak derivative is defined by integration by parts. $H^1$ controls both the field and its first derivatives.

**Self-test.** Show that $\sqrt3\mu$ has norm one under $d\mu/2$. Why does small $L^2$ error in a streamfunction fail to guarantee small wind error? Which object is the derivative of a step?

# Differential equations and eigenfunction theory {#ch-odes}

## Initial-value equations and integrating factors

**Result and motivation.** Linear evolution balances forcing against a response kernel. The same integrating-factor formula solves a single spectral mode of a PDE. Sources: [@ArfkenWeber2005, Sections 9.2, 9.7].

An ordinary differential equation (ODE) relates an unknown function of one independent variable to its derivatives. Its order is the highest derivative present. An initial condition specifies its state at an initial time. A linear equation has the unknown and its derivatives only to the first power, with coefficients independent of that unknown. "Homogeneous" means zero forcing.

Let $a(t)$ be an unknown scalar amplitude, $\gamma(t)$ a known decay rate, $b(t)$ a known forcing, and $a(0)=a_0$. Define $I(t)=\exp(\int_0^t\gamma(s)ds)$. Since $I'=\gamma I$,

$$
a'+\gamma a=b
\quad\Longrightarrow\quad
(Ia)'=Ib
\quad\Longrightarrow\quad
a(t)=I(t)^{-1}\left[a_0+\int_0^t I(s)b(s)ds\right].
\tag{5.1}
$$

For constant $\gamma$, this is $a(t)=a_0e^{-\gamma t}+\int_0^t e^{-\gamma(t-s)}b(s)ds$. Positive real $\gamma$ damps an initial perturbation; purely imaginary $\gamma$ changes phase; negative real $\gamma$ amplifies it. These statements concern the homogeneous response. Nonzero forcing can sustain a nonzero state.

For a vector state, $\mathbf a'=A\mathbf a$ has solution $\mathbf a(t)=e^{tA}\mathbf a(0)$, where $e^{tA}=\sum_{n\ge0}t^nA^n/n!$. If $A$ has an eigenbasis, each eigencomponent evolves as $e^{\lambda_jt}$. Eigenvalues alone need not describe transient growth for a nonnormal matrix ($AA^*\ne A^*A$); we use orthogonal diagonalization only when its hypotheses hold.

## Boundary conditions and Sturm-Liouville operators

**Result and motivation.** An operator includes its domain and boundary conditions. Self-adjoint boundary conditions produce real eigenvalues and orthogonal eigenfunctions. Sources: [@ArfkenWeber2005, Sections 9.3, 10.1-10.2].

On a finite interval $[a,b]$, let real $p,p',q,w$ be continuous with $p>0$ and $w>0$. Define

$$
\mathcal Ly=\frac1w\left[-(py')'+qy\right],
\qquad \mathcal Ly=\lambda y,
\qquad \langle f,g\rangle_w=\int_a^bf\overline g\,w\,dx.
\tag{5.2}
$$

The functions admitted by an operator, including their boundary conditions, form its domain. Dirichlet conditions specify $y$ at an endpoint; Neumann conditions specify its normal derivative; Robin conditions specify a linear combination. For homogeneous separated conditions use $\alpha_ay(a)+\beta_ap(a)y'(a)=0$ and $\alpha_by(b)+\beta_bp(b)y'(b)=0$, with real coefficient pairs not both zero. Integration by parts gives

$$
\langle\mathcal Lf,g\rangle_w-\langle f,\mathcal Lg\rangle_w
=\left[p(f\overline{g'}-f'\overline g)\right]_a^b=0.
\tag{5.3}
$$

Here $[h]_a^b=h(b)-h(a)$. The separated boundary conditions make each endpoint bracket zero. Matching periodic $y$ and $py'$ also cancels it. This proves symmetry; the regular Sturm-Liouville realization with these conditions is self-adjoint (its operator domain equals that of its adjoint). For a general unbounded differential operator, formal symmetry alone would not establish this stronger statement.

Apply (5.3) to eigenfunctions $y_j,y_k$. The argument in (1.3) gives real $\lambda_j$ and

$$
(\lambda_j-\lambda_k)\int_a^b y_j\overline{y_k}w\,dx=0.
\tag{5.4}
$$

The regular Sturm-Liouville theorem further gives a complete orthonormal eigenbasis in $L_w^2$, a discrete spectrum bounded below, and eigenvalues tending to $+\infty$. These existence and completeness assertions are quoted from AW, Chapter 10; orthogonality has just been derived. Singular endpoints, such as $p=1-x^2=0$ at $x=\pm1$, require separate endpoint regularity conditions and cannot be covered by pretending $p>0$ on the closed interval.

## Separation of variables and spectral solution

**Result and motivation.** Separation turns a linear PDE with compatible geometry into a spatial eigenproblem and scalar time equations. The spatial boundary conditions select the allowed modes. Sources: [@ArfkenWeber2005, Sections 9.3, 9.8, 10.4].

Consider diffusion on $0<x<d$, where $d>0$ is the interval length, $\kappa>0$, $u(0,t)=u(d,t)=0$, and $u(x,0)=u_0(x)$ with $u_0\in L^2(0,d)$. Seek a product $u=X(x)T(t)$. Dividing $XT'=\kappa X''T$ by $\kappa XT$ where nonzero yields $T'/(\kappa T)=X''/X=-\lambda$, because one side depends only on time and the other only on space. Thus

$$
-X''=\lambda X,\quad X(0)=X(d)=0,
\qquad T'=-\kappa\lambda T.
\tag{5.5}
$$

A nonzero eigenfunction requires $\lambda_n=(n\pi/d)^2$ and $X_n=\sqrt{2/d}\sin(n\pi x/d)$, $n=1,2,\ldots$. For $\lambda=0$ the linear solution vanishes at both endpoints only if zero; for $\lambda<0$ the exponential solutions likewise give no nonzero Dirichlet mode. Expanding the initial condition gives

$$
u(x,t)=\sum_{n=1}^{\infty}a_n e^{-\kappa\lambda_nt}X_n(x),
\qquad a_n=\int_0^d u_0(x)X_n(x)dx.
\tag{5.6}
$$

This holds in $L^2$ at $t=0$ and is smooth in the interior for $t>0$. High modes decay faster. Neumann endpoints instead admit a constant mode with eigenvalue zero, so the spatial mean persists.

## Green's functions and solvability

**Result and motivation.** A Green's function is the response to a point source with specified boundary conditions. A zero eigenvalue replaces ordinary inversion with a compatibility condition. Sources: [@ArfkenWeber2005, Sections 1.15, 9.7, 10.5].

For $\mathcal L$ with orthonormal eigenfunctions $e_n$ in measure $d\nu$ and nonzero eigenvalues $\lambda_n$, solving $\mathcal Lu=f$ gives $u_n=f_n/\lambda_n$. Formally, or in the appropriate distributional sense,

$$
G(x,y)=\sum_n\frac{e_n(x)\overline{e_n(y)}}{\lambda_n},
\qquad u(x)=\int G(x,y)f(y)d\nu(y).
\tag{5.7}
$$

The delta identity for this measure is $\int\delta_\nu(x,y)f(y)d\nu(y)=f(x)$. Then $\mathcal L_xG=\delta_\nu$. If $\lambda_0=0$ with normalized eigenfunction $e_0$, solvability requires $\langle f,e_0\rangle=0$. Excluding that mode gives $\mathcal L_xG=\delta_\nu-e_0(x)\overline{e_0(y)}$. Set $u_0=0$ to choose one solution.

For a direct check, on $0<x<d$ the Dirichlet Green's function of $-d^2/dx^2$ is $G(x,y)=x_<(d-x_>)/d$, where $x_<=\min(x,y)$ and $x_>=\max(x,y)$. It vanishes at the endpoints, is continuous at $x=y$, and its derivative in $x$ jumps by $-1$. Therefore $-\partial_x^2G=\delta(x-y)$, with the required sign.

## Chapter summary and self-test

**Main results and terms.** The integrating factor gives the forced modal solution (5.1). Initial conditions specify a state; boundary conditions restrict spatial behavior. A regular self-adjoint Sturm-Liouville operator has real eigenvalues and a complete weighted orthonormal eigenbasis. Separation yields spatial eigenvalues and time factors as in (5.5)-(5.6). A Green's function is a kernel for inversion; nullspace components require compatibility and a normalization.

**Self-test.** For $u_0=\sin(2\pi x/d)$ in (5.6), what is the decay time? Why can $-u''=1$ on a periodic interval have no periodic solution?

# Partial differential equations and physical models {#ch-pdes}

## Order, classification, and well-posedness

**Result and motivation.** A PDE is defined by its differential equation together with its domain and data. Elliptic, parabolic, and hyperbolic equations ask different kinds of physical questions. Sources: [@ArfkenWeber2005, Sections 9.1, 9.3, 9.8].

A partial differential equation (PDE) relates a field of several independent variables to its partial derivatives. Its order is the highest derivative order. A PDE is linear if it has the form $Lu=f$ with $L$ linear and $f$ prescribed. A nonlinear term such as $u\partial_xu$ makes superposition invalid: the sum of solutions need not be a solution.

For a real second-order scalar equation in two variables whose highest-order part is $A u_{xx}+2B u_{xy}+C u_{yy}$, the sign of $B^2-AC$ classifies that part as elliptic if negative, parabolic if zero, or hyperbolic if positive. Coefficients can depend on position; the classification can change with position. More general systems use their principal symbol, the polynomial formed from the highest-order derivatives by replacing derivatives with frequency components. The two-variable discriminant is not a universal classification rule for all evolution equations.

The prototypes are

$$
-\Delta u=f\quad\text{(Poisson)},\qquad
\partial_tu=\kappa\Delta u\quad\text{(diffusion)},\qquad
\partial_t^2u=c^2\Delta u\quad\text{(wave)}.
\tag{6.1}
$$

Here $\kappa>0$ is diffusivity and $c>0$ wave speed. Poisson's equation determines a spatial balance from boundary data. Diffusion takes one initial field. The wave equation takes both initial displacement and initial velocity. Advection $\partial_tu+\mathbf v\cdot\nabla u=0$ is first-order transport along trajectories; inflow boundaries specify arriving values, not arbitrary data on all boundaries.

A problem is well posed in a chosen norm if a solution exists, is unique, and depends continuously on its data. This is a property of the full initial/boundary-value problem. A formula alone does not guarantee it. For backward diffusion, a Fourier mode grows as $e^{\kappa k^2t}$; arbitrarily small high-frequency errors can grow without bound, so this inverse-time problem is not continuously stable in $L^2$.

## Energy estimates, uniqueness, and weak formulation

**Result and motivation.** Multiplication by the solution and integration by parts can prove decay and uniqueness without knowing a closed-form solution. Sources: [@ArfkenWeber2005, Sections 1.13-1.14, 9.8, 10.2, 17.4].

On a bounded smooth domain $D$, take real diffusion with zero Dirichlet data, homogeneous Neumann data, or matching periodic data, so boundary terms vanish. Define squared-amplitude energy $E(t)=\frac12\int_Du^2dV$. Equations (2.9) and (6.1) imply

$$
\frac{dE}{dt}=\int_Du\partial_tu\,dV
=\kappa\int_Du\Delta u\,dV
=-\kappa\int_D|\nabla u|^2dV\le0.
\tag{6.2}
$$

This is a mathematical energy; its physical units depend on $u$. For two solutions with the same forcing and data, their difference obeys the homogeneous equation and starts with zero energy. Equation (6.2) keeps that difference zero, proving uniqueness and a contraction estimate. A nonzero boundary flux would enter the budget rather than vanish.

For real $f\in L^2(D)$, $-\Delta u=f$, and zero Dirichlet data, a weak solution $u\in H_0^1(D)$ satisfies

$$
\int_D\nabla u\cdot\nabla\eta\,dV=\int_Df\eta\,dV
\quad\text{for every real }\eta\in H_0^1(D).
\tag{6.3}
$$

Only one weak derivative of $u$ is required. The same equation comes from stationarity of the functional (a map from functions to numbers)
$\mathcal J[u]=\frac12\int|\nabla u|^2-\int fu$: substitute $u+\varepsilon\eta$, differentiate with respect to the real parameter $\varepsilon$ at zero, and set the result to zero. The positive quadratic term makes this the energy minimization principle under the stated boundary constraints. For a bounded smooth domain and $f\in L^2(D)$, existence and uniqueness in $H_0^1(D)$ are a separate weak Dirichlet theorem [@HunterPDE, Section 4.5]. The variation derives the equation; it does not prove that theorem.

With Neumann data $\partial_nu=g$, integrate $-\Delta u=f$ to obtain the necessary compatibility condition $\int_Df\,dV=-\int_{\partial D}g\,dA$. A constant can still be added to $u$. On a closed sphere the corresponding condition is zero integral of $f$.

## Characteristics, waves, and dispersion

**Result and motivation.** Characteristics track transport; dispersion describes the frequency-dependent phase of waves. These notions explain why diffusion smooths while advection moves patterns. Sources: [@ArfkenWeber2005, Sections 9.1-9.3, 15.4, 15.7].

For $\partial_tu+c\partial_xu=0$ with constant real $c$, the curves $x(t)=x_0+ct$ have $du(x(t),t)/dt=0$, so $u(x,t)=u_0(x-ct)$. These curves are characteristics. In contrast, $u_t+uu_x=0$ carries each initial value at its own speed; characteristics can cross, after which a classical differentiable solution fails and a conservation-law weak solution needs an additional admissibility rule. No such shock theory is assumed below.

A plane wave has the form $u=Ae^{i(kx-\omega t)}$, where $A$ is amplitude, $k$ angular wavenumber, and $\omega$ angular frequency. Substituting into $u_{tt}=c^2u_{xx}$ gives

$$
\omega^2=c^2k^2,\qquad c_{\rm phase}=\omega/k,
\qquad c_{\rm group}=d\omega/dk.
\tag{6.4}
$$

The phase speed moves constant-phase crests; the group speed moves the envelope of a narrow packet when the dispersion relation is smooth. For the one-dimensional wave equation the right- and left-traveling branches have constant speeds $\pm c$. Other equations have $\omega(k)$ nonlinear in $k$, so different scales travel at different phase speeds. A complex $\omega$ also encodes decay or growth through $e^{\operatorname{Im}\omega\,t}$.

For the wave equation, multiply by $u_t$ and integrate to obtain conservation of $\frac12\int(u_t^2+c^2|\nabla u|^2)dV$ when the boundary transmits no energy. This differs from diffusion's monotone decay of $\int u^2$.

## Nondimensionalization and competing scales

**Result and motivation.** Dimensionless ratios identify which terms can compete. Neglecting a term is a scale-dependent physical assumption. Sources: [@ArfkenWeber2005, Section 9.1, dimensional structure of the prototype equations]; fluid scaling: [@Vallis2006, Sections 1.11, 2.7-2.8].

For advection-diffusion $q_t+\mathbf u\cdot\nabla q=\kappa\Delta q$, take length $L_*>0$, speed $U_*>0$, amplitude $Q_*>0$, and advective time $T_*=L_*/U_*$. Write $\mathbf x=L_*\widetilde{\mathbf x}$, $t=T_*\widetilde t$, $q=Q_*\widetilde q$, and $\mathbf u=U_*\widetilde{\mathbf u}$. Dividing by $Q_*U_*/L_*$ gives

$$
\partial_{\widetilde t}\widetilde q+
\widetilde{\mathbf u}\cdot\widetilde\nabla\widetilde q
=\mathrm{Pe}^{-1}\widetilde\Delta\widetilde q,
\qquad \mathrm{Pe}=\frac{U_*L_*}{\kappa}.
\tag{6.5}
$$

The Peclet number $\mathrm{Pe}$ is the ratio of diffusion time $L_*^2/\kappa$ to advection time. In momentum dynamics, the Reynolds number is $\mathrm{Re}=U_*L_*/\nu$ with kinematic viscosity $\nu$, and the Rossby number is $\mathrm{Ro}=U_*/(|f_*|L_*)$ with a nonzero reference Coriolis parameter $f_*$. Large $\mathrm{Pe}$ does not make diffusion negligible at all scales: diffusion at length $\ell$ scales as $\kappa/\ell^2$. Small scales or thin boundary layers can retain it.

## Chapter summary and self-test

**Main results and terms.** A PDE problem includes its domain, boundary data, initial data, and norm. Elliptic balance, parabolic diffusion, hyperbolic waves, and transport have different data requirements. Well-posedness means existence, uniqueness, and continuous dependence. Energy identities prove stability and uniqueness. A weak formulation lowers the derivative requirement. Characteristics carry information; a dispersion relation links frequency to wavenumber. Dimensionless numbers compare terms at stated scales.

**Self-test.** Use (6.2) to compare two diffusion solutions with different initial fields. Why is a homogeneous Neumann Poisson solution unique only after fixing its mean? Can a large Peclet number justify dropping diffusion at arbitrarily small length?

# Fourier analysis {#ch-fourier}

## Periodic modes and coefficient recovery

**Result and motivation.** Fourier modes diagonalize translation-invariant differentiation on a periodic domain. Orthogonality determines the coefficients and normalization. Sources: [@ArfkenWeber2005, Sections 14.1-14.4].

Let $x$ be a length coordinate with period $d>0$: values at $x$ and $x+d$ are identified. The integer mode index is $n\in\mathbb Z$ and angular wavenumber is $k_n=2\pi n/d$. Define $c_n$ by

$$
f(x)=\sum_{n\in\mathbb Z}c_ne^{ik_nx},
\qquad c_n=\frac1d\int_0^df(x)e^{-ik_nx}dx,
\qquad \frac1d\int_0^de^{i(k_n-k_m)x}dx=\delta_{nm}.
\tag{7.1}
$$

For $n\ne m$, integrate the exponential and use $e^{2\pi i(n-m)}=1$ to obtain zero. For $n=m$, the integrand is one. Multiplying the expansion by $e^{-ik_mx}$ and integrating therefore selects $c_m$. With normalized measure $dx/d$, these exponentials are orthonormal and $c_n$ has the units of $f$. Under $dx$, the normalized basis would instead be $d^{-1/2}e^{ik_nx}$.

The completeness theorem gives convergence in $L^2$ for $f\in L^2$ and Parseval's identity

$$
\frac1d\int_0^d|f|^2dx=\sum_n|c_n|^2,
\qquad \widehat{\partial_xf}_n=ik_nc_n.
\tag{7.2}
$$

The derivative formula follows by integration by parts when $f$ is differentiable and its periodic endpoint values match. For a real field $c_{-n}=\overline{c_n}$; the pair $n,-n$ is $2\operatorname{Re}(c_ne^{ik_nx})$. The zero mode $c_0$ is the spatial mean. Taking real and imaginary parts gives the equivalent sine-cosine series.

For $f=A\cos(k_px)+B\sin(k_px)$, with positive integer $p$ and real amplitudes $A,B$, the only nonzero coefficients are $c_p=(A-iB)/2$ and $c_{-p}=(A+iB)/2$. Equation (7.2) gives mean square $(A^2+B^2)/2$, checking both the conjugation and the factor two.

## Convergence, smoothness, and Gibbs oscillations

**Result and motivation.** Smoothness controls coefficient decay, but a truncated expansion near a jump retains an overshoot. Spectral accuracy requires appropriate regularity and periodic matching. Sources: [@ArfkenWeber2005, Sections 5.5, 14.4-14.5].

If $f$ has $p$ integrable derivatives with matching periodic traces through derivative order $p-1$, repeated integration by parts yields, for $n\ne0$,

$$
c_n=\frac{\widehat{f^{(p)}}_n}{(ik_n)^p},
\qquad |c_n|\le\frac{1}{d|k_n|^p}\int_0^d|f^{(p)}(x)|dx.
\tag{7.3}
$$

The endpoint requirements remove boundary terms. Smoothness on the open interval alone is insufficient: the periodic extension of $f(x)=x$ on $(-\pi,\pi)$ has a jump at the identified endpoints and coefficients of order $1/|n|$.

For a piecewise smooth periodic $f$, its Fourier sum at a jump tends to the midpoint of its one-sided limits. Partial sums overshoot near a jump; increasing the cutoff narrows this region without making its limiting relative height vanish (Gibbs phenomenon). For the square wave $f(x)=1$ on $(0,\pi)$ and $f(x)=-1$ on $(-\pi,0)$,

$$
b_n=\frac2\pi\int_0^\pi\sin(nx)dx
=\frac{2[1-(-1)^n]}{\pi n},
\qquad f(x)\sim\frac4\pi\sum_{j=0}^{\infty}\frac{\sin((2j+1)x)}{2j+1}.
\tag{7.4}
$$

Here $\sim$ denotes the Fourier representation with the convergence just specified, rather than equality at every assigned point value. Damping high modes can suppress ringing but changes the approximated function. Parseval still permits good mean-square approximation when a uniform approximation near a jump is impossible.

## The Fourier transform and its normalization

**Result and motivation.** On the whole line, wavenumber becomes continuous. The transform turns constant-coefficient differentiation into multiplication. Sources: [@ArfkenWeber2005, Sections 15.1-15.4].

For $f\in L^1(\mathbb R)$ define the angular-wavenumber transform, with the following sign convention:

$$
\widehat f(k)=\int_{\mathbb R}f(x)e^{-ikx}dx,
\qquad f(x)=\frac1{2\pi}\int_{\mathbb R}\widehat f(k)e^{ikx}dk.
\tag{7.5}
$$

The inverse formula holds, for example, for smooth rapidly decaying functions. More generally, integrability of both $f$ and $\widehat f$ gives the continuous representative almost everywhere; $L^2$ inversion is in norm and uses the Plancherel extension, not necessarily an absolutely convergent integral. A rapidly decaying smooth function and all its derivatives decay faster than every inverse power of $|x|$.

To see the factor $1/(2\pi)$, put the periodic problem on $[-d/2,d/2]$ and define $\Delta k=2\pi/d$. Then $c_n=d^{-1}\int f(x)e^{-ik_nx}dx\approx\widehat f(k_n)\Delta k/(2\pi)$. As $d\to\infty$, the Fourier sum becomes the integral in (7.5), under suitable decay assumptions. AW often uses a symmetric $1/\sqrt{2\pi}$ normalization and the opposite forward sign; coefficients must be converted before comparison.

Integration by parts, a change of variable, and Parseval give respectively

$$
\begin{aligned}
\widehat{f'}(k)&=ik\widehat f(k),\qquad \widehat{f''}(k)=-k^2\widehat f(k),\\
\mathcal F[f(x-a)](k)&=e^{-ika}\widehat f(k),\\
\int_{\mathbb R}|f|^2dx&=\frac1{2\pi}\int_{\mathbb R}|\widehat f|^2dk.
\end{aligned}
\tag{7.6}
$$

The symbol $\mathcal F$ denotes the transform in (7.5), and $a$ is a spatial shift. With $[x]=\mathrm m$ and $[f]=U$, $[k]=\mathrm m^{-1}$ and $[\widehat f]=U\,\mathrm m$. A transform with cyclic frequency $\xi=k/(2\pi)$ instead has $e^{-2\pi i\xi x}$ and no inverse $1/(2\pi)$ prefactor. The variable and the measure change together.

## Convolution and the heat kernel

**Result and motivation.** Convolution sums responses to shifted sources. Fourier multiplication provides both its algebraic representation and a direct diffusion solution. Sources: [@ArfkenWeber2005, Sections 9.8, 15.4-15.5].

For integrable $f,g$, define convolution by $(f*g)(x)=\int_{\mathbb R}f(y)g(x-y)dy$. Changing variables $z=x-y$ in its Fourier transform yields

$$
\widehat{f*g}(k)
=\int\!\int f(y)g(z)e^{-ik(y+z)}dy\,dz
=\widehat f(k)\widehat g(k).
\tag{7.7}
$$

Absolute integrability justifies changing the integration order. A product instead becomes $\widehat{fg}(k)=(2\pi)^{-1}(\widehat f*\widehat g)(k)$, when the functions have enough integrability. Thus nonlinear multiplication couples frequencies rather than acting diagonally.

For $u_t=\kappa u_{xx}$ on $\mathbb R$, transforming only in $x$ gives $\partial_t\widehat u=-\kappa k^2\widehat u$. Solve this scalar ODE and invert:

$$
\widehat u(k,t)=e^{-\kappa k^2t}\widehat u_0(k),
\qquad u(x,t)=(G_t*u_0)(x),
\qquad G_t(x)=\frac{e^{-x^2/(4\kappa t)}}{\sqrt{4\pi\kappa t}},\quad t>0.
\tag{7.8}
$$

To verify the inverse Gaussian, let $I(x)=\int_{\mathbb R}e^{-ak^2}e^{ikx}dk$ for $a>0$. Integrating $\partial_k(e^{-ak^2})$ by parts gives $I'=-xI/(2a)$, hence $I(x)=I(0)e^{-x^2/(4a)}$. Squaring $I(0)$ and using polar coordinates gives $I(0)^2=\int_{\mathbb R^2}e^{-a(k^2+s^2)}dkds=\pi/a$. With $a=\kappa t$, dividing by $2\pi$ gives (7.8). The kernel integrates to one and has units of inverse length, preserving total mass for integrable initial data. Its width grows as $\sqrt{\kappa t}$.

## The discrete transform and aliasing

**Result and motivation.** A DFT exactly represents a finite vector. Its coefficients equal continuous Fourier coefficients only with adequate sampling assumptions. Sources: [@ArfkenWeber2005, Section 14.6].

For $N$ samples $f_j=f(jd/N)$, $j=0,\ldots,N-1$, use normalized discrete coefficients

$$
\widetilde c_n=\frac1N\sum_{j=0}^{N-1}f_je^{-2\pi inj/N},
\qquad f_j=\sum_{n=0}^{N-1}\widetilde c_ne^{2\pi inj/N}.
\tag{7.9}
$$

The discrete orthogonality sum $N^{-1}\sum_j e^{2\pi i(n-m)j/N}$ is one when $n-m$ is a multiple of $N$ and zero otherwise, by the geometric-series formula. Therefore mode indices are defined modulo $N$; indices above half the sample count represent negative wavenumbers. For even $N$, the Nyquist index $N/2$ coincides with its negative, so it is a special endpoint and cannot represent two independent traveling phases.

Substituting a sufficiently convergent continuous Fourier series into (7.9) gives

$$
\widetilde c_n=\sum_{r\in\mathbb Z}c_{n+rN},
\qquad \frac1N\sum_j|f_j|^2=\sum_{n=0}^{N-1}|\widetilde c_n|^2.
\tag{7.10}
$$

The first formula is aliasing: unresolved modes contaminate the same sampled coefficient. A field bandlimited to $|n|\le K$ (all higher coefficients zero) is recovered uniquely if $N\ge2K+1$. With $N=8$, mode $6$ samples exactly as mode $-2$. A correct forward-inverse round trip cannot detect that loss of continuous information. The fast Fourier transform (FFT) computes the same DFT in $O(N\log N)$ work; it is an algorithm, not a different transform. Discrete convolution is circular (indices wrap modulo $N$); linear convolution requires padding.

## Chapter summary and self-test

**Main results and terms.** Fourier coefficients follow from periodic orthogonality. Differentiation multiplies by $ik$; the Laplacian multiplies by $-k^2$. Parseval equates mean square or integrated square with coefficient power under the stated normalization. Endpoint regularity controls coefficient decay. The whole-line transform has a continuous wavenumber and a paired inverse factor. Convolution becomes multiplication; diffusion becomes Gaussian smoothing. A DFT is exact for samples, while aliasing limits its interpretation as continuous analysis.

**Self-test.** Find the nonzero Fourier coefficients and mean square of $3\cos(2x)$ on a $2\pi$ interval. Explain why a round trip of an undersampled wave can be exact. Derive the decay rate of the $n$th periodic diffusion mode.

# Legendre polynomials and spherical harmonics {#ch-harmonics}

## Angular separation and Legendre's equation

**Result and motivation.** Spherical harmonics are the globally regular eigenfunctions of the spherical Laplacian. Longitude periodicity and pole regularity quantize their two indices. Sources: [@ArfkenWeber2005, Sections 9.3-9.5, 12.1-12.6].

Seek $\Delta_\Omega Y=-\Lambda Y$ on the unit sphere, where $\Lambda$ is dimensionless and $Y(\theta,\lambda)=\Theta(\theta)\Phi(\lambda)$. Substitution into (3.5) separates the longitude equation $\Phi''+m^2\Phi=0$. Single-valued $2\pi$-periodicity requires an integer $m$, and choose $\Phi=e^{im\lambda}$. The remaining equation, written in $\mu=\cos\theta$, is

$$
\frac{d}{d\mu}\left[(1-\mu^2)\frac{d\Theta}{d\mu}\right]
+\left[\Lambda-\frac{m^2}{1-\mu^2}\right]\Theta=0.
\tag{8.1}
$$

For $m=0$, insert a power series $\Theta=\sum_{j\ge0}a_j\mu^j$. Equal powers give

$$
a_{j+2}=\frac{j(j+1)-\Lambda}{(j+2)(j+1)}a_j.
\tag{8.2}
$$

If $\Lambda=\ell(\ell+1)$ for $\ell\in\mathbb N_0$, one parity branch terminates at degree $\ell$. Its normalization $P_\ell(1)=1$ defines the Legendre polynomial $P_\ell$. The other independent solution is singular at an endpoint. The global regularity theorem for (8.1) selects these discrete eigenvalues; the recurrence exhibits the regular polynomial solutions but is not by itself a proof that all other $\Lambda$ fail both endpoint conditions. For integer $m\ne0$, admissible degrees satisfy $\ell\ge|m|$.

For $m=0$ the Legendre equation has singular Sturm-Liouville endpoints because $p=1-\mu^2$ vanishes at $\pm1$. The boundary condition is regularity of the scalar on the sphere, rather than arbitrary Dirichlet data at coordinate poles.

## Polynomial normalization and associated functions

**Result and motivation.** Explicit normalization and phase conventions make coefficients comparable. Associated Legendre functions supply the latitude dependence for nonzero longitude order. Sources: [@ArfkenWeber2005, Sections 12.2-12.5].

Rodrigues' formula, the first polynomials, and their orthogonality are

$$
\begin{aligned}
P_\ell(\mu)&=\frac1{2^\ell\ell!}\frac{d^\ell}{d\mu^\ell}(\mu^2-1)^\ell,\\
P_0&=1,\quad P_1=\mu,\quad P_2=\tfrac12(3\mu^2-1),\\
\int_{-1}^1P_\ell(\mu)P_j(\mu)d\mu&=\frac2{2\ell+1}\delta_{\ell j}.
\end{aligned}
\tag{8.3}
$$

Orthogonality for different degrees follows by multiplying their differential equations, subtracting, and integrating; the boundary factor $1-\mu^2$ makes the regular polynomial boundary terms zero. The norm can also be derived from Rodrigues. The leading coefficient of $P_\ell$ is $a_\ell=(2\ell)!/[2^\ell(\ell!)^2]$. Since $P_\ell-a_\ell\mu^\ell$ has lower degree, orthogonality gives $\int P_\ell^2=a_\ell\int P_\ell\mu^\ell$. Define $I_\ell=\int_{-1}^1(1-\mu^2)^\ell d\mu$. Integrating Rodrigues by parts $\ell$ times gives $\int P_\ell\mu^\ell=2^{-\ell}I_\ell$: all endpoint terms vanish and $d^\ell\mu^\ell/d\mu^\ell=\ell!$.

For $\ell\ge1$, integrate the derivative of $\mu(1-\mu^2)^\ell$ over $[-1,1]$ to get $0=I_\ell-2\ell(I_{\ell-1}-I_\ell)$. Thus $I_\ell=2\ell I_{\ell-1}/(2\ell+1)$ with $I_0=2$. Iterating gives $I_\ell=2^{2\ell+1}(\ell!)^2/(2\ell+1)!$, and the norm is $a_\ell2^{-\ell}I_\ell=2/(2\ell+1)$.


For integer $0\le m\le\ell$, choose the Condon-Shortley phase by defining

$$
P_\ell^m(\mu)=(-1)^m(1-\mu^2)^{m/2}\frac{d^mP_\ell}{d\mu^m},
\qquad
\int_{-1}^1(P_\ell^m)^2d\mu
=\frac2{2\ell+1}\frac{(\ell+m)!}{(\ell-m)!}.
\tag{8.4}
$$

Differentiating Legendre's equation $m$ times and multiplying by $(1-\mu^2)^{m/2}$ gives (8.1). The associated-function norm in (8.4) is quoted from AW, Section 12.5; its repeated-integration proof is not reproduced here. The factor $(1-\mu^2)^{m/2}=\sin^m\theta$ enforces the required vanishing of a regular scalar's nonzero longitude order at the poles. Odd-$m$ associated functions are not polynomials in $\mu$.

A stable degree recurrence follows from Rodrigues or the generating function:
$(\ell+1)P_{\ell+1}=(2\ell+1)\mu P_\ell-\ell P_{\ell-1}$. It constructs all degrees from $P_0,P_1$; high-degree numerical algorithms still need controlled normalization to avoid overflow.

## Spherical harmonic expansion and Parseval

**Result and motivation.** The spherical harmonic transform is longitude Fourier analysis coupled to weighted latitude analysis. Degree measures total angular scale; order measures longitude variation. Sources: [@ArfkenWeber2005, Sections 12.5-12.6].

For $m\ge0$, define

$$
Y_\ell^m(\theta,\lambda)=N_{\ell m}P_\ell^m(\cos\theta)e^{im\lambda},
\qquad N_{\ell m}=\left[\frac{2\ell+1}{4\pi}\frac{(\ell-m)!}{(\ell+m)!}\right]^{1/2},
\qquad Y_\ell^{-m}=(-1)^m\overline{Y_\ell^m}.
\tag{8.5}
$$

Degree is $\ell=0,1,\ldots$ and order is $-\ell\le m\le\ell$. Combining longitude orthogonality with (8.4) gives

$$
\int_{S^2}Y_\ell^m\overline{Y_j^n}d\Omega=\delta_{\ell j}\delta_{mn},
\qquad \Delta_sY_\ell^m=-\frac{\ell(\ell+1)}{R^2}Y_\ell^m.
\tag{8.6}
$$

The symbol $S^2$ denotes the unit sphere; these angular functions are also evaluated on $S_R^2$. They are normalized under $d\Omega$, not physical area $dA$. In particular $Y_0^0=1/\sqrt{4\pi}$ and $Y_1^0=\sqrt{3/(4\pi)}\cos\theta$.

For $f\in L^2(S^2,d\Omega)$, completeness gives

$$
\begin{aligned}
f&=\sum_{\ell=0}^{\infty}\sum_{m=-\ell}^{\ell}f_\ell^mY_\ell^m,
& f_\ell^m&=\int_{S^2}f\overline{Y_\ell^m}d\Omega,\\
\int_{S^2}|f|^2d\Omega&=\sum_{\ell,m}|f_\ell^m|^2,
& \langle f\rangle_A&=f_0^0/\sqrt{4\pi}.
\end{aligned}
\tag{8.7}
$$

The expansion converges in $L^2$; smooth fields admit stronger convergence. Real $f$ obeys $f_\ell^{-m}=(-1)^m\overline{f_\ell^m}$. A cutoff $0\le\ell\le L$ retains $(L+1)^2$ basis functions, or the same number of independent real coefficients for a real field. The physical inverse length is approximately $\sqrt{\ell(\ell+1)}/R$; degree zero is the mean, not a finite wavelength.

For $f=\mu^2$, equation (8.3) gives $\mu^2=P_0/3+2P_2/3$. Hence $f_0^0=\sqrt{4\pi}/3$, $f_2^0=(2/3)\sqrt{4\pi/5}$, and all other coefficients vanish. The area mean is $1/3$. Parseval gives $\int\mu^4d\Omega=4\pi/5$, agreeing with direct integration.

## Zonal means, tangent vectors, and isotropy

**Result and motivation.** Longitude averaging keeps only order zero. Tangent vectors need geometric basis functions, while rotationally invariant scalar filters must act identically on all orders of a degree. Sources: [@ArfkenWeber2005, Sections 12.6, 12.8, 12.11].

The zonal mean is $\overline f(\mu)=(2\pi)^{-1}\int_0^{2\pi}f(\mu,\lambda)d\lambda$. Because the average of $e^{im\lambda}$ is zero for $m\ne0$, only $m=0$ survives. For a profile use $b_\ell(\mu)=\sqrt{2\ell+1}P_\ell(\mu)$, orthonormal under $d\mu/2$. Then $\overline f=\sum_\ell a_\ell b_\ell$ with $a_\ell=\frac12\int_{-1}^1\overline f b_\ell d\mu$. A scalar profile and an eastward velocity component have different pole regularity: an arbitrary scalar Legendre expansion of speed does not by itself define a smooth tangent vector field.

For $\ell\ge1$, dimensionless tangent vector harmonics are

$$
\mathbf E_\ell^m=\frac{R\nabla_sY_\ell^m}{\sqrt{\ell(\ell+1)}},
\qquad
\mathbf B_\ell^m=\mathbf e_r\times\mathbf E_\ell^m.
\tag{8.8}
$$

Integration by parts and (8.6) show unit norms under $d\Omega$. The gradient family is curl-free on the surface; the rotated-gradient family is divergence-free. AW's vector harmonics also include radial components and use a coupled angular-momentum convention. Equation (8.8) specifies the tangent gradient/rotated-gradient convention used here; its normalization follows from (3.8) and (8.6), rather than from equating names across conventions.

For a smooth tangent field $\mathbf v$, let $\delta=\nabla_s\cdot\mathbf v$ and $\zeta=(\nabla\times\mathbf v)\cdot\mathbf e_r$. Both have zero area integral by the surface divergence and Stokes identities. Scalar harmonic inversion therefore supplies zero-mean potentials $\chi,\psi$ with $\Delta_s\chi=\delta$ and $\Delta_s\psi=\zeta$, by dividing each degree-$\ell\ge1$ coefficient by $-\ell(\ell+1)/R^2$. Then $\mathbf w=\mathbf v-\nabla_s\chi-\mathbf e_r\times\nabla_s\psi$ has zero divergence and radial curl. Such a field is called a harmonic tangent field.

The sphere is simply connected: every closed loop can be continuously shrunk to a point. Stokes' theorem therefore makes the integral of a curl-free smooth tangent field around every loop zero. Its line integral from a reference point is path-independent and defines a scalar $h$ with $\mathbf w=\nabla_sh$ (the potential-field argument of AW, Section 1.13). Since $\Delta_sh=0$, (3.8) gives $\int|\nabla_sh|^2dA=0$, hence $\mathbf w=0$. This proves the smooth decomposition $\mathbf v=\nabla_s\chi+\mathbf e_r\times\nabla_s\psi$. In particular, a divergence-free smooth field has the streamfunction representation. Expanding these potentials gives the $\mathbf E/\mathbf B$ modes; the construction here only needs smooth fields. A velocity generated from a streamfunction uses the latter family; treating its coordinate components as unrelated scalars does not encode that constraint.

For unit vectors $\mathbf n,\mathbf n'$ separated by angle $\gamma$, with $\cos\gamma=\mathbf n\cdot\mathbf n'$, the addition theorem is

$$
P_\ell(\mathbf n\cdot\mathbf n')
=\frac{4\pi}{2\ell+1}\sum_{m=-\ell}^{\ell}Y_\ell^m(\mathbf n)\overline{Y_\ell^m(\mathbf n')}.
\tag{8.9}
$$

This theorem is quoted from AW, Section 12.8. It shows why an isotropic kernel, depending only on angular separation, multiplies every order at fixed degree by the same scalar. Chapter 12 derives the multiplier. Keeping all orders through a degree gives a rotation-invariant subspace (triangular truncation). Selecting unrelated orders can break that property.

## Chapter summary and self-test

**Main results and terms.** Longitude periodicity selects integer order $m$; global regularity selects integer degree $\ell\ge|m|$. Rodrigues' formula defines $P_\ell$, and the Condon-Shortley choice fixes the phase of $P_\ell^m$. Equations (8.5)-(8.7) define the normalized spherical harmonic transform, eigenvalues, and Parseval identity. Zonal means keep $m=0$. Vector harmonics separate gradient and nondivergent tangent fields. The addition theorem underlies isotropic spherical kernels.

**Self-test.** Expand $\mu^2-1/3$ and solve $\Delta_s\psi=A(\mu^2-1/3)$ with zero mean. How many independent real degrees of freedom remain at cutoff $L=2$? Why is a two-dimensional periodic FFT on latitude-longitude coordinates not spherical harmonic analysis?

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

# Rotating fluids, vorticity, and spectra {#ch-fluids}

## Mass, momentum, and rotating frames

**Result and motivation.** In a rotating frame the apparent Coriolis acceleration turns motion without doing work. Conservation and scale assumptions reduce the fluid equations to the horizontal models used in idealized geophysical dynamics. Sources: [@Vallis2006, Sections 1.2-1.3, 1.9-1.11, 2.1-2.3]; vector identities: [@ArfkenWeber2005, Sections 1.8-1.9].

Let $\rho$ be mass density, $p$ pressure, $\mathbf u$ velocity relative to a frame rotating at constant vector angular velocity $\boldsymbol\Omega$, and $\Phi$ effective gravitational potential per unit mass, including the centrifugal potential. For a constant-density incompressible Newtonian fluid with constant kinematic viscosity $\nu$ and other acceleration $\mathbf F$,

$$
\nabla\cdot\mathbf u=0,\qquad
\frac{D\mathbf u}{Dt}+2\boldsymbol\Omega\times\mathbf u
=-\frac1\rho\nabla p-\nabla\Phi+\nu\Delta\mathbf u+\mathbf F.
\tag{10.1}
$$

The viscous Laplacian form assumes these constitutive and incompressibility conditions; it is not the general compressible stress law. Pressure enforces the divergence constraint. A Newtonian fluid has stress proportional to strain rate. In a changing basis, the inertial derivative of a vector is its rotating derivative plus $\boldsymbol\Omega\times$ that vector. Applying this rule twice to position produces $2\boldsymbol\Omega\times\mathbf u$ and $\boldsymbol\Omega\times(\boldsymbol\Omega\times\mathbf x)$; the latter is absorbed in $\Phi$. Coriolis does no work since $\mathbf u\cdot(\boldsymbol\Omega\times\mathbf u)=0$.

For a shallow horizontal layer, the traditional horizontal Coriolis term uses the local vertical component $f=2\Omega\sin\varphi$, where $\Omega=|\boldsymbol\Omega|$. This approximation and the shallow geometry have physical limits; they do not follow from vector algebra alone. Near reference latitude $\varphi_0$, a tangent plane with east coordinate $x$ and north coordinate $y$ gives $f\approx f_0+\beta y$, where $f_0=2\Omega\sin\varphi_0$ and $\beta=2\Omega\cos\varphi_0/R$. This is the beta-plane approximation. An $f$-plane keeps only $f_0$.

## Streamfunction and the barotropic vorticity equation

**Result and motivation.** In a constant-depth nondivergent layer, absolute vertical vorticity is materially conserved in the inviscid unforced limit. Streamfunction converts the velocity-vorticity relation into a Poisson inversion. Sources: [@Vallis2006, Sections 4.1-4.6, 5.1]; geometry follows Chapter 3.

Barotropic means pressure is a function of density alone, so $\nabla\rho\times\nabla p=0$. A constant-density, constant-depth nondivergent layer is a particular model reduction; the word alone does not imply every one of those assumptions. In three dimensions the inviscid vorticity equation includes stretching of absolute vorticity. In a shallow layer its vertical component is
$D(\zeta+f)/Dt=-(\zeta+f)\nabla_s\cdot\mathbf u$, subject to the horizontal-model assumptions. If depth changes, stretching matters and potential vorticity $(\zeta+f)/h$ is conserved instead, with $h$ layer thickness. We now take constant $h$ and zero divergence.

Define absolute vorticity $q=\zeta+f$, forcing $F$ and dissipation $D$ in vorticity units per time ($\mathrm s^{-2}$). With the streamfunction convention (3.7),

$$
\partial_t\zeta+J_s(\psi,\zeta+f)=F+D,
\qquad \zeta=\Delta_s\psi,
\qquad
J_s(a,b)=\frac{\partial_\lambda a\,\partial_\varphi b-
\partial_\varphi a\,\partial_\lambda b}{R^2\cos\varphi}.
\tag{10.2}
$$

Indeed, $\mathbf u\cdot\nabla_sb=u\partial_\lambda b/(R\cos\varphi)+v\partial_\varphi b/R=J_s(\psi,b)$. This fixes the sign rather than choosing it from memory. Time evolution advances $\zeta$; elliptic inversion supplies $\psi$ and then velocity. Since $\int\Delta_s\psi=0$, a globally smooth relative-vorticity field has zero area mean, and forcing must respect this compatibility. Fix $\psi_0^0=0$; then

$$
\psi_\ell^m=-\frac{R^2}{\ell(\ell+1)}\zeta_\ell^m,\quad\ell\ge1.
\tag{10.3}
$$

On a beta-plane, $u=-\psi_y$, $v=\psi_x$, $\zeta=\Delta\psi$, and $J(a,b)=a_xb_y-a_yb_x$. Equation (10.2) becomes $\zeta_t+J(\psi,\zeta)+\beta\psi_x=F+D$. Units check: $[J_s(\psi,q)]=[\psi][q]/R^2=\mathrm s^{-2}$.

## Rossby waves and physical propagation

**Result and motivation.** A parcel displaced across a planetary-vorticity gradient changes relative vorticity. This coupling supports dispersive Rossby waves. Sources: [@Vallis2006, Sections 5.7-5.8].

Linearize the unforced beta-plane equation about rest by neglecting the quadratic term $J(\psi,\Delta\psi)$. For a wave $\psi=Ae^{i(kx+ly-\omega t)}$, where $k,l$ are east and north angular wavenumbers, respectively,

$$
\partial_t\Delta\psi+\beta\partial_x\psi=0
\quad\Longrightarrow\quad
\omega=-\frac{\beta k}{k^2+l^2}.
\tag{10.4}
$$

Substitution gives $i\omega(k^2+l^2)+i\beta k=0$. For $\beta>0$ the zonal phase speed $\omega/k$ is negative whenever $k\ne0$: crests propagate westward relative to the resting background. The zonal group speed is $\partial\omega/\partial k=\beta(k^2-l^2)/(k^2+l^2)^2$, which can have either sign. Phase and energy-envelope propagation must not be conflated. A uniform eastward background speed $U$ adds a Doppler shift $Uk$ to $\omega$.

On the full sphere, $J_s(\psi,f)=2\Omega\partial_\lambda\psi/R^2$. Substituting $\psi=A Y_\ell^m e^{-i\omega t}$ into the linearized equation yields

$$
\omega=-\frac{2\Omega m}{\ell(\ell+1)},\qquad \ell\ge1.
\tag{10.5}
$$

These are global barotropic Rossby modes about rest. The spherical eigenvalue replaces the planar squared wavenumber. The linear calculation neglects finite-amplitude interactions; it does not assert that every forced turbulent field is a superposition of independently evolving waves.

## Energy, enstrophy, and scale spectra

**Result and motivation.** Conservation identities provide physical diagnostics, while spherical Parseval identities locate variance and kinetic energy by angular scale. Sources: [@Vallis2006, Sections 4.5, 8.1-8.3]; spectral formulas are derived from [@ArfkenWeber2005, Sections 12.6, 12.11].

Use $\langle a\rangle_A=(4\pi R^2)^{-1}\int a\,dA$. For smooth inviscid unforced nondivergent flow on a closed sphere with time-independent $f$, define area-mean kinetic energy $K=\frac12\langle|\mathbf u|^2\rangle_A$ and absolute enstrophy $Q=\frac12\langle q^2\rangle_A$. "Enstrophy" means one half of mean squared vorticity; specify whether that vorticity is relative or absolute. Incompressibility gives

$$
\frac{d}{dt}\langle C(q)\rangle_A
=-\langle\mathbf u\cdot\nabla_s C(q)\rangle_A=0
\tag{10.6}
$$

for differentiable $C$ for which the integral exists. Taking $C(q)=q^2/2$ conserves $Q$. The identity uses a divergence theorem on the closed surface. Energy satisfies $K=-\frac12\langle\psi\zeta\rangle_A$ by (3.8). Self-adjointness gives $K'=-\langle\psi\zeta_t\rangle_A=\langle\psi J_s(\psi,q)\rangle_A=0$, because integration by parts moves advection onto $\psi$ and $J_s(\psi,\psi)=0$. With forcing and dissipation, $K'=-\langle\psi(F+D)\rangle_A$ instead.

Expand $\psi$ using (8.7). Define relative enstrophy $Z=\frac12\langle\zeta^2\rangle_A$ and its degree spectrum $Z_\ell$, and define $K_\ell$ analogously. Integration by parts and Parseval give

$$
\begin{aligned}
K&=\sum_{\ell\ge1}K_\ell,&
K_\ell&=\frac{\ell(\ell+1)}{8\pi R^2}\sum_{m=-\ell}^{\ell}|\psi_\ell^m|^2,\\
Z&=\sum_{\ell\ge1}Z_\ell,&
Z_\ell&=\frac{[\ell(\ell+1)]^2}{8\pi R^4}\sum_m|\psi_\ell^m|^2
=\frac{\ell(\ell+1)}{R^2}K_\ell.
\end{aligned}
\tag{10.7}
$$

Thus $[K]=\mathrm m^2\,\mathrm s^{-2}$ and $[Z]=\mathrm s^{-2}$. These are global means; area-integrated quantities have another factor $4\pi R^2$. A coefficient sum for a real field includes both positive and negative orders, or equivalent multiplicity weights if only nonnegative orders are stored. Missing those weights changes the spectrum. These spectra use relative vorticity, whereas (10.6) is stated for absolute vorticity.

Spectra describe how a quadratic quantity is distributed, not the direction of its transfer. A cascade claim requires a scale-transfer budget or other evidence. Likewise, no conservation law alone fixes a turbulent spectral slope or a jet count. Zonal averaging splits a field into its mean and departure, $a=\overline a+a'$ with $\overline{a'}=0$. Then $\overline{uv}=\overline u\,\overline v+\overline{u'v'}$; the covariance term represents transport by correlated departures and cannot generally be reconstructed from the two means alone.

## Chapter summary and self-test

**Main results and terms.** Coriolis acceleration follows from rotating-frame differentiation and does no work. A shallow constant-depth nondivergent model materially conserves absolute vorticity. Streamfunction and vorticity are linked by spherical Poisson inversion. The beta effect produces the dispersions (10.4)-(10.5); phase and group velocities differ. Smooth inviscid unforced flow conserves kinetic energy and absolute-vorticity functionals. Parseval yields degree spectra with explicit radius and area normalization. Spectral shape alone does not establish a cascade.

**Self-test.** Check the sign of a Rossby wave's phase speed for positive $\beta$. Derive the units in (10.3). What happens to $K_\ell$ and $Z_\ell$ when all streamfunction power moves from degree $\ell=2$ to degree $\ell=4$ while total $K$ is held fixed?

# Probability, averages, and climatological estimates {#ch-statistics}

## Random variables, expectation, and covariance

**Result and motivation.** Probability distinguishes an ensemble average from one observed realization. Covariance measures the dependence that determines uncertainty in averages. Sources: [@ArfkenWeber2005, Sections 19.1-19.2, 19.5-19.6].

A probability space consists of possible outcomes, a collection of events, and a probability measure $P$ assigning nonnegative probabilities, total probability one, and countably additive probabilities for disjoint events (the probability of a countable disjoint union is the sum of the probabilities). A real random variable $X$ is a measurable function of an outcome. A realization is one observed value. If $X$ has density $p_X(x)$, probabilities and expectations satisfy

$$
P(X\in A)=\int_Ap_X(x)dx,\quad \int_{\mathbb R}p_Xdx=1,
\qquad \mathbb E[g(X)]=\int_{\mathbb R}g(x)p_X(x)dx.
\tag{11.1}
$$

For a discrete variable, replace the integral by a sum over values weighted by their probabilities. Expectations require the stated moment to exist. Define mean $m_X=\mathbb E X$, variance $\sigma_X^2=\mathbb E[(X-m_X)^2]$, and covariance $\operatorname{Cov}(X,Y)=\mathbb E[(X-m_X)(Y-m_Y)]$. Variance has squared units; standard deviation $\sigma_X$ has the variable's units. For nonzero standard deviations, correlation is $\operatorname{Corr}(X,Y)=\operatorname{Cov}(X,Y)/(\sigma_X\sigma_Y)$ and lies in $[-1,1]$ by Cauchy-Schwarz.

Independence means the joint probabilities factor for all events concerning the two variables. It implies zero covariance when second moments exist, but the reverse is false. For a variable $X$ uniform on $[-1,1]$, let $Y=X^2$. Symmetry gives $\operatorname{Cov}(X,Y)=\mathbb E X^3-\mathbb E X\mathbb E X^2=0$, yet $Y$ is determined by $X$.

A Gaussian (normal) variable has density $p_X(x)=(2\pi\sigma_X^2)^{-1/2}\exp[-(x-m_X)^2/(2\sigma_X^2)]$ when $\sigma_X>0$. Normality is an additional distributional assumption, not a consequence of having a mean and variance. For independent identically distributed samples with finite variance, the sample mean has variance $\sigma_X^2/N$. The central limit theorem gives an asymptotically Gaussian standardized mean under these assumptions; correlated time samples need additional hypotheses.

## Spatial, temporal, and ensemble means

**Result and motivation.** The integration measure and sampling mechanism define an average. Spatial, temporal, and ensemble means answer different questions. Sources: [@ArfkenWeber2005, Sections 19.2, 19.6]; fluid averaging and correlation: [@Vallis2006, Sections 8.1, 10.2].

For a field $q(\mathbf x,t,\omega)$, $\omega$ labels a random outcome, not wave frequency in this chapter. An ensemble mean is $\mathbb E[q(\mathbf x,t,\omega)]$ at fixed position and time. A time mean of one realization over duration $T$ is $\overline q_T(\mathbf x)=T^{-1}\int_0^Tq(\mathbf x,t,\omega)dt$. A global spatial mean is $\langle q\rangle_A$ from Chapter 10. None equals the others by definition.

A time series is weakly stationary if its mean is time-independent, its variance is finite and constant, and its covariance depends only on lag. Strict stationarity means all finite joint distributions are invariant under a common time shift. Ergodicity, for an observable, means its long-time average equals the corresponding ensemble expectation almost surely (with probability one), under an invariant distribution. Stationarity alone does not guarantee this property. For example, $X(t)=B$ with one random constant $B$ for an entire trajectory is stationary, but its time mean is the realized $B$, not generally $\mathbb EB$.

A finite-time climatological estimate can retain initial-state transients, sampling variability, and slow fluctuations. Excluding an initial adjustment interval (spin-up) is a modeling decision whose adequacy requires diagnostics; it is not a theorem that any fixed exclusion time yields equilibrium. Independent simulations and adjacent windows of one simulation are not interchangeable sampling units.

## Autocorrelation and uncertainty of a mean

**Result and motivation.** Positive serial correlation reduces the information in a fixed number of time samples. The variance of a mean follows from all pairwise covariances. Sources: [@ArfkenWeber2005, Section 19.6]; time-correlation interpretation: [@Vallis2006, Section 10.2].

Let $X_1,\ldots,X_N$ be equally spaced weakly stationary samples with variance $\sigma^2>0$. Define autocorrelation at integer lag $k$ by $\rho_k=\operatorname{Cov}(X_j,X_{j+k})/\sigma^2$, independent of $j$. For $\overline X=N^{-1}\sum_jX_j$, expand its variance:

$$
\begin{aligned}
\operatorname{Var}(\overline X)
&=\frac1{N^2}\sum_{i,j}\operatorname{Cov}(X_i,X_j)\\
&=\frac{\sigma^2}{N}\left[1+2\sum_{k=1}^{N-1}\left(1-\frac{k}{N}\right)\rho_k\right].
\end{aligned}
\tag{11.2}
$$

There are $N-k$ pairs at each positive lag and the same number at negative lag, explaining the factor two. Define $N_{\rm eff}=N/[1+2\sum_{k=1}^{N-1}(1-k/N)\rho_k]$ when the denominator is positive; then $\operatorname{Var}(\overline X)=\sigma^2/N_{\rm eff}$. This is a variance-equivalent sample count, not literally a count of independent observations. Negative correlation can make it exceed $N$.

For $\rho_k=r^k$, $|r|<1$, and $N$ long relative to the correlation decay, the bracket approaches $(1+r)/(1-r)$. With $r=0.8$, $N_{\rm eff}\approx N/9$. If correlations are estimated from a short series, the estimated effective count is itself uncertain. A decorrelation formula does not establish stationarity or supply independent replicas.

## Squared-error prediction and normalization

**Result and motivation.** The conditional mean minimizes expected squared error. This identifies the target of a quadratic loss but does not establish optimality for a relative-error loss. Sources: [@ArfkenWeber2005, Sections 19.2, 19.6]; projection argument follows Chapter 4.

For predictor information $X$ and square-integrable scalar target $Y$, the conditional expectation $m(X)=\mathbb E[Y\mid X]$ is the mean given that information; it is characterized by $\mathbb E[(Y-m(X))h(X)]=0$ for suitable functions $h$. For any predictor $a(X)$,

$$
\mathbb E[(Y-a(X))^2\mid X]
=\operatorname{Var}(Y\mid X)+[m(X)-a(X)]^2.
\tag{11.3}
$$

Expand $Y-a=(Y-m)+(m-a)$; the cross term vanishes conditionally. This proves the optimum. It extends to a fixed weighted quadratic norm on finite-dimensional profiles by summing the component identities. It does not automatically extend to $\mathbb E[\|Y-a\|/\|Y\|]$, whose weighting and unsquared norm differ. Also, variability between targets with the same external configuration need not be irreducible when the predictor sees extra state information.

For a scalar training variable $x$, a mean $m$, standard deviation $s$, and small positive $\epsilon$ in the same units as $x$, affine normalization is $z=(x-m)/(s+\epsilon)$, with inverse $x=(s+\epsilon)z+m$. Fit these scales on training data only to avoid using held-out information. Equal sample weights for a numerical scaling convention need not coincide with physical area weights for a climatological mean. One changes coordinates for learning; the other defines an observable.

## Chapter summary and self-test

**Main results and terms.** Probability assigns weights to outcomes; expectation, variance, and covariance depend on that distribution. Zero covariance does not imply independence. Ensemble, time, zonal, and area averages are different operators. Stationarity is time-shift invariance of specified statistics; ergodicity is an additional long-time averaging property. Equation (11.2) gives exact sample-mean variance from autocorrelations. The conditional mean minimizes quadratic risk by (11.3). Normalization and physical averaging need separate definitions.

**Self-test.** Can ten overlapping windows from one run be assumed independent? For $r=0.8$, how many variance-equivalent samples do $900$ long-series samples supply approximately? Why does predicting the conditional mean not remove conditional variance?

# Integral operators, symmetries, and learned maps {#ch-operators}

## Kernels and spectral multipliers

**Result and motivation.** Many solution operators are global integral maps. Symmetry can reduce a two-position kernel to one multiplier per Fourier mode or spherical degree. Sources: [@ArfkenWeber2005, Sections 10.5, 12.8, 15.5, 16.1-16.4].

For input function $f$ on a domain $D$ with measure $d\nu$, an integral operator has the form

$$
(\mathcal Kf)(x)=\int_DK(x,y)f(y)d\nu(y).
\tag{12.1}
$$

The kernel $K(x,y)$ weights the influence of source point $y$ on output point $x$. This operator is linear when $K$ is fixed; a kernel depending on $f$ can produce a nonlinear overall map. Its physical units must combine those of $f$ and $d\nu$ to give the output units. The Green's operator (5.7) is one example.

On a periodic interval, a translation-invariant kernel $K(x,y)=k(x-y)$ gives circular convolution. With normalized integration $dy/d$, its Fourier coefficients multiply: $(\mathcal Kf)_n=k_nf_n$. With unnormalized $dy$, the multiplier is $dk_n$. Normalization of the integral and of the coefficients must be specified together.

On the unit sphere, assume $k\in L^2([-1,1])$ and $f\in L^2(S^2,d\Omega)$, and interpret the expansions in $L^2$. Let $K(\mathbf n,\mathbf n')=k(\mathbf n\cdot\mathbf n')$ be isotropic, meaning dependent only on angular separation. Expand $k(t)=\sum_{\ell\ge0}a_\ell P_\ell(t)$, with $a_\ell=(2\ell+1)\int_{-1}^1k(t)P_\ell(t)dt/2$. Apply (8.9) in (12.1), using $d\nu=d\Omega'$, and integrate against $f$. Orthogonality yields

$$
(\mathcal Kf)_\ell^m=\kappa_\ell f_\ell^m,
\qquad \kappa_\ell=\frac{4\pi a_\ell}{2\ell+1}
=2\pi\int_{-1}^1k(t)P_\ell(t)dt.
\tag{12.2}
$$

The same $\kappa_\ell$ acts for every $m$. For $k=1$, only $\kappa_0=4\pi$ survives and $\mathcal Kf=\int f\,d\Omega$ is constant, verifying the normalization. An integral under physical area $dA'$ supplies an additional $R^2$. An arbitrary position-dependent kernel couples harmonic modes; choosing spherical harmonics alone does not make an operator diagonal.

## Rotations and equivariance

**Result and motivation.** Equivariance means that transforming the input and then applying a map agrees with transforming its output. It is a precise property with specific group, field-type, and discretization assumptions. Sources: [@ArfkenWeber2005, Sections 1.2, 4.1-4.3, 12.8]; operator formulation: [@Bonev2023sfno, Sections 3.2-4.2].

A group is a set of transformations closed under composition, with an identity, an inverse for every transformation, and associative composition. The rotation group $SO(3)$ consists of real $3\times3$ matrices $Q$ satisfying $Q^{\mathsf T}Q=I$ and $\det Q=1$. On scalar fields define the rotation action $(T_Qf)(\mathbf n)=f(Q^{-1}\mathbf n)$. A scalar-to-scalar map $\mathcal G$ is rotation-equivariant if

$$
\mathcal G(T_Qf)=T_Q\mathcal G(f)\quad\text{for every }Q\in SO(3).
\tag{12.3}
$$

It is invariant if $\mathcal G(T_Qf)=\mathcal G(f)$, as for an area integral. A vector field uses the action $T_Q\mathbf v(\mathbf n)=Q\mathbf v(Q^{-1}\mathbf n)$ instead; rotating only scalar component images misses the vector rotation.

Rotations mix orders within a fixed degree. Consequently, a scalar linear multiplier shared by every $m$ at degree $\ell$ commutes with rotations; a separate arbitrary multiplier for each $m$ generally does not. An isotropic kernel satisfies this property by (12.2). Multiple scalar channels can mix through one channel matrix per degree, still shared across orders.

These statements concern full rotations of scalar fields with no preferred direction. A rotating planet has a specified rotation axis: holding that axis fixed reduces the physical symmetry. Geographic positional features, direction-dependent forcing, or latitude-dependent coefficients can deliberately reduce it. Continuous equivariance also does not guarantee exact discrete equivariance after approximate quadrature and unresolved nonlinear products.

## Neural operators and loss functions

**Result and motivation.** A neural operator approximates a map between functions from sampled input-output pairs. Its spectral layer uses the same analysis-multiply-synthesis structure as a classical integral operator. Sources: [@Li2021fno, Sections 2-4]; spherical construction: [@Bonev2023sfno, Sections 3.4-4.2].

Let $\mathcal G$ map an input field $a$ (an initial condition, forcing, or coefficient) to an output field $u$. A PDE solution map is an example; it can be nonlinear even though parts of its solver are linear. A parameter vector $\vartheta\in\mathbb R^p$ defines an approximation $\mathcal G_\vartheta$. For training pairs $(a_j,u_j)$, $j=1,\ldots,N$, a quadratic empirical risk is

$$
\mathcal R_N(\vartheta)=\frac1N\sum_{j=1}^N
\|\mathcal G_\vartheta(a_j)-u_j\|_Y^2,
\tag{12.4}
$$

where $\|\cdot\|_Y$ is a specified output norm, including its spatial weights and units. Empirical means refer to this finite dataset; population risk is the expectation under a stated distribution. Good training fit alone proves neither small held-out risk nor correct behavior outside the training distribution.

A common hidden-field update, with layer index $r$, is

$$
v_{r+1}(x)=\sigma\left(W_rv_r(x)+b_r(x)
+\mathcal T^{-1}\!\left[R_r\,\mathcal T v_r\right](x)\right).
\tag{12.5}
$$

Here $v_r(x)$ is a vector of real scalar features (channels); $W_r$ is a channel matrix applied at each point; $b_r$ is a bias; $\sigma$ is a nonlinear activation applied to each component, for example $\max(0,z)$ for real $z$; $\mathcal T$ is Fourier or spherical harmonic analysis; $R_r$ is a learned spectral channel matrix, possibly truncated by degree; and $\mathcal T^{-1}$ synthesizes a field. The real formulation requires real $W_r,b_r$ and conjugate-compatible spectral weights: Fourier matrices satisfy $R_r(-n)=\overline{R_r(n)}$, with real weights at self-conjugate zero and Nyquist modes. A spherical matrix shared across all orders of a degree must be real to preserve $f_\ell^{-m}=(-1)^m\overline{f_\ell^m}$. These conditions keep synthesis real before the real activation. A complex architecture instead needs an explicitly chosen complex activation. Input and output pointwise maps convert between physical variables and hidden features. The chain rule computes derivatives of (12.4) with respect to $\vartheta$; a gradient update $\vartheta\leftarrow\vartheta-\eta\nabla_\vartheta\mathcal R_N$ uses positive step size $\eta$. Learning these finite parameters does not mean optimizing directly over every possible function.

For a rotation-equivariant scalar spherical spectral layer, $R_r$ must be shared across $m$ at fixed $\ell$, and the remaining operations must respect the same action. Spatial nonlinearities create higher degrees, so truncation and sampling again matter. A fixed-parameter continuum formulation can be evaluated at several resolutions, but accuracy transfer still depends on quadrature, resolved scales, data, and the complete architecture. It is not established by matching array dimensions.

## An end-to-end mathematical example

**Result and motivation.** A single spherical diffusion mode connects geometry, eigenfunctions, PDE evolution, quadrature, statistics, and operator approximation without an implementation-specific assumption. Sources: [@ArfkenWeber2005, Sections 9.8, 12.6, 16.2]; steps follow the preceding chapters.

Let the physical sphere have radius $R$, diffusivity $\kappa>0$, and real initial scalar $u_0=A(\mu^2-1/3)$, where $A$ is an amplitude with units $U$. Set no forcing and solve $u_t=\kappa\Delta_su$. Since $\mu^2-1/3=(2/3)P_2(\mu)$, only $(\ell,m)=(2,0)$ is present. Equations (5.1) and (8.6) give

$$
u(\mu,t)=A(\mu^2-1/3)e^{-6\kappa t/R^2},
\qquad \langle u\rangle_A=0,
\qquad \langle u^2\rangle_A=\frac{4A^2}{45}e^{-12\kappa t/R^2}.
\tag{12.6}
$$

For the mean square, integrate $\mu^4-2\mu^2/3+1/9$ under $d\mu/2$ to get $1/5-2/9+1/9=4/45$. A degree-$2$ harmonic representation is exact. Three Gaussian latitudes integrate its squared amplitude (degree four) exactly, and five equally spaced longitudes suffice for general degree-$2$ recovery. The decay time is $R^2/(6\kappa)$; a forward-Euler update is stable for this isolated mode if $\Delta t\le R^2/(3\kappa)$.

The time-$t$ solution operator has multiplier $e^{-\kappa\ell(\ell+1)t/R^2}$ at every degree. An isotropic learned linear map could approximate these multipliers. Changing a cutoff changes representable inputs; changing $R$ changes physical decay; an incorrect area rule changes reported mean-square error. Agreement on one sampled field does not verify all these properties. If $A$ is random with finite second moment, ensemble mean square replaces $A^2$ by $\mathbb EA^2$, which is a different average from the spatial one.

## Chapter summary and self-test

**Main results and terms.** Integral kernels encode nonlocal linear maps. Translation invariance and spherical isotropy give spectral multipliers with normalization fixed by the integration measure. Equivariance commutes with a specified transformation action; invariance removes the transformed dependence. A learned operator approximates a function-to-function map using finite parameters and a stated loss. Spectral layers reuse classical analysis and synthesis, while nonlinearities couple modes. Equation (12.6) supplies a complete analytic check of this chain.

**Self-test.** For the spherical kernel $k(t)=t$, which degrees survive, and what is their multiplier? Does allowing a different coefficient for each $m$ preserve all rotations? What must be specified before calling a model's error "small"?

# Self-test answers {.unnumbered #answers}

**Chapter 1.** Equation (1.1) gives $|e^{i\alpha}c|^2=|c|^2$. The second row of the proposed linear system is $0=1$, so there is no solution, rather than a merely nonunique one. If the second right-hand entry were zero, the second unknown would be arbitrary.

**Chapter 2.** Apply (2.10) with $q=\rho$, flux $\rho\mathbf u$, and zero mass source. Expansion gives $D\rho/Dt=-\rho\nabla\cdot\mathbf u$, so incompressibility implies constant density along trajectories. For the translating profile, $q_t=-cq_0'$ and $cq_x=cq_0'$ cancel; advection accounts for the local change.

**Chapter 3.** In (3.6), $\partial_\mu[(1-\mu^2)\partial_\mu\mu]=-2\mu$, and the longitude term is zero. For $\psi=A\sin\varphi=A\mu$, (3.7) gives $u=-A\cos\varphi/R$, $v=0$, and $\zeta=-2A\sin\varphi/R^2$. Here $[A]=\mathrm m^2\,\mathrm s^{-1}$, so speeds have units $\mathrm m\,\mathrm s^{-1}$ and vorticity $\mathrm s^{-1}$.

**Chapter 4.** Its squared norm is $\frac12\int_{-1}^13\mu^2d\mu=1$. The example $\sin(nx)/n$ has vanishing field norm but a derivative of nonvanishing norm; deriving wind differentiates streamfunction. The derivative of a step is a Dirac delta distribution, not an $L^2$ function.

**Chapter 5.** The single mode has decay time $\tau=[\kappa(2\pi/d)^2]^{-1}$. Integrating $-u''=1$ over a periodic interval gives $0=d$, contradicting $d>0$. The forcing is not orthogonal to the constant nullspace.

**Chapter 6.** Their difference $w$ obeys diffusion with homogeneous data at the boundary, so (6.2) implies $\|w(t)\|_2\le\|w(0)\|_2$. Constants have zero normal derivative and zero Laplacian, leaving the Neumann mean undetermined. A large Peclet number at one reference length cannot suppress diffusion at all shorter lengths because its rate scales as $\kappa/\ell^2$.

**Chapter 7.** $c_2=c_{-2}=3/2$ and all others vanish, so the mean square is $9/2$. A DFT round trip recovers a finite sample vector, which is identical for aliased continuous modes by (7.10). The $n$th periodic diffusion coefficient decays at rate $\kappa(2\pi n/d)^2$; the zero mode is unchanged.

**Chapter 8.** $\mu^2-1/3=(2/3)\sqrt{4\pi/5}Y_2^0$. Since its eigenvalue is $-6/R^2$, the zero-mean Poisson solution is $\psi=-AR^2(\mu^2-1/3)/6$. A real degree-$2$ field has $1+3+5=9$ independent real coefficients. A latitude-longitude periodic FFT assumes a rectangular periodic geometry; the sphere instead has a nonuniform area measure, coordinate poles, and associated Legendre latitude eigenfunctions.

**Chapter 9.** At $L=3$, sufficient linear sizes are $n=4$, $M=7$, and sufficient quadratic sizes are $n=5$, $M=10$. More grid points at a fixed cutoff improve quadrature but do not introduce additional retained harmonics. A stable implicit step may damp a resolved mode at the wrong rate if the step is too large; stability is a bound on growth, not an accuracy estimate.

**Chapter 10.** Equation (10.4) gives $\omega/k=-\beta/(k^2+l^2)<0$ when $k\ne0$ and $\beta>0$. In (10.3), $R^2\zeta$ has units $\mathrm m^2\,\mathrm s^{-1}$, as required for $\psi$. At fixed total $K$ concentrated at one degree, moving from degree $2$ to $4$ multiplies $Z$ by $4\cdot5/(2\cdot3)=10/3$. This is a comparison of two spectra, not an inviscid-transfer trajectory constrained by all invariants.

**Chapter 11.** Overlap shares observations and usually creates dependence; independence requires evidence about the sampling process. The geometric-correlation approximation gives $900/9=100$ variance-equivalent samples. Predicting $m(X)$ removes the squared bias term in (11.3), but not the remaining conditional variance, which concerns information absent from $X$.

**Chapter 12.** $k(t)=P_1(t)$ has only degree one and multiplier $\kappa_1=4\pi/3$ by (12.2). Arbitrary order-dependent coefficients generally fail to commute with rotations that mix orders. A claim about error needs the output variable, units or normalization, norm and spatial weights, target distribution, sampling unit, and comparison scale.

Retry a missed prompt using only its chapter summary, then reconstruct the derivation from the chapter. If a result cannot be recovered, revisit the relevant definition or assumption before adding more practice.

# Repository reading map {.unnumbered #repository-map}

This map locates applications of the general theory. Paths identify source locations, not additional mathematical assumptions. It describes the inspected source tree at base commit `d4e3594`; it does not claim that an experiment or saved notebook output was rerun.

| Read in the repository | Mathematical prerequisites |
|:--|:--|
| [Simulation overview](../../sim/README.md); [model methods](../../docs/isca-barotropic-stirring.md) | Conservation and rotating vorticity: Chapters 2, 3, 6, 10 |
| [Grid conventions](../../docs/grids.md); [grid diagnostics](../../ml/src/ml/diagnostics/grid.py) | Surface measure and Gaussian quadrature: Chapters 3, 8, 9 |
| [Spectra](../../ml/src/ml/diagnostics/spectra.py); [enstrophy](../../ml/src/ml/diagnostics/enstrophy.py) | Parseval, vorticity inversion, spectra: Chapters 7-10 |
| [Norm conventions](../../docs/norms.md); [error diagnostics](../../ml/src/ml/diagnostics/errors.py) | Weighted norms and statistical objectives: Chapters 4, 9, 11 |
| [Climatological targets](../../ml/src/ml/data/climatology.py); [convergence](../../ml/src/ml/diagnostics/convergence.py) | Time means and serial dependence: Chapter 11 |
| [Model construction](../../ml/src/ml/training/model.py); [spectral adapter](../../ml/src/ml/patches/neuralop.py) | Basis choice, spectral multipliers, learned maps: Chapters 8, 9, 12 |

The general theory is also rendered in `book/` from the same chapter sources. Project-specific settings, data schemas, and implementation behavior belong in `docs/`, `sim/`, and `ml/`.

# References {.unnumbered #references}

::: {#refs}
:::
