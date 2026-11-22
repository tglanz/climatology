# Rotating fluids, vorticity, and spectra {#ch-fluids}

How do the mathematical operators become a model of rotating horizontal flow? We identify the physical assumptions that reduce momentum dynamics to vorticity transport, then derive Rossby-wave frequencies and conserved quadratic quantities. The model determines which deductions apply; the spherical geometry fixes their signs and scale factors.

## Mass, momentum, and rotating frames

In a rotating frame the apparent Coriolis acceleration turns motion without doing work. Conservation and scale assumptions reduce the fluid equations to the horizontal models used in idealized geophysical dynamics. Sources: [@Vallis2006, Sections 1.2-1.3, 1.9-1.11, 2.1-2.3]; vector identities: [@ArfkenWeber2005, Sections 1.8-1.9].

::: {.tb-definition #obj-10-1}
**Definition 10.1 - Fluid variables and rotating coordinates**

Let $\rho$ be mass density, $p$ pressure, $\mathbf u$ velocity relative to a frame rotating at constant vector angular velocity $\boldsymbol\Omega$, and $\Phi$ effective gravitational potential per unit mass, including the centrifugal potential.
:::

::: {.tb-model #obj-10-2}
**Model 10.2 - Constant-density incompressible Newtonian fluid**

Assume constant density $\rho>0$, constant kinematic viscosity $\nu$, and a frame rotating with constant $\boldsymbol\Omega$. A Newtonian constitutive relation makes viscous stress proportional to strain rate; under these assumptions its acceleration is $\nu\Delta\mathbf u$. Other prescribed acceleration is $\mathbf F$.
:::

::: {.tb-law #obj-10-3}
**Law 10.3 - Mass conservation and Newton's second law**

A material parcel conserves mass, and its inertial acceleration equals the total applied force per unit mass. Pressure and gravity supply their respective force densities. The Newtonian viscous relation is an adopted constitutive model, rather than a theorem of vector calculus [@Vallis2006, Sections 1.2-1.3].
:::

::: {.tb-result #obj-10-4}
**Result 10.4 - Momentum in a uniformly rotating frame**

For the preceding model, with centrifugal acceleration absorbed into the effective potential $\Phi$, the governing equations are

$$
\nabla\cdot\mathbf u=0,\qquad
\frac{D\mathbf u}{Dt}+2\boldsymbol\Omega\times\mathbf u
=-\frac1\rho\nabla p-\nabla\Phi+\nu\Delta\mathbf u+\mathbf F.
\tag{10.1}
$$
:::

::: {.tb-proof}
**Derivation of Result 10.4**

The viscous Laplacian form assumes these constitutive and incompressibility conditions; it is not the general compressible stress law. Pressure enforces the divergence constraint. A Newtonian fluid has stress proportional to strain rate. In a changing basis, the inertial derivative of a vector is its rotating derivative plus $\boldsymbol\Omega\times$ that vector. Applying this rule twice to position produces $2\boldsymbol\Omega\times\mathbf u$ and $\boldsymbol\Omega\times(\boldsymbol\Omega\times\mathbf x)$; the latter is absorbed in $\Phi$. Coriolis does no work since $\mathbf u\cdot(\boldsymbol\Omega\times\mathbf u)=0$.
:::

::: {.tb-model #obj-10-5}
**Model 10.5 - Traditional Coriolis parameter and tangent-plane limits**

For a shallow horizontal layer, the traditional horizontal Coriolis term uses the local vertical component $f=2\Omega\sin\varphi$, where $\Omega=|\boldsymbol\Omega|$. This approximation and the shallow geometry have physical limits; they do not follow from vector algebra alone. Near reference latitude $\varphi_0$, a tangent plane with east coordinate $x$ and north coordinate $y$ gives $f\approx f_0+\beta y$, where $f_0=2\Omega\sin\varphi_0$ and $\beta=2\Omega\cos\varphi_0/R$. This is the beta-plane approximation. An $f$-plane keeps only $f_0$.
:::

::: {.tb-exercise #ex-10-1}
**Exercise 10.1 - Check Coriolis work**

*Conceptual proof.* For an arbitrary velocity $\mathbf u$ and constant $\boldsymbol\Omega$, show that $2\boldsymbol\Omega\times\mathbf u$ cannot change kinetic energy directly.
:::

## Streamfunction and the barotropic vorticity equation

In a constant-depth nondivergent layer, absolute vertical vorticity is materially conserved in the inviscid unforced limit. Streamfunction converts the velocity-vorticity relation into a Poisson inversion. Sources: [@Vallis2006, Sections 4.1-4.6, 5.1]; geometry follows Chapter 3.

::: {.tb-definition #obj-10-6}
**Definition 10.6 - Barotropic pressure relation**

Following Vallis, a barotropic fluid has density determined by pressure alone, $\rho=\rho(p)$, including the special case $\rho=\mathrm{constant}$ [@Vallis2006, Section 1.3, p. 15]. For differentiable relations this makes $\nabla\rho\times\nabla p=0$. An invertible relation can also be written $p=p(\rho)$; constant density removes the baroclinic source even when pressure varies in space.
:::

::: {.tb-model #obj-10-7}
**Model 10.7 - Shallow constant-depth nondivergent layer**

A constant-density, constant-depth nondivergent layer is a particular model reduction; the word alone does not imply every one of those assumptions. In three dimensions the inviscid vorticity equation includes stretching of absolute vorticity. In a shallow layer its vertical component is
$D(\zeta+f)/Dt=-(\zeta+f)\nabla_s\cdot\mathbf u$, subject to the horizontal-model assumptions. If depth changes, stretching matters and potential vorticity $(\zeta+f)/h$ is conserved instead, with $h$ layer thickness. We now take constant $h$ and zero divergence.
:::

::: {.tb-definition #obj-10-8}
**Definition 10.8 - Absolute vorticity and its sources**

Define absolute vorticity $q=\zeta+f$, forcing $F$ and dissipation $D$ in vorticity units per time ($\mathrm s^{-2}$).
:::

::: {.tb-result #obj-10-9}
**Result 10.9 - Forced and dissipative barotropic vorticity equation**

In the shallow constant-depth model, with the streamfunction convention (3.7) and a stationary planetary $f$,

$$
\partial_t\zeta+J_s(\psi,\zeta+f)=F+D,
\qquad \zeta=\Delta_s\psi,
\qquad
J_s(a,b)=\frac{\partial_\lambda a\,\partial_\varphi b-
\partial_\varphi a\,\partial_\lambda b}{R^2\cos\varphi}.
\tag{10.2}
$$
:::

::: {.tb-proof}
**Derivation of Result 10.9**

Take the vertical curl of horizontal momentum. The barotropic pressure term has no baroclinic curl source. The shallow absolute-vorticity stretching term is $-(\zeta+f)\nabla_s\cdot\mathbf u$, which vanishes under nondivergence. The remaining transport is $\partial_t\zeta+\mathbf u\cdot\nabla_s(\zeta+f)$. Substitution of (3.7) gives $\mathbf u\cdot\nabla_sb=(\psi_\lambda b_\varphi-\psi_\varphi b_\lambda)/(R^2\cos\varphi)$, fixing the sign in (10.2).
:::

::: {.tb-result #obj-10-10}
**Result 10.10 - Recovering streamfunction from relative vorticity**

For a smooth relative-vorticity field with zero area mean, choose $\psi_0^0=0$. Harmonic inversion gives

$$
\psi_\ell^m=-\frac{R^2}{\ell(\ell+1)}\zeta_\ell^m,\quad\ell\ge1.
\tag{10.3}
$$
:::

::: {.tb-proof}
**Proof of Result 10.10**

The spherical Laplacian has eigenvalue $-\ell(\ell+1)/R^2$ at degree $\ell$. Divide each nonzero-degree coefficient of $\zeta=\Delta_s\psi$ by that eigenvalue. The omitted constant mode explains both the zero-mean compatibility condition and the freedom to choose the mean of $\psi$. $\square$
:::

::: {.tb-example #obj-10-11}
**Example 10.11 - The beta-plane form and dimensional check**

On a beta-plane, $u=-\psi_y$, $v=\psi_x$, $\zeta=\Delta\psi$, and $J(a,b)=a_xb_y-a_yb_x$. Equation (10.2) becomes $\zeta_t+J(\psi,\zeta)+\beta\psi_x=F+D$. Units check: $[J_s(\psi,q)]=[\psi][q]/R^2=\mathrm s^{-2}$.
:::

::: {.tb-exercise #ex-10-2}
**Exercise 10.2 - A one-degree inversion**

*Application.* If $\zeta=B Y_2^0$ with $[B]=\mathrm s^{-1}$, find the zero-mean $\psi$ and its units.
:::

## Rossby waves and physical propagation

A parcel displaced across a planetary-vorticity gradient changes relative vorticity. This coupling supports dispersive Rossby waves. Sources: [@Vallis2006, Sections 5.7-5.8].

::: {.tb-model #obj-10-12}
**Model 10.12 - Small barotropic waves about rest**

Set both forcing and dissipation to zero, $F=D=0$, and linearize the beta-plane equation about rest by neglecting the quadratic term $J(\psi,\Delta\psi)$. The omitted term is quadratic in disturbance amplitude.
:::

::: {.tb-definition #obj-10-13}
**Definition 10.13 - Planar wave parameters**

Write $\psi=Ae^{i(kx+ly-\omega t)}$, where $k,l$ are eastward and northward angular wavenumbers and $\omega$ is angular frequency.
:::

::: {.tb-result #obj-10-14}
**Result 10.14 - Beta-plane Rossby dispersion**

For a nonzero wave with $k^2+l^2>0$ in the linear beta-plane model about rest with $F=D=0$,

$$
\partial_t\Delta\psi+\beta\partial_x\psi=0
\quad\Longrightarrow\quad
\omega=-\frac{\beta k}{k^2+l^2}.
\tag{10.4}
$$
:::

::: {.tb-proof}
**Derivation of Result 10.14**

Substitution gives $i\omega(k^2+l^2)+i\beta k=0$. For $\beta>0$ the zonal phase speed $\omega/k$ is negative whenever $k\ne0$: crests propagate westward relative to the resting background. The zonal group speed is $\partial\omega/\partial k=\beta(k^2-l^2)/(k^2+l^2)^2$, which can have either sign. Phase and energy-envelope propagation must not be conflated. A uniform eastward background speed $U$ adds a Doppler shift $Uk$ to $\omega$.
:::

::: {.tb-result #obj-10-15}
**Result 10.15 - Spherical barotropic Rossby frequencies**

For the corresponding linearization about rest on the whole sphere, with $F=D=0$ and $f=2\Omega\sin\varphi$, the mode $\psi=A Y_\ell^m e^{-i\omega t}$ has

$$
\omega=-\frac{2\Omega m}{\ell(\ell+1)},\qquad \ell\ge1.
\tag{10.5}
$$
:::

::: {.tb-proof}
**Derivation of Result 10.15**

On the full sphere, $J_s(\psi,f)=2\Omega\partial_\lambda\psi/R^2$. Substituting $\psi=A Y_\ell^m e^{-i\omega t}$ into the linearized equation gives the modal relation. The resulting coefficient equation is $i\ell(\ell+1)\omega+2i\Omega m=0$.
:::

::: {.tb-remark #obj-10-16}
**Remark 10.16 - The scope of linear modal propagation**

These are global barotropic Rossby modes about rest. The spherical eigenvalue replaces the planar squared wavenumber. The linear calculation neglects finite-amplitude interactions; it does not assert that every forced turbulent field is a superposition of independently evolving waves.
:::

::: {.tb-exercise #ex-10-3}
**Exercise 10.3 - Read a global frequency**

*Calculation and units.* For $\ell=2$, $m=1$, determine $\omega/\Omega$. If $\Omega$ has units $\mathrm s^{-1}$, what are the units of the period $2\pi/|\omega|$?
:::

## Energy, enstrophy, and scale spectra

Conservation identities provide physical diagnostics, while spherical Parseval identities locate variance and kinetic energy by angular scale. Sources: [@Vallis2006, Sections 4.5, 8.1-8.3]; spectral formulas are derived from [@ArfkenWeber2005, Sections 12.6, 12.11].

::: {.tb-assumption #obj-10-17}
**Assumption 10.17 - Closed, inviscid, unforced nondivergent flow**

Take smooth flow on a closed sphere, zero forcing and dissipation, zero horizontal divergence, and time-independent planetary $f$.
:::

::: {.tb-definition #obj-10-18}
**Definition 10.18 - Area-mean energy and absolute enstrophy**

Use $\langle a\rangle_A=(4\pi R^2)^{-1}\int a\,dA$. Define $K=\tfrac12\langle|\mathbf u|^2\rangle_A$ and $Q=\tfrac12\langle q^2\rangle_A$. Enstrophy means half the mean squared vorticity; specify relative or absolute vorticity.
:::

::: {.tb-result #obj-10-19}
**Result 10.19 - Material invariants and kinetic-energy conservation**

Under the preceding assumptions, every differentiable $C(q)$ with finite integral obeys

$$
\frac{d}{dt}\langle C(q)\rangle_A
=-\langle\mathbf u\cdot\nabla_s C(q)\rangle_A=0
\tag{10.6}
$$

In particular $Q$ is constant. Kinetic energy $K$ is also constant.
:::

::: {.tb-proof}
**Derivation of Result 10.19**

Because $Dq/Dt=0$, the chain rule gives $\partial_tC(q)=-\mathbf u\cdot\nabla_sC(q)$. Rewrite this as a divergence using nondivergence and integrate on the closed sphere to obtain (10.6).

For energy, integration by parts gives $K=-\tfrac12\langle\psi\zeta\rangle_A$. Self-adjointness of $\Delta_s$ makes $K\prime=-\langle\psi\zeta_t\rangle_A=\langle\psi J_s(\psi,q)\rangle_A$. Move advection onto $\psi$ under the integral; its derivative along $\mathbf u$ is $J_s(\psi,\psi)=0$. Thus $K\prime=0$. With sources the same calculation instead gives $K\prime=-\langle\psi(F+D)\rangle_A$.
:::

::: {.tb-definition #obj-10-20}
**Definition 10.20 - Relative-enstrophy and kinetic-energy spectra**

Expand $\psi$ using (8.7). Define relative enstrophy $Z=\frac12\langle\zeta^2\rangle_A$ and its degree spectrum $Z_\ell$, and define $K_\ell$ analogously. The spectra group coefficients by degree.
:::

::: {.tb-result #obj-10-21}
**Result 10.21 - Spectral weighting by angular scale**

For a smooth real streamfunction expanded in the convention (8.7), the area-mean spectra are

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
:::

::: {.tb-proof}
**Proof of Result 10.21**

Green's identity gives $K=-\tfrac12\langle\psi\Delta_s\psi\rangle_A$; each harmonic contributes its eigenvalue $-\ell(\ell+1)/R^2$. For $Z$, square the vorticity coefficient $-\ell(\ell+1)\psi_\ell^m/R^2$. Parseval and $\langle a\rangle_A=(4\pi)^{-1}\int a\,d\Omega$ give the factors in (10.7). $\square$
:::

::: {.tb-remark #obj-10-22}
**Remark 10.22 - Units, normalization, and order multiplicities**

Thus $[K]=\mathrm m^2\,\mathrm s^{-2}$ and $[Z]=\mathrm s^{-2}$. These are global means; area-integrated quantities have another factor $4\pi R^2$. A coefficient sum for a real field includes both positive and negative orders, or equivalent multiplicity weights if only nonnegative orders are stored. Missing those weights changes the spectrum. These spectra use relative vorticity, whereas (10.6) is stated for absolute vorticity.
:::

::: {.tb-remark #obj-10-23}
**Remark 10.23 - A spectrum is not a transfer budget**

Spectra describe how a quadratic quantity is distributed, not the direction of its transfer. A cascade claim requires a scale-transfer budget or other evidence. Likewise, no conservation law alone fixes a turbulent spectral slope or a jet count. Zonal averaging splits a field into its mean and departure, $a=\overline a+a'$ with $\overline{a'}=0$. Then $\overline{uv}=\overline u\,\overline v+\overline{u'v'}$; the covariance term represents transport by correlated departures and cannot generally be reconstructed from the two means alone.
:::

::: {.tb-exercise #ex-10-4}
**Exercise 10.4 - Remove a source of false conservation**

*Model evaluation.* If forcing and dissipation are restored, is $K\prime$ still necessarily zero? Give its budget in terms of $\psi,F,D$.
:::

## Chapter summary

Coriolis acceleration follows from rotating-frame differentiation and does no work. A shallow constant-depth nondivergent model materially conserves absolute vorticity. Streamfunction and vorticity are linked by spherical Poisson inversion. The beta effect produces the dispersions (10.4)-(10.5); phase and group velocities differ. Smooth inviscid unforced flow conserves kinetic energy and absolute-vorticity functionals. Parseval yields degree spectra with explicit radius and area normalization. Spectral shape alone does not establish a cascade.

::: {.tb-exercise #ex-10-5}
**Exercise 10.5 - Connect the chapter results**

*Synthesis.* Check the sign of a Rossby wave's phase speed for positive $\beta$. Derive the units in (10.3). What happens to $K_\ell$ and $Z_\ell$ when all streamfunction power moves from degree $\ell=2$ to degree $\ell=4$ while total $K$ is held fixed?
:::
