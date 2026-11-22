# Instructor solutions

These checked solutions are author/editor material for the physical-prerequisites textbook. They are deliberately separate from the student PDF and Markdown. Exercise identifiers follow the companion chapter numbers.

# Kinematics and mathematical language

## Solution to Exercise 1.1 - A steady gradient (straightforward)

The trajectory is $X_x=x_0+Ut$, so $b(\mathbf{X}(t))=b_0+Gx_0+GUt$ and $Db/Dt=GU$. Steadiness sets only the local derivative to zero; material conservation fails when $GU\ne0$.

## Solution to Exercise 1.2 - Flux through a cube (intermediate)

Divergence is $3c$, so its volume integral is $3cL^3$. Each outward face has normal component $cL/2$ and area $L^2$. Adding all six face fluxes gives $6(cL/2)L^2=3cL^3$, confirming the divergence theorem. If $\mathbf{a}$ has velocity units, both sides have units $\mathrm{m^3\,s^{-1}}$.

## Solution to Exercise 1.3 - Uniform expansion (intermediate)

Divergence is $3c$. The transport rule gives $dV/dt=3cV$, hence $V(t)=V_0e^{3ct}$. This agrees with each linear dimension increasing as $e^{ct}$.

# Mass, forces, and the momentum equation

## Solution to Exercise 2.1 - Advected nonuniform density (conceptual)

Yes. Continuity and $\nabla\cdot\mathbf{v}=0$ give $D\rho/Dt=0$, allowing different parcels to retain different densities. Spatial homogeneity is an additional condition.

## Solution to Exercise 2.2 - Linear pressure gradient (straightforward)

The initial acceleration is $-(G_p/\rho_0)\hat{\mathbf{x}}$. Since $[G_p]=\mathrm{Pa\,m^{-1}}=\mathrm{kg\,m^{-2}\,s^{-2}}$, division by $\mathrm{kg\,m^{-3}}$ gives $\mathrm{m\,s^{-2}}$.

## Solution to Exercise 2.3 - What boundary terms were removed? (model evaluation)

Periodic opposite faces have identical fields and opposite normals, so their surface fluxes cancel. An open boundary can transport pressure work and kinetic energy; the cancellations need not hold there.

# Rotation and large-scale balances

## Solution to Exercise 3.1 - Inertial deflection (straightforward)

Initially $\dot v=-f_0U>0$, so it turns northward. The identity $u^2+v^2=U^2$ keeps its speed fixed in either hemisphere.

## Solution to Exercise 3.2 - When geostrophy fails as an ordering (intermediate)

Because $f_0=2\Omega\sin\phi_0\to0$, $\mathrm{Ro}=U/(|f_0|L)$ diverges rather than remaining small. Recovering $u_g,v_g$ requires division by $f_0$ and is invalid at $f_0=0$.

## Solution to Exercise 3.3 - A linear Boussinesq profile (intermediate)

Here $d\bar\rho/dz=-\gamma$, so $N^2=g\gamma/\rho_0>0$. The displacement equation is $\ddot\eta+N^2\eta=0$ and its period is $2\pi/N$.

# Vorticity and circulation

## Solution to Exercise 4.1 - A square in uniform shear (intermediate)

The vertical vorticity is $-c$, so Stokes gives $\Gamma=-cL^2$. Directly, the two horizontal sides differ in eastward velocity by $cL$, and their opposite traversal directions give the same $-cL^2$.

## Solution to Exercise 4.2 - Which Kelvin hypothesis fails? (model evaluation)

No. The pressure acceleration has curl $\rho^{-2}\nabla\rho\times\nabla p\ne0$ and cannot generally be written as one scalar gradient. This invalidates the closed-loop gradient cancellation used in (4.3).

## Solution to Exercise 4.3 - A northward material patch (intermediate)

Absolute circulation and fixed area conserve $\zeta+f$. Since $\Delta f=\beta\Delta y$, the relative change is $\Delta\zeta=-\beta\Delta y$.

# A shallow layer and the barotropic reduction

## Solution to Exercise 5.1 - Thickness and latitude change together (intermediate)

Equating $(\zeta_1+f_1)/h_1=(\zeta_2+f_2)/h_2$ gives $\zeta_2=(h_2/h_1)(\zeta_1+f_1)-f_2$. Thickness change and latitude change therefore contribute separately.

## Solution to Exercise 5.2 - A rigid lid above topography (model evaluation)

No. Thickness varies with horizontal position, and a column moving over topography can change $h$. Continuity gives $D_hh/Dt=-h\nabla_h\cdot\mathbf{u}$, so a rigid lid does not by itself force horizontal divergence to zero.

## Solution to Exercise 5.3 - Relative vorticity on a beta-plane (straightforward)

The BVE gives $D_h\zeta/Dt=-D_hf/Dt=-\beta v$. The local time derivative of the fixed planetary field vanishes, but the parcel crosses its spatial gradient.

# The BVE on a rotating sphere

## Solution to Exercise 6.1 - Why a constant cannot be relative vorticity (conceptual)

No for vorticity: its integral would be $4\pi a^2c\ne0$, violating (6.5). Yes for streamfunction: a constant has zero gradient and Laplacian and only changes its gauge.

## Solution to Exercise 6.2 - Axisymmetric streamfunction (intermediate)

Differentiation gives $u=U_s\cos\phi$ and $v=0$. The spherical curl is $\zeta=-(a\cos\phi)^{-1}\partial_\phi(U_s\cos^2\phi)=2U_s\sin\phi/a$.

## Solution to Exercise 6.3 - Rotation, mean current, and wave phase (intermediate)

Stationary phase requires $U=\beta/(k_x^2+k_y^2)$. Doubling both wavenumbers multiplies $K^2$ by four, so the intrinsic zonal phase speed $-\beta/K^2$ becomes one quarter of its previous value.

# Invariants, turbulence, and eddy-driven flow

## Solution to Exercise 7.1 - Why absolute-vorticity moments? (conceptual)

The advected scalar is $Q=\zeta+f$, so $D_hG(Q)/Dt=G'(Q)D_hQ/Dt=0$. Relative vorticity changes when parcels cross $f$ gradients, and an arbitrary function of it need not satisfy that transport law.

## Solution to Exercise 7.2 - A different three-scale exchange (intermediate)

Equation (7.3) gives $\delta E_1=4\Delta/5$ and $\delta E_3=\Delta/5$. Enstrophy gains are $(4/5)\kappa_0^2\Delta$ and $(16/5)\kappa_0^2\Delta$, adding to $4\kappa_0^2\Delta$, the middle-scale loss.

## Solution to Exercise 7.3 - Momentum-flux convergence (straightforward)

Its northward derivative is $-C$, so the convergence is $-\partial_y\overline{u'v'}=C>0$. The mean eastward current accelerates at rate $C$, whose units are $\mathrm{m\,s^{-2}}$.

# Spherical harmonics, inversion, and dissipation

## Solution to Exercise 8.1 - A degree-one coefficient (straightforward)

Equation (8.3) gives $\widehat\psi_1^0=-a^2A_\zeta/2$. Equation (8.4) gives $E=a^4A_\zeta^2/4$ and $Z=a^2A_\zeta^2/2$, so $Z/E=2/a^2$.

## Solution to Exercise 8.2 - A smaller transform grid (intermediate)

The inequalities give $N_\lambda\geq3(21)+1=64$ and $N_\phi\geq\lceil64/2\rceil=32$. Thus 64 longitudes and 32 Gaussian latitudes meet those specific quadratic conditions; they do not guarantee temporal stability or arbitrary nonlinear accuracy.

## Solution to Exercise 8.3 - Amplitude versus enstrophy decay (intermediate)

The amplitude follows $e^{-\gamma t}$, giving $t_A=\log2/\gamma$. Enstrophy is proportional to its squared amplitude and follows $e^{-2\gamma t}$, giving $t_Z=\log2/(2\gamma)$.

# Stochastic stirring and the closed forced model

## Solution to Exercise 9.1 - Forcing spinup from zero (intermediate)

The variance formula gives $V_n/\sigma_s^2=1-\alpha^{2n}=1-e^{-2t/\tau}$. The threshold is reached or exceeded when $n\Delta t\geq\tau$. Thus the first step is $n_*=\lceil\tau/\Delta t\rceil$, at time $t_*=\Delta t\lceil\tau/\Delta t\rceil$. The exponential curve reaches the threshold at $t=\tau$, but that is a sampled time only when $\tau/\Delta t$ is an integer.

## Solution to Exercise 9.2 - Uniform versus unit-variance noise (straightforward)

The innovation variance is reduced by $1/3$, so stationary variance is $\sigma_s^2/3$. Replacing $\eta^n$ by $\sqrt3\eta^n$ restores unit innovation variance and stationary variance $\sigma_s^2$.

## Solution to Exercise 9.3 - An unobserved stirring state (model evaluation)

The same vorticity gives the same inversion, velocity, advection, and dissipation. Subtracting the two copies of (9.1) gives $\partial_t\zeta_1-\partial_t\zeta_2=S_1-S_2$. The current stirring state is information needed for the conditional future law.

# Relating the theory to this repository

## Solution to Exercise 10.1 - Comparing two drag settings (straightforward)

Both times halve: amplitude decay has time $1/r$, while energy decay from drag alone has time $1/(2r)$. This statement concerns the sink alone, not the response times of the coupled forced flow.

## Solution to Exercise 10.2 - The diagnostic called pv (conceptual)

In this code it is $\zeta+f$, normal absolute vorticity. It is proportional to layer potential vorticity only when thickness is a fixed constant; the diagnostic does not carry a variable layer thickness.

## Solution to Exercise 10.3 - Daily averages as dynamical states (model evaluation)

A daily mean omits within-day structure, and nonlinear advection does not commute with averaging. The present stirring state and random-generator state are also omitted. Reproduction additionally requires the actual configuration, instantaneous initial state, code and patches, and the discrete time-step state.
