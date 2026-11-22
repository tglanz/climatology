# Mathematical prerequisites - instructor solutions

This editor key accompanies the student textbook. Exercise numbers identify the matching prompts in the chapter sources. The student PDF does not include these solutions.

## Chapter 1

**Solution to Exercise 1.1 - Check a decay exponent**

Its dimensions are $\mathrm m$, so it is inadmissible. The exponent $-\kappa k^2t$ is dimensionless.

**Solution to Exercise 1.2 - Change coefficients without changing length**

$Q\mathbf u=(-1,2)^{\mathsf T}$ and both squared lengths equal $5$. Direct multiplication gives $Q^{\mathsf T}Q=I$, so $Q$ is orthogonal.

**Solution to Exercise 1.3 - Project onto a line**

The coefficient is $3/\sqrt2$, so the projection is $(3/2,3/2)$. The residual has squared length $1/2$. Its difference from $(1,1)$ has squared length $1/2$, whereas $(2,1)-(1,1)$ has squared length $1$.

**Solution to Exercise 1.4 - Connect the chapter results**

Equation (1.1) gives $|e^{i\alpha}c|^2=|c|^2$. The second row of the proposed linear system is $0=1$, so there is no solution, rather than a merely nonunique one. If the second right-hand entry were zero, the second unknown would be arbitrary.

## Chapter 2

**Solution to Exercise 2.1 - Evaluate an advective rate**

$q_t=y$, $\nabla q=(2x,t)$, so $Dq/Dt=y+2Ux$.

**Solution to Exercise 2.2 - Divergence does not determine curl**

Both divergences vanish. The first curl is $(0,0,2)$ and the second is zero; divergence does not determine local rotation.

**Solution to Exercise 2.3 - Check an area factor**

The cross product of $(1,0,0)$ and $(0,1,0)$ has length one, so the area is $6$ square length units.

**Solution to Exercise 2.4 - Identify the compression term**

It satisfies $Dq/Dt=-d_0q$, hence $q(t)=q(0)e^{-d_0t}$. Expansion dilutes concentration per volume.

**Solution to Exercise 2.5 - Connect the chapter results**

Apply (2.10) with $q=\rho$, flux $\rho\mathbf u$, and zero mass source. Expansion gives $D\rho/Dt=-\rho\nabla\cdot\mathbf u$, so incompressibility implies constant density along trajectories. For the translating profile, $q_t=-cq_0'$ and $cq_x=cq_0'$ cancel; advection accounts for the local change.

## Chapter 3

**Solution to Exercise 3.1 - Compute a spherical moment**

$\langle\mu^4\rangle_A=\frac12\int_{-1}^1\mu^4d\mu=1/5$, independent of radius.

**Solution to Exercise 3.2 - Check an eigenfunction before using harmonics**

The results are $-2\mu/R^2$ and zero, respectively. The first follows from $\partial_\mu(1-\mu^2)=-2\mu$; the second has no derivatives.

**Solution to Exercise 3.3 - Diagnose an incompatible vorticity field**

No. Integrating gives $0=4\pi R^2c$, contrary to $c\ne0$. This is the constant-nullspace compatibility obstruction.

**Solution to Exercise 3.4 - Connect the chapter results**

In (3.6), $\partial_\mu[(1-\mu^2)\partial_\mu\mu]=-2\mu$, and the longitude term is zero. For $\psi=A\sin\varphi=A\mu$, (3.7) gives $u=-A\cos\varphi/R$, $v=0$, and $\zeta=-2A\sin\varphi/R^2$. Here $[A]=\mathrm m^2\,\mathrm s^{-1}$, so speeds have units $\mathrm m\,\mathrm s^{-1}$ and vorticity $\mathrm s^{-1}$.

## Chapter 4

**Solution to Exercise 4.1 - Compare two measures**

The values are $2$ and $1$. Normalizing the measure changes coefficient normalization and turns the integral of a constant into its mean square.

**Solution to Exercise 4.2 - Check a quadratic basis function**

The mean is $\sqrt5(3/3-1)/2=0$. Its squared norm is $(5/4)(9/5-6/3+1)=1$.

**Solution to Exercise 4.3 - Distinguish a weak derivative from a distribution**

It is bounded on a finite interval, hence in $L^2$. Its derivative is a Dirac delta, which is not represented by an $L^2$ function; therefore it is not in $H^1$.

**Solution to Exercise 4.4 - Connect the chapter results**

Its squared norm is $\frac12\int_{-1}^13\mu^2d\mu=1$. The example $\sin(nx)/n$ has vanishing field norm but a derivative of nonvanishing norm; deriving wind differentiates streamfunction. The derivative of a step is a Dirac delta distribution, not an $L^2$ function.


**Solution to Exercise 4.5 - Prove the converse Parseval test**

If $f$ is orthogonal to every $e_j$, the coefficient sum is zero. The hypothesis gives $\|f\|^2=0$, hence $f=0$. This is precisely completeness.

## Chapter 5

**Solution to Exercise 5.1 - Solve a forced scalar mode**

$a(t)=b_0(1-e^{-\gamma t})/\gamma$, so $a(t)\to b_0/\gamma$.

**Solution to Exercise 5.2 - Identify the zero mode**

It fails the Dirichlet conditions but satisfies both Neumann derivative conditions with eigenvalue zero.

**Solution to Exercise 5.3 - Use two modes**

$u=e^{-\kappa(\pi/d)^2t}\sin(\pi x/d)+2e^{-4\kappa(\pi/d)^2t}\sin(2\pi x/d)$. The first rate is $\kappa\pi^2/d^2$.

**Solution to Exercise 5.4 - Check the sign of the Green function**

The integral gives $u(x)=(d-x)x^2/(2d)+x(d-x)^2/(2d)=x(d-x)/2$. Its second derivative is $-1$ and the boundary values vanish.

**Solution to Exercise 5.5 - Connect the chapter results**

The single mode has decay time $\tau=[\kappa(2\pi/d)^2]^{-1}$. Integrating $-u''=1$ over a periodic interval gives $0=d$, contradicting $d>0$. The forcing is not orthogonal to the constant nullspace.

## Chapter 6

**Solution to Exercise 6.1 - Count the required time data**

Diffusion uses $u(0)$, while the wave equation also needs $u_t(0)$. For a spatial mode, the second-order time ODE admits different motions sharing one displacement but different initial velocities.

**Solution to Exercise 6.2 - Estimate the difference of two solutions**

The difference $w=u-v$ satisfies the same diffusion equation and homogeneous boundary conditions. Integrating (6.2) gives $\|w(t)\|_2^2\le\|w(0)\|_2^2$; take square roots.

**Solution to Exercise 6.3 - Compare phase and group velocity**

The phase speed is $ak$ and the group speed is $2ak$. They differ because the relation is nonlinear in wavenumber.

**Solution to Exercise 6.4 - Compare two length scales**

It is $1$. The large-scale ratio alone therefore does not justify neglecting diffusion at the smaller scale.

**Solution to Exercise 6.5 - Connect the chapter results**

Their difference $w$ obeys diffusion with homogeneous data at the boundary, so (6.2) implies $\|w(t)\|_2\le\|w(0)\|_2$. Constants have zero normal derivative and zero Laplacian, leaving the Neumann mean undetermined. A large Peclet number at one reference length cannot suppress diffusion at all shorter lengths because its rate scales as $\kappa/\ell^2$.


**Solution to Exercise 6.6 - Construct unstable backward data**

Time differentiation multiplies by $n^2$, while $-\partial_x^2$ does the same. Since $\int_0^{2\pi}\sin^2(nx)dx=\pi$, the initial norm is $\sqrt\pi e^{-n^2T}\to0$, but the norm at $T$ is $\sqrt\pi$. Continuous dependence in $L^2$ fails.

## Chapter 7

**Solution to Exercise 7.1 - A phase-rotated coefficient**

$c_1=e^{-i\alpha}/2$ and $c_{-1}=e^{i\alpha}/2$. Their squared moduli sum to $1/2$, independent of phase.

**Solution to Exercise 7.2 - Find the missing endpoint hypothesis**

No. For $f(x)=x$, the values at zero and $d$ do not match, so the periodic extension jumps and its nonzero coefficients decay only as $1/|n|$.

**Solution to Exercise 7.3 - Track transform units**

They are $\mathrm K\,m$, $\mathrm m^{-1}$, and $\mathrm K$. The dimensionless inverse prefactor changes no units.

**Solution to Exercise 7.4 - Read a diffusive length**

$|x|=2\sqrt{\kappa t}$. It doubles when time is quadrupled; the characteristic width scales as $\sqrt t$.

**Solution to Exercise 7.5 - Find the aliased index**

Mode $-3$, because $7-(-3)=10$ and $e^{2\pi i10j/10}=1$.

**Solution to Exercise 7.6 - Connect the chapter results**

$c_2=c_{-2}=3/2$ and all others vanish, so the mean square is $9/2$. A DFT round trip recovers a finite sample vector, which is identical for aliased continuous modes by (7.10). The $n$th periodic diffusion coefficient decays at rate $\kappa(2\pi n/d)^2$; the zero mode is unchanged.

## Chapter 8

**Solution to Exercise 8.1 - Terminate a recurrence**

For the odd branch, $a_3=[1\cdot2-2]a_1/(3\cdot2)=0$, so it terminates at $a_1\mu$. Normalization gives $P(\mu)=\mu$.

**Solution to Exercise 8.2 - Generate the next degree**

$3P_3=5\mu P_2-2P_1=(15\mu^3-9\mu)/2$, so $P_3=(5\mu^3-3\mu)/2$.

**Solution to Exercise 8.3 - Recover a constant mode**

$f_0^0=C\int(4\pi)^{-1/2}d\Omega=C\sqrt{4\pi}$; dividing by $\sqrt{4\pi}$ gives $C$.

**Solution to Exercise 8.4 - Apply zonal averaging**

The integral of $e^{im\lambda}$ vanishes for nonzero integer $m$, so the mean is zero. An order-zero harmonic is unchanged.

**Solution to Exercise 8.5 - Connect the chapter results**

$\mu^2-1/3=(2/3)\sqrt{4\pi/5}Y_2^0$. Since its eigenvalue is $-6/R^2$, the zero-mean Poisson solution is $\psi=-AR^2(\mu^2-1/3)/6$. A real degree-$2$ field has $1+3+5=9$ independent real coefficients. A latitude-longitude periodic FFT assumes a rectangular periodic geometry; the sphere instead has a nonuniform area measure, coordinate poles, and associated Legendre latitude eigenfunctions.

## Chapter 9

**Solution to Exercise 9.1 - Diagonalize one linear term**

$a_j\prime=-j^2a_j$, so $a_j(t)=A_je^{-j^2t}$.

**Solution to Exercise 9.2 - Choose a quadrature order**

We need $2n-1\ge8$, hence $n\ge5$. Two nodes are exact only through degree three and do not suffice for $\mu^4$.

**Solution to Exercise 9.3 - A strict longitude bound**

$2n-1\ge12$ requires $n\ge7$, and $M>12$ requires $M\ge13$. With $M=12$, a frequency $3L=12$ can alias to zero.

**Solution to Exercise 9.4 - Separate stability from accuracy**

Backward Euler gives $1/11\approx0.091$, whereas the exact factor is $e^{-10}\approx4.54\times10^{-5}$. It is stable but poorly resolves this decay.

**Solution to Exercise 9.5 - Check the zero predictor**

It is one when truth has nonzero norm. For zero-norm truth the ratio is undefined, including the zero-versus-zero case.

**Solution to Exercise 9.6 - Connect the chapter results**

At $L=3$, sufficient linear sizes are $n=4$, $M=7$, and sufficient quadratic sizes are $n=5$, $M=10$. More grid points at a fixed cutoff improve quadrature but do not introduce additional retained harmonics. A stable implicit step may damp a resolved mode at the wrong rate if the step is too large; stability is a bound on growth, not an accuracy estimate.


**Solution to Exercise 9.7 - A conserved mean in exact Galerkin transport**

Test the Galerkin equation with the constant harmonic. The tendency is proportional to $-\int\mathbf u\cdot\nabla_sq\,d\Omega=-\int\nabla_s\cdot(q\mathbf u)d\Omega=0$. The closed-surface identity and nondivergence give zero. Approximate quadrature must reproduce that integral cancellation; residual orthogonality with an inexact inner product does not alone establish it.

## Chapter 10

**Solution to Exercise 10.1 - Check Coriolis work**

The cross product is perpendicular to $\mathbf u$, so its scalar product with $\mathbf u$ is zero. It changes direction but makes no contribution to $D|\mathbf u|^2/(2Dt)$.

**Solution to Exercise 10.2 - A one-degree inversion**

$\psi=-BR^2Y_2^0/6$, with units $\mathrm m^2\,s^{-1}$. Applying the Laplacian multiplies by $-6/R^2$ and recovers the original vorticity.

**Solution to Exercise 10.3 - Read a global frequency**

$\omega/\Omega=-2/(2\cdot3)=-1/3$. The period is $6\pi/\Omega$, with units seconds.

**Solution to Exercise 10.4 - Remove a source of false conservation**

No. The budget is $K\prime=-\langle\psi(F+D)\rangle_A$, whose value depends on how the sources correlate with the streamfunction.

**Solution to Exercise 10.5 - Connect the chapter results**

Equation (10.4) gives $\omega/k=-\beta/(k^2+l^2)<0$ when $k\ne0$ and $\beta>0$. In (10.3), $R^2\zeta$ has units $\mathrm m^2\,\mathrm s^{-1}$, as required for $\psi$. At fixed total $K$ concentrated at one degree, moving from degree $2$ to $4$ multiplies $Z$ by $4\cdot5/(2\cdot3)=10/3$. This is a comparison of two spectra, not an inviscid-transfer trajectory constrained by all invariants.

## Chapter 11

**Solution to Exercise 11.1 - Scale a random variable**

$\mathbb EY=3m_X+2$ and $\operatorname{Var}(Y)=9\sigma_X^2$, because $Y-\mathbb EY=3(X-m_X)$.

**Solution to Exercise 11.2 - Name the missing averaging assumption**

No. For $X(t)=B$, every trajectory keeps its realized $B$, while the ensemble mean is $\mathbb EB$. Equality requires an ergodic averaging property, not stationarity alone.

**Solution to Exercise 11.3 - Use negative correlation**

The ratio is $(1-r)/(1+r)=3$. It is a variance-equivalent quantity, not a literal count of independent observations.

**Solution to Exercise 11.4 - Invert a normalization**

$x=(s+\epsilon)z+m$. The scale $\epsilon$ must have the same dimensions as $x$ and $s$ so the sum and resulting dimensionless $z$ are meaningful.

**Solution to Exercise 11.5 - Connect the chapter results**

Overlap shares observations and usually creates dependence; independence requires evidence about the sampling process. The geometric-correlation approximation gives $900/9=100$ variance-equivalent samples. Predicting $m(X)$ removes the squared bias term in (11.3), but not the remaining conditional variance, which concerns information absent from $X$.

## Chapter 12

**Solution to Exercise 12.1 - A degree-two kernel**

Legendre orthogonality gives $\kappa_2=2\pi\int_{-1}^1P_2^2dt=4\pi/5$; every other degree vanishes.

**Solution to Exercise 12.2 - Distinguish invariance and equivariance**

The area integral is invariant. The identity field map is equivariant: rotating before or after the identity gives the same rotated field.

**Solution to Exercise 12.3 - Detect a reality violation**

It produces $i\cos x$, so it does not preserve reality. It needs $R(-1)=\overline{R(1)}=-i$.

**Solution to Exercise 12.4 - Change physical radius at fixed angular shape**

The decay time $R^2/(6\kappa)$ becomes four times larger. The initial area-mean square stays $4A^2/45$ because its angular shape and amplitude are unchanged.

**Solution to Exercise 12.5 - Connect the chapter results**

$k(t)=P_1(t)$ has only degree one and multiplier $\kappa_1=4\pi/3$ by (12.2). Arbitrary order-dependent coefficients generally fail to commute with rotations that mix orders. A claim about error needs the output variable, units or normalization, norm and spatial weights, target distribution, sampling unit, and comparison scale.


**Solution to Exercise 12.6 - Bound an integral operator**

At almost every $x$, $|\mathcal Kf(x)|^2\le(\int|K(x,y)|^2d\nu(y))\|f\|_2^2$. Integrating in $x$ gives $\|\mathcal Kf\|_2^2\le C_K^2\|f\|_2^2$. By linearity, $\|\mathcal Kf-\mathcal Kg\|_2\le C_K\|f-g\|_2$, a bound on the amplification of an input perturbation.
