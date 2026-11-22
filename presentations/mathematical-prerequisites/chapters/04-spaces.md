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
