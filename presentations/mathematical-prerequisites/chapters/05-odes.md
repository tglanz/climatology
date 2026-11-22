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
