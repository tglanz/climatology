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
