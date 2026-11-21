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
