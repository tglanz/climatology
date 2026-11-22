---
title: "Mathematical prerequisites"
subtitle: "From fields and conservation to spherical analysis and operator maps"
date: "22 November 2026"
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

Read Chapters 1-8 in order. Chapter 9 adds discretization, Chapter 10 fluid applications, Chapter 11 statistics, and Chapter 12 operator maps. Teaching objects share one counter per chapter; equations and exercises have separate counters. Definitions have a left rule, results a frame, and examples a top rule. Proofs and derivations identify their target result. Exercises close sections; checked solutions are supplied in a separate instructor key.

# Mathematical language and linear algebra {#ch-language}

What information must accompany a field before we can calculate with it? Domains and units tell us which operations are meaningful; a basis tells us what its stored coefficients represent. We develop these ideas first for finite vectors, where projection and inversion can be seen directly, before applying them to functions in Chapter 4.

## Scalars, functions, and dimensions

A field assigns a value to each position and time. Its domain, units, and type determine which equations and averages are meaningful. This is the starting point for interpreting either a PDE or an array of samples. Sources: [@ArfkenWeber2005, Sections 1.1-1.4, 2.6, 6.1].

::: {.tb-definition #obj-1-1}
**Definition 1.1 - Fields, domains, and number systems**

The sets $\mathbb R$, $\mathbb C$, $\mathbb Z$, and $\mathbb N_0$ denote real numbers, complex numbers, integers, and nonnegative integers. The notation $x\in D$ means that $x$ belongs to the set $D$; $f:D\to V$ assigns a unique element of $V$ to every element of $D$. The image $f(x)$ is the value at $x$. A domain is the region on which a field is defined. A scalar field takes real or complex values; a vector field takes values in a vector space. A component is a scalar coordinate in a chosen basis.

Write position as $\mathbf x=(x_1,x_2,x_3)$, time as $t$, and a real scalar field as $q(\mathbf x,t)$. A sampled array $q_{ij}$ stores values at specified positions; its indices are not physical coordinates. A continuous field and its finite sample array are different mathematical objects.
:::

::: {.tb-definition #obj-1-2}
**Definition 1.2 - Complex numbers and oscillatory notation**

The imaginary unit $i$ satisfies $i^2=-1$. For real $a,b$, define $z=a+ib$, conjugate $\overline z=a-ib$, real part $\operatorname{Re}z=a$, and modulus $|z|=(a^2+b^2)^{1/2}$.

Here $\alpha$ is a dimensionless angle in radians. The exponential can be defined by $e^z=\sum_{n=0}^{\infty}z^n/n!$, where $n!=1\cdot2\cdots n$ and $0!=1$. A sum means repeated addition; an infinite sum denotes the limit of its finite partial sums. The sine and cosine are the imaginary and real parts of $e^{i\alpha}$.
:::

::: {.tb-result #obj-1-3}
**Result 1.3 - Euler's identity and unit-modulus phase**

For every real dimensionless angle $\alpha$, the complex exponential satisfies the following identities [@ArfkenWeber2005, Section 6.1].

$$
e^{i\alpha}=\cos\alpha+i\sin\alpha,\qquad
\overline{e^{i\alpha}}=e^{-i\alpha},\qquad |e^{i\alpha}|=1.
\tag{1.1}
$$
:::

::: {.tb-proof}
**Proof of Result 1.3**

Separate the even and odd terms of the exponential series. The even terms sum to $\cos\alpha$, and the odd terms sum to $i\sin\alpha$. Conjugating changes $i$ to $-i$; multiplying the two conjugate exponentials gives $e^{i\alpha}e^{-i\alpha}=1$. $\square$
:::

::: {.tb-definition #obj-1-4}
**Definition 1.4 - Physical dimensions and admissible operations**

Use $[q]$ for the physical dimensions of $q$. An equation can add only quantities with the same dimensions. If length and time have units $\mathrm m$ and $\mathrm s$, velocity has $[u]=\mathrm m\,\mathrm s^{-1}$, vorticity has $[\zeta]=\mathrm s^{-1}$, and a diffusivity has $[\kappa]=\mathrm m^2\,\mathrm s^{-1}$. Derivatives divide by the units of the independent variable. A logarithm or an exponential requires a dimensionless argument. For example, $\exp(-\kappa k^2t)$ is admissible when $k$ has units $\mathrm m^{-1}$.
:::

::: {.tb-exercise #ex-1-1}
**Exercise 1.1 - Check a decay exponent**

*Application.* A decay model uses $e^{-\kappa kt}$. If $[\kappa]=\mathrm m^2\,\mathrm s^{-1}$, $[k]=\mathrm m^{-1}$, and $[t]=\mathrm s$, is the exponent admissible? How would a diffusive exponent change?
:::

## Vectors, bases, and linear maps

A basis separates a mathematical object from the coefficients used to store it. Changing basis changes coefficients, while the underlying vector or field stays the same. Sources: [@ArfkenWeber2005, Sections 1.2-1.5, 3.2-3.4].

::: {.tb-definition #obj-1-5}
**Definition 1.5 - Vector spaces, independence, and bases**

A vector space is a set closed under addition and multiplication by scalars, with associative and commutative addition, a zero vector, additive inverses, and the distributive rules. Vectors $\mathbf e_1,\ldots,\mathbf e_n$ are linearly independent if $\sum_jc_j\mathbf e_j=0$ implies every $c_j=0$. Their span is the set of all such linear combinations. They form a basis of a space if they are independent and span it. The number $n$ of basis vectors is its dimension.
:::

::: {.tb-definition #obj-1-6}
**Definition 1.6 - Euclidean products and orientation**

In a real orthonormal Cartesian basis, the dot product and length are

$$
\mathbf u\cdot\mathbf v=\sum_{j=1}^{n}u_jv_j,
\qquad |\mathbf u|^2=\mathbf u\cdot\mathbf u.
\tag{1.2}
$$

Orthonormal means $\mathbf e_j\cdot\mathbf e_k=\delta_{jk}$, where the Kronecker symbol $\delta_{jk}$ is one for $j=k$ and zero otherwise. In three dimensions the cross product is the vector perpendicular to its arguments with components $(\mathbf u\times\mathbf v)_i=\sum_{j,k}\epsilon_{ijk}u_jv_k$. The permutation symbol $\epsilon_{ijk}$ is zero if an index repeats, $+1$ for an even permutation of $(1,2,3)$, and $-1$ for an odd permutation. Its sign fixes a right-handed orientation.
:::

::: {.tb-definition #obj-1-7}
**Definition 1.7 - Linear maps, matrices, and nullspaces**

A map $A$ is linear if $A(\alpha\mathbf u+\beta\mathbf v)=\alpha A\mathbf u+\beta A\mathbf v$. A matrix represents that map in chosen input and output bases: $(A\mathbf u)_i=\sum_jA_{ij}u_j$. Matrix multiplication represents composition. The identity matrix $I$ leaves vectors unchanged. The nullspace is $\ker A=\{\mathbf u:A\mathbf u=0\}$; the range is the set of outputs.
:::

::: {.tb-result #obj-1-8}
**Result 1.8 - Invertibility in finite dimensions (quoted)**

For a linear map between two $n$-dimensional spaces, an inverse exists if and only if its kernel is zero, equivalently its range is the whole target. For a square representing matrix, this is also equivalent to a nonzero determinant, its signed volume factor [@ArfkenWeber2005, Section 3.2].
:::

::: {.tb-definition #obj-1-9}
**Definition 1.9 - Complex inner products and adjoint matrices**

For complex vectors use the inner product $\langle\mathbf u,\mathbf v\rangle=\sum_j u_j\overline{v_j}$, linear in its first argument throughout this guide. The adjoint matrix $A^*=\overline A^{\mathsf T}$ is the conjugate transpose. A Hermitian matrix has $A=A^*$; a unitary matrix has $A^*A=I$. Unitary changes of coordinates preserve inner products and norms. A real unitary matrix is called orthogonal.
:::

::: {.tb-exercise #ex-1-2}
**Exercise 1.2 - Change coefficients without changing length**

*Application.* Let $Q=\begin{pmatrix}0&-1\\1&0\end{pmatrix}$ and $\mathbf u=(2,1)^{\mathsf T}$. Compute $Q\mathbf u$ and compare lengths. Is $Q$ orthogonal?
:::

## Eigenvectors, projection, and conditioning

Hermitian operators admit orthogonal modes. In those modes differentiation, diffusion, and elliptic inversion become scalar calculations. Small eigenvalues also expose unstable inversions. Sources: [@ArfkenWeber2005, Sections 3.5-3.6, 10.2-10.3].

::: {.tb-definition #obj-1-10}
**Definition 1.10 - Eigenvectors and eigenvalues**

An eigenvector is a nonzero vector $\mathbf v$ such that $A\mathbf v=\lambda\mathbf v$; $\lambda$ is its eigenvalue.
:::

::: {.tb-result #obj-1-11}
**Result 1.11 - Hermitian eigenvalues and orthogonality**

If $A=A^*$ in the complex Euclidean inner product, every eigenvalue is real and eigenvectors with distinct eigenvalues are orthogonal.
:::

::: {.tb-proof}
**Proof of Result 1.11**

Use the adjoint identity to compare the scalar with its conjugate. For $A\mathbf v=\lambda\mathbf v$ and $\mathbf v\ne0$,

$$
\lambda\|\mathbf v\|^2
=\langle A\mathbf v,\mathbf v\rangle
=\langle\mathbf v,A\mathbf v\rangle
=\overline\lambda\|\mathbf v\|^2.
\tag{1.3}
$$

Thus $\lambda$ is real. Applying the same identity to eigenvectors with eigenvalues $\lambda$ and $\eta$ gives $(\lambda-\eta)\langle\mathbf v,\mathbf w\rangle=0$; distinct eigenvalues have orthogonal eigenvectors. $\square$
:::

::: {.tb-result #obj-1-12}
**Result 1.12 - Finite-dimensional spectral theorem (quoted)**

Every Hermitian matrix has an orthonormal eigenbasis: $A=Q\Lambda Q^*$, where $Q$ is unitary and $\Lambda$ is a real diagonal matrix [@ArfkenWeber2005, Sections 3.5-3.6]. The differential analogue will need boundary conditions in Chapter 5.
:::

::: {.tb-definition #obj-1-13}
**Definition 1.13 - Orthogonal projection**

For orthonormal $\mathbf e_j$, the projection onto their span is $P\mathbf u=\sum_j\langle\mathbf u,\mathbf e_j\rangle\mathbf e_j$.
:::

::: {.tb-result #obj-1-14}
**Result 1.14 - Projection gives the best squared-error approximation**

For an orthonormal family $\mathbf e_j$, let $P$ project onto its span. For every $\mathbf u$ and every $\mathbf v$ in that span,

$$
\|\mathbf u-\mathbf v\|^2
=\|\mathbf u-P\mathbf u\|^2+\|P\mathbf u-\mathbf v\|^2.
\tag{1.4}
$$

Consequently $P\mathbf u$ minimizes the error over that span.
:::

::: {.tb-proof}
**Proof of Result 1.14**

The residual $\mathbf u-P\mathbf u$ is orthogonal to each $\mathbf e_j$, hence to $P\mathbf u-\mathbf v$. Expand the squared norm of their sum; both cross terms vanish. This proves (1.4), and its second term is nonnegative. $\square$
:::

::: {.tb-definition #obj-1-15}
**Definition 1.15 - Induced norm and condition number**

For invertible $A$, define $\sup$ as the least upper bound of a set of real numbers. Its induced norm is $\|A\|=\sup_{\mathbf v\ne0}\|A\mathbf v\|/\|\mathbf v\|$ and condition number $\operatorname{cond}(A)=\|A\|\|A^{-1}\|$.
:::

::: {.tb-result #obj-1-16}
**Result 1.16 - Sensitivity to right-hand-side errors**

Let $A$ be invertible, $A\mathbf u=\mathbf b$ with $\mathbf b\ne0$, and let $A(\mathbf u+\delta\mathbf u)=\mathbf b+\delta\mathbf b$. Then

$$
\frac{\|\delta\mathbf u\|}{\|\mathbf u\|}
\le\operatorname{cond}(A)\frac{\|\delta\mathbf b\|}{\|\mathbf b\|}.
\tag{1.5}
$$
:::

::: {.tb-proof}
**Proof of Result 1.16**

Subtract the equations to get $\delta\mathbf u=A^{-1}\delta\mathbf b$. The induced norm gives $\|\delta\mathbf u\|\le\|A^{-1}\|\|\delta\mathbf b\|$ and $\|\mathbf b\|\le\|A\|\|\mathbf u\|$. Combine these bounds and divide by the nonzero norms. $\square$
:::

::: {.tb-example #obj-1-17}
**Example 1.17 - A small eigenvalue amplifies noise**

For $A=\operatorname{diag}(1,\varepsilon)$ with $0<\varepsilon\ll1$, noise in the second component is amplified by $1/\varepsilon$. A zero eigenvalue requires a compatibility condition and an additional choice fixing the nullspace component; division by zero is not an inversion method.
:::

::: {.tb-exercise #ex-1-3}
**Exercise 1.3 - Project onto a line**

*Application.* Project $(2,1)$ onto the span of $(1,1)/\sqrt2$. Verify (1.4) with comparison vector $(1,1)$.
:::

## Chapter summary

A field has a domain, value type, and units. A basis defines coefficients; a linear map acts on vectors; its nullspace controls uniqueness. Complex conjugation defines a positive inner product. Hermitian matrices have real eigenvalues and orthonormal eigenbases. Orthogonal projection minimizes squared error by (1.4). Conditioning measures sensitivity through (1.5).

::: {.tb-exercise #ex-1-4}
**Exercise 1.4 - Connect the chapter results**

*Synthesis.* Why does multiplying a complex Fourier coefficient by $e^{i\alpha}$ preserve its squared modulus? What prevents a unique solution of $\operatorname{diag}(1,0)\mathbf u=(1,1)$?
:::

# Calculus, fluxes, and conservation {#ch-calculus}

How does a local rate become a conservation equation? The derivative describes change along a direction or a trajectory; integration identifies what crosses the boundary of a region. This chapter connects those two descriptions, providing the transport and energy identities used throughout the PDE chapters.

## Derivatives, local linearization, and transport

A derivative is a local linear approximation. Following a moving parcel introduces advection through the chain rule. Sources: [@ArfkenWeber2005, Sections 1.6, 5.5-5.7, 9.2].

::: {.tb-definition #obj-2-1}
**Definition 2.1 - Derivatives and local remainder estimates**

For a scalar function $f(x)$, $f'(x)=\lim_{h\to0}[f(x+h)-f(x)]/h$ when this limit exists. A partial derivative $\partial_jf=\partial f/\partial x_j$ holds all other variables fixed. Write $f\in C^k$ if its derivatives through order $k$ exist and are continuous. The notation $r(h)=O(h^p)$ means $|r(h)|\le C|h|^p$ for a constant $C$ and sufficiently small $|h|$; $r(h)=o(h)$ means $r(h)/h\to0$.
:::

::: {.tb-definition #obj-2-2}
**Definition 2.2 - Jacobian, gradient, and Hessian**

A differentiable map $\mathbf F:\mathbb R^n\to\mathbb R^m$ has a Jacobian matrix $(D\mathbf F)_{ij}=\partial_jF_i$ satisfying $\mathbf F(\mathbf x+\mathbf h)=\mathbf F(\mathbf x)+D\mathbf F(\mathbf x)\mathbf h+o(|\mathbf h|)$. A scalar's gradient is the vector $\nabla f=(\partial_1f,\ldots,\partial_nf)$. Its Hessian $H_f$ is the matrix $(\partial_i\partial_jf)$.
:::

::: {.tb-result #obj-2-3}
**Result 2.3 - Second-order Taylor expansion (quoted)**

For a $C^3$ scalar field near $\mathbf x$, with its derivatives evaluated at $\mathbf x$,

$$
f(\mathbf x+\mathbf h)=f(\mathbf x)+\nabla f\cdot\mathbf h
+\tfrac12\mathbf h^{\mathsf T}H_f\mathbf h+O(|\mathbf h|^3).
\tag{2.1}
$$

The remainder bound is local [@ArfkenWeber2005, Section 5.6].
:::

::: {.tb-result #obj-2-4}
**Result 2.4 - Hessian test at a critical point (quoted)**

The Hessian is symmetric for $C^2$ functions because mixed partial derivatives commute. A critical point has $\nabla f=0$; a positive-definite Hessian at a critical point, meaning $\mathbf h^{\mathsf T}H_f\mathbf h>0$ for every nonzero $\mathbf h$, implies a strict local minimum. This is the second-derivative test, quoted under the stated smoothness conditions [@ArfkenWeber2005, Section 5.6].
:::

::: {.tb-definition #obj-2-5}
**Definition 2.5 - Composition and definite integration**

For differentiable one-variable functions, the product rule is $(fg)'=f'g+fg'$ and the chain rule is $(f\circ g)'(x)=f'(g(x))g'(x)$, where $f\circ g$ means composition. The familiar derivatives $(e^x)'=e^x$, $(\sin x)'=\cos x$, and $(\cos x)'=-\sin x$ follow from their defining series. A definite integral $\int_a^b f(x)dx$ is the limit of sums $\sum_j f(\xi_j)\Delta x_j$ as the largest partition width tends to zero, for continuous $f$; $\xi_j$ is a point in the $j$th subinterval. The fundamental theorem of calculus and the product rule give
:::

::: {.tb-result #obj-2-6}
**Result 2.6 - Fundamental theorem and integration by parts**

Let $f$ be continuous with antiderivative $F$, and let $f,g$ be $C^1$ for the second identity. With $[h]_a^b=h(b)-h(a)$,

$$
F'(x)=f(x)\ \Longrightarrow\ \int_a^b f(x)dx=F(b)-F(a),
\qquad
\int_a^b f g'\,dx=[fg]_a^b-\int_a^b f'g\,dx.
\tag{2.2}
$$

The fundamental theorem is quoted as a basic calculus result; the second identity follows from it.
:::

::: {.tb-proof}
**Proof of Result 2.6**

For the integration-by-parts identity, integrate the product rule $(fg)\prime=f\prime g+fg\prime$ over $[a,b]$ and use the fundamental theorem on the left. Rearrange the resulting equality. This proves the second assertion; the first is the quoted fundamental theorem. $\square$
:::

::: {.tb-example #obj-2-7}
**Example 2.7 - An integral with a polynomial factor**

Take $f=x$, $g'=e^x$, $g=e^x$ to obtain $\int_0^1xe^x dx=[xe^x]_0^1-\int_0^1e^x dx=e-(e-1)=1$. The multivariable chain rule is the same local-linearization rule applied to a trajectory.
:::

::: {.tb-definition #obj-2-8}
**Definition 2.8 - Parcel path and material derivative**

A parcel path $\mathbf X(t)$ satisfies $\mathbf X\prime(t)=\mathbf u(\mathbf X(t),t)$. The material derivative $Dq/Dt$ is the rate of $q(\mathbf X(t),t)$ along this path. The symbol $:=$ means "is defined as."
:::

::: {.tb-result #obj-2-9}
**Result 2.9 - Transport is a chain-rule term**

For a differentiable scalar $q(\mathbf x,t)$ and a differentiable parcel path following $\mathbf u$,

$$
\frac{Dq}{Dt}:=\frac{d}{dt}q(\mathbf X(t),t)
=\partial_tq+\mathbf u\cdot\nabla q.
\tag{2.3}
$$
:::

::: {.tb-proof}
**Proof of Result 2.9**

Differentiate $q(\mathbf X(t),t)$ by the multivariable chain rule: the spatial contribution is $\sum_j(\partial_jq)X_j\prime$. Substitute $X_j\prime=u_j$ and collect the dot product. $\square$
:::

::: {.tb-example #obj-2-10}
**Example 2.10 - A translating profile**

Local change $\partial_tq$ is measured at a fixed location; advection $\mathbf u\cdot\nabla q$ measures motion across spatial gradients. For constant speed $c$, $q(x,t)=q_0(x-ct)$ satisfies $\partial_tq+c\partial_xq=0$ even while a fixed sensor sees a changing signal.
:::

::: {.tb-exercise #ex-2-1}
**Exercise 2.1 - Evaluate an advective rate**

*Application.* For $q(x,y,t)=x^2+yt$ and velocity $\mathbf u=(U,0)$, compute $Dq/Dt$ at a fixed $(x,y,t)$. Assume $x,y,t$ are dimensionless in this algebraic example.
:::

## Gradient, divergence, curl, and Laplacian

Gradient measures directional change, divergence measures outward flux density, and curl measures circulation density. The scalar Laplacian is the divergence of a gradient. Sources: [@ArfkenWeber2005, Sections 1.6-1.9].

::: {.tb-definition #obj-2-11}
**Definition 2.11 - Cartesian differential operators**

In right-handed Cartesian coordinates and for a $C^1$ vector field $\mathbf F=(F_1,F_2,F_3)$, define

$$
\nabla\cdot\mathbf F=\sum_i\partial_iF_i,
\qquad (\nabla\times\mathbf F)_i=\sum_{j,k}\epsilon_{ijk}\partial_jF_k,
\qquad \Delta q=\nabla\cdot\nabla q=\sum_i\partial_i^2q.
\tag{2.4}
$$
:::

::: {.tb-example #obj-2-12}
**Example 2.12 - Local expansion and rigid rotation**

For a unit direction $\mathbf n$, $\mathbf n\cdot\nabla q$ is change per unit distance along $\mathbf n$. For velocity, $\nabla\cdot\mathbf u>0$ means a small parcel expands. The vorticity $\boldsymbol\omega=\nabla\times\mathbf u$ measures twice the local rigid rotation rate. Solid-body planar rotation $\mathbf u=(-\Omega y,\Omega x,0)$ has $\nabla\cdot\mathbf u=0$ and $\boldsymbol\omega=(0,0,2\Omega)$; circulation is not the same as speed.
:::

::: {.tb-result #obj-2-13}
**Result 2.13 - Product and commuting-derivative identities**

For $C^2$ fields in Cartesian coordinates,

$$
\begin{aligned}
\nabla\cdot(q\mathbf F)&=\nabla q\cdot\mathbf F+q\nabla\cdot\mathbf F,\\
\nabla\times\nabla q&=0,\qquad \nabla\cdot(\nabla\times\mathbf F)=0,\\
\nabla\times(\nabla\times\mathbf F)&=\nabla(\nabla\cdot\mathbf F)-\Delta\mathbf F.
\end{aligned}
\tag{2.5}
$$
:::

::: {.tb-proof}
**Proof of Result 2.13**

Expand the product derivative componentwise. In the curl of a gradient, the terms $\partial_j\partial_kq$ cancel in antisymmetric pairs. The divergence of a curl cancels the same way. For the double curl, contraction of the two permutation symbols leaves $\partial_i\sum_j\partial_jF_j-\sum_j\partial_j^2F_i$. $\square$
:::

::: {.tb-remark #obj-2-14}
**Remark 2.14 - Components in a moving basis**

The vector Laplacian in the last line acts on Cartesian components. These identities assume enough continuous derivatives. Curvilinear components require basis-variation terms; differentiating each spherical component as a Cartesian scalar is generally incorrect.
:::

::: {.tb-exercise #ex-2-2}
**Exercise 2.2 - Divergence does not determine curl**

*Application.* Compute divergence and curl of $\mathbf F=(-y,x,0)$ and of the zero field. What do equal divergences fail to tell us?
:::

## Integration, Jacobians, and integral theorems

Conservation laws relate what crosses a boundary to what changes inside. Correct integration also fixes the weights in global means. Sources: [@ArfkenWeber2005, Sections 1.10-1.12, 2.1-2.2].

::: {.tb-definition #obj-2-15}
**Definition 2.15 - Measures and oriented boundaries**

An integral sums a density over lengths, areas, or volumes. Write $dV$ for volume, $dA$ for surface area, and $d\mathbf l$ for an oriented tangent line element. Let $V\subset\mathbb R^3$ have a piecewise smooth closed boundary $\partial V$ with outward unit normal $\mathbf n$.
:::

::: {.tb-result #obj-2-16}
**Result 2.16 - Divergence theorem (quoted)**

For a $C^1$ field on a region $V$ and its piecewise smooth closed boundary with outward normal $\mathbf n$,

$$
\int_V\nabla\cdot\mathbf F\,dV
=\int_{\partial V}\mathbf F\cdot\mathbf n\,dA.
\tag{2.6}
$$

This is the divergence theorem [@ArfkenWeber2005, Section 1.11].
:::

::: {.tb-result #obj-2-17}
**Result 2.17 - Stokes' theorem (quoted)**

For an oriented smooth surface $S$ with boundary curve $\partial S$, oriented by the right-hand rule, Stokes' theorem is

$$
\int_S(\nabla\times\mathbf F)\cdot\mathbf n\,dA
=\oint_{\partial S}\mathbf F\cdot d\mathbf l.
\tag{2.7}
$$

The circle on $\oint$ denotes integration around a closed curve. These identities require fields regular on the integration region; a singular vortex cannot be ignored inside it.
:::

::: {.tb-result #obj-2-18}
**Result 2.18 - Jacobian change of volume**

A smooth invertible coordinate map $\mathbf x=\mathbf X(\mathbf q)$ changes volume by

$$
dV=\left|\det D\mathbf X(\mathbf q)\right|\,dq_1dq_2dq_3.
\tag{2.8}
$$
:::

::: {.tb-proof}
**Proof of Result 2.18**

The determinant is the Jacobian factor: a small coordinate box maps to a parallelepiped spanned by $\partial_{q_i}\mathbf X\,dq_i$. $\square$
:::

::: {.tb-definition #obj-2-19}
**Definition 2.19 - Area of a parametrized surface**

For a smooth surface $\mathbf X(a,b)$, the area factor is $|\partial_a\mathbf X\times\partial_b\mathbf X|$. Coordinate labels become physical measures through these factors.
:::

::: {.tb-result #obj-2-20}
**Result 2.20 - Green's first identity**

For real $C^2$ functions $f,g$ on a regular region $V$, with $\partial_ng=\mathbf n\cdot\nabla g$,

$$
\int_V f\Delta g\,dV
=\int_{\partial V}f\partial_ng\,dA-\int_V\nabla f\cdot\nabla g\,dV,
\qquad \partial_ng=\mathbf n\cdot\nabla g.
\tag{2.9}
$$
:::

::: {.tb-proof}
**Proof of Result 2.20**

Apply the divergence theorem to $\mathbf F=f\nabla g$. The product rule gives $\nabla\cdot(f\nabla g)=\nabla f\cdot\nabla g+f\Delta g$; rearrange the integrated identity. $\square$
:::

::: {.tb-remark #obj-2-21}
**Remark 2.21 - Boundary terms and complex fields**

This is multidimensional integration by parts. For complex $f$, replace $f$ by $\overline f$ when constructing energy or adjoint identities. A boundary condition determines whether the boundary term vanishes.
:::

::: {.tb-exercise #ex-2-3}
**Exercise 2.3 - Check an area factor**

*Application.* For $\mathbf X(a,b)=(a,b,0)$, compute its surface area factor. What area corresponds to $0\le a\le2$, $0\le b\le3$?
:::

## From a balance law to a PDE

A local conservation PDE is the differential form of a balance for every fixed control volume. It distinguishes transport from sources. Sources: [@ArfkenWeber2005, Sections 1.7, 1.11, 9.8]; fluid interpretation: [@Vallis2006, Sections 1.2, 1.7].

::: {.tb-model #obj-2-22}
**Model 2.22 - A transported amount with sources**

Let $q$ be amount per unit volume, $\mathbf J$ its flux (amount per area per time), and $s$ its production per volume per time.
:::

::: {.tb-law #obj-2-23}
**Law 2.23 - Integral conservation balance**

For every fixed control volume, rate of accumulation equals inward net flux plus production. This physical balance supplies the left statement in (2.10); smoothness will permit its localization.
:::

::: {.tb-result #obj-2-24}
**Result 2.24 - Local conservation from every control volume**

Suppose $q,\mathbf J,s$ are sufficiently smooth and the integral balance holds for every regular fixed volume $V$. Then the local PDE follows:

$$
\frac{d}{dt}\int_Vq\,dV=-\int_{\partial V}\mathbf J\cdot\mathbf n\,dA+\int_Vs\,dV
\quad\Longrightarrow\quad
\partial_tq+\nabla\cdot\mathbf J=s.
\tag{2.10}
$$
:::

::: {.tb-proof}
**Proof of Result 2.24**

The implication uses (2.6) and the fact that the integral of a continuous function over every small volume vanishes only if that function is zero. $\square$
:::

::: {.tb-model #obj-2-25}
**Model 2.25 - Advective transport with Fickian diffusion**

For an advected concentration with constant diffusivity $\kappa>0$, choose the constitutive flux $\mathbf J=q\mathbf u-\kappa\nabla q$. Diffusion is directed down the concentration gradient.
:::

::: {.tb-result #obj-2-26}
**Result 2.26 - Advection, compression, diffusion, and production**

Under the preceding flux model, (2.10) expands to

$$
\partial_tq+\mathbf u\cdot\nabla q+q\nabla\cdot\mathbf u
=\kappa\Delta q+s.
\tag{2.11}
$$
:::

::: {.tb-proof}
**Proof of Result 2.26**

Use $\nabla\cdot(q\mathbf u)=\mathbf u\cdot\nabla q+q\nabla\cdot\mathbf u$ and constant $\kappa$, so $\nabla\cdot(\kappa\nabla q)=\kappa\Delta q$. $\square$
:::

::: {.tb-remark #obj-2-27}
**Remark 2.27 - Concentration and mixing ratio**

When $\nabla\cdot\mathbf u=0$, conservative and advective forms agree. Otherwise the compression term matters. A concentration per volume differs from a mixing ratio per unit mass; the latter uses mass continuity in its transport equation.
:::

::: {.tb-exercise #ex-2-4}
**Exercise 2.4 - Identify the compression term**

*Application.* Set diffusion and production to zero. If a uniform concentration is carried by a flow with constant divergence $d_0>0$, what ODE does a parcel concentration satisfy?
:::

## Chapter summary

The Jacobian is the local derivative map and its determinant changes volume. The gradient, divergence, curl, and Laplacian have the meanings in (2.4). The material derivative (2.3) follows parcels. Divergence and Stokes' theorems convert volume or surface integrals to boundary flux or circulation. Green's identity (2.9) controls energy and adjoints. Equation (2.10) connects integral conservation with a local PDE.

::: {.tb-exercise #ex-2-5}
**Exercise 2.5 - Connect the chapter results**

*Synthesis.* Derive $\partial_t\rho+\nabla\cdot(\rho\mathbf u)=0$ for mass density $\rho$. Under what condition does it imply $D\rho/Dt=0$? Why is no source needed for the translating-profile example above?
:::

# Geometry and calculus on the sphere {#ch-sphere}

Why do uniform latitude weights and Cartesian derivative formulas fail on a sphere? Coordinate increments correspond to different physical lengths at different latitudes. We derive the metric factors first, then use length, flux, and circulation to construct the surface operators and streamfunction convention.

## Coordinates, metric factors, and area

Spherical coordinates have unequal physical scale factors. The area measure becomes uniform in sine of latitude, which explains Gaussian latitude weights. Sources: [@ArfkenWeber2005, Sections 2.1-2.2, 2.5].

::: {.tb-definition #obj-3-1}
**Definition 3.1 - Spherical and geographic coordinates**

Let $r>0$ be radius, $\theta\in[0,\pi]$ colatitude measured from the north pole, and $\lambda\in[0,2\pi)$ east longitude. Latitude is $\varphi=\pi/2-\theta$. Write

$$
\mathbf x=r(\sin\theta\cos\lambda,\sin\theta\sin\lambda,\cos\theta),
\qquad \mu=\cos\theta=\sin\varphi.
\tag{3.1}
$$
:::

::: {.tb-definition #obj-3-2}
**Definition 3.2 - Scale factors and orthonormal directions**

The unit vectors $\mathbf e_r,\mathbf e_\theta,\mathbf e_\lambda$ point toward increasing coordinates. The scale factor is $h_i=|\partial_{q_i}\mathbf x|$.
:::

::: {.tb-result #obj-3-3}
**Result 3.3 - Spherical distance and volume**

For the coordinate map (3.1), away from its coordinate singularities, the scale factors are $1,r,r\sin\theta$. Thus

$$
ds^2=dr^2+r^2d\theta^2+r^2\sin^2\theta\,d\lambda^2,
\qquad dV=r^2\sin\theta\,dr\,d\theta\,d\lambda.
\tag{3.2}
$$
:::

::: {.tb-proof}
**Proof of Result 3.3**

Differentiate (3.1) in $r,\theta,\lambda$. The resulting vectors are perpendicular and have lengths $1,r,r\sin\theta$. Their squared lengths give the distance formula; their product gives the positive volume factor. $\square$
:::

::: {.tb-definition #obj-3-4}
**Definition 3.4 - Sphere and solid-angle measure**

On the radius-$R$ sphere $S_R^2=\{\mathbf x:|\mathbf x|=R\}$, use solid angle $d\Omega=dA/R^2$.
:::

::: {.tb-result #obj-3-5}
**Result 3.5 - Surface area becomes uniform in sine of latitude**

For an integrable scalar $q$ on the radius-$R$ sphere,

$$
dA=R^2\sin\theta\,d\theta\,d\lambda
=R^2\cos\varphi\,d\varphi\,d\lambda,
\qquad
\int_{S_R^2}q\,dA=R^2\int_{-1}^1\int_0^{2\pi}q(\mu,\lambda)\,d\lambda\,d\mu.
\tag{3.3}
$$
:::

::: {.tb-proof}
**Proof of Result 3.5**

The last equality reverses the $\mu$ bounds to absorb $d\mu=-\sin\theta\,d\theta$. The integration uses positive area measure. $\square$
:::

::: {.tb-example #obj-3-6}
**Example 3.6 - Mean of sine-squared latitude**

The total area is $4\pi R^2$. For $q=\mu^2$, its global area mean is $\frac12\int_{-1}^1\mu^2\,d\mu=1/3$; equal weights on equally spaced latitudes would give a different average.
:::

::: {.tb-exercise #ex-3-1}
**Exercise 3.1 - Compute a spherical moment**

*Application.* Find the area mean of $\mu^4$ on a sphere, where $\mu=\sin\varphi$.
:::

## Tangent differential operators

Physical derivatives divide coordinate derivatives by arc lengths. These scale factors determine the spherical Laplacian and the correct signs of wind and vorticity. Sources: [@ArfkenWeber2005, Sections 2.2, 2.5].

::: {.tb-definition #obj-3-7}
**Definition 3.7 - Tangent gradient and physical components**

The surface gradient $\nabla_s q$ is tangent to the sphere and satisfies $dq=\nabla_s q\cdot d\mathbf x$ for tangent displacements. For $\mathbf F=F_\theta\mathbf e_\theta+F_\lambda\mathbf e_\lambda$, $F_\theta,F_\lambda$ are its physical components along the two tangent unit directions.
:::

::: {.tb-result #obj-3-8}
**Result 3.8 - Surface gradient, divergence, and radial curl**

For smooth scalars and tangent vector fields on $S_R^2$, with the physical components just defined,

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
:::

::: {.tb-proof}
**Proof of Result 3.8**

The gradient follows by matching $dq$ to the physical line element. For flux and circulation use the same small spherical patch:

For the divergence formula, consider a small patch with sides $R\,d\theta$ and $R\sin\theta\,d\lambda$. The difference of meridional fluxes through its latitude edges is $R\partial_\theta(\sin\theta F_\theta)d\theta d\lambda$; the longitude edges contribute $R\partial_\lambda F_\lambda d\theta d\lambda$. Divide by patch area. Applying Stokes' theorem to the same patch yields the curl formula, with counterclockwise orientation viewed from outside. $\square$
:::

::: {.tb-definition #obj-3-9}
**Definition 3.9 - Laplace-Beltrami and angular operators**

The Laplace-Beltrami operator is the surface divergence of the surface gradient. Define $\Delta_\Omega=R^2\Delta_s$.
:::

::: {.tb-result #obj-3-10}
**Result 3.10 - Spherical scalar Laplacian**

For a smooth scalar $q$, the surface operator is

$$
\Delta_s q:=\nabla_s\cdot\nabla_s q
=\frac1{R^2}\left[\frac1{\sin\theta}\partial_\theta(\sin\theta\partial_\theta q)
+\frac1{\sin^2\theta}\partial_\lambda^2q\right].
\tag{3.5}
$$

In latitude or $\mu=\sin\varphi$,

$$
\Delta_s q=\frac1{R^2\cos\varphi}\partial_\varphi(\cos\varphi\partial_\varphi q)
+\frac1{R^2\cos^2\varphi}\partial_\lambda^2q
=\frac1{R^2}\left[\partial_\mu((1-\mu^2)\partial_\mu q)
+\frac{\partial_\lambda^2q}{1-\mu^2}\right].
\tag{3.6}
$$
:::

::: {.tb-proof}
**Proof of Result 3.10**

Substitute the gradient components from (3.4) into its divergence formula. Then use $\partial_\theta=-\sin\theta\,\partial_\mu$ and $\cos\varphi=\sin\theta$ to obtain the two coordinate forms. $\square$
:::

::: {.tb-remark #obj-3-11}
**Remark 3.11 - Intrinsic surface derivatives and physical radius**

In three-dimensional space, the full scalar Laplacian is $\Delta q=r^{-2}\partial_r(r^2\partial_rq)+r^{-2}\Delta_\Omega q$. Restricting to a surface and assuming radial independence are distinct operations; (3.5) is intrinsic to the surface. Its units are field units divided by $\mathrm m^2$.
:::

::: {.tb-exercise #ex-3-2}
**Exercise 3.2 - Check an eigenfunction before using harmonics**

*Application.* Apply (3.6) to $q=\mu$ and to $q=1$.
:::

## Regularity, streamfunction, and the closed surface

Poles are coordinate singularities, not physical edges. A smooth nondivergent tangent velocity on the sphere has a streamfunction whose mean is arbitrary. Sources: [@ArfkenWeber2005, Sections 1.16, 2.5, 12.11]; fluid application: [@Vallis2006, Sections 2.2, 4.5].

::: {.tb-remark #obj-3-12}
**Remark 3.12 - Pole regularity is geometric**

All longitudes at a pole describe one point. A smooth scalar has a unique value there; nonzero longitude Fourier orders must vanish at the poles with the behavior derived in Chapter 8. The local tangent basis itself depends on longitude, so smooth vector components need not be longitude-independent at a pole. Smoothness is a geometric condition, not a command to set all derivatives to zero.
:::

::: {.tb-definition #obj-3-13}
**Definition 3.13 - Streamfunction velocity**

For a smooth real streamfunction $\psi$ with units $\mathrm m^2\,\mathrm s^{-1}$, set $\mathbf u=\mathbf e_r\times\nabla_s\psi$. Let $u$ be eastward speed and $v$ northward speed, so $F_\lambda=u$ and $F_\theta=-v$.
:::

::: {.tb-result #obj-3-14}
**Result 3.14 - A streamfunction gives nondivergent flow**

For a smooth real streamfunction with velocity $\mathbf u=\mathbf e_r\times\nabla_s\psi$, the eastward and northward components and radial vorticity satisfy

$$
u=-\frac1R\partial_\varphi\psi,
\qquad v=\frac1{R\cos\varphi}\partial_\lambda\psi,
\qquad \nabla_s\cdot\mathbf u=0,
\qquad \zeta:=(\nabla\times\mathbf u)\cdot\mathbf e_r=\Delta_s\psi.
\tag{3.7}
$$
:::

::: {.tb-proof}
**Proof of Result 3.14**

To check divergence, substitute the first two expressions into $[\partial_\lambda u+\partial_\varphi(v\cos\varphi)]/(R\cos\varphi)$; the mixed partials cancel. Substituting into the radial curl yields (3.6). $\square$
:::

::: {.tb-remark #obj-3-15}
**Remark 3.15 - The undetermined mean and global representation**

Adding a spatial constant to $\psi$ changes neither speed nor vorticity. The converse for every smooth divergence-free tangent field on the whole sphere is justified by the potential decomposition in Section 8.4. Until then, (3.7) defines the velocity class considered. Domains with holes can require additional circulation modes.
:::

::: {.tb-result #obj-3-16}
**Result 3.16 - Integration by parts on a closed sphere**

For smooth real scalars $f,g$ on $S_R^2$,

$$
\int_{S_R^2}f\Delta_sg\,dA=-\int_{S_R^2}\nabla_sf\cdot\nabla_sg\,dA,
\qquad \int_{S_R^2}\Delta_sg\,dA=0.
\tag{3.8}
$$
:::

::: {.tb-proof}
**Proof of Result 3.16**

Integrate the surface divergence of $f\nabla_sg$ over the closed sphere. There is no external boundary, so its integral is zero. Expand the product divergence and rearrange. Set $f=1$ for the second identity. $\square$
:::

::: {.tb-remark #obj-3-17}
**Remark 3.17 - Poisson compatibility and coordinate cuts**

Here $f,g$ are smooth real scalars. The second identity uses $f=1$. Thus $\Delta_sg=h$ requires zero area integral of $h$. The coordinate cuts at longitude $0$ and the poles are not physical boundaries; periodicity and regularity cancel their apparent terms.
:::

::: {.tb-exercise #ex-3-3}
**Exercise 3.3 - Diagnose an incompatible vorticity field**

*Reasoning.* Can a globally smooth streamfunction satisfy $\Delta_s\psi=c$ for a nonzero spatial constant $c$?
:::

## Chapter summary

Colatitude $\theta$, latitude $\varphi$, and longitude $\lambda$ follow (3.1); $\mu=\sin\varphi$. Scale factors define distance, area, and differential operators. Area is uniform in $(\mu,\lambda)$, not $(\varphi,\lambda)$. The physical Laplace-Beltrami operator is $\Delta_s=R^{-2}\Delta_\Omega$. With the convention $\mathbf u=\mathbf e_r\times\nabla_s\psi$, vorticity is $\zeta=\Delta_s\psi$. The Laplacian has zero integral and a constant nullspace.

::: {.tb-exercise #ex-3-4}
**Exercise 3.4 - Connect the chapter results**

*Synthesis.* Verify $\Delta_s\mu=-2\mu/R^2$. If $\psi=A\sin\varphi$, find $u$, $v$, and $\zeta$, including their units.
:::

# Function spaces, limits, and weak derivatives {#ch-spaces}

In what sense does a sequence of approximate fields approach the desired field? We need a measure and a norm before we can compare errors or call a basis complete. The chapter develops the geometry behind least-squares approximation, then introduces the weak derivatives needed when classical smoothness is unavailable.

## Norms, inner products, and convergence

A function expansion is meaningful only after specifying the measure and the kind of convergence. Mean-square accuracy does not imply accuracy at every point or of every derivative. Sources: [@ArfkenWeber2005, Sections 5.5, 10.2-10.4, 14.1, 14.4].

::: {.tb-definition #obj-4-1}
**Definition 4.1 - Norms, measures, and integral function spaces**

Let $D$ be an interval, a spatial region, or a sphere, with positive integration measure $d\nu$ (for example $dx$, $dV$, or $d\Omega$). A norm $\|\cdot\|$ is nonnegative, zero only on the zero element, homogeneous ($\|af\|=|a|\|f\|$), and obeys the triangle inequality. For $1\le p<\infty$, define

$$
L^p(D,d\nu)=\left\{f:\int_D|f|^p\,d\nu<\infty\right\},
\qquad \|f\|_p=\left(\int_D|f|^p\,d\nu\right)^{1/p}.
\tag{4.1}
$$

Functions here are measurable, meaning their level sets can be assigned the chosen measure. Functions that differ only on a set of measure zero are identified. "Almost everywhere" means except on such a set. For $L^\infty$, the norm is the essential supremum: the smallest bound valid almost everywhere. These identifications make the integral norms genuine norms. We use the standard completeness of $L^p$ without a measure-theoretic proof.
:::

::: {.tb-definition #obj-4-2}
**Definition 4.2 - Complex function inner product**

For complex functions in $L^2(D,d\nu)$, set $\langle f,g\rangle=\int_Df\overline g\,d\nu$, linear in the first argument. Its norm is $\|f\|_2^2=\langle f,f\rangle$.
:::

::: {.tb-result #obj-4-3}
**Result 4.3 - Cauchy-Schwarz inequality**

For $f,g\in L^2(D,d\nu)$, the inner product and norm satisfy

$$
\langle f,g\rangle=\int_D f\overline g\,d\nu,
\qquad \|f\|_2^2=\langle f,f\rangle,
\qquad |\langle f,g\rangle|\le\|f\|_2\|g\|_2.
\tag{4.2}
$$
:::

::: {.tb-proof}
**Proof of Result 4.3**

When $g\ne0$, set $a=\langle f,g\rangle/\|g\|_2^2$ and expand $0\le\|f-ag\|_2^2=\|f\|_2^2-|\langle f,g\rangle|^2/\|g\|_2^2$. If $g=0$, the inequality is immediate. $\square$
:::

::: {.tb-definition #obj-4-4}
**Definition 4.4 - Weighted measure and three notions of convergence**

A positive weight $w(x)$ defines $d\nu=w(x)dx$ and therefore changes orthogonality, projections, and losses. A sequence $f_n$ converges in $L^2$ to $f$ if $\|f_n-f\|_2\to0$. It converges pointwise if $f_n(x)\to f(x)$ at each $x$, and uniformly if $\sup_x|f_n(x)-f(x)|\to0$.
:::

::: {.tb-result #obj-4-5}
**Result 4.5 - Uniform convergence controls mean square on finite measure**

Let $f_n,f\in L^2(D,d\nu)$, choose their representatives, and suppose $\nu(D)<\infty$. If these representatives converge uniformly, then $f_n\to f$ in $L^2$.
:::

::: {.tb-proof}
**Proof of Result 4.5**

The pointwise bound $|f_n-f|^2\le\sup_D|f_n-f|^2$ integrates to $\|f_n-f\|_2^2\le\nu(D)\sup_D|f_n-f|^2$, whose right side tends to zero. $\square$
:::

::: {.tb-counterexample #obj-4-6}
**Counterexample 4.6 - Small integral error with fixed peak error**

A triangular pulse of height one and width $1/n$ has vanishing $L^2$ norm but maximum one. Thus norm convergence does not imply uniform convergence.
:::

::: {.tb-definition #obj-4-7}
**Definition 4.7 - Cauchy sequences, completeness, and Hilbert spaces**

A sequence is Cauchy if $\|f_n-f_m\|\to0$ as both indices grow. A space is complete when every Cauchy sequence has a limit in it. A Hilbert space is a complete inner product space.
:::

::: {.tb-result #obj-4-8}
**Result 4.8 - Completeness of the energy space (quoted)**

$L^2(D,d\nu)$ is a Hilbert space. Continuous functions equipped only with the $L^2$ norm need not form a complete space: continuous transitions can converge in that norm to a step. We use completeness as a standard function-space theorem [@ArfkenWeber2005, Sections 10.2-10.4; @HunterPDE, Section 1.4].
:::

::: {.tb-exercise #ex-4-1}
**Exercise 4.1 - Compare two measures**

*Application.* Compute the squared norm of $1$ on $[-1,1]$ under $d\mu$ and under $d\mu/2$. What changes when the measure is normalized?
:::

## Orthogonal expansions and approximation

An orthonormal basis converts squared function error into a sum of squared coefficient errors. Truncation is the best approximation in the chosen norm, rather than a claim of pointwise exactness. Sources: [@ArfkenWeber2005, Sections 10.3-10.4].

::: {.tb-definition #obj-4-9}
**Definition 4.9 - Complete orthonormal systems and finite projection**

Functions $e_j$ are orthonormal if $\langle e_j,e_k\rangle=\delta_{jk}$. A complete orthonormal system has no nonzero function orthogonal to all its members. For such a system in a Hilbert space, define coefficients $c_j=\langle f,e_j\rangle$ and projection $P_Nf=\sum_{j=1}^Nc_je_j$.
:::

::: {.tb-result #obj-4-10}
**Result 4.10 - Projection identity, Bessel inequality, and Parseval**

Let $e_j$ be orthonormal in a Hilbert space and $c_j=\langle f,e_j\rangle$. The first identity below holds for each finite $N$. If the system is complete, the second holds and $P_Nf\to f$ in norm.

$$
\|f-P_Nf\|_2^2=\|f\|_2^2-\sum_{j=1}^N|c_j|^2,
\qquad \|f\|_2^2=\sum_{j=1}^{\infty}|c_j|^2.
\tag{4.3}
$$
:::

::: {.tb-proof}
**Proof of Result 4.10**

Expand the squared norm and use $\langle e_j,e_k\rangle=\delta_{jk}$; the cross terms reduce to the retained coefficient sum. Nonnegativity gives Bessel's inequality. For a complete system the closed span is the whole space, so projections approach $f$ and the remainder tends to zero, yielding Parseval. The same orthogonal-remainder argument as (1.4) gives least-squares optimality. $\square$
:::

::: {.tb-definition #obj-4-11}
**Definition 4.11 - Gram-Schmidt construction**

For independent functions $f_j$, Gram-Schmidt constructs an orthonormal system by

$$
g_n=f_n-\sum_{j<n}\langle f_n,e_j\rangle e_j,
\qquad e_n=g_n/\|g_n\|_2.
\tag{4.4}
$$
:::

::: {.tb-example #obj-4-12}
**Example 4.12 - A latitude basis in normalized measure**

For example, with normalized measure $d\mu/2$ on $[-1,1]$, the functions $1$, $\sqrt3\mu$, and $\frac{\sqrt5}{2}(3\mu^2-1)$ are orthonormal. For example, $\tfrac12\int_{-1}^1 1\cdot\sqrt3\mu\,d\mu=0$ by oddness, and $\tfrac12\int_{-1}^1(\sqrt3\mu)^2d\mu=(3/2)(2/3)=1$. Their normalization differs from that under $d\mu$. This distinction explains factors of $2$ and $4\pi$ in latitude and spherical expansions.
:::

::: {.tb-exercise #ex-4-2}
**Exercise 4.2 - Check a quadratic basis function**

*Application.* Verify that $b_2(\mu)=\sqrt5(3\mu^2-1)/2$ is orthogonal to $1$ and has norm one under $d\mu/2$.
:::

## Distributions, weak derivatives, and energy spaces

Weak derivatives transfer differentiation to smooth test functions. They describe finite-energy fields and point sources without pretending that every solution is classically smooth. Sources: [@ArfkenWeber2005, Sections 1.15, 9.7, 10.5]; the $H^1$ definition follows [@HunterPDE, Sections 3.5 and 3.9].

::: {.tb-definition #obj-4-13}
**Definition 4.13 - Test functions, distributions, and point sources**

A test function $\eta\in C_c^\infty(D)$ is infinitely differentiable and zero outside a closed bounded subset lying inside $D$ (compact support). A distribution $T$ is a linear rule assigning a scalar $T[\eta]$ to each test function, continuous in the following sense: if all test functions have support in one fixed compact subset and every derivative converges uniformly to zero, their values under $T$ tend to zero. A locally integrable function (one integrable on every compact subset of $D$) defines $T_f[\eta]=\int_D f\eta$. The Dirac delta at $x_0$ is the distribution $\delta_{x_0}[\eta]=\eta(x_0)$; it is not an ordinary function of infinite height.
:::

::: {.tb-definition #obj-4-14}
**Definition 4.14 - Distributional and weak derivatives**

$$
T_f'[\eta]=-T_f[\eta'],\qquad
\int f\eta'=-\int g\eta\ \Longrightarrow\ g=\partial_x f
\text{ in the weak sense}.
\tag{4.5}
$$

The integral equality must hold for every test function $\eta$; it defines an ordinary weak derivative when the distribution is represented by the locally integrable function $g$.
:::

::: {.tb-example #obj-4-15}
**Example 4.15 - The derivative of a step**

There is no boundary term because the test function vanishes near the boundary. For the step $H(x)=0$ for $x<0$, $H(x)=1$ for $x>0$,
$T_H'[\eta]=-\int_0^\infty\eta'(x)dx=\eta(0)$, so $H'=\delta_0$ as distributions. Values at $x=0$ do not affect this identity.
:::

::: {.tb-definition #obj-4-16}
**Definition 4.16 - First-order energy spaces**

The Sobolev space $H^1(D)$ consists of $L^2$ functions whose first weak partial derivatives are also in $L^2$. With dimensionless coordinates, its norm is $\|f\|_{H^1}^2=\|f\|_2^2+\sum_j\|\partial_jf\|_2^2$. With dimensional coordinates one can insert a reference length squared on the derivative terms; otherwise the displayed sum mixes units. $H_0^1(D)$ consists of all limits in the $H^1$ norm of sequences of compactly supported smooth functions. On a sufficiently regular bounded domain it encodes zero boundary values. This functional-analytic notation is an explicit extension of AW's energy and integration-by-parts methods; no general Sobolev embedding theorem is needed here.
:::

::: {.tb-counterexample #obj-4-17}
**Counterexample 4.17 - Converging fields with nonconverging gradients**

On the dimensionless $2\pi$-periodic coordinate $x$, $f_n(x)=\sin(nx)/n$ tends uniformly to zero, but $f_n'(x)=\cos(nx)$ does not tend to zero in $L^2$. An $L^2$ approximation to a field does not by itself control gradients, wind inferred from a streamfunction, or vorticity inferred from wind.
:::

::: {.tb-exercise #ex-4-3}
**Exercise 4.3 - Distinguish a weak derivative from a distribution**

*Reasoning.* On $(-1,1)$, does the step $H$ belong to $L^2$? Does it belong to $H^1$? Explain using its derivative.
:::

## Chapter summary

The measure belongs to the definition of an $L^p$ norm. A Hilbert space is complete with an inner product. Pointwise, uniform, and norm convergence are distinct. Projection, Bessel's inequality, and Parseval follow from orthogonality plus the appropriate completeness assumption. A distribution acts on test functions; a weak derivative is defined by integration by parts. $H^1$ controls both the field and its first derivatives.

::: {.tb-exercise #ex-4-4}
**Exercise 4.4 - Connect the chapter results**

*Synthesis.* Show that $\sqrt3\mu$ has norm one under $d\mu/2$. Why does small $L^2$ error in a streamfunction fail to guarantee small wind error? Which object is the derivative of a step?
:::

::: {.tb-exercise #ex-4-5}
**Exercise 4.5 - Prove the converse Parseval test**

*Independent proof.* Let $e_j$ be orthonormal in a Hilbert space. Suppose $\sum_j|\langle f,e_j\rangle|^2=\|f\|^2$ for every $f$. Prove completeness using the definition in this chapter.
:::

# Differential equations and eigenfunction theory {#ch-odes}

How can a differential equation become a set of independent scalar equations? An integrating factor solves one forced mode, while boundary conditions select the spatial modes themselves. We develop this connection through self-adjoint eigenproblems, then use it for diffusion and Green's-function inversion.

## Initial-value equations and integrating factors

Linear evolution balances forcing against a response kernel. The same integrating-factor formula solves a single spectral mode of a PDE. Sources: [@ArfkenWeber2005, Sections 9.2, 9.7].

::: {.tb-definition #obj-5-1}
**Definition 5.1 - ODE, initial condition, order, and linearity**

An ordinary differential equation (ODE) relates an unknown function of one independent variable to its derivatives. Its order is the highest derivative present. An initial condition specifies its state at an initial time. A linear equation has the unknown and its derivatives only to the first power, with coefficients independent of that unknown. "Homogeneous" means zero forcing.
:::

::: {.tb-result #obj-5-2}
**Result 5.2 - Integrating-factor solution**

Let $\gamma,b$ be continuous functions of time, let $a(0)=a_0$, and define $I(t)=\exp(\int_0^t\gamma(s)ds)$. Then the unique solution of $a\prime+\gamma a=b$ is

$$
a'+\gamma a=b
\quad\Longrightarrow\quad
(Ia)'=Ib
\quad\Longrightarrow\quad
a(t)=I(t)^{-1}\left[a_0+\int_0^t I(s)b(s)ds\right].
\tag{5.1}
$$
:::

::: {.tb-proof}
**Proof of Result 5.2**

The strategic choice $I\prime=\gamma I$ turns the left side into a product derivative: $(Ia)\prime=I(a\prime+\gamma a)=Ib$. Integrate from zero to $t$ and use $I(0)=1$. The same calculation for the difference of two solutions gives zero, proving uniqueness. $\square$
:::

::: {.tb-example #obj-5-3}
**Example 5.3 - Constant decay and sustained forcing**

For constant $\gamma$, this is $a(t)=a_0e^{-\gamma t}+\int_0^t e^{-\gamma(t-s)}b(s)ds$. Positive real $\gamma$ damps an initial perturbation; purely imaginary $\gamma$ changes phase; negative real $\gamma$ amplifies it. These statements concern the homogeneous response. For constant forcing $b(t)=b_0$ and real $\gamma>0$, evaluate the integral to obtain $a(t)=a_0e^{-\gamma t}+(b_0/\gamma)(1-e^{-\gamma t})$. Thus $a(t)\to b_0/\gamma$: forcing sustains a nonzero equilibrium when $b_0\ne0$.
:::

::: {.tb-result #obj-5-4}
**Result 5.4 - Matrix exponential evolution**

For a constant finite matrix $A$, the initial-value problem $\mathbf a\prime=A\mathbf a$ has solution $\mathbf a(t)=e^{tA}\mathbf a(0)$, with $e^{tA}=\sum_{n\ge0}t^nA^n/n!$.
:::

::: {.tb-proof}
**Proof of Result 5.4**

The matrix power series converges on finite time intervals and can be differentiated termwise there. Its derivative is $Ae^{tA}$, and $e^{0A}=I$, verifying both the equation and initial value. $\square$
:::

::: {.tb-remark #obj-5-5}
**Remark 5.5 - Modes and transient growth**

If $A$ has an eigenbasis, each eigencomponent evolves as $e^{\lambda_jt}$. Eigenvalues alone need not describe transient growth for a nonnormal matrix ($AA^*\ne A^*A$); we use orthogonal diagonalization only when its hypotheses hold.
:::

::: {.tb-exercise #ex-5-1}
**Exercise 5.1 - Solve a forced scalar mode**

*Application.* For constant $\gamma>0$ and constant $b_0$, solve $a\prime+\gamma a=b_0$, $a(0)=0$. Give the long-time limit.
:::

## Boundary conditions and Sturm-Liouville operators

An operator includes its domain and boundary conditions. Self-adjoint boundary conditions produce real eigenvalues and orthogonal eigenfunctions. Sources: [@ArfkenWeber2005, Sections 9.3, 10.1-10.2].

::: {.tb-definition #obj-5-6}
**Definition 5.6 - Regular weighted Sturm-Liouville expression**

On a finite interval $[a,b]$, let real $p,p',q,w$ be continuous with $p>0$ and $w>0$. Define

$$
\mathcal Ly=\frac1w\left[-(py')'+qy\right],
\qquad \mathcal Ly=\lambda y,
\qquad \langle f,g\rangle_w=\int_a^bf\overline g\,w\,dx.
\tag{5.2}
$$
:::

::: {.tb-definition #obj-5-7}
**Definition 5.7 - Operator domains and boundary conditions**

The functions admitted by an operator, including their boundary conditions, form its domain. Dirichlet conditions specify $y$ at an endpoint; Neumann conditions specify its normal derivative; Robin conditions specify a linear combination. For homogeneous separated conditions use $\alpha_ay(a)+\beta_ap(a)y'(a)=0$ and $\alpha_by(b)+\beta_bp(b)y'(b)=0$, with real coefficient pairs not both zero.
:::

::: {.tb-result #obj-5-8}
**Result 5.8 - Boundary form and symmetry**

Let $p,p\prime,q,w$ satisfy the regular hypotheses above. For sufficiently smooth functions $f,g$ obeying the same homogeneous separated real boundary conditions,

$$
\langle\mathcal Lf,g\rangle_w-\langle f,\mathcal Lg\rangle_w
=\left[p(f\overline{g'}-f'\overline g)\right]_a^b=0.
\tag{5.3}
$$
:::

::: {.tb-proof}
**Proof of Result 5.8**

Integrate the term $-(pf\prime)\prime\overline g$ once and subtract the expression with the derivative transferred to $g$. The $q$ terms cancel. At either endpoint the real boundary relation makes $f\overline{g\prime}-f\prime\overline g=0$. For matching periodic $y,py\prime$, the two endpoint values cancel instead. $\square$
:::

::: {.tb-remark #obj-5-9}
**Remark 5.9 - Symmetric expression and self-adjoint realization**

Here $[h]_a^b=h(b)-h(a)$. The separated boundary conditions make each endpoint bracket zero. Matching periodic $y$ and $py'$ also cancels it. This proves symmetry; the regular Sturm-Liouville realization with these conditions is self-adjoint (its operator domain equals that of its adjoint). For a general unbounded differential operator, formal symmetry alone would not establish this stronger statement.
:::

::: {.tb-result #obj-5-10}
**Result 5.10 - Weighted eigenfunction orthogonality**

For the regular self-adjoint realization of (5.2), eigenvalues are real. Eigenfunctions $y_j,y_k$ satisfy

$$
(\lambda_j-\lambda_k)\int_a^b y_j\overline{y_k}w\,dx=0.
\tag{5.4}
$$

Thus distinct eigenvalues are orthogonal in the weighted inner product.
:::

::: {.tb-proof}
**Proof of Result 5.10**

Apply (5.3) to the eigenfunctions and substitute $\mathcal Ly_j=\lambda_jy_j$. With the same eigenfunction in both slots the eigenvalue equals its conjugate. With two real eigenvalues, subtracting gives (5.4). $\square$
:::

::: {.tb-result #obj-5-11}
**Result 5.11 - Regular Sturm-Liouville spectral theorem (quoted)**

The regular Sturm-Liouville theorem further gives a complete orthonormal eigenbasis in $L_w^2$, a discrete spectrum bounded below, and eigenvalues tending to $+\infty$. These existence and completeness assertions are quoted from AW, Chapter 10; orthogonality has just been derived.
:::

::: {.tb-remark #obj-5-12}
**Remark 5.12 - Singular endpoints require another condition**

Singular endpoints, such as $p=1-x^2=0$ at $x=\pm1$, require separate endpoint regularity conditions and cannot be covered by pretending $p>0$ on the closed interval.
:::

::: {.tb-exercise #ex-5-2}
**Exercise 5.2 - Identify the zero mode**

*Reasoning.* For $-y\prime\prime=\lambda y$ on $(0,d)$, compare whether a nonzero constant eigenfunction satisfies homogeneous Dirichlet versus homogeneous Neumann conditions.
:::

## Separation of variables and spectral solution

Separation turns a linear PDE with compatible geometry into a spatial eigenproblem and scalar time equations. The spatial boundary conditions select the allowed modes. Sources: [@ArfkenWeber2005, Sections 9.3, 9.8, 10.4].

::: {.tb-model #obj-5-13}
**Model 5.13 - Diffusion on a finite interval**

Consider diffusion on $0<x<d$, where $d>0$ is the interval length, $\kappa>0$, $u(0,t)=u(d,t)=0$, and $u(x,0)=u_0(x)$ with $u_0\in L^2(0,d)$. The governing equation is $u_t=\kappa u_{xx}$.
:::

::: {.tb-result #obj-5-14}
**Result 5.14 - Separated diffusion modes**

In this constant-diffusivity zero-Dirichlet model, a nonzero separated solution $u=XT$ obeys

$$
-X''=\lambda X,\quad X(0)=X(d)=0,
\qquad T'=-\kappa\lambda T.
\tag{5.5}
$$
:::

::: {.tb-proof}
**Proof of Result 5.14**

Seek a product $u=X(x)T(t)$. Dividing $XT'=\kappa X''T$ by $\kappa XT$ where nonzero yields $T'/(\kappa T)=X''/X=-\lambda$, because one side depends only on time and the other only on space. This gives the separated equations (5.5). $\square$
:::

::: {.tb-result #obj-5-15}
**Result 5.15 - Dirichlet eigenmodes and evolution**

For $u_0\in L^2(0,d)$, let $\lambda_n=(n\pi/d)^2$ and $X_n=\sqrt{2/d}\sin(n\pi x/d)$, $n\ge1$. The diffusion solution is

$$
u(x,t)=\sum_{n=1}^{\infty}a_n e^{-\kappa\lambda_nt}X_n(x),
\qquad a_n=\int_0^d u_0(x)X_n(x)dx.
\tag{5.6}
$$

Convergence is in $L^2$ at zero time and the solution is smooth in the interior for positive time.
:::

::: {.tb-proof}
**Proof of Result 5.15**

A nonzero eigenfunction requires $\lambda_n=(n\pi/d)^2$ and $X_n=\sqrt{2/d}\sin(n\pi x/d)$, $n=1,2,\ldots$. For $\lambda=0$ the linear solution vanishes at both endpoints only if zero; for $\lambda<0$ the exponential solutions likewise give no nonzero Dirichlet mode. Expand $u_0$ in the orthonormal sine basis. Each coefficient satisfies $a_n\prime=-\kappa\lambda_na_n$, whose integrating-factor solution is $a_n(t)=a_n(0)e^{-\kappa\lambda_nt}$. Completeness supplies the initial limit. $\square$
:::

::: {.tb-remark #obj-5-16}
**Remark 5.16 - Decay and the Neumann mean**

High modes decay faster. Neumann endpoints instead admit a constant mode with eigenvalue zero, so the spatial mean persists.
:::

::: {.tb-exercise #ex-5-3}
**Exercise 5.3 - Use two modes**

*Application.* For $u_0(x)=\sin(\pi x/d)+2\sin(2\pi x/d)$, write $u(x,t)$ and identify the slower decay rate.
:::

## Green's functions and solvability

A Green's function is the response to a point source with specified boundary conditions. A zero eigenvalue replaces ordinary inversion with a compatibility condition. Sources: [@ArfkenWeber2005, Sections 1.15, 9.7, 10.5].

::: {.tb-definition #obj-5-17}
**Definition 5.17 - Green's function for a chosen measure**

For a specified operator domain and boundary conditions, $G(x,y)$ is a response to a point source: $\mathcal L_xG=\delta_\nu(x,y)$, where $\int\delta_\nu(x,y)f(y)d\nu(y)=f(x)$.
:::

::: {.tb-result #obj-5-18}
**Result 5.18 - Inverse as an eigenfunction kernel**

Suppose $\mathcal L$ has a complete orthonormal eigenbasis $e_n$ in $L^2(d\nu)$, real nonzero eigenvalues, and an inverse on the data under discussion. Then, in the appropriate norm or distributional interpretation,

$$
G(x,y)=\sum_n\frac{e_n(x)\overline{e_n(y)}}{\lambda_n},
\qquad u(x)=\int G(x,y)f(y)d\nu(y).
\tag{5.7}
$$
:::

::: {.tb-proof}
**Proof of Result 5.18**

Expand $f$ and $u$ in $e_n$. The equation requires $u_n=f_n/\lambda_n$. Substitute these coefficients into the expansion for $u$ and use $f_n=\int f(y)\overline{e_n(y)}d\nu(y)$ to obtain the kernel formula. The hypotheses control the sense of the resulting series. $\square$
:::

::: {.tb-result #obj-5-19}
**Result 5.19 - A null mode imposes compatibility**

Let $\mathcal L$ be self-adjoint in $L^2(d\nu)$ with a complete orthonormal eigenbasis and only one normalized null mode $e_0$. Assume it is invertible on the orthogonal complement of $e_0$. Then $\mathcal Lu=f$ is solvable exactly for $\langle f,e_0\rangle=0$ on that inverse domain. Removing the null mode from (5.7) gives $\mathcal L_xG=\delta_\nu-e_0(x)\overline{e_0(y)}$; choosing solution coefficient $u_0=0$ fixes the remaining null-mode freedom.
:::

::: {.tb-proof}
**Proof of Result 5.19**

Self-adjointness gives $\langle\mathcal Lu,e_0\rangle=\langle u,\mathcal Le_0\rangle=0$, proving necessity. For orthogonal data, invert each nonzero eigenvalue using the assumed inverse on that complement. The completeness kernel with its $e_0$ term removed is exactly $\delta_\nu-e_0(x)\overline{e_0(y)}$. Two solutions differ only in the null mode, which the chosen coefficient removes. $\square$
:::

::: {.tb-example #obj-5-20}
**Example 5.20 - A one-dimensional Dirichlet Green function**

For a direct check, on $0<x<d$ the Dirichlet Green's function of $-d^2/dx^2$ is $G(x,y)=x_<(d-x_>)/d$, where $x_<=\min(x,y)$ and $x_>=\max(x,y)$. It vanishes at the endpoints, is continuous at $x=y$, and its derivative in $x$ jumps by $-1$. Therefore $-\partial_x^2G=\delta(x-y)$, with the required sign.
:::

::: {.tb-exercise #ex-5-4}
**Exercise 5.4 - Check the sign of the Green function**

*Application.* Use $G(x,y)=x_<(d-x_>)/d$ to solve $-u\prime\prime=1$ with $u(0)=u(d)=0$.
:::

## Chapter summary

The integrating factor gives the forced modal solution (5.1). Initial conditions specify a state; boundary conditions restrict spatial behavior. A regular self-adjoint Sturm-Liouville operator has real eigenvalues and a complete weighted orthonormal eigenbasis. Separation yields spatial eigenvalues and time factors as in (5.5)-(5.6). A Green's function is a kernel for inversion; nullspace components require compatibility and a normalization.

::: {.tb-exercise #ex-5-5}
**Exercise 5.5 - Connect the chapter results**

*Synthesis.* For $u_0=\sin(2\pi x/d)$ in (5.6), what is the decay time? Why can $-u''=1$ on a periodic interval have no periodic solution?
:::

# Partial differential equations and physical models {#ch-pdes}

Which data make a PDE problem meaningful, and what can be proved without an explicit solution? We distinguish balance, transport, diffusion, and waves, then use energy estimates to control solutions. Nondimensionalization finally identifies which terms can compete at a stated physical scale.

## Order, classification, and well-posedness

A PDE is defined by its differential equation together with its domain and data. Elliptic, parabolic, and hyperbolic equations ask different kinds of physical questions. Sources: [@ArfkenWeber2005, Sections 9.1, 9.3, 9.8].

::: {.tb-definition #obj-6-1}
**Definition 6.1 - PDE order, linearity, and superposition**

A partial differential equation (PDE) relates a field of several independent variables to its partial derivatives. Its order is the highest derivative order. A PDE is linear if it has the form $Lu=f$ with $L$ linear and $f$ prescribed. A nonlinear term such as $u\partial_xu$ makes superposition invalid: the sum of solutions need not be a solution.
:::

::: {.tb-definition #obj-6-2}
**Definition 6.2 - Second-order type and principal symbol**

For a real second-order scalar equation in two variables whose highest-order part is $A u_{xx}+2B u_{xy}+C u_{yy}$, the sign of $B^2-AC$ classifies that part as elliptic if negative, parabolic if zero, or hyperbolic if positive. Coefficients can depend on position; the classification can change with position. More general systems use their principal symbol, the polynomial formed from the highest-order derivatives by replacing derivatives with frequency components. The two-variable discriminant is not a universal classification rule for all evolution equations.
:::

::: {.tb-model #obj-6-3}
**Model 6.3 - Three prototype equations**

The prototypes are

$$
-\Delta u=f\quad\text{(Poisson)},\qquad
\partial_tu=\kappa\Delta u\quad\text{(diffusion)},\qquad
\partial_t^2u=c^2\Delta u\quad\text{(wave)}.
\tag{6.1}
$$

Here $\kappa>0$ is diffusivity and $c>0$ wave speed. Poisson's equation determines a spatial balance from boundary data. Diffusion takes one initial field. The wave equation takes both initial displacement and initial velocity. Advection $\partial_tu+\mathbf v\cdot\nabla u=0$ is first-order transport along trajectories; inflow boundaries specify arriving values, not arbitrary data on all boundaries.
:::

::: {.tb-definition #obj-6-4}
**Definition 6.4 - Well-posedness and its norm**

A problem is well posed in a chosen norm if a solution exists, is unique, and depends continuously on its data. This is a property of the full initial/boundary-value problem. A formula alone does not guarantee it.
:::

::: {.tb-counterexample #obj-6-5}
**Counterexample 6.5 - Backward diffusion amplifies unresolved scales**

For backward diffusion, a Fourier mode grows as $e^{\kappa k^2t}$; arbitrarily small high-frequency errors can grow without bound, so this inverse-time problem is not continuously stable in $L^2$.
:::

::: {.tb-exercise #ex-6-1}
**Exercise 6.1 - Count the required time data**

*Reasoning.* Compare the initial data required by $u_t=\kappa\Delta u$ and $u_{tt}=c^2\Delta u$. Why is the same initial field alone insufficient for the latter?
:::

## Energy estimates, uniqueness, and weak formulation

Multiplication by the solution and integration by parts can prove decay and uniqueness without knowing a closed-form solution. Sources: [@ArfkenWeber2005, Sections 1.13-1.14, 9.8, 10.2, 17.4].

::: {.tb-assumption #obj-6-6}
**Assumption 6.6 - Regularity and nontransmitting boundaries**

On a bounded smooth domain $D$, take real diffusion with zero Dirichlet data, homogeneous Neumann data, or matching periodic data, so boundary terms vanish.
:::

::: {.tb-definition #obj-6-7}
**Definition 6.7 - Squared-amplitude energy**

Set $E(t)=\frac12\int_Du^2dV$ for the real diffusion field.
:::

::: {.tb-result #obj-6-8}
**Result 6.8 - Diffusion dissipates squared amplitude**

Let $\kappa>0$ and let $u$ solve $u_t=\kappa\Delta u$ with enough regularity for integration by parts and one of the homogeneous or periodic boundary conditions just stated. Then

$$
\frac{dE}{dt}=\int_Du\partial_tu\,dV
=\kappa\int_Du\Delta u\,dV
=-\kappa\int_D|\nabla u|^2dV\le0.
\tag{6.2}
$$
:::

::: {.tb-proof}
**Proof of Result 6.8**

Differentiate $E$ under the integral, insert the diffusion equation, and apply Green's first identity (2.9). The boundary term vanishes under the chosen conditions. Since $\kappa>0$, the remaining gradient-square integral is nonpositive. $\square$
:::

::: {.tb-result #obj-6-9}
**Result 6.9 - Diffusion uniqueness and contraction**

Let $u,v$ be sufficiently regular solutions with the same positive constant diffusivity, forcing, and homogeneous Dirichlet, homogeneous Neumann, or periodic boundary conditions of Result 6.8. Then $\|u(t)-v(t)\|_2\le\|u(0)-v(0)\|_2$. In particular, the same initial field gives a unique solution. This mathematical energy has units determined by the field.
:::

::: {.tb-proof}
**Proof of Result 6.9**

The difference $w=u-v$ obeys unforced diffusion with homogeneous boundary conditions. Applying (6.2) to $w$ and integrating in time gives $\|w(t)\|_2^2\le\|w(0)\|_2^2$. Take square roots. If the initial difference is zero, its norm stays zero. $\square$
:::

::: {.tb-definition #obj-6-10}
**Definition 6.10 - Weak Dirichlet formulation**

For real $f\in L^2(D)$, $-\Delta u=f$, and zero Dirichlet data, a weak solution $u\in H_0^1(D)$ satisfies

$$
\int_D\nabla u\cdot\nabla\eta\,dV=\int_Df\eta\,dV
\quad\text{for every real }\eta\in H_0^1(D).
\tag{6.3}
$$
:::

::: {.tb-result #obj-6-11}
**Result 6.11 - Variational equation and weak existence**

For real $f\in L^2(D)$ on a bounded smooth domain with zero Dirichlet data, the stationary points of $\mathcal J[u]=\frac12\int_D|\nabla u|^2dV-\int_Dfu\,dV$ satisfy (6.3). A unique solution exists in $H_0^1(D)$; existence is a quoted weak Dirichlet theorem [@HunterPDE, Section 4.5].
:::

::: {.tb-proof}
**Proof of Result 6.11**

For the variational assertion, substitute $u+\varepsilon\eta$ and differentiate at $\varepsilon=0$. The coefficient of $\varepsilon$ is $\int\nabla u\cdot\nabla\eta-\int f\eta$, giving (6.3). This derives the stationary equation, while the existence assertion uses the cited theorem. $\square$
:::

::: {.tb-result #obj-6-12}
**Result 6.12 - Neumann compatibility and an arbitrary constant**

If a $C^2$ function $u$ solves $-\Delta u=f$ on a bounded regular region $D$ with $\partial_nu=g$, the data necessarily satisfy $\int_Df\,dV=-\int_{\partial D}g\,dA$. Adding a spatial constant to a solution preserves its equation and boundary data. On a closed sphere the corresponding compatibility condition is zero integral of $f$.
:::

::: {.tb-proof}
**Proof of Result 6.12**

Integrate $-\Delta u=f$ over $D$ and apply the divergence theorem to $\nabla u$; substitute $\partial_nu=g$. A constant has zero gradient and zero Laplacian, proving the stated freedom. On the closed sphere there is no boundary flux. $\square$
:::

::: {.tb-exercise #ex-6-2}
**Exercise 6.2 - Estimate the difference of two solutions**

*Proof.* If two homogeneous-boundary diffusion solutions have initial fields differing by $w_0$, prove $\|u(t)-v(t)\|_2\le\|w_0\|_2$.
:::

## Characteristics, waves, and dispersion

Characteristics track transport; dispersion describes the frequency-dependent phase of waves. These notions explain why diffusion smooths while advection moves patterns. Sources: [@ArfkenWeber2005, Sections 9.1-9.3, 15.4, 15.7].

::: {.tb-example #obj-6-13}
**Example 6.13 - Transport along characteristics**

For $\partial_tu+c\partial_xu=0$ with constant real $c$, the curves $x(t)=x_0+ct$ have $du(x(t),t)/dt=0$, so $u(x,t)=u_0(x-ct)$. These curves are characteristics.
:::

::: {.tb-counterexample #obj-6-14}
**Counterexample 6.14 - Nonlinear transport need not stay smooth**

For nonlinear transport, $u_t+uu_x=0$ carries each initial value at its own speed; characteristics can cross, after which a classical differentiable solution fails and a conservation-law weak solution needs an additional admissibility rule. For a concrete smooth periodic initial field $u_0(\xi)=-\sin\xi$, a characteristic is $x(\xi,t)=\xi-t\sin\xi$. Its derivative $\partial x/\partial\xi=1-t\cos\xi$ first vanishes at $t=1$, so the smooth invertible characteristic map fails there. For $t>1$ nearby characteristics cross. No further shock theory is needed here.
:::

::: {.tb-definition #obj-6-15}
**Definition 6.15 - Plane waves and dispersion**

A plane wave has the form $u=Ae^{i(kx-\omega t)}$, where $A$ is amplitude, $k$ angular wavenumber, and $\omega$ angular frequency. A dispersion relation specifies the allowed $\omega$ as a function of wavenumber.
:::

::: {.tb-result #obj-6-16}
**Result 6.16 - Wave frequency, phase speed, and group speed**

For the one-dimensional wave equation with constant $c>0$, a nonzero plane wave has $\omega^2=c^2k^2$. For $k\ne0$, phase speed is $\omega/k$; a smooth branch has group speed $d\omega/dk$:

$$
\omega^2=c^2k^2,\qquad c_{\rm phase}=\omega/k,
\qquad c_{\rm group}=d\omega/dk.
\tag{6.4}
$$
:::

::: {.tb-proof}
**Proof of Result 6.16**

Two time derivatives multiply the plane wave by $-\omega^2$, and two spatial derivatives multiply it by $-k^2$. Substitute into $u_{tt}=c^2u_{xx}$ and cancel the nonzero wave. Constant phase $kx-\omega t$ gives $dx/dt=\omega/k$; linearizing $\omega(k)$ about a narrow packet's central wavenumber gives its envelope speed. $\square$
:::

::: {.tb-remark #obj-6-17}
**Remark 6.17 - Propagation versus amplitude change**

The phase speed moves constant-phase crests; the group speed moves the envelope of a narrow packet when the dispersion relation is smooth. For the one-dimensional wave equation the right- and left-traveling branches have constant speeds $\pm c$. Other equations have $\omega(k)$ nonlinear in $k$, so different scales travel at different phase speeds. A complex $\omega$ also encodes decay or growth through $e^{\operatorname{Im}\omega\,t}$.
:::

::: {.tb-result #obj-6-18}
**Result 6.18 - Wave energy with no boundary flux**

For a sufficiently smooth real solution of $u_{tt}=c^2\Delta u$ with constant $c>0$, define $E=\tfrac12\int_D(u_t^2+c^2|\nabla u|^2)dV$. If the boundary flux satisfies $\int_{\partial D}u_t\partial_nu\,dA=0$, then $E$ is constant. Homogeneous fixed Dirichlet, homogeneous Neumann, and matching periodic data supply this condition.
:::

::: {.tb-proof}
**Proof of Result 6.18**

Differentiation gives $E\prime=\int_Du_tu_{tt}+c^2\nabla u\cdot\nabla u_t\,dV$. Substitute the wave equation and integrate $\int u_t\Delta u$ by parts. The two interior gradient integrals cancel, leaving $E\prime=c^2\int_{\partial D}u_t\partial_nu\,dA=0$. $\square$
:::

::: {.tb-exercise #ex-6-3}
**Exercise 6.3 - Compare phase and group velocity**

*Application.* For a hypothetical dispersion relation $\omega=ak^2$ with $a>0$ and $k>0$, find both speeds. Are they equal?
:::

## Nondimensionalization and competing scales

Dimensionless ratios identify which terms can compete. Neglecting a term is a scale-dependent physical assumption. Sources: [@ArfkenWeber2005, Section 9.1, dimensional structure of the prototype equations]; fluid scaling: [@Vallis2006, Sections 1.11, 2.7-2.8].

::: {.tb-assumption #obj-6-19}
**Assumption 6.19 - Reference scales and dimensionless variables**

For advection-diffusion $q_t+\mathbf u\cdot\nabla q=\kappa\Delta q$, take length $L_*>0$, speed $U_*>0$, amplitude $Q_*>0$, and advective time $T_*=L_*/U_*$. Write $\mathbf x=L_*\widetilde{\mathbf x}$, $t=T_*\widetilde t$, $q=Q_*\widetilde q$, and $\mathbf u=U_*\widetilde{\mathbf u}$. All quantities with a tilde are dimensionless.
:::

::: {.tb-result #obj-6-20}
**Result 6.20 - Peclet number in advection-diffusion**

For constant $\kappa>0$ and the positive reference scales just chosen, advection-diffusion takes the dimensionless form

$$
\partial_{\widetilde t}\widetilde q+
\widetilde{\mathbf u}\cdot\widetilde\nabla\widetilde q
=\mathrm{Pe}^{-1}\widetilde\Delta\widetilde q,
\qquad \mathrm{Pe}=\frac{U_*L_*}{\kappa}.
\tag{6.5}
$$
:::

::: {.tb-proof}
**Proof of Result 6.20**

The time derivative contributes $Q_*/T_*=Q_*U_*/L_*$; advection contributes the same factor. Diffusion contributes $\kappa Q_*/L_*^2$. Dividing by $Q_*U_*/L_*$ leaves $\kappa/(U_*L_*)=\mathrm{Pe}^{-1}$. $\square$
:::

::: {.tb-definition #obj-6-21}
**Definition 6.21 - Peclet, Reynolds, and Rossby numbers**

The Peclet number $\mathrm{Pe}$ is the ratio of diffusion time $L_*^2/\kappa$ to advection time. In momentum dynamics, the Reynolds number is $\mathrm{Re}=U_*L_*/\nu$ with kinematic viscosity $\nu$, and the Rossby number is $\mathrm{Ro}=U_*/(|f_*|L_*)$ with a nonzero reference Coriolis parameter $f_*$.
:::

::: {.tb-remark #obj-6-22}
**Remark 6.22 - A scale-dependent approximation**

Large $\mathrm{Pe}$ does not make diffusion negligible at all scales: diffusion at length $\ell$ scales as $\kappa/\ell^2$. Small scales or thin boundary layers can retain it.
:::

::: {.tb-exercise #ex-6-4}
**Exercise 6.4 - Compare two length scales**

*Application.* A flow has $\mathrm{Pe}=100$ at length $L_*$. With the same speed and diffusivity, what is the Peclet number at $L_*/100$?
:::

## Chapter summary

A PDE problem includes its domain, boundary data, initial data, and norm. Elliptic balance, parabolic diffusion, hyperbolic waves, and transport have different data requirements. Well-posedness means existence, uniqueness, and continuous dependence. Energy identities prove stability and uniqueness. A weak formulation lowers the derivative requirement. Characteristics carry information; a dispersion relation links frequency to wavenumber. Dimensionless numbers compare terms at stated scales.

::: {.tb-exercise #ex-6-5}
**Exercise 6.5 - Connect the chapter results**

*Synthesis.* Use (6.2) to compare two diffusion solutions with different initial fields. Why is a homogeneous Neumann Poisson solution unique only after fixing its mean? Can a large Peclet number justify dropping diffusion at arbitrarily small length?
:::

::: {.tb-exercise #ex-6-6}
**Exercise 6.6 - Construct unstable backward data**

*Independent proof.* Use dimensionless periodic $x\in[0,2\pi]$, a dimensionless time $t$, and fixed $T>0$. For $u_t=-u_{xx}$, for positive integers $n$, consider $u_n(x,t)=e^{-n^2T}e^{n^2t}\sin(nx)$. Verify the PDE and show that its initial $L^2$ norm tends to zero while its norm at $T$ does not. What well-posedness property fails?
:::

# Fourier analysis {#ch-fourier}

Why does decomposing a field into oscillations simplify differential equations? Periodic exponentials turn differentiation into multiplication, while the whole-line limit replaces a discrete mode sum by a continuous wavenumber integral. We derive these conventions first and then distinguish an exact discrete transform from adequate physical sampling.

## Periodic modes and coefficient recovery

Fourier modes diagonalize translation-invariant differentiation on a periodic domain. Orthogonality determines the coefficients and normalization. Sources: [@ArfkenWeber2005, Sections 14.1-14.4].

::: {.tb-definition #obj-7-1}
**Definition 7.1 - Periodic coordinate and Fourier coefficients**

Let $x$ be a length coordinate with period $d>0$: values at $x$ and $x+d$ are identified. The integer mode index is $n\in\mathbb Z$ and angular wavenumber is $k_n=2\pi n/d$. Define $c_n$ by

$$
f(x)=\sum_{n\in\mathbb Z}c_ne^{ik_nx},
\qquad c_n=\frac1d\int_0^df(x)e^{-ik_nx}dx,
\qquad \frac1d\int_0^de^{i(k_n-k_m)x}dx=\delta_{nm}.
\tag{7.1}
$$
:::

::: {.tb-result #obj-7-2}
**Result 7.2 - Periodic orthogonality and coefficient selection**

The exponentials $e^{ik_nx}$, $k_n=2\pi n/d$, are orthonormal under $dx/d$. For an expansion whose convergence permits integration term by term, its coefficients are those in (7.1).
:::

::: {.tb-proof}
**Proof of Result 7.2**

For $n\ne m$, integrate the exponential and use $e^{2\pi i(n-m)}=1$ to obtain zero. For $n=m$, the integrand is one. Multiplying the expansion by $e^{-ik_mx}$ and integrating therefore selects $c_m$. With normalized measure $dx/d$, these exponentials are orthonormal and $c_n$ has the units of $f$. Under $dx$, the normalized basis would instead be $d^{-1/2}e^{ik_nx}$. $\square$
:::

::: {.tb-result #obj-7-3}
**Result 7.3 - Fourier completeness, Parseval, and derivatives**

The periodic exponentials form a complete orthonormal system in $L^2([0,d],dx/d)$. Parseval holds for every such field; if $f$ is continuously differentiable with matching periodic values, its derivative coefficients satisfy

$$
\frac1d\int_0^d|f|^2dx=\sum_n|c_n|^2,
\qquad \widehat{\partial_xf}_n=ik_nc_n.
\tag{7.2}
$$
:::

::: {.tb-proof}
**Proof of Result 7.3**

Completeness is the Fourier completeness theorem [@ArfkenWeber2005, Sections 14.1-14.4]. Apply the abstract Parseval identity from Chapter 4. For differentiation, integrate $d^{-1}\int_0^df\prime e^{-ik_nx}dx$ by parts; periodicity removes the endpoint term and leaves $ik_nc_n$. $\square$
:::

::: {.tb-remark #obj-7-4}
**Remark 7.4 - Reality and the mean**

For a real field $c_{-n}=\overline{c_n}$; the pair $n,-n$ is $2\operatorname{Re}(c_ne^{ik_nx})$. The zero mode $c_0$ is the spatial mean. Taking real and imaginary parts gives the equivalent sine-cosine series.
:::

::: {.tb-example #obj-7-5}
**Example 7.5 - A sine-cosine pair and its mean square**

For $f=A\cos(k_px)+B\sin(k_px)$, with positive integer $p$ and real amplitudes $A,B$, the only nonzero coefficients are $c_p=(A-iB)/2$ and $c_{-p}=(A+iB)/2$. Equation (7.2) gives mean square $(A^2+B^2)/2$, checking both the conjugation and the factor two.
:::

::: {.tb-exercise #ex-7-1}
**Exercise 7.1 - A phase-rotated coefficient**

*Application.* For $f(x)=\cos(x-\alpha)$ on a $2\pi$ interval, find $c_1,c_{-1}$ and the mean square.
:::

## Convergence, smoothness, and Gibbs oscillations

Smoothness controls coefficient decay, but a truncated expansion near a jump retains an overshoot. Spectral accuracy requires appropriate regularity and periodic matching. Sources: [@ArfkenWeber2005, Sections 5.5, 14.4-14.5].

::: {.tb-result #obj-7-6}
**Result 7.6 - Smooth periodic data have decaying coefficients**

Let $p\ge1$ be an integer and $f\in C^p([0,d])$, with matching periodic derivatives through order $p-1$. Then, for $n\ne0$,

$$
c_n=\frac{\widehat{f^{(p)}}_n}{(ik_n)^p},
\qquad |c_n|\le\frac{1}{d|k_n|^p}\int_0^d|f^{(p)}(x)|dx.
\tag{7.3}
$$
:::

::: {.tb-proof}
**Proof of Result 7.6**

Integrate the coefficient integral by parts $p$ times. Matching periodic traces through order $p-1$ remove every endpoint term. Divide by $(ik_n)^p$ and bound the remaining integral by its absolute integral to obtain (7.3). $\square$
:::

::: {.tb-counterexample #obj-7-7}
**Counterexample 7.7 - Smooth inside an interval is not smooth periodically**

The endpoint requirements remove boundary terms. Smoothness on the open interval alone is insufficient: the periodic extension of $f(x)=x$ on $(-\pi,\pi)$ has a jump at the identified endpoints and coefficients of order $1/|n|$.
:::

::: {.tb-result #obj-7-8}
**Result 7.8 - Pointwise convergence and Gibbs behavior (quoted)**

For a piecewise smooth periodic $f$, its Fourier sum at a jump tends to the midpoint of its one-sided limits. Partial sums overshoot near a jump; increasing the cutoff narrows this region without making its limiting relative height vanish (Gibbs phenomenon). [@ArfkenWeber2005, Sections 14.4-14.5].
:::

::: {.tb-example #obj-7-9}
**Example 7.9 - A discontinuous square wave**

For the square wave $f(x)=1$ on $(0,\pi)$ and $f(x)=-1$ on $(-\pi,0)$,

$$
b_n=\frac2\pi\int_0^\pi\sin(nx)dx
=\frac{2[1-(-1)^n]}{\pi n},
\qquad f(x)\sim\frac4\pi\sum_{j=0}^{\infty}\frac{\sin((2j+1)x)}{2j+1}.
\tag{7.4}
$$

Here $\sim$ denotes the Fourier representation with the convergence just specified, rather than equality at every assigned point value. Damping high modes can suppress ringing but changes the approximated function. Parseval still permits good mean-square approximation when a uniform approximation near a jump is impossible.
:::

::: {.tb-exercise #ex-7-2}
**Exercise 7.2 - Find the missing endpoint hypothesis**

*Counterexample.* A polynomial is smooth on $[0,d]$. Does that alone guarantee rapid decay of its periodic Fourier coefficients? Give a counterexample.
:::

## The Fourier transform and its normalization

On the whole line, wavenumber becomes continuous. The transform turns constant-coefficient differentiation into multiplication. Sources: [@ArfkenWeber2005, Sections 15.1-15.4].

::: {.tb-definition #obj-7-10}
**Definition 7.10 - Angular-wavenumber Fourier pair**

For $f\in L^1(\mathbb R)$ define the angular-wavenumber transform, with the following sign convention:

$$
\widehat f(k)=\int_{\mathbb R}f(x)e^{-ikx}dx,
\qquad f(x)=\frac1{2\pi}\int_{\mathbb R}\widehat f(k)e^{ikx}dk.
\tag{7.5}
$$
:::

::: {.tb-result #obj-7-11}
**Result 7.11 - Fourier inversion and its sense of convergence (quoted)**

The inverse formula holds, for example, for smooth rapidly decaying functions. More generally, integrability of both $f$ and $\widehat f$ gives the continuous representative almost everywhere; $L^2$ inversion is in norm and uses the Plancherel extension, not necessarily an absolutely convergent integral. A rapidly decaying smooth function and all its derivatives decay faster than every inverse power of $|x|$. [@ArfkenWeber2005, Section 15.3].
:::

::: {.tb-example #obj-7-12}
**Example 7.12 - The continuum limit fixes the inverse factor**

To see the factor $1/(2\pi)$, put the periodic problem on $[-d/2,d/2]$ and define $\Delta k=2\pi/d$. Then $c_n=d^{-1}\int f(x)e^{-ik_nx}dx\approx\widehat f(k_n)\Delta k/(2\pi)$. As $d\to\infty$, the Fourier sum becomes the integral in (7.5), under suitable decay assumptions. AW often uses a symmetric $1/\sqrt{2\pi}$ normalization and the opposite forward sign; coefficients must be converted before comparison.
:::

::: {.tb-result #obj-7-13}
**Result 7.13 - Differentiation, translation, and Plancherel**

For smooth rapidly decaying $f$, with $\mathcal F$ denoting (7.5) and $a$ a spatial shift,

$$
\begin{aligned}
\widehat{f'}(k)&=ik\widehat f(k),\qquad \widehat{f''}(k)=-k^2\widehat f(k),\\
\mathcal F[f(x-a)](k)&=e^{-ika}\widehat f(k),\\
\int_{\mathbb R}|f|^2dx&=\frac1{2\pi}\int_{\mathbb R}|\widehat f|^2dk.
\end{aligned}
\tag{7.6}
$$

The last identity extends to $L^2$ by the Plancherel theorem.
:::

::: {.tb-proof}
**Proof of Result 7.13**

Integration by parts removes the boundary term for $f\prime$ and produces $ik$; repeat once for $f\prime\prime$. For a shift set $y=x-a$ in the defining integral. The final identity is the Fourier Parseval theorem under the normalization in (7.5) [@ArfkenWeber2005, Sections 15.3-15.4]. $\square$
:::

::: {.tb-remark #obj-7-14}
**Remark 7.14 - Dimensions and cyclic frequency**

The symbol $\mathcal F$ denotes the transform in (7.5), and $a$ is a spatial shift. With $[x]=\mathrm m$ and $[f]=U$, $[k]=\mathrm m^{-1}$ and $[\widehat f]=U\,\mathrm m$. A transform with cyclic frequency $\xi=k/(2\pi)$ instead has $e^{-2\pi i\xi x}$ and no inverse $1/(2\pi)$ prefactor. The variable and the measure change together.
:::

::: {.tb-exercise #ex-7-3}
**Exercise 7.3 - Track transform units**

*Application.* If $[f]=\mathrm K$ and $[x]=\mathrm m$, what are the units of $\widehat f(k)$, $dk$, and the inverse integral?
:::

## Convolution and the heat kernel

Convolution sums responses to shifted sources. Fourier multiplication provides both its algebraic representation and a direct diffusion solution. Sources: [@ArfkenWeber2005, Sections 9.8, 15.4-15.5].

::: {.tb-definition #obj-7-15}
**Definition 7.15 - Whole-line convolution**

For integrable $f,g$, define convolution by $(f*g)(x)=\int_{\mathbb R}f(y)g(x-y)dy$.
:::

::: {.tb-result #obj-7-16}
**Result 7.16 - Convolution becomes multiplication**

If $f,g\in L^1(\mathbb R)$, their convolution has transform

$$
\widehat{f*g}(k)
=\int\!\int f(y)g(z)e^{-ik(y+z)}dy\,dz
=\widehat f(k)\widehat g(k).
\tag{7.7}
$$
:::

::: {.tb-proof}
**Proof of Result 7.16**

In the double integral set $z=x-y$. Absolute integrability of $f(y)g(z)$ permits interchange of the integrals; the exponential factors into $e^{-iky}e^{-ikz}$, leaving the product in (7.7). $\square$
:::

::: {.tb-remark #obj-7-17}
**Remark 7.17 - Products couple wavenumbers**

Absolute integrability justifies changing the integration order. A product instead becomes $\widehat{fg}(k)=(2\pi)^{-1}(\widehat f*\widehat g)(k)$, when the functions have enough integrability. Thus nonlinear multiplication couples frequencies rather than acting diagonally.
:::

::: {.tb-model #obj-7-18}
**Model 7.18 - Diffusion on the whole line**

Take $u_t=\kappa u_{xx}$, $\kappa>0$, on $\mathbb R$, with smooth rapidly decaying initial data $u_0$. We seek the field at $t>0$.
:::

::: {.tb-result #obj-7-19}
**Result 7.19 - Heat evolution is Gaussian smoothing**

In this model the Fourier amplitudes and physical solution are

$$
\widehat u(k,t)=e^{-\kappa k^2t}\widehat u_0(k),
\qquad u(x,t)=(G_t*u_0)(x),
\qquad G_t(x)=\frac{e^{-x^2/(4\kappa t)}}{\sqrt{4\pi\kappa t}},\quad t>0.
\tag{7.8}
$$
:::

::: {.tb-proof}
**Proof of Result 7.19**

For $u_t=\kappa u_{xx}$ on $\mathbb R$, transforming only in $x$ gives $\partial_t\widehat u=-\kappa k^2\widehat u$. Solve this scalar ODE and invert:

To verify the inverse Gaussian, let $I(x)=\int_{\mathbb R}e^{-ak^2}e^{ikx}dk$ for $a>0$. Integrating $\partial_k(e^{-ak^2})$ by parts gives $I'=-xI/(2a)$, hence $I(x)=I(0)e^{-x^2/(4a)}$. Squaring $I(0)$ and using polar coordinates gives $I(0)^2=\int_{\mathbb R^2}e^{-a(k^2+s^2)}dkds=\pi/a$. With $a=\kappa t$, dividing by $2\pi$ gives (7.8). The kernel integrates to one and has units of inverse length, preserving total mass for integrable initial data. Its width grows as $\sqrt{\kappa t}$. $\square$
:::

::: {.tb-exercise #ex-7-4}
**Exercise 7.4 - Read a diffusive length**

*Application.* In (7.8), at what $|x|$ has the Gaussian exponent reached $-1$? How does that distance change when time is multiplied by four?
:::

## The discrete transform and aliasing

A DFT exactly represents a finite vector. Its coefficients equal continuous Fourier coefficients only with adequate sampling assumptions. Sources: [@ArfkenWeber2005, Section 14.6].

::: {.tb-definition #obj-7-20}
**Definition 7.20 - Normalized DFT and synthesis**

For $N$ samples $f_j=f(jd/N)$, $j=0,\ldots,N-1$, use normalized discrete coefficients

$$
\widetilde c_n=\frac1N\sum_{j=0}^{N-1}f_je^{-2\pi inj/N},
\qquad f_j=\sum_{n=0}^{N-1}\widetilde c_ne^{2\pi inj/N}.
\tag{7.9}
$$
:::

::: {.tb-result #obj-7-21}
**Result 7.21 - Discrete orthogonality and finite inversion**

For any complex vector of length $N$, the DFT pair (7.9) is an exact inverse pair. Its frequencies are equivalent modulo $N$.
:::

::: {.tb-proof}
**Proof of Result 7.21**

The discrete orthogonality sum $N^{-1}\sum_j e^{2\pi i(n-m)j/N}$ is one when $n-m$ is a multiple of $N$ and zero otherwise, by the geometric-series formula. Therefore mode indices are defined modulo $N$; indices above half the sample count represent negative wavenumbers. For even $N$, the Nyquist index $N/2$ coincides with its negative, so it is a special endpoint and cannot represent two independent traveling phases. $\square$
:::

::: {.tb-result #obj-7-22}
**Result 7.22 - Aliasing and discrete Parseval**

Let $f$ be a continuous periodic function with absolutely summable Fourier coefficients, $\sum_n|c_n|<\infty$. Sampling this continuous representative on $N$ equally spaced nodes gives the first identity below. The second holds for every finite sample vector.

$$
\widetilde c_n=\sum_{r\in\mathbb Z}c_{n+rN},
\qquad \frac1N\sum_j|f_j|^2=\sum_{n=0}^{N-1}|\widetilde c_n|^2.
\tag{7.10}
$$
:::

::: {.tb-proof}
**Proof of Result 7.22**

Insert the absolutely convergent Fourier series into the DFT sum and interchange the finite sample sum with the series. Discrete orthogonality retains exactly indices $n+rN$. For Parseval insert the finite synthesis into $N^{-1}\sum_jf_j\overline f_j$; all unequal discrete modes cancel. $\square$
:::

::: {.tb-example #obj-7-23}
**Example 7.23 - An exact round trip can conceal an aliased wave**

The first formula is aliasing: unresolved modes contaminate the same sampled coefficient. A field bandlimited to $|n|\le K$ (all higher coefficients zero) is recovered uniquely if $N\ge2K+1$. With $N=8$, mode $6$ samples exactly as mode $-2$. A correct forward-inverse round trip cannot detect that loss of continuous information. The fast Fourier transform (FFT) computes the same DFT in $O(N\log N)$ work; it is an algorithm, not a different transform. Discrete convolution is circular (indices wrap modulo $N$); linear convolution requires padding.
:::

::: {.tb-exercise #ex-7-5}
**Exercise 7.5 - Find the aliased index**

*Application.* On $N=10$ equally spaced points, which signed mode in $[-5,4]$ has the same samples as mode $7$?
:::

## Chapter summary

Fourier coefficients follow from periodic orthogonality. Differentiation multiplies by $ik$; the Laplacian multiplies by $-k^2$. Parseval equates mean square or integrated square with coefficient power under the stated normalization. Endpoint regularity controls coefficient decay. The whole-line transform has a continuous wavenumber and a paired inverse factor. Convolution becomes multiplication; diffusion becomes Gaussian smoothing. A DFT is exact for samples, while aliasing limits its interpretation as continuous analysis.

::: {.tb-exercise #ex-7-6}
**Exercise 7.6 - Connect the chapter results**

*Synthesis.* Find the nonzero Fourier coefficients and mean square of $3\cos(2x)$ on a $2\pi$ interval. Explain why a round trip of an undersampled wave can be exact. Derive the decay rate of the $n$th periodic diffusion mode.
:::

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

# Rotating fluids, vorticity, and spectra {#ch-fluids}

How do the mathematical operators become a model of rotating horizontal flow? We identify the physical assumptions that reduce momentum dynamics to vorticity transport, then derive Rossby-wave frequencies and conserved quadratic quantities. The model determines which deductions apply; the spherical geometry fixes their signs and scale factors.

## Mass, momentum, and rotating frames

In a rotating frame the apparent Coriolis acceleration turns motion without doing work. Conservation and scale assumptions reduce the fluid equations to the horizontal models used in idealized geophysical dynamics. Sources: [@Vallis2006, Sections 1.2-1.3, 1.9-1.11, 2.1-2.3]; vector identities: [@ArfkenWeber2005, Sections 1.8-1.9].

::: {.tb-definition #obj-10-1}
**Definition 10.1 - Fluid variables and rotating coordinates**

Let $\rho$ be mass density, $p$ pressure, $\mathbf u$ velocity relative to a frame rotating at constant vector angular velocity $\boldsymbol\Omega$, and $\Phi$ effective gravitational potential per unit mass, including the centrifugal potential.
:::

::: {.tb-model #obj-10-2}
**Model 10.2 - Constant-density incompressible Newtonian fluid**

Assume constant density $\rho>0$, constant kinematic viscosity $\nu$, and a frame rotating with constant $\boldsymbol\Omega$. A Newtonian constitutive relation makes viscous stress proportional to strain rate; under these assumptions its acceleration is $\nu\Delta\mathbf u$. Other prescribed acceleration is $\mathbf F$.
:::

::: {.tb-law #obj-10-3}
**Law 10.3 - Mass conservation and Newton's second law**

A material parcel conserves mass, and its inertial acceleration equals the total applied force per unit mass. Pressure and gravity supply their respective force densities. The Newtonian viscous relation is an adopted constitutive model, rather than a theorem of vector calculus [@Vallis2006, Sections 1.2-1.3].
:::

::: {.tb-result #obj-10-4}
**Result 10.4 - Momentum in a uniformly rotating frame**

For the preceding model, with centrifugal acceleration absorbed into the effective potential $\Phi$, the governing equations are

$$
\nabla\cdot\mathbf u=0,\qquad
\frac{D\mathbf u}{Dt}+2\boldsymbol\Omega\times\mathbf u
=-\frac1\rho\nabla p-\nabla\Phi+\nu\Delta\mathbf u+\mathbf F.
\tag{10.1}
$$
:::

::: {.tb-proof}
**Derivation of Result 10.4**

The viscous Laplacian form assumes these constitutive and incompressibility conditions; it is not the general compressible stress law. Pressure enforces the divergence constraint. A Newtonian fluid has stress proportional to strain rate. In a changing basis, the inertial derivative of a vector is its rotating derivative plus $\boldsymbol\Omega\times$ that vector. Applying this rule twice to position produces $2\boldsymbol\Omega\times\mathbf u$ and $\boldsymbol\Omega\times(\boldsymbol\Omega\times\mathbf x)$; the latter is absorbed in $\Phi$. Coriolis does no work since $\mathbf u\cdot(\boldsymbol\Omega\times\mathbf u)=0$.
:::

::: {.tb-model #obj-10-5}
**Model 10.5 - Traditional Coriolis parameter and tangent-plane limits**

For a shallow horizontal layer, the traditional horizontal Coriolis term uses the local vertical component $f=2\Omega\sin\varphi$, where $\Omega=|\boldsymbol\Omega|$. This approximation and the shallow geometry have physical limits; they do not follow from vector algebra alone. Near reference latitude $\varphi_0$, a tangent plane with east coordinate $x$ and north coordinate $y$ gives $f\approx f_0+\beta y$, where $f_0=2\Omega\sin\varphi_0$ and $\beta=2\Omega\cos\varphi_0/R$. This is the beta-plane approximation. An $f$-plane keeps only $f_0$.
:::

::: {.tb-exercise #ex-10-1}
**Exercise 10.1 - Check Coriolis work**

*Conceptual proof.* For an arbitrary velocity $\mathbf u$ and constant $\boldsymbol\Omega$, show that $2\boldsymbol\Omega\times\mathbf u$ cannot change kinetic energy directly.
:::

## Streamfunction and the barotropic vorticity equation

In a constant-depth nondivergent layer, absolute vertical vorticity is materially conserved in the inviscid unforced limit. Streamfunction converts the velocity-vorticity relation into a Poisson inversion. Sources: [@Vallis2006, Sections 4.1-4.6, 5.1]; geometry follows Chapter 3.

::: {.tb-definition #obj-10-6}
**Definition 10.6 - Barotropic pressure relation**

Following Vallis, a barotropic fluid has density determined by pressure alone, $\rho=\rho(p)$, including the special case $\rho=\mathrm{constant}$ [@Vallis2006, Section 1.3, p. 15]. For differentiable relations this makes $\nabla\rho\times\nabla p=0$. An invertible relation can also be written $p=p(\rho)$; constant density removes the baroclinic source even when pressure varies in space.
:::

::: {.tb-model #obj-10-7}
**Model 10.7 - Shallow constant-depth nondivergent layer**

A constant-density, constant-depth nondivergent layer is a particular model reduction; the word alone does not imply every one of those assumptions. In three dimensions the inviscid vorticity equation includes stretching of absolute vorticity. In a shallow layer its vertical component is
$D(\zeta+f)/Dt=-(\zeta+f)\nabla_s\cdot\mathbf u$, subject to the horizontal-model assumptions. If depth changes, stretching matters and potential vorticity $(\zeta+f)/h$ is conserved instead, with $h$ layer thickness. We now take constant $h$ and zero divergence.
:::

::: {.tb-definition #obj-10-8}
**Definition 10.8 - Absolute vorticity and its sources**

Define absolute vorticity $q=\zeta+f$, forcing $F$ and dissipation $D$ in vorticity units per time ($\mathrm s^{-2}$).
:::

::: {.tb-result #obj-10-9}
**Result 10.9 - Forced and dissipative barotropic vorticity equation**

In the shallow constant-depth model, with the streamfunction convention (3.7) and a stationary planetary $f$,

$$
\partial_t\zeta+J_s(\psi,\zeta+f)=F+D,
\qquad \zeta=\Delta_s\psi,
\qquad
J_s(a,b)=\frac{\partial_\lambda a\,\partial_\varphi b-
\partial_\varphi a\,\partial_\lambda b}{R^2\cos\varphi}.
\tag{10.2}
$$
:::

::: {.tb-proof}
**Derivation of Result 10.9**

Take the vertical curl of horizontal momentum. The barotropic pressure term has no baroclinic curl source. The shallow absolute-vorticity stretching term is $-(\zeta+f)\nabla_s\cdot\mathbf u$, which vanishes under nondivergence. The remaining transport is $\partial_t\zeta+\mathbf u\cdot\nabla_s(\zeta+f)$. Substitution of (3.7) gives $\mathbf u\cdot\nabla_sb=(\psi_\lambda b_\varphi-\psi_\varphi b_\lambda)/(R^2\cos\varphi)$, fixing the sign in (10.2).
:::

::: {.tb-result #obj-10-10}
**Result 10.10 - Recovering streamfunction from relative vorticity**

For a smooth relative-vorticity field with zero area mean, choose $\psi_0^0=0$. Harmonic inversion gives

$$
\psi_\ell^m=-\frac{R^2}{\ell(\ell+1)}\zeta_\ell^m,\quad\ell\ge1.
\tag{10.3}
$$
:::

::: {.tb-proof}
**Proof of Result 10.10**

The spherical Laplacian has eigenvalue $-\ell(\ell+1)/R^2$ at degree $\ell$. Divide each nonzero-degree coefficient of $\zeta=\Delta_s\psi$ by that eigenvalue. The omitted constant mode explains both the zero-mean compatibility condition and the freedom to choose the mean of $\psi$. $\square$
:::

::: {.tb-example #obj-10-11}
**Example 10.11 - The beta-plane form and dimensional check**

On a beta-plane, $u=-\psi_y$, $v=\psi_x$, $\zeta=\Delta\psi$, and $J(a,b)=a_xb_y-a_yb_x$. Equation (10.2) becomes $\zeta_t+J(\psi,\zeta)+\beta\psi_x=F+D$. Units check: $[J_s(\psi,q)]=[\psi][q]/R^2=\mathrm s^{-2}$.
:::

::: {.tb-exercise #ex-10-2}
**Exercise 10.2 - A one-degree inversion**

*Application.* If $\zeta=B Y_2^0$ with $[B]=\mathrm s^{-1}$, find the zero-mean $\psi$ and its units.
:::

## Rossby waves and physical propagation

A parcel displaced across a planetary-vorticity gradient changes relative vorticity. This coupling supports dispersive Rossby waves. Sources: [@Vallis2006, Sections 5.7-5.8].

::: {.tb-model #obj-10-12}
**Model 10.12 - Small barotropic waves about rest**

Set both forcing and dissipation to zero, $F=D=0$, and linearize the beta-plane equation about rest by neglecting the quadratic term $J(\psi,\Delta\psi)$. The omitted term is quadratic in disturbance amplitude.
:::

::: {.tb-definition #obj-10-13}
**Definition 10.13 - Planar wave parameters**

Write $\psi=Ae^{i(kx+ly-\omega t)}$, where $k,l$ are eastward and northward angular wavenumbers and $\omega$ is angular frequency.
:::

::: {.tb-result #obj-10-14}
**Result 10.14 - Beta-plane Rossby dispersion**

For a nonzero wave with $k^2+l^2>0$ in the linear beta-plane model about rest with $F=D=0$,

$$
\partial_t\Delta\psi+\beta\partial_x\psi=0
\quad\Longrightarrow\quad
\omega=-\frac{\beta k}{k^2+l^2}.
\tag{10.4}
$$
:::

::: {.tb-proof}
**Derivation of Result 10.14**

Substitution gives $i\omega(k^2+l^2)+i\beta k=0$. For $\beta>0$ the zonal phase speed $\omega/k$ is negative whenever $k\ne0$: crests propagate westward relative to the resting background. The zonal group speed is $\partial\omega/\partial k=\beta(k^2-l^2)/(k^2+l^2)^2$, which can have either sign. Phase and energy-envelope propagation must not be conflated. A uniform eastward background speed $U$ adds a Doppler shift $Uk$ to $\omega$.
:::

::: {.tb-result #obj-10-15}
**Result 10.15 - Spherical barotropic Rossby frequencies**

For the corresponding linearization about rest on the whole sphere, with $F=D=0$ and $f=2\Omega\sin\varphi$, the mode $\psi=A Y_\ell^m e^{-i\omega t}$ has

$$
\omega=-\frac{2\Omega m}{\ell(\ell+1)},\qquad \ell\ge1.
\tag{10.5}
$$
:::

::: {.tb-proof}
**Derivation of Result 10.15**

On the full sphere, $J_s(\psi,f)=2\Omega\partial_\lambda\psi/R^2$. Substituting $\psi=A Y_\ell^m e^{-i\omega t}$ into the linearized equation gives the modal relation. The resulting coefficient equation is $i\ell(\ell+1)\omega+2i\Omega m=0$.
:::

::: {.tb-remark #obj-10-16}
**Remark 10.16 - The scope of linear modal propagation**

These are global barotropic Rossby modes about rest. The spherical eigenvalue replaces the planar squared wavenumber. The linear calculation neglects finite-amplitude interactions; it does not assert that every forced turbulent field is a superposition of independently evolving waves.
:::

::: {.tb-exercise #ex-10-3}
**Exercise 10.3 - Read a global frequency**

*Calculation and units.* For $\ell=2$, $m=1$, determine $\omega/\Omega$. If $\Omega$ has units $\mathrm s^{-1}$, what are the units of the period $2\pi/|\omega|$?
:::

## Energy, enstrophy, and scale spectra

Conservation identities provide physical diagnostics, while spherical Parseval identities locate variance and kinetic energy by angular scale. Sources: [@Vallis2006, Sections 4.5, 8.1-8.3]; spectral formulas are derived from [@ArfkenWeber2005, Sections 12.6, 12.11].

::: {.tb-assumption #obj-10-17}
**Assumption 10.17 - Closed, inviscid, unforced nondivergent flow**

Take smooth flow on a closed sphere, zero forcing and dissipation, zero horizontal divergence, and time-independent planetary $f$.
:::

::: {.tb-definition #obj-10-18}
**Definition 10.18 - Area-mean energy and absolute enstrophy**

Use $\langle a\rangle_A=(4\pi R^2)^{-1}\int a\,dA$. Define $K=\tfrac12\langle|\mathbf u|^2\rangle_A$ and $Q=\tfrac12\langle q^2\rangle_A$. Enstrophy means half the mean squared vorticity; specify relative or absolute vorticity.
:::

::: {.tb-result #obj-10-19}
**Result 10.19 - Material invariants and kinetic-energy conservation**

Under the preceding assumptions, every differentiable $C(q)$ with finite integral obeys

$$
\frac{d}{dt}\langle C(q)\rangle_A
=-\langle\mathbf u\cdot\nabla_s C(q)\rangle_A=0
\tag{10.6}
$$

In particular $Q$ is constant. Kinetic energy $K$ is also constant.
:::

::: {.tb-proof}
**Derivation of Result 10.19**

Because $Dq/Dt=0$, the chain rule gives $\partial_tC(q)=-\mathbf u\cdot\nabla_sC(q)$. Rewrite this as a divergence using nondivergence and integrate on the closed sphere to obtain (10.6).

For energy, integration by parts gives $K=-\tfrac12\langle\psi\zeta\rangle_A$. Self-adjointness of $\Delta_s$ makes $K\prime=-\langle\psi\zeta_t\rangle_A=\langle\psi J_s(\psi,q)\rangle_A$. Move advection onto $\psi$ under the integral; its derivative along $\mathbf u$ is $J_s(\psi,\psi)=0$. Thus $K\prime=0$. With sources the same calculation instead gives $K\prime=-\langle\psi(F+D)\rangle_A$.
:::

::: {.tb-definition #obj-10-20}
**Definition 10.20 - Relative-enstrophy and kinetic-energy spectra**

Expand $\psi$ using (8.7). Define relative enstrophy $Z=\frac12\langle\zeta^2\rangle_A$ and its degree spectrum $Z_\ell$, and define $K_\ell$ analogously. The spectra group coefficients by degree.
:::

::: {.tb-result #obj-10-21}
**Result 10.21 - Spectral weighting by angular scale**

For a smooth real streamfunction expanded in the convention (8.7), the area-mean spectra are

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
:::

::: {.tb-proof}
**Proof of Result 10.21**

Green's identity gives $K=-\tfrac12\langle\psi\Delta_s\psi\rangle_A$; each harmonic contributes its eigenvalue $-\ell(\ell+1)/R^2$. For $Z$, square the vorticity coefficient $-\ell(\ell+1)\psi_\ell^m/R^2$. Parseval and $\langle a\rangle_A=(4\pi)^{-1}\int a\,d\Omega$ give the factors in (10.7). $\square$
:::

::: {.tb-remark #obj-10-22}
**Remark 10.22 - Units, normalization, and order multiplicities**

Thus $[K]=\mathrm m^2\,\mathrm s^{-2}$ and $[Z]=\mathrm s^{-2}$. These are global means; area-integrated quantities have another factor $4\pi R^2$. A coefficient sum for a real field includes both positive and negative orders, or equivalent multiplicity weights if only nonnegative orders are stored. Missing those weights changes the spectrum. These spectra use relative vorticity, whereas (10.6) is stated for absolute vorticity.
:::

::: {.tb-remark #obj-10-23}
**Remark 10.23 - A spectrum is not a transfer budget**

Spectra describe how a quadratic quantity is distributed, not the direction of its transfer. A cascade claim requires a scale-transfer budget or other evidence. Likewise, no conservation law alone fixes a turbulent spectral slope or a jet count. Zonal averaging splits a field into its mean and departure, $a=\overline a+a'$ with $\overline{a'}=0$. Then $\overline{uv}=\overline u\,\overline v+\overline{u'v'}$; the covariance term represents transport by correlated departures and cannot generally be reconstructed from the two means alone.
:::

::: {.tb-exercise #ex-10-4}
**Exercise 10.4 - Remove a source of false conservation**

*Model evaluation.* If forcing and dissipation are restored, is $K\prime$ still necessarily zero? Give its budget in terms of $\psi,F,D$.
:::

## Chapter summary

Coriolis acceleration follows from rotating-frame differentiation and does no work. A shallow constant-depth nondivergent model materially conserves absolute vorticity. Streamfunction and vorticity are linked by spherical Poisson inversion. The beta effect produces the dispersions (10.4)-(10.5); phase and group velocities differ. Smooth inviscid unforced flow conserves kinetic energy and absolute-vorticity functionals. Parseval yields degree spectra with explicit radius and area normalization. Spectral shape alone does not establish a cascade.

::: {.tb-exercise #ex-10-5}
**Exercise 10.5 - Connect the chapter results**

*Synthesis.* Check the sign of a Rossby wave's phase speed for positive $\beta$. Derive the units in (10.3). What happens to $K_\ell$ and $Z_\ell$ when all streamfunction power moves from degree $\ell=2$ to degree $\ell=4$ while total $K$ is held fixed?
:::

# Probability, averages, and climatological estimates {#ch-statistics}

What does an average estimated from a simulation mean? Spatial integration, time averaging, and ensemble expectation are distinct operations. We introduce their probability assumptions, derive the effect of serial dependence on an estimated mean, and identify what a quadratic prediction objective can recover.

## Random variables, expectation, and covariance

Probability distinguishes an ensemble average from one observed realization. Covariance measures the dependence that determines uncertainty in averages. Sources: [@ArfkenWeber2005, Sections 19.1-19.2, 19.5-19.6].

::: {.tb-definition #obj-11-1}
**Definition 11.1 - Probability space and a random variable**

A probability space consists of possible outcomes, a collection of events, and a probability measure $P$ assigning nonnegative probabilities, total probability one, and countably additive probabilities for disjoint events (the probability of a countable disjoint union is the sum of the probabilities). A real random variable $X$ is a measurable function of an outcome. A realization is one observed value. If $X$ has density $p_X(x)$, probabilities and expectations satisfy

$$
P(X\in A)=\int_Ap_X(x)dx,\quad \int_{\mathbb R}p_Xdx=1,
\qquad \mathbb E[g(X)]=\int_{\mathbb R}g(x)p_X(x)dx.
\tag{11.1}
$$
:::

::: {.tb-definition #obj-11-2}
**Definition 11.2 - Mean, variance, covariance, and correlation**

For a discrete variable, replace the integral by a sum over values weighted by their probabilities. Expectations require the stated moment to exist. Define mean $m_X=\mathbb E X$, variance $\sigma_X^2=\mathbb E[(X-m_X)^2]$, and covariance $\operatorname{Cov}(X,Y)=\mathbb E[(X-m_X)(Y-m_Y)]$. Variance has squared units; standard deviation $\sigma_X$ has the variable's units. For nonzero standard deviations, correlation is $\operatorname{Corr}(X,Y)=\operatorname{Cov}(X,Y)/(\sigma_X\sigma_Y)$ and lies in $[-1,1]$ by Cauchy-Schwarz.
:::

::: {.tb-definition #obj-11-3}
**Definition 11.3 - Independence**

Independence means the joint probabilities factor for all events concerning the two variables. It implies zero covariance when second moments exist, but the reverse is false.
:::

::: {.tb-counterexample #obj-11-4}
**Counterexample 11.4 - Uncorrelated variables can be dependent**

For a variable $X$ uniform on $[-1,1]$, let $Y=X^2$. Symmetry gives $\operatorname{Cov}(X,Y)=\mathbb E X^3-\mathbb E X\mathbb E X^2=0$, yet $Y$ is determined by $X$.
:::

::: {.tb-definition #obj-11-5}
**Definition 11.5 - Gaussian distribution and its extra assumption**

A Gaussian (normal) variable has density $p_X(x)=(2\pi\sigma_X^2)^{-1/2}\exp[-(x-m_X)^2/(2\sigma_X^2)]$ when $\sigma_X>0$. Normality is an additional distributional assumption, not a consequence of having a mean and variance.
:::

::: {.tb-result #obj-11-6}
**Result 11.6 - Independent means and the central limit theorem (quoted)**

For independent identically distributed samples with variance $0<\sigma_X^2<\infty$, the sample mean has variance $\sigma_X^2/N$. The central limit theorem gives an asymptotically Gaussian standardized mean under these assumptions; correlated time samples need additional hypotheses. [@ArfkenWeber2005, Sections 19.5-19.6].
:::

::: {.tb-exercise #ex-11-1}
**Exercise 11.1 - Scale a random variable**

*Application.* If $Y=3X+2$ with finite second moments, express its mean and variance in terms of those of $X$.
:::

## Spatial, temporal, and ensemble means

The integration measure and sampling mechanism define an average. Spatial, temporal, and ensemble means answer different questions. Sources: [@ArfkenWeber2005, Sections 19.2, 19.6]; fluid averaging and correlation: [@Vallis2006, Sections 8.1, 10.2].

::: {.tb-definition #obj-11-7}
**Definition 11.7 - Ensemble, time, and area means**

For a field $q(\mathbf x,t,\omega)$, $\omega$ labels a random outcome, not wave frequency in this chapter. An ensemble mean is $\mathbb E[q(\mathbf x,t,\omega)]$ at fixed position and time. A time mean of one realization over duration $T$ is $\overline q_T(\mathbf x)=T^{-1}\int_0^Tq(\mathbf x,t,\omega)dt$. A global spatial mean is $\langle q\rangle_A$ from Chapter 10. None equals the others by definition.
:::

::: {.tb-definition #obj-11-8}
**Definition 11.8 - Stationarity and observable ergodicity**

A time series is weakly stationary if its mean is time-independent, its variance is finite and constant, and its covariance depends only on lag. Strict stationarity means all finite joint distributions are invariant under a common time shift. Ergodicity, for an observable, means its long-time average equals the corresponding ensemble expectation almost surely (with probability one), under an invariant distribution. Stationarity alone does not guarantee this property.
:::

::: {.tb-counterexample #obj-11-9}
**Counterexample 11.9 - A stationary trajectory with a random time mean**

For example, $X(t)=B$ with one random constant $B$ for an entire trajectory is stationary, but its time mean is the realized $B$, not generally $\mathbb EB$.
:::

::: {.tb-remark #obj-11-10}
**Remark 11.10 - Finite-time climate estimates and spin-up**

A finite-time climatological estimate can retain initial-state transients, sampling variability, and slow fluctuations. Excluding an initial adjustment interval (spin-up) is a modeling decision whose adequacy requires diagnostics; it is not a theorem that any fixed exclusion time yields equilibrium. Independent simulations and adjacent windows of one simulation are not interchangeable sampling units.
:::

::: {.tb-exercise #ex-11-2}
**Exercise 11.2 - Name the missing averaging assumption**

*Reasoning.* A time series has constant ensemble mean and covariance depending only on lag. Does that prove its long-time mean equals the ensemble mean? Explain with the random-constant example.
:::

## Autocorrelation and uncertainty of a mean

Positive serial correlation reduces the information in a fixed number of time samples. The variance of a mean follows from all pairwise covariances. Sources: [@ArfkenWeber2005, Section 19.6]; time-correlation interpretation: [@Vallis2006, Section 10.2].

::: {.tb-assumption #obj-11-11}
**Assumption 11.11 - Equally spaced stationary samples**

Let $X_1,\ldots,X_N$ be equally spaced weakly stationary samples with variance $\sigma^2>0$. Define autocorrelation at integer lag $k$ by $\rho_k=\operatorname{Cov}(X_j,X_{j+k})/\sigma^2$, independent of $j$.
:::

::: {.tb-result #obj-11-12}
**Result 11.12 - Variance of a correlated sample mean**

For $\overline X=N^{-1}\sum_{j=1}^NX_j$ under the preceding assumptions,

$$
\begin{aligned}
\operatorname{Var}(\overline X)
&=\frac1{N^2}\sum_{i,j}\operatorname{Cov}(X_i,X_j)\\
&=\frac{\sigma^2}{N}\left[1+2\sum_{k=1}^{N-1}\left(1-\frac{k}{N}\right)\rho_k\right].
\end{aligned}
\tag{11.2}
$$
:::

::: {.tb-proof}
**Proof of Result 11.12**

Expand the centered sum before taking expectation to obtain the double covariance sum. There are $N$ diagonal terms and $N-k$ pairs at each positive lag $k$, with the same number at negative lag. Substituting $\operatorname{Cov}(X_j,X_{j+k})=\sigma^2\rho_k$ gives (11.2). $\square$
:::

::: {.tb-definition #obj-11-13}
**Definition 11.13 - Variance-equivalent effective sample count**

There are $N-k$ pairs at each positive lag and the same number at negative lag, explaining the factor two. Define $N_{\rm eff}=N/[1+2\sum_{k=1}^{N-1}(1-k/N)\rho_k]$ when the denominator is positive; then $\operatorname{Var}(\overline X)=\sigma^2/N_{\rm eff}$. This is a variance-equivalent sample count, not literally a count of independent observations. Negative correlation can make it exceed $N$.
:::

::: {.tb-example #obj-11-14}
**Example 11.14 - Geometric serial correlation**

For $\rho_k=r^k$, $|r|<1$, and $N$ long relative to the correlation decay, the bracket approaches $(1+r)/(1-r)$. With $r=0.8$, $N_{\rm eff}\approx N/9$. If correlations are estimated from a short series, the estimated effective count is itself uncertain. A decorrelation formula does not establish stationarity or supply independent replicas.
:::

::: {.tb-exercise #ex-11-3}
**Exercise 11.3 - Use negative correlation**

*Interpretation.* For a long series with $\rho_k=r^k$ and $r=-1/2$, what is the approximate ratio $N_{\rm eff}/N$? Does this denote a literal count of independent observations?
:::

## Squared-error prediction and normalization

The conditional mean minimizes expected squared error. This identifies the target of a quadratic loss but does not establish optimality for a relative-error loss. Sources: [@ArfkenWeber2005, Sections 19.2, 19.6]; projection argument follows Chapter 4.

::: {.tb-definition #obj-11-15}
**Definition 11.15 - Conditional mean and conditional variance**

For predictor information $X$ and square-integrable scalar target $Y$, the conditional expectation $m(X)=\mathbb E[Y\mid X]$ is the mean given that information; it is characterized by $\mathbb E[(Y-m(X))h(X)]=0$ for suitable functions $h$. For a square-integrable predictor $a(X)$, the conditional variance is $\operatorname{Var}(Y\mid X)=\mathbb E[(Y-m(X))^2\mid X]$.
:::

::: {.tb-result #obj-11-16}
**Result 11.16 - The conditional mean minimizes quadratic risk**

Let $Y$ and the predictor $a(X)$ have finite second moments. For $m(X)=\mathbb E[Y\mid X]$,

$$
\mathbb E[(Y-a(X))^2\mid X]
=\operatorname{Var}(Y\mid X)+[m(X)-a(X)]^2.
\tag{11.3}
$$

Consequently $a(X)=m(X)$ minimizes expected squared error.
:::

::: {.tb-proof}
**Proof of Result 11.16**

Expand $Y-a=(Y-m)+(m-a)$; the cross term vanishes conditionally. This proves the optimum. It extends to a fixed weighted quadratic norm on finite-dimensional profiles by summing the component identities. It does not automatically extend to $\mathbb E[\|Y-a\|/\|Y\|]$, whose weighting and unsquared norm differ. Also, variability between targets with the same external configuration need not be irreducible when the predictor sees extra state information. $\square$
:::

::: {.tb-definition #obj-11-17}
**Definition 11.17 - Affine normalization for learning**

For a scalar training variable $x$, a mean $m$, standard deviation $s$, and small positive $\epsilon$ in the same units as $x$, affine normalization is $z=(x-m)/(s+\epsilon)$, with inverse $x=(s+\epsilon)z+m$. Fit these scales on training data only to avoid using held-out information. Equal sample weights for a numerical scaling convention need not coincide with physical area weights for a climatological mean. One changes coordinates for learning; the other defines an observable.
:::

::: {.tb-exercise #ex-11-4}
**Exercise 11.4 - Invert a normalization**

*Application.* If $z=(x-m)/(s+\epsilon)$, derive the inverse and state what dimensions $\epsilon$ must have.
:::

## Chapter summary

Probability assigns weights to outcomes; expectation, variance, and covariance depend on that distribution. Zero covariance does not imply independence. Ensemble, time, zonal, and area averages are different operators. Stationarity is time-shift invariance of specified statistics; ergodicity is an additional long-time averaging property. Equation (11.2) gives exact sample-mean variance from autocorrelations. The conditional mean minimizes quadratic risk by (11.3). Normalization and physical averaging need separate definitions.

::: {.tb-exercise #ex-11-5}
**Exercise 11.5 - Connect the chapter results**

*Synthesis.* Can ten overlapping windows from one run be assumed independent? For $r=0.8$, how many variance-equivalent samples do $900$ long-series samples supply approximately? Why does predicting the conditional mean not remove conditional variance?
:::

# Integral operators, symmetries, and learned maps {#ch-operators}

How do the same bases describe both a PDE solution map and a learned operator? A kernel exposes the influence of one location on another. Symmetry reduces some kernels to spectral multipliers; the remaining question is which assumptions survive when those multipliers and nonlinear updates are learned from sampled data.

## Kernels and spectral multipliers

Many solution operators are global integral maps. Symmetry can reduce a two-position kernel to one multiplier per Fourier mode or spherical degree. Sources: [@ArfkenWeber2005, Sections 10.5, 12.8, 15.5, 16.1-16.4].

::: {.tb-definition #obj-12-1}
**Definition 12.1 - Integral kernel and its measure**

For input function $f$ on a domain $D$ with measure $d\nu$, an integral operator has the form

$$
(\mathcal Kf)(x)=\int_DK(x,y)f(y)d\nu(y).
\tag{12.1}
$$

The kernel $K(x,y)$ weights the influence of source point $y$ on output point $x$. This operator is linear when $K$ is fixed; a kernel depending on $f$ can produce a nonlinear overall map. Its physical units must combine those of $f$ and $d\nu$ to give the output units. The Green's operator (5.7) is one example.
:::

::: {.tb-result #obj-12-2}
**Result 12.2 - Translation-invariant kernels on a periodic interval**

Let $f,k\in L^2([0,d])$ be periodic, with $K(x,y)=k(x-y)$. Write $k_n=2\pi n/d$ for angular wavenumber and $f_n$ for the coefficients of $f$ in the basis $e^{ik_nx}$. Define the kernel coefficients by $\beta_n=d^{-1}\int_0^d k(z)e^{-ik_nz}dz$. Under normalized integration $dy/d$, the operator has coefficients $(\mathcal Kf)_n=\beta_nf_n$. Under unnormalized $dy$ the multiplier is $d\beta_n$. The measure and coefficient normalization determine the factor together.
:::

::: {.tb-proof}
**Proof of Result 12.2**

In the coefficient integral for $\mathcal Kf$, set $z=x-y$ modulo the period. The factor $e^{-ik_nx}$ becomes $e^{-ik_nz}e^{-ik_ny}$. The normalized $z$ integral is $\beta_n$ and the remaining normalized $y$ integral is $f_n$. Removing normalization in the operator integral multiplies the answer by $d$. Finite-measure $L^2$ functions are in $L^1$, which justifies these integrals. $\square$
:::

::: {.tb-assumption #obj-12-3}
**Assumption 12.3 - Square-integrable isotropic scalar kernel**

On the unit sphere, assume $k\in L^2([-1,1])$ and $f\in L^2(S^2,d\Omega)$, and interpret the expansions in $L^2$. Let $K(\mathbf n,\mathbf n')=k(\mathbf n\cdot\mathbf n')$ be isotropic, meaning dependent only on angular separation.
:::

::: {.tb-result #obj-12-4}
**Result 12.4 - Isotropic spherical multiplier**

For $k\in L^2([-1,1])$ and $f\in L^2(S^2,d\Omega)$, let $a_\ell=(2\ell+1)\int_{-1}^1 k(t)P_\ell(t)dt/2$. The isotropic kernel $k(\mathbf n\cdot\mathbf n\prime)$ acting under solid-angle measure has the same multiplier for every order of a fixed degree:

$$
(\mathcal Kf)_\ell^m=\kappa_\ell f_\ell^m,
\qquad \kappa_\ell=\frac{4\pi a_\ell}{2\ell+1}
=2\pi\int_{-1}^1k(t)P_\ell(t)dt.
\tag{12.2}
$$
:::

::: {.tb-proof}
**Proof of Result 12.4**

Expand $k(t)=\sum_{\ell\ge0}a_\ell P_\ell(t)$, with $a_\ell=(2\ell+1)\int_{-1}^1k(t)P_\ell(t)dt/2$. Apply (8.9) in (12.1), using $d\nu=d\Omega'$, and integrate against $f$. The addition theorem writes each kernel degree as a sum of $Y_\ell^m(\mathbf n)\overline{Y_\ell^m(\mathbf n\prime)}$. Integration against $f$ extracts its coefficients, giving the multiplier in (12.2). Interpret the expansions in $L^2$ under the stated hypotheses. $\square$
:::

::: {.tb-example #obj-12-5}
**Example 12.5 - Constant kernel and a normalization check**

The same $\kappa_\ell$ acts for every $m$. For $k=1$, only $\kappa_0=4\pi$ survives and $\mathcal Kf=\int f\,d\Omega$ is constant, verifying the normalization. An integral under physical area $dA'$ supplies an additional $R^2$. An arbitrary position-dependent kernel couples harmonic modes; choosing spherical harmonics alone does not make an operator diagonal.
:::

::: {.tb-exercise #ex-12-1}
**Exercise 12.1 - A degree-two kernel**

*Application.* For $k(t)=P_2(t)$ under $d\Omega$, find the only nonzero multiplier.
:::

## Rotations and equivariance

Equivariance means that transforming the input and then applying a map agrees with transforming its output. It is a precise property with specific group, field-type, and discretization assumptions. Sources: [@ArfkenWeber2005, Sections 1.2, 4.1-4.3, 12.8]; operator formulation: [@Bonev2023sfno, Sections 3.2-4.2].

::: {.tb-definition #obj-12-6}
**Definition 12.6 - Rotations and scalar equivariance**

A group is a set of transformations closed under composition, with an identity, an inverse for every transformation, and associative composition. The rotation group $SO(3)$ consists of real $3\times3$ matrices $Q$ satisfying $Q^{\mathsf T}Q=I$ and $\det Q=1$. On scalar fields define the rotation action $(T_Qf)(\mathbf n)=f(Q^{-1}\mathbf n)$. A scalar-to-scalar map $\mathcal G$ is rotation-equivariant if

$$
\mathcal G(T_Qf)=T_Q\mathcal G(f)\quad\text{for every }Q\in SO(3).
\tag{12.3}
$$
:::

::: {.tb-definition #obj-12-7}
**Definition 12.7 - Invariance and vector-field rotation**

It is invariant if $\mathcal G(T_Qf)=\mathcal G(f)$, as for an area integral. A vector field uses the action $T_Q\mathbf v(\mathbf n)=Q\mathbf v(Q^{-1}\mathbf n)$ instead; rotating only scalar component images misses the vector rotation.
:::

::: {.tb-result #obj-12-8}
**Result 12.8 - Order-independent multipliers commute with rotations**

Rotations mix orders within a fixed degree. Consequently, a scalar linear multiplier shared by every $m$ at degree $\ell$ commutes with rotations; a separate arbitrary multiplier for each $m$ generally does not. An isotropic kernel satisfies this property by (12.2). Multiple scalar channels can mix through one channel matrix per degree, still shared across orders.
:::

::: {.tb-proof}
**Proof of Result 12.8**

A rotation maps the span of the $2\ell+1$ orders of degree $\ell$ into itself. A scalar multiple of the identity on that span commutes with every such mixing matrix. With scalar channels, a common channel matrix also commutes because it acts on channels, not orders [@Bonev2023sfno, Sections 3.4-4.1]. $\square$
:::

::: {.tb-remark #obj-12-9}
**Remark 12.9 - Preferred axes and discretization**

These statements concern full rotations of scalar fields with no preferred direction. A rotating planet has a specified rotation axis: holding that axis fixed reduces the physical symmetry. Geographic positional features, direction-dependent forcing, or latitude-dependent coefficients can deliberately reduce it. Continuous equivariance also does not guarantee exact discrete equivariance after approximate quadrature and unresolved nonlinear products.
:::

::: {.tb-exercise #ex-12-2}
**Exercise 12.2 - Distinguish invariance and equivariance**

*Conceptual.* Is the area integral of a scalar field invariant or equivariant under rotation? What about the scalar field itself under the identity map?
:::

## Neural operators and loss functions

A neural operator approximates a map between functions from sampled input-output pairs. Its spectral layer uses the same analysis-multiply-synthesis structure as a classical integral operator. Sources: [@Li2021fno, Sections 2-4]; spherical construction: [@Bonev2023sfno, Sections 3.4-4.2].

::: {.tb-definition #obj-12-10}
**Definition 12.10 - Function-to-function learning and empirical risk**

Let $\mathcal G$ map an input field $a$ (an initial condition, forcing, or coefficient) to an output field $u$. A PDE solution map is an example; it can be nonlinear even though parts of its solver are linear. A parameter vector $\vartheta\in\mathbb R^p$ defines an approximation $\mathcal G_\vartheta$. For training pairs $(a_j,u_j)$, $j=1,\ldots,N$, a quadratic empirical risk is

$$
\mathcal R_N(\vartheta)=\frac1N\sum_{j=1}^N
\|\mathcal G_\vartheta(a_j)-u_j\|_Y^2,
\tag{12.4}
$$

where $\|\cdot\|_Y$ is a specified output norm, including its spatial weights and units. Empirical means refer to this finite dataset; population risk is the expectation under a stated distribution. Good training fit alone proves neither small held-out risk nor correct behavior outside the training distribution.
:::

::: {.tb-model #obj-12-11}
**Model 12.11 - A spectral hidden-field update**

A common hidden-field update, with layer index $r$, is

$$
v_{r+1}(x)=\sigma\left(W_rv_r(x)+b_r(x)
+\mathcal T^{-1}\!\left[R_r\,\mathcal T v_r\right](x)\right).
\tag{12.5}
$$
:::

::: {.tb-definition #obj-12-12}
**Definition 12.12 - Channels, activation, and spectral weights**

Here $v_r(x)$ is a vector of real scalar features (channels); $W_r$ is a channel matrix applied at each point; $b_r$ is a bias; $\sigma$ is a nonlinear activation applied to each component, for example $\max(0,z)$ for real $z$; $\mathcal T$ is Fourier or spherical harmonic analysis; $R_r$ is a learned spectral channel matrix, possibly truncated by degree; and $\mathcal T^{-1}$ synthesizes a field.
:::

::: {.tb-result #obj-12-13}
**Result 12.13 - Spectral constraints preserve real features**

The real formulation requires real $W_r,b_r$ and conjugate-compatible spectral weights: Fourier matrices satisfy $R_r(-n)=\overline{R_r(n)}$, with real weights at self-conjugate zero and Nyquist modes. A spherical matrix shared across all orders of a degree must be real to preserve $f_\ell^{-m}=(-1)^m\overline{f_\ell^m}$. These conditions keep synthesis real before the real activation. A complex architecture instead needs an explicitly chosen complex activation.
:::

::: {.tb-proof}
**Proof of Result 12.13**

For Fourier coefficients, the product must obey the same conjugacy as its input: $R(-n)\widehat v(-n)=\overline{R(n)\widehat v(n)}$. The stated condition ensures this for every real input. On the sphere a multiplier shared across $m$ preserves $v_\ell^{-m}=(-1)^m\overline{v_\ell^m}$ for every input when that common channel matrix is real. Real pointwise weights and biases then keep the activation input real. $\square$
:::

::: {.tb-definition #obj-12-14}
**Definition 12.14 - Pointwise maps and finite-parameter gradient updates**

Input and output pointwise maps convert between physical variables and hidden features. The chain rule computes derivatives of (12.4) with respect to $\vartheta$; a gradient update $\vartheta\leftarrow\vartheta-\eta\nabla_\vartheta\mathcal R_N$ uses positive step size $\eta$. Learning these finite parameters does not mean optimizing directly over every possible function.
:::

::: {.tb-remark #obj-12-15}
**Remark 12.15 - Equivariance and resolution require the whole model**

For a rotation-equivariant scalar spherical spectral layer, $R_r$ must be shared across $m$ at fixed $\ell$, and the remaining operations must respect the same action. Spatial nonlinearities create higher degrees, so truncation and sampling again matter. A fixed-parameter continuum formulation can be evaluated at several resolutions, but accuracy transfer still depends on quadrature, resolved scales, data, and the complete architecture. It is not established by matching array dimensions.
:::

::: {.tb-exercise #ex-12-3}
**Exercise 12.3 - Detect a reality violation**

*Counterexample.* A scalar Fourier filter has $R(1)=i$ and $R(-1)=i$. Applied to $\cos x$, does it preserve a real field? What paired value would be needed?
:::

## An end-to-end mathematical example

A single spherical diffusion mode connects geometry, eigenfunctions, PDE evolution, quadrature, statistics, and operator approximation without an implementation-specific assumption. Sources: [@ArfkenWeber2005, Sections 9.8, 12.6, 16.2]; steps follow the preceding chapters.

::: {.tb-model #obj-12-16}
**Model 12.16 - A degree-two diffusion initial condition**

Let the physical sphere have radius $R$, diffusivity $\kappa>0$, and real initial scalar $u_0=A(\mu^2-1/3)$, where $A$ is an amplitude with units $U$. Set no forcing and solve $u_t=\kappa\Delta_su$.
:::

::: {.tb-result #obj-12-17}
**Result 12.17 - One mode through the complete analytic chain**

For the preceding model with amplitude $A$ in units $U$,

$$
u(\mu,t)=A(\mu^2-1/3)e^{-6\kappa t/R^2},
\qquad \langle u\rangle_A=0,
\qquad \langle u^2\rangle_A=\frac{4A^2}{45}e^{-12\kappa t/R^2}.
\tag{12.6}
$$
:::

::: {.tb-proof}
**Proof of Result 12.17**

The identity $\mu^2-1/3=(2/3)P_2(\mu)$ leaves only degree two, whose Laplacian eigenvalue is $-6/R^2$. The modal integrating-factor solution gives the time exponential. The mean is zero; the mean square follows from $\tfrac12\int_{-1}^1(\mu^2-1/3)^2d\mu=1/5-2/9+1/9=4/45$. $\square$
:::

::: {.tb-example #obj-12-18}
**Example 12.18 - Representation, integration, and a stable time step**

For the mean square, integrate $\mu^4-2\mu^2/3+1/9$ under $d\mu/2$ to get $1/5-2/9+1/9=4/45$. A degree-$2$ harmonic representation is exact. Three Gaussian latitudes integrate its squared amplitude (degree four) exactly, and five equally spaced longitudes suffice for general degree-$2$ recovery. The decay time is $R^2/(6\kappa)$; a forward-Euler update is stable for this isolated mode if $\Delta t\le R^2/(3\kappa)$.
:::

::: {.tb-remark #obj-12-19}
**Remark 12.19 - What an exact example verifies**

The time-$t$ solution operator has multiplier $e^{-\kappa\ell(\ell+1)t/R^2}$ at every degree. An isotropic learned linear map could approximate these multipliers. Changing a cutoff changes representable inputs; changing $R$ changes physical decay; an incorrect area rule changes reported mean-square error. Agreement on one sampled field does not verify all these properties. If $A$ is random with finite second moment, ensemble mean square replaces $A^2$ by $\mathbb EA^2$, which is a different average from the spatial one.
:::

::: {.tb-exercise #ex-12-4}
**Exercise 12.4 - Change physical radius at fixed angular shape**

*Application.* In (12.6), double $R$ while keeping $A$ and $\kappa$ fixed. What happens to the decay time and to the initial area-mean square?
:::

## Chapter summary

Integral kernels encode nonlocal linear maps. Translation invariance and spherical isotropy give spectral multipliers with normalization fixed by the integration measure. Equivariance commutes with a specified transformation action; invariance removes the transformed dependence. A learned operator approximates a function-to-function map using finite parameters and a stated loss. Spectral layers reuse classical analysis and synthesis, while nonlinearities couple modes. Equation (12.6) supplies a complete analytic check of this chain.

::: {.tb-exercise #ex-12-5}
**Exercise 12.5 - Connect the chapter results**

*Synthesis.* For the spherical kernel $k(t)=t$, which degrees survive, and what is their multiplier? Does allowing a different coefficient for each $m$ preserve all rotations? What must be specified before calling a model's error "small"?
:::

::: {.tb-exercise #ex-12-6}
**Exercise 12.6 - Bound an integral operator**

*Independent proof.* Let $K$ be a measurable kernel and define the nonnegative constant $C_K$ by

$$
C_K^2=\int_D\int_D|K(x,y)|^2d\nu(y)d\nu(x)<\infty.
$$

For $f\in L^2(D,d\nu)$, use Cauchy-Schwarz at fixed $x$, then integrate, to prove $\|\mathcal Kf\|_2\le C_K\|f\|_2$. Apply the bound to two $L^2$ inputs to describe noise amplification.
:::

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
