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
