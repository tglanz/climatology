# Rotating fluids, vorticity, and spectra {#ch-fluids}

## Mass, momentum, and rotating frames

**Result and motivation.** In a rotating frame the apparent Coriolis acceleration turns motion without doing work. Conservation and scale assumptions reduce the fluid equations to the horizontal models used in idealized geophysical dynamics. Sources: [@Vallis2006, Sections 1.2-1.3, 1.9-1.11, 2.1-2.3]; vector identities: [@ArfkenWeber2005, Sections 1.8-1.9].

Let $\rho$ be mass density, $p$ pressure, $\mathbf u$ velocity relative to a frame rotating at constant vector angular velocity $\boldsymbol\Omega$, and $\Phi$ effective gravitational potential per unit mass, including the centrifugal potential. For a constant-density incompressible Newtonian fluid with constant kinematic viscosity $\nu$ and other acceleration $\mathbf F$,

$$
\nabla\cdot\mathbf u=0,\qquad
\frac{D\mathbf u}{Dt}+2\boldsymbol\Omega\times\mathbf u
=-\frac1\rho\nabla p-\nabla\Phi+\nu\Delta\mathbf u+\mathbf F.
\tag{10.1}
$$

The viscous Laplacian form assumes these constitutive and incompressibility conditions; it is not the general compressible stress law. Pressure enforces the divergence constraint. A Newtonian fluid has stress proportional to strain rate. In a changing basis, the inertial derivative of a vector is its rotating derivative plus $\boldsymbol\Omega\times$ that vector. Applying this rule twice to position produces $2\boldsymbol\Omega\times\mathbf u$ and $\boldsymbol\Omega\times(\boldsymbol\Omega\times\mathbf x)$; the latter is absorbed in $\Phi$. Coriolis does no work since $\mathbf u\cdot(\boldsymbol\Omega\times\mathbf u)=0$.

For a shallow horizontal layer, the traditional horizontal Coriolis term uses the local vertical component $f=2\Omega\sin\varphi$, where $\Omega=|\boldsymbol\Omega|$. This approximation and the shallow geometry have physical limits; they do not follow from vector algebra alone. Near reference latitude $\varphi_0$, a tangent plane with east coordinate $x$ and north coordinate $y$ gives $f\approx f_0+\beta y$, where $f_0=2\Omega\sin\varphi_0$ and $\beta=2\Omega\cos\varphi_0/R$. This is the beta-plane approximation. An $f$-plane keeps only $f_0$.

## Streamfunction and the barotropic vorticity equation

**Result and motivation.** In a constant-depth nondivergent layer, absolute vertical vorticity is materially conserved in the inviscid unforced limit. Streamfunction converts the velocity-vorticity relation into a Poisson inversion. Sources: [@Vallis2006, Sections 4.1-4.6, 5.1]; geometry follows Chapter 3.

Barotropic means pressure is a function of density alone, so $\nabla\rho\times\nabla p=0$. A constant-density, constant-depth nondivergent layer is a particular model reduction; the word alone does not imply every one of those assumptions. In three dimensions the inviscid vorticity equation includes stretching of absolute vorticity. In a shallow layer its vertical component is
$D(\zeta+f)/Dt=-(\zeta+f)\nabla_s\cdot\mathbf u$, subject to the horizontal-model assumptions. If depth changes, stretching matters and potential vorticity $(\zeta+f)/h$ is conserved instead, with $h$ layer thickness. We now take constant $h$ and zero divergence.

Define absolute vorticity $q=\zeta+f$, forcing $F$ and dissipation $D$ in vorticity units per time ($\mathrm s^{-2}$). With the streamfunction convention (3.7),

$$
\partial_t\zeta+J_s(\psi,\zeta+f)=F+D,
\qquad \zeta=\Delta_s\psi,
\qquad
J_s(a,b)=\frac{\partial_\lambda a\,\partial_\varphi b-
\partial_\varphi a\,\partial_\lambda b}{R^2\cos\varphi}.
\tag{10.2}
$$

Indeed, $\mathbf u\cdot\nabla_sb=u\partial_\lambda b/(R\cos\varphi)+v\partial_\varphi b/R=J_s(\psi,b)$. This fixes the sign rather than choosing it from memory. Time evolution advances $\zeta$; elliptic inversion supplies $\psi$ and then velocity. Since $\int\Delta_s\psi=0$, a globally smooth relative-vorticity field has zero area mean, and forcing must respect this compatibility. Fix $\psi_0^0=0$; then

$$
\psi_\ell^m=-\frac{R^2}{\ell(\ell+1)}\zeta_\ell^m,\quad\ell\ge1.
\tag{10.3}
$$

On a beta-plane, $u=-\psi_y$, $v=\psi_x$, $\zeta=\Delta\psi$, and $J(a,b)=a_xb_y-a_yb_x$. Equation (10.2) becomes $\zeta_t+J(\psi,\zeta)+\beta\psi_x=F+D$. Units check: $[J_s(\psi,q)]=[\psi][q]/R^2=\mathrm s^{-2}$.

## Rossby waves and physical propagation

**Result and motivation.** A parcel displaced across a planetary-vorticity gradient changes relative vorticity. This coupling supports dispersive Rossby waves. Sources: [@Vallis2006, Sections 5.7-5.8].

Linearize the unforced beta-plane equation about rest by neglecting the quadratic term $J(\psi,\Delta\psi)$. For a wave $\psi=Ae^{i(kx+ly-\omega t)}$, where $k,l$ are east and north angular wavenumbers, respectively,

$$
\partial_t\Delta\psi+\beta\partial_x\psi=0
\quad\Longrightarrow\quad
\omega=-\frac{\beta k}{k^2+l^2}.
\tag{10.4}
$$

Substitution gives $i\omega(k^2+l^2)+i\beta k=0$. For $\beta>0$ the zonal phase speed $\omega/k$ is negative whenever $k\ne0$: crests propagate westward relative to the resting background. The zonal group speed is $\partial\omega/\partial k=\beta(k^2-l^2)/(k^2+l^2)^2$, which can have either sign. Phase and energy-envelope propagation must not be conflated. A uniform eastward background speed $U$ adds a Doppler shift $Uk$ to $\omega$.

On the full sphere, $J_s(\psi,f)=2\Omega\partial_\lambda\psi/R^2$. Substituting $\psi=A Y_\ell^m e^{-i\omega t}$ into the linearized equation yields

$$
\omega=-\frac{2\Omega m}{\ell(\ell+1)},\qquad \ell\ge1.
\tag{10.5}
$$

These are global barotropic Rossby modes about rest. The spherical eigenvalue replaces the planar squared wavenumber. The linear calculation neglects finite-amplitude interactions; it does not assert that every forced turbulent field is a superposition of independently evolving waves.

## Energy, enstrophy, and scale spectra

**Result and motivation.** Conservation identities provide physical diagnostics, while spherical Parseval identities locate variance and kinetic energy by angular scale. Sources: [@Vallis2006, Sections 4.5, 8.1-8.3]; spectral formulas are derived from [@ArfkenWeber2005, Sections 12.6, 12.11].

Use $\langle a\rangle_A=(4\pi R^2)^{-1}\int a\,dA$. For smooth inviscid unforced nondivergent flow on a closed sphere with time-independent $f$, define area-mean kinetic energy $K=\frac12\langle|\mathbf u|^2\rangle_A$ and absolute enstrophy $Q=\frac12\langle q^2\rangle_A$. "Enstrophy" means one half of mean squared vorticity; specify whether that vorticity is relative or absolute. Incompressibility gives

$$
\frac{d}{dt}\langle C(q)\rangle_A
=-\langle\mathbf u\cdot\nabla_s C(q)\rangle_A=0
\tag{10.6}
$$

for differentiable $C$ for which the integral exists. Taking $C(q)=q^2/2$ conserves $Q$. The identity uses a divergence theorem on the closed surface. Energy satisfies $K=-\frac12\langle\psi\zeta\rangle_A$ by (3.8). Self-adjointness gives $K'=-\langle\psi\zeta_t\rangle_A=\langle\psi J_s(\psi,q)\rangle_A=0$, because integration by parts moves advection onto $\psi$ and $J_s(\psi,\psi)=0$. With forcing and dissipation, $K'=-\langle\psi(F+D)\rangle_A$ instead.

Expand $\psi$ using (8.7). Define relative enstrophy $Z=\frac12\langle\zeta^2\rangle_A$ and its degree spectrum $Z_\ell$, and define $K_\ell$ analogously. Integration by parts and Parseval give

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

Thus $[K]=\mathrm m^2\,\mathrm s^{-2}$ and $[Z]=\mathrm s^{-2}$. These are global means; area-integrated quantities have another factor $4\pi R^2$. A coefficient sum for a real field includes both positive and negative orders, or equivalent multiplicity weights if only nonnegative orders are stored. Missing those weights changes the spectrum. These spectra use relative vorticity, whereas (10.6) is stated for absolute vorticity.

Spectra describe how a quadratic quantity is distributed, not the direction of its transfer. A cascade claim requires a scale-transfer budget or other evidence. Likewise, no conservation law alone fixes a turbulent spectral slope or a jet count. Zonal averaging splits a field into its mean and departure, $a=\overline a+a'$ with $\overline{a'}=0$. Then $\overline{uv}=\overline u\,\overline v+\overline{u'v'}$; the covariance term represents transport by correlated departures and cannot generally be reconstructed from the two means alone.

## Chapter summary and self-test

**Main results and terms.** Coriolis acceleration follows from rotating-frame differentiation and does no work. A shallow constant-depth nondivergent model materially conserves absolute vorticity. Streamfunction and vorticity are linked by spherical Poisson inversion. The beta effect produces the dispersions (10.4)-(10.5); phase and group velocities differ. Smooth inviscid unforced flow conserves kinetic energy and absolute-vorticity functionals. Parseval yields degree spectra with explicit radius and area normalization. Spectral shape alone does not establish a cascade.

**Self-test.** Check the sign of a Rossby wave's phase speed for positive $\beta$. Derive the units in (10.3). What happens to $K_\ell$ and $Z_\ell$ when all streamfunction power moves from degree $\ell=2$ to degree $\ell=4$ while total $K$ is held fixed?
