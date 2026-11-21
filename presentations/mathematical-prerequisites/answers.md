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
