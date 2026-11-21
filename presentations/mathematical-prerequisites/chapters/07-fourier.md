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
