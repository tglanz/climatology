---
title: "Physical prerequisites for barotropic dynamics"
subtitle: "From continuum mechanics to the stochastically stirred vorticity equation"
date: "21 November 2026"
lang: en-US
---

<!-- markdown-toc:start -->

**Contents**

1. [Kinematics and mathematical language](#kinematics-and-mathematical-language)
2. [Mass, forces, and the momentum equation](#mass-forces-and-the-momentum-equation)
3. [Rotation and large-scale balances](#rotation-and-large-scale-balances)
4. [Vorticity and circulation](#vorticity-and-circulation)
5. [A shallow layer and the barotropic reduction](#a-shallow-layer-and-the-barotropic-reduction)
6. [The BVE on a rotating sphere](#the-bve-on-a-rotating-sphere)
7. [Invariants, turbulence, and eddy-driven flow](#invariants-turbulence-and-eddy-driven-flow)
8. [Spherical harmonics, inversion, and dissipation](#spherical-harmonics-inversion-and-dissipation)
9. [Stochastic stirring and the closed forced model](#stochastic-stirring-and-the-closed-forced-model)
10. [Relating the theory to this repository](#relating-the-theory-to-this-repository)

<!-- markdown-toc:end -->

# Reading map {.unnumbered}

The target is to derive, interpret, and close the forced barotropic vorticity equation (BVE) on a rotating sphere. The path is conservation of mass and momentum, rotating frames, vorticity and circulation, a constant-depth layer, spherical geometry, invariants, spectral inversion, and stochastic forcing. Basic differentiation, integration, linear algebra, and Newton's second law are assumed. The fluid mechanics, differential operators, and probability used below are defined where needed.

The main sources are the **2006 first edition** of Vallis [@Vallis2006], the supplied unsigned notes *The barotropic vorticity equation* [@BarotropicNotes], and **Arfken and Weber, sixth edition (2005)** [@ArfkenWeber2005]. Section and page locators refer to printed numbering, not PDF viewer indices. Their arguments are reconstructed here, rather than quoted. The final forcing construction also uses the locally supplied Vallis et al. **2004** paper [@VallisEtAl2004]; its filename contains `2024`, but its title page and journal volume identify 2004. The three main sources alone do not specify that stirring process.

All fields are smooth enough for the differentiations and integrations stated, except where stochastic forcing is explicitly discussed. Ideal conservation results concern continuous equations. Discretization, forcing, and damping can change those budgets. A sphere has no lateral boundary; planar examples use periodic boundaries unless otherwise stated. Coordinates have SI units, angles in differential formulas are radians, and time is in seconds. A superscript on a time-indexed random variable is an index, not a power. A hat on a field coefficient denotes a spectral coefficient; a hat on a basis vector denotes unit length. Symbols are defined locally and collected at the end.

# Kinematics and mathematical language

## Fields, parcels, and the material derivative

**Result and motivation.** A derivative at a fixed location differs from the rate experienced by a moving fluid parcel by an advection term. This distinction turns Newton's law into a field equation. [@Vallis2006, secs. 1.1-1.2]

A **continuum** replaces molecular positions with smoothly varying averages on scales large compared with molecular spacing. Let $\mathbf{x}=(x,y,z)$ be Cartesian position, $t$ time, and $\mathbf{v}(\mathbf{x},t)$ the velocity field, with units $\mathrm{m\,s^{-1}}$. A **parcel** is a small collection of fluid that moves with the velocity. Its trajectory $\mathbf{X}(t)$ satisfies $d\mathbf{X}/dt=\mathbf{v}(\mathbf{X}(t),t)$. The Eulerian description uses fields at fixed $\mathbf{x}$; the Lagrangian description follows $\mathbf{X}(t)$.

For a scalar field $b(\mathbf{x},t)$, the chain rule gives

$$
\frac{d}{dt}b(\mathbf{X}(t),t)
=\frac{\partial b}{\partial t}
 +\frac{dX_x}{dt}\frac{\partial b}{\partial x}
 +\frac{dX_y}{dt}\frac{\partial b}{\partial y}
 +\frac{dX_z}{dt}\frac{\partial b}{\partial z}.
$$

The **material derivative**, denoted $D/Dt$, is therefore

[]{#law-material}
$$
\boxed{\frac{Db}{Dt}=\partial_t b+\mathbf{v}\cdot\nabla b.}
\tag{1.1}
$$

Here $\partial_t$ means the partial derivative with respect to time; $\nabla$ is the spatial gradient defined next. The term $\mathbf{v}\cdot\nabla b$ is **advection**, the change caused by transport through a spatial gradient. In Cartesian components, $D\mathbf{v}/Dt=\partial_t\mathbf{v}+(\mathbf{v}\cdot\nabla)\mathbf{v}$ is parcel acceleration. A steady field ($\partial_t b=0$) need not be materially constant ($Db/Dt=0$).

For example, take $b=b_0+Gx$ and a uniform velocity $\mathbf{v}=U\hat{\mathbf{x}}$. Here $b_0$ is a constant, $G$ a constant spatial gradient, $U$ a speed, and $\hat{\mathbf{x}}$ the eastward Cartesian unit vector. Then $\partial_t b=0$, but $Db/Dt=UG$. This will matter when a parcel moves across latitude-dependent planetary vorticity.

## Gradient, divergence, curl, and Laplacian

**Result and motivation.** Gradients describe spatial differences, divergence describes local expansion and flux outflow, and curl describes local circulation. Their integral identities convert conservation laws into differential equations. [@ArfkenWeber2005, secs. 1.6-1.12]

For a scalar $b$ and vector $\mathbf{a}=(a_x,a_y,a_z)$, define

[]{#law-operators}
$$
\begin{aligned}
\nabla b&=(\partial_x b,\partial_y b,\partial_z b),\\
\nabla\cdot\mathbf{a}&=\partial_x a_x+\partial_y a_y+\partial_z a_z,\\
\nabla\times\mathbf{a}&=(\partial_y a_z-\partial_z a_y,
\partial_z a_x-\partial_x a_z,\partial_x a_y-\partial_y a_x),\\
\nabla^2b&=\nabla\cdot\nabla b=\partial_x^2b+\partial_y^2b+\partial_z^2b.
\end{aligned}\tag{1.2}
$$

The dot denotes the Euclidean inner product; $|\mathbf{a}|^2=\mathbf{a}\cdot\mathbf{a}$. The cross product $\mathbf{a}\times\mathbf{b}$ is perpendicular to both factors with right-hand orientation. The Laplacian $\nabla^2$ measures curvature: for $b=e^{ikx}$, $\nabla^2b=-k^2b$, where $i^2=-1$ and $k$ is a spatial wavenumber ($\mathrm{m^{-1}}$). A gradient has units of its field divided by length; divergence and curl add the same inverse-length factor.

Let $V$ be a volume bounded by the surface $\partial V$, $\mathbf{n}$ its outward unit normal, and $dV,dA$ volume and area elements. The **divergence theorem** states

$$
\int_V\nabla\cdot\mathbf{a}\,dV=\int_{\partial V}\mathbf{a}\cdot\mathbf{n}\,dA.
$$

For an oriented surface $\Sigma$ with boundary curve $C=\partial\Sigma$, the **Stokes theorem** is

$$
\int_\Sigma (\nabla\times\mathbf{a})\cdot\mathbf{n}\,dA
=\oint_C\mathbf{a}\cdot d\boldsymbol{\ell}.
$$

The line element $d\boldsymbol{\ell}$ points along $C$ in the right-hand direction relative to $\mathbf{n}$. These formulas explain why divergence is net outward flux per unit volume and normal curl is circulation per unit area. They have intrinsic surface counterparts on the sphere.

Mixed partial derivatives commute for smooth fields. Consequently $\nabla\times\nabla b=0$ and $\nabla\cdot(\nabla\times\mathbf{a})=0$. Two identities used later are

[]{#law-identities}
$$
\begin{aligned}
\nabla\cdot(b\mathbf{a})&=\mathbf{a}\cdot\nabla b+b\nabla\cdot\mathbf{a},\\
(\mathbf{v}\cdot\nabla)\mathbf{v}
&=\nabla\left(\tfrac12|\mathbf{v}|^2\right)
-\mathbf{v}\times(\nabla\times\mathbf{v}).
\end{aligned}\tag{1.3}
$$

Both follow by expanding Cartesian components. The second separates acceleration into a gradient and a rotational contribution.

## Material volumes and transport

**Result and motivation.** The integral of a field over a moving volume changes both because the field changes and because the volume expands. This is the bridge from parcel conservation to local balance laws. [@Vallis2006, sec. 1.2]

Let $V(t)$ move with the fluid. An infinitesimal material volume $\delta V$ changes at the rate $D\delta V/Dt=(\nabla\cdot\mathbf{v})\delta V$: differences between velocities on opposite faces give the three normal expansion rates in (1.2). Summing over the moving volume gives the **transport theorem**

[]{#law-transport}
$$
\frac{d}{dt}\int_{V(t)}b\,dV
=\int_{V(t)}\left(\frac{Db}{Dt}+b\nabla\cdot\mathbf{v}\right)dV
=\int_{V(t)}\left(\partial_tb+\nabla\cdot(b\mathbf{v})\right)dV.
\tag{1.4}
$$

Here $b$ is a density per unit volume of whatever is being integrated. It need not be mass density. For a material area $A(t)$ transported by a tangent velocity $\mathbf{u}$ on a surface, the analogous area change is $D\delta A/Dt=(\nabla_h\cdot\mathbf{u})\delta A$. The subscript $h$ denotes operators within the horizontal surface. Thus non-divergent surface motion preserves area.

## Chapter summary

- A field is an Eulerian quantity; a trajectory follows a Lagrangian parcel. Parcel acceleration is $\partial_t\mathbf{v}+\mathbf{v}\cdot\nabla\mathbf{v}$.
- The material derivative (1.1) combines local change and advection.
- Gradient, divergence, curl, and Laplacian are defined by (1.2). Divergence and Stokes theorems connect local derivatives with flux and circulation.
- The transport theorem (1.4) includes material volume expansion. Non-divergent motion preserves the relevant volume or area.

# Mass, forces, and the momentum equation

## Mass conservation and incompressibility

**Result and motivation.** Conservation of parcel mass gives the continuity equation. Incompressibility constrains volume change; it does not by itself make density spatially uniform. [@Vallis2006, secs. 1.2, 1.9]

Let $\rho(\mathbf{x},t)>0$ be mass density ($\mathrm{kg\,m^{-3}}$). A material volume contains constant mass, so set $b=\rho$ in (1.4). Because this holds for every material volume,

[]{#law-continuity}
$$
\boxed{\partial_t\rho+\nabla\cdot(\rho\mathbf{v})=0,
\qquad \frac{D\rho}{Dt}=-\rho\nabla\cdot\mathbf{v}.}
\tag{2.1}
$$

An **incompressible flow** preserves parcel volume: $\nabla\cdot\mathbf{v}=0$. Then $D\rho/Dt=0$, although different parcels can retain different densities. A **homogeneous fluid** has spatially uniform density. The constant-density, incompressible model uses one fixed density $\rho_0$. These distinctions prevent the incorrect inference that incompressibility alone removes buoyancy (acceleration due to density contrasts in gravity) or density gradients.

Three-dimensional incompressibility gives $\partial_xu+\partial_yv=-\partial_zw$, where $(u,v,w)$ are velocity components. Thus horizontal divergence need not vanish in an incompressible three-dimensional fluid. The later BVE imposes the stronger, separate restriction $\nabla_h\cdot\mathbf{u}=0$ on the horizontal velocity $\mathbf{u}=(u,v)$.

## Pressure, stress, and body forces

**Result and motivation.** Newton's law balances parcel acceleration against pressure forces, viscous stress, and body forces. The constant-viscosity Laplacian is a special case of the stress divergence. [@Vallis2006, sec. 1.3]

**Pressure** $p$ is the compressive normal force per unit area ($\mathrm{Pa}=\mathrm{kg\,m^{-1}\,s^{-2}}$). A surface with outward normal $\mathbf{n}$ experiences traction $\boldsymbol{\sigma}\mathbf{n}$, where the **stress tensor** $\boldsymbol{\sigma}$ maps a surface orientation to force per area. Write $\boldsymbol{\sigma}=-p\mathbf{I}+\boldsymbol{\tau}$, where $\mathbf{I}$ is the identity tensor and $\boldsymbol{\tau}$ the viscous stress. Let $\mathbf{b}$ be body force per unit mass ($\mathrm{m\,s^{-2}}$), such as gravity.

Newton's law on a material volume is

$$
\frac{d}{dt}\int_{V(t)}\rho\mathbf{v}\,dV
=\int_{\partial V(t)}\boldsymbol{\sigma}\mathbf{n}\,dA
+\int_{V(t)}\rho\mathbf{b}\,dV.
$$

Apply (1.4), cancel terms using (2.1), and apply the divergence theorem component by component to the stress. Localization gives

[]{#law-cauchy}
$$
\boxed{\rho\frac{D\mathbf{v}}{Dt}=-\nabla p+\nabla\cdot\boldsymbol{\tau}+\rho\mathbf{b}.}
\tag{2.2}
$$

In Cartesian components, $(\nabla\cdot\boldsymbol{\tau})_i=\sum_j\partial_j\tau_{ij}$. The indices $i,j$ run over three coordinate directions. Every term has units of force per volume. Pressure accelerates fluid toward lower pressure; a uniform pressure has no bulk acceleration because forces on opposite faces cancel.

For a constant-density, incompressible **Newtonian fluid** with constant dynamic viscosity $\mu\geq0$ ($\mathrm{Pa\,s}$), the viscous force density is $\nabla\cdot\boldsymbol{\tau}=\mu\nabla^2\mathbf{v}$. Newtonian means local viscous shear stress is proportional to local shear rate. This is a constitutive assumption about the material, not a consequence of Newton's second law. We use the constant-density viscosity model of Vallis, sec. 1.3.3; a general compressible stress law requires additional terms. With $\nu=\mu/\rho_0$ the kinematic viscosity ($\mathrm{m^2\,s^{-1}}$), (2.2) becomes the incompressible **Navier-Stokes equation**

[]{#law-ns}
$$
\frac{D\mathbf{v}}{Dt}=-\frac{1}{\rho_0}\nabla p+\nu\nabla^2\mathbf{v}+\mathbf{b},
\qquad \nabla\cdot\mathbf{v}=0.
\tag{2.3}
$$

Dropping viscous stress gives the **Euler equation**. A force is **conservative** if it is minus a potential gradient: $\mathbf{b}=-\nabla\Phi$, where $\Phi$ has units $\mathrm{m^2\,s^{-2}}$. Its curl vanishes. This property, rather than the mere absence of friction, is needed for circulation conservation.

## Pressure closure and kinetic energy

**Result and motivation.** Incompressible pressure enforces the divergence constraint. Viscosity dissipates kinetic energy, whereas pressure redistributes it in a closed constant-density domain. [@Vallis2006, secs. 1.4, 1.10]

In the unrotating, constant-density system with conservative body force, define $\Pi=p/\rho_0+\Phi$. Take the divergence of (2.3). Since $\nabla\cdot\mathbf{v}=0$ at all times,

$$
\nabla^2\Pi=-\nabla\cdot[(\mathbf{v}\cdot\nabla)\mathbf{v}].
$$

Thus pressure is determined diagnostically by an elliptic equation: a spatial boundary-value problem, here a Poisson equation, solved across the domain at each time, rather than independently stepped in time. An additive spatial constant in pressure does not affect motion. This closure is specific to the incompressible reduction. A compressible atmosphere instead also needs an equation of state and a thermodynamic evolution law. For example $p=\rho R T$ relates ideal-gas pressure, absolute temperature $T$, and specific gas constant $R$; it is not by itself a complete evolution system. The constant-density BVE does not retain that thermodynamic system.

Let $K=|\mathbf{v}|^2/2$ be kinetic energy per unit mass ($\mathrm{m^2\,s^{-2}}$). Dot (2.3) with $\mathbf{v}$. Use $\mathbf{v}\cdot\nabla\Pi=\nabla\cdot(\Pi\mathbf{v})$ and
$\mathbf{v}\cdot\nabla^2\mathbf{v}=\nabla^2K-\sum_{i,j}(\partial_jv_i)^2$. On a periodic volume,

[]{#law-ke3d}
$$
\frac{d}{dt}\int_V K\,dV
=-\nu\int_V\sum_{i,j}(\partial_jv_i)^2\,dV\leq0.
\tag{2.4}
$$

Flux terms integrate to zero by periodicity. The same conclusion holds with suitable stationary no-slip walls. Locally, pressure can do work; its net contribution vanishes under these boundary conditions. Molecular viscosity removes kinetic energy into internal energy; neglecting heat in the reduced equations does not change the sign of this kinetic-energy sink.

## Chapter summary

- Density $\rho$, pressure $p$, stress $\boldsymbol{\sigma}$, and body acceleration $\mathbf{b}$ enter mass conservation (2.1) and momentum conservation (2.2).
- Incompressibility means volume preservation; homogeneity means spatially uniform density. Horizontal non-divergence is an additional restriction.
- The viscous term $\nu\nabla^2\mathbf{v}$ requires constant viscosity and incompressibility. The inviscid counterpart is Euler's equation.
- Incompressible pressure enforces the velocity constraint. Conservative forces are potential gradients. Viscosity is a kinetic-energy sink under the stated boundary conditions.

# Rotation and large-scale balances

## Transforming Newton's law to a rotating frame

**Result and motivation.** Uniform rotation adds Coriolis and centrifugal accelerations. Coriolis changes velocity direction without doing work. [@Vallis2006, secs. 2.1-2.2]

Let $\boldsymbol{\Omega}$ be the constant angular velocity of the reference frame, $\Omega=|\boldsymbol{\Omega}|$, and $\mathbf{r}$ position relative to its fixed origin. Let subscripts $I$ and $R$ denote inertial and rotating observers. Rotating basis vectors obey $d\hat{\mathbf{e}}/dt=\boldsymbol{\Omega}\times\hat{\mathbf{e}}$. Differentiating vector components and basis vectors gives

$$
\left(\frac{d\mathbf{a}}{dt}\right)_I
=\left(\frac{d\mathbf{a}}{dt}\right)_R+\boldsymbol{\Omega}\times\mathbf{a}.
$$

Apply this to $\mathbf{r}$ and then its velocity:

[]{#law-rotation}
$$
\begin{aligned}
\mathbf{v}_I&=\mathbf{v}_R+\boldsymbol{\Omega}\times\mathbf{r},\\
\mathbf{a}_I&=\frac{D\mathbf{v}_R}{Dt}
+2\boldsymbol{\Omega}\times\mathbf{v}_R
+\boldsymbol{\Omega}\times(\boldsymbol{\Omega}\times\mathbf{r}).
\end{aligned}\tag{3.1}
$$

There is no angular-acceleration term because $\boldsymbol{\Omega}$ is constant. From now on $\mathbf{v}$ means velocity relative to the rotating frame. With gravitational potential $\Phi_g$, define the **effective geopotential**
$\Phi=\Phi_g-|\boldsymbol{\Omega}\times\mathbf{r}|^2/2$. Indeed $\nabla(|\boldsymbol{\Omega}\times\mathbf{r}|^2/2)=-\boldsymbol{\Omega}\times(\boldsymbol{\Omega}\times\mathbf{r})$, so centrifugal acceleration is included in $-\nabla\Phi$. The momentum equation is

[]{#law-rotating-momentum}
$$
\frac{D\mathbf{v}}{Dt}+2\boldsymbol{\Omega}\times\mathbf{v}
=-\frac{1}{\rho}\nabla p-\nabla\Phi+\mathbf{F}.
\tag{3.2}
$$

Here $\mathbf{F}$ collects non-conservative accelerations, including viscosity if retained. Coriolis acceleration on the right-hand side is $-2\boldsymbol{\Omega}\times\mathbf{v}$. Because $\mathbf{v}\cdot(\boldsymbol{\Omega}\times\mathbf{v})=0$, it contributes no kinetic-energy work. Rotation nevertheless changes which velocity fields solve the equation.

## The Coriolis parameter and local planes

**Result and motivation.** The radial projection of planetary vorticity varies with latitude. Its northward gradient provides the restoring mechanism of Rossby waves. [@Vallis2006, sec. 2.3]

Let $a$ be planetary radius, $\phi$ latitude, $\lambda$ longitude, and $\hat{\mathbf{k}}$ the local outward radial unit vector. Define $\hat{\mathbf{e}}_\lambda$ eastward and $\hat{\mathbf{e}}_\phi$ northward; $\hat{\mathbf{e}}_\lambda\times\hat{\mathbf{e}}_\phi=\hat{\mathbf{k}}$. The **Coriolis parameter** is

[]{#law-coriolis}
$$
f=2\boldsymbol{\Omega}\cdot\hat{\mathbf{k}}=2\Omega\sin\phi.
\tag{3.3}
$$

It has units $\mathrm{s^{-1}}$. Retaining only this component of rotation in horizontal momentum is the **traditional approximation**. For horizontal speed $U$ and vertical speed magnitude $|w|$, the neglected horizontal coupling is small relative to $|f|U$ when $(|w|/U)|\cot\phi|\ll1$. Neglecting the corresponding vertical Coriolis contribution also requires a consistent vertical momentum scaling, such as the shallow, stratified large-scale regime discussed by Vallis. It is an approximation, not a statement that the full rotation vector is vertical. On a strictly two-dimensional constrained spherical shell, the tangent Coriolis acceleration from tangent velocity is exactly $-f\hat{\mathbf{k}}\times\mathbf{u}$.

In a small neighborhood of latitude $\phi_0$, let $x=a\cos\phi_0(\lambda-\lambda_0)$ and $y=a(\phi-\phi_0)$ be local eastward and northward distances; $\lambda_0$ is a reference longitude. Taylor expansion gives

[]{#law-beta}
$$
f=f_0+\beta y+O\!\left(\Omega y^2/a^2\right),\quad
f_0=2\Omega\sin\phi_0,\quad
\beta=\frac{2\Omega\cos\phi_0}{a}.
\tag{3.4}
$$

$O(\cdot)$ denotes the scale of omitted terms. An **$f$-plane** uses constant $f_0$; a **$\beta$-plane** retains $\beta y$ but otherwise uses flat geometry. Here $\beta$ has units $\mathrm{m^{-1}\,s^{-1}}$. This expansion needs distances small compared with $a$. The sphere later retains the full sine and metric factors. A constant-$f$ homogeneous layer has no planetary-vorticity-gradient Rossby waves, although other potential-vorticity gradients can support analogous waves.

## Scaling, hydrostatic balance, and geostrophy

**Result and motivation.** Small aspect ratio and small Rossby number justify useful leading balances, but neither alone derives the non-divergent BVE. [@Vallis2006, secs. 1.11, 2.7-2.8]

Choose representative horizontal speed $U$, horizontal length $L$, depth $H$, and advective time $L/U$. The **aspect ratio** is $H/L$. The **Rossby number** and **Reynolds number** are

[]{#law-scales}
$$
\mathrm{Ro}=\frac{U}{|f_0|L},\qquad
\mathrm{Re}=\frac{UL}{\nu}.
\tag{3.5}
$$

They compare advective acceleration with Coriolis acceleration, and advection with molecular viscosity. Both are dimensionless. If the evolution time differs substantially from $L/U$, also compare its inverse with $|f_0|$. Large $\mathrm{Re}$ does not mean all dissipation can be omitted at unresolved small scales. Small $\mathrm{Ro}$ is not required by the full BVE; it is used for geostrophic interpretation. Formula (3.5) does not define a useful geostrophic ordering at $f_0=0$.

For incompressible large-scale flow, continuity suggests vertical speed of order $UH/L$. Vertical acceleration then scales as $U^2H/L^2$. A **hydrostatic approximation** drops this acceleration relative to the vertical pressure and gravity balance:

[]{#law-hydrostatic}
$$
\partial_zp=-\rho g,
\tag{3.6}
$$

where $z$ increases upward and $g>0$ is effective gravitational acceleration. A necessary smallness estimate is $U^2H/(gL^2)\ll1$; accurate horizontal pressure gradients can require a stronger ordering based on pressure departures and stratification, as emphasized by Vallis, sec. 2.7. Hydrostatic balance does not set vertical velocity to zero and does not remove horizontal density variation.

For constant reference density $\rho_0$ and $\mathrm{Ro}\ll1$, the leading horizontal balance on an $f$-plane is **geostrophy**:

[]{#law-geostrophy}
$$
f_0\hat{\mathbf{k}}\times\mathbf{u}_g=-\frac{1}{\rho_0}\nabla_hp,
\qquad
u_g=-\frac{1}{\rho_0f_0}\partial_yp,\quad
v_g=\frac{1}{\rho_0f_0}\partial_xp.
\tag{3.7}
$$

Here $\mathbf{u}_g=(u_g,v_g)$ is geostrophic velocity. Opposing pressure-gradient and Coriolis forces give flow along pressure contours, rather than direct flow toward low pressure. Defining $\psi_g=p/(\rho_0f_0)$ gives $\mathbf{u}_g=\hat{\mathbf{k}}\times\nabla_h\psi_g$. Its divergence vanishes for constant $f_0$. With latitude-dependent $f$, this pressure-based velocity is not exactly non-divergent. The BVE streamfunction below is defined kinematically, without imposing geostrophy.

## Barotropic density and the role of stratification

**Result and motivation.** A barotropic equation of state eliminates baroclinic vorticity production; a one-layer, depth-independent velocity is a further modeling restriction. This distinction explains what stochastic stirring replaces. [@Vallis2006, secs. 2.4, 2.8-2.9, 4.2]

A **barotropic fluid** satisfies $p=p(\rho)$, or locally $\rho=\rho(p)$ where invertible. Pressure and density gradients are parallel, so $\nabla\rho\times\nabla p=0$. **Baroclinicity** means these gradients are not parallel. A constant-density fluid also makes this cross product zero. The thermodynamic definition alone does not force every possible velocity field to be independent of height.

To see the connection under balanced conditions, use a local Boussinesq model: density departures $\rho'$ from constant $\rho_0$ are retained in the vertical buoyancy acceleration $b=-g\rho'/\rho_0$ but omitted from inertia. Buoyancy is the acceleration caused by a parcel's density difference from its hydrostatic surroundings; a denser parcel has $b<0$. Let $p'$ be pressure relative to a hydrostatic reference state. Combine $f_0\hat{\mathbf{k}}\times\mathbf{u}_g=-\nabla_hp'/\rho_0$ with $\partial_zp'=-g\rho'$. Differentiating the former with respect to $z$ gives **thermal-wind balance**

[]{#law-thermalwind}
$$
f_0\hat{\mathbf{k}}\times\partial_z\mathbf{u}_g
=\frac{g}{\rho_0}\nabla_h\rho'.
\tag{3.8}
$$

It relates vertical shear of geostrophic velocity to horizontal density gradients; it is not an extra wind component. In this approximation, no horizontal density gradient implies no vertical geostrophic shear. Arbitrary unbalanced motions need not obey this inference.

For a resting Boussinesq reference density $\bar\rho(z)$, a small upward parcel displacement $\eta$ leaves the parcel with density excess $-\eta\,d\bar\rho/dz$. Its buoyancy acceleration is $-N^2\eta$, where

$$
N^2=-\frac{g}{\rho_0}\frac{d\bar\rho}{dz}.
$$

$N$ is the **buoyancy frequency** when $N^2>0$: the stratification is stable and resists displacement. Negative $N^2$ indicates instability in this simple parcel model. For dry ideal-gas air, define **potential temperature** $\theta_T=T(p_{\mathrm{ref}}/p)^{R/c_p}$, where $p_{\mathrm{ref}}>0$ is a fixed reference pressure and $c_p$ is constant specific heat at constant pressure ($\mathrm{J\,kg^{-1}\,K^{-1}}$). It is the temperature a parcel would have after compression or expansion to $p_{\mathrm{ref}}$ without heat exchange; it is conserved in dry reversible adiabatic motion. In compressible air, the corresponding stability criterion uses potential temperature, not the raw vertical density gradient; we do not apply this Boussinesq formula to a compressible atmospheric profile. Stratification and thermal wind allow three-dimensional baroclinic dynamics that a homogeneous single-layer BVE omits. Random stirring can parameterize some eddy input from such omitted motions without reproducing their thermodynamics.

## Chapter summary

- A rotating frame adds Coriolis acceleration and centrifugal acceleration. The latter enters effective geopotential; Coriolis does no work.
- $f=2\Omega\sin\phi$ is planetary vorticity normal to the surface; $\beta=2\Omega\cos\phi_0/a$ is its local northward gradient.
- Rossby number, Reynolds number, and aspect ratio describe distinct approximations. Hydrostatic balance is vertical; geostrophic balance is horizontal.
- Barotropy removes the density-pressure cross product. Thermal wind links balanced vertical shear to horizontal density variation. Stable stratification resists vertical displacement.
- The two-dimensional constant-depth BVE requires explicit restrictions beyond hydrostasy, geostrophy, or thermodynamic barotropy.

# Vorticity and circulation

## Local spin and integrated circulation

**Result and motivation.** Vorticity is local circulation per unit area. Its magnitude is twice the local rigid-rotation rate, not the angular momentum of a parcel about the planet's axis. [@Vallis2006, sec. 4.1]

Define **relative vorticity** $\boldsymbol{\omega}=\nabla\times\mathbf{v}$, with units $\mathrm{s^{-1}}$. For a closed curve $C$ bounding $\Sigma$, define **circulation** $\Gamma$ by

[]{#law-circulation}
$$
\Gamma=\oint_C\mathbf{v}\cdot d\boldsymbol{\ell}
=\int_\Sigma\boldsymbol{\omega}\cdot\mathbf{n}\,dA.
\tag{4.1}
$$

Circulation has units $\mathrm{m^2\,s^{-1}}$. For a sufficiently small planar loop, its normal vorticity is $\Gamma/\delta A$. The antisymmetric part of the local velocity gradient describes rigid rotation at angular velocity $\boldsymbol{\omega}/2$; the symmetric part deforms the parcel.

A direct check is solid rotation in a horizontal plane: $u=-\Omega_s y$, $v=\Omega_s x$, with rotation rate $\Omega_s$. The vertical vorticity is $\zeta=\partial_xv-\partial_yu=2\Omega_s$. In contrast, a shear flow $u=U(y)$, $v=0$ has $\zeta=-dU/dy$ even though its streamlines (curves everywhere tangent to instantaneous velocity) are straight. Curved trajectories and local spin are different concepts.

## Taking the curl of momentum

**Result and motivation.** Vorticity changes through stretching and tilting, divergence, baroclinicity, and the curl of non-conservative forces. A scalar conservation law emerges only after these terms are controlled. [@Vallis2006, secs. 4.2, 4.4]

Start with (3.2), use (1.3), and define **absolute vorticity** $\boldsymbol{\omega}_a=\boldsymbol{\omega}+2\boldsymbol{\Omega}$. The resulting vector-invariant momentum equation is

$$
\partial_t\mathbf{v}+\boldsymbol{\omega}_a\times\mathbf{v}
=-\nabla\left(\Phi+\tfrac12|\mathbf{v}|^2\right)
-\rho^{-1}\nabla p+\mathbf{F}.
$$

The curl of the gradient vanishes. The pressure term gives

$$
\nabla\times(-\rho^{-1}\nabla p)
=-\nabla(\rho^{-1})\times\nabla p
=\rho^{-2}\nabla\rho\times\nabla p.
$$

For vector fields $\mathbf{a},\mathbf{b}$, the product identity

$$
\nabla\times(\mathbf{a}\times\mathbf{b})
=\mathbf{a}\nabla\cdot\mathbf{b}-\mathbf{b}\nabla\cdot\mathbf{a}
+(\mathbf{b}\cdot\nabla)\mathbf{a}-(\mathbf{a}\cdot\nabla)\mathbf{b}
$$

follows componentwise. Apply it with $\mathbf{a}=\boldsymbol{\omega}_a$, $\mathbf{b}=\mathbf{v}$. Since $\nabla\cdot\boldsymbol{\omega}_a=0$ and $\boldsymbol{\Omega}$ is a constant vector in rotating Cartesian coordinates, obtain

[]{#law-vorticity3d}
$$
\boxed{
\frac{D\boldsymbol{\omega}_a}{Dt}
=(\boldsymbol{\omega}_a\cdot\nabla)\mathbf{v}
-\boldsymbol{\omega}_a\nabla\cdot\mathbf{v}
+\frac{\nabla\rho\times\nabla p}{\rho^2}
+\nabla\times\mathbf{F}.}
\tag{4.2}
$$

The first term differentiates velocity along the vorticity direction. It stretches a vortex when neighboring points separate along it, and tilts it when that separation changes direction. The second accounts for volume expansion. The third is **baroclinic production**, present when density and pressure surfaces are misaligned. The last represents friction or applied torque. For constant viscosity and homogeneous incompressible flow, molecular viscosity contributes $\nu\nabla^2\boldsymbol{\omega}$.

Using continuity, the divergence term can instead be absorbed into vorticity per unit density:

$$
\frac{D}{Dt}\left(\frac{\boldsymbol{\omega}_a}{\rho}\right)
=\left(\frac{\boldsymbol{\omega}_a}{\rho}\cdot\nabla\right)\mathbf{v}
+\frac{\nabla\rho\times\nabla p}{\rho^3}
+\frac{\nabla\times\mathbf{F}}{\rho}.
$$

This is still a vector stretching equation, not the shallow-water potential-vorticity conservation law derived next. In spherical coordinates the local basis varies with position; one must not discard that variation by treating (4.2) as three unrelated scalar equations.

## Kelvin's theorem and rotation

**Result and motivation.** Inviscid barotropic motion under conservative body forces conserves circulation around a moving material loop. In a rotating frame the conserved quantity is absolute circulation. [@Vallis2006, sec. 4.3]

First use an inertial frame, with material loop $C(t)$. Parametrize it by $s$ and position $\mathbf{X}(s,t)$. Differentiating its line element gives $D(d\boldsymbol{\ell})/Dt=d\mathbf{v}$. Therefore

$$
\frac{d\Gamma}{dt}
=\oint_{C(t)}\frac{D\mathbf{v}}{Dt}\cdot d\boldsymbol{\ell}
+\oint_{C(t)}\mathbf{v}\cdot d\mathbf{v}.
$$

The second integral is $\oint d(|\mathbf{v}|^2/2)=0$. In a barotropic fluid define the pressure potential $\mathcal{H}(p)=\int^p dp'/\rho(p')$. Here $p'$ is an integration variable, not a pressure perturbation. Then $\rho^{-1}\nabla p=\nabla\mathcal{H}$. Euler's equation with $\mathbf{b}=-\nabla\Phi_g$ gives

[]{#law-kelvin}
$$
\frac{d\Gamma}{dt}=-\oint_{C(t)}\nabla(\mathcal{H}+\Phi_g)\cdot d\boldsymbol{\ell}=0.
\tag{4.3}
$$

The same result follows for homogeneous density. It requires a material loop, conservative body forces, and no non-conservative stress contribution to the circulation budget.

For rotating velocity $\mathbf{v}$, inertial velocity is $\mathbf{v}+\boldsymbol{\Omega}\times\mathbf{r}$. Stokes' theorem gives

[]{#law-absolute-circulation}
$$
\Gamma_a
=\oint_{C(t)}(\mathbf{v}+\boldsymbol{\Omega}\times\mathbf{r})\cdot d\boldsymbol{\ell}
=\int_{\Sigma(t)}(\boldsymbol{\omega}+2\boldsymbol{\Omega})\cdot\mathbf{n}\,dA.
\tag{4.4}
$$

$\Gamma_a$ denotes absolute circulation. The factor 2 comes from the curl of solid-body rotational velocity. For a small horizontal loop on the sphere, $\Gamma_a\simeq(\zeta+f)\delta A$, where $\zeta=\hat{\mathbf{k}}\cdot\boldsymbol{\omega}$. If the loop preserves area, Kelvin's theorem implies $D(\zeta+f)/Dt=0$. A poleward-moving loop in the Northern Hemisphere encounters larger $f$ and develops smaller relative vorticity. This is the $\beta$ effect, even though planetary rotation rate is constant.

## Chapter summary

- Relative vorticity $\boldsymbol{\omega}$ is curl of relative velocity; circulation $\Gamma$ is its surface integral. Local rigid spin is $\boldsymbol{\omega}/2$.
- Absolute vorticity $\boldsymbol{\omega}_a=\boldsymbol{\omega}+2\boldsymbol{\Omega}$ obeys (4.2), with stretching, divergence, baroclinic, and non-conservative-force terms.
- Kelvin's theorem conserves circulation only under its stated dynamical and material-loop assumptions. In a rotating frame, absolute circulation (4.4) is the conserved quantity.
- Normal absolute vorticity is conserved on an area-preserving spherical material patch. Relative vorticity alone generally is not.

# A shallow layer and the barotropic reduction

## Layer momentum and thickness conservation

**Result and motivation.** A homogeneous shallow layer can still stretch vertically. Its conserved scalar includes layer thickness, which must become constant before absolute vorticity itself is materially conserved. [@Vallis2006, secs. 3.1, 3.6]

Consider a constant-density layer on a local rotating plane. A stationary flat bottom is at $z=0$ and a free surface at $z=h(x,y,t)>0$. The **layer thickness** is $h$ ($\mathrm{m}$). Assume hydrostatic pressure, small depth-to-horizontal-scale ratio, and horizontal velocity $\mathbf{u}(x,y,t)=(u,v)$ independent of depth to leading order. Pressure at the surface is a spatial constant $p_s$, so integration of (3.6) gives $p=p_s+\rho_0g(h-z)$ and $\nabla_hp/\rho_0=g\nabla_hh$ at fixed $z$.

Define the horizontal material derivative $D_h/Dt=\partial_t+u\partial_x+v\partial_y$. In the absence of forcing and friction, the **shallow-water equations** are

[]{#law-shallow-water}
$$
\begin{aligned}
\frac{D_hu}{Dt}-fv&=-g\partial_xh,\\
\frac{D_hv}{Dt}+fu&=-g\partial_yh,\\
\partial_th+\nabla_h\cdot(h\mathbf{u})&=0,
\quad\text{or}\quad \frac{D_hh}{Dt}=-h\nabla_h\cdot\mathbf{u}.
\end{aligned}\tag{5.1}
$$

The third equation follows by conserving the volume $h\delta A$ of each moving column. The surface is material, so its upward motion is compatible with horizontal convergence. Even though the three-dimensional fluid is incompressible, the depth-independent horizontal velocity may have nonzero divergence because thickness changes.

## Potential vorticity and vortex stretching

**Result and motivation.** The shallow-water **potential vorticity** is normal absolute vorticity divided by thickness. Stretching a column amplifies its absolute vorticity. [@Vallis2006, sec. 3.6.1, eqs. 3.77-3.78]

Define horizontal divergence $\delta=\partial_xu+\partial_yv$ and vertical relative vorticity $\zeta=\partial_xv-\partial_yu$. Take $\partial_x$ of the northward equation in (5.1) minus $\partial_y$ of the eastward equation. Mixed pressure derivatives cancel. The acceleration derivatives satisfy

$$
\partial_x(D_hv/Dt)-\partial_y(D_hu/Dt)
=\frac{D_h\zeta}{Dt}+\zeta\delta.
$$

For $f=f(y)$ the Coriolis derivatives give $f\delta+v\partial_yf$. Hence, since $\partial_tf=0$,

[]{#law-layer-vorticity}
$$
\frac{D_h(\zeta+f)}{Dt}=-(\zeta+f)\delta.
\tag{5.2}
$$

Define $q=(\zeta+f)/h$, with units $\mathrm{m^{-1}\,s^{-1}}$. Apply the quotient rule and the thickness equation:

[]{#law-pv}
$$
\boxed{
\frac{D_hq}{Dt}
=\frac{1}{h}\frac{D_h(\zeta+f)}{Dt}
-\frac{\zeta+f}{h^2}\frac{D_hh}{Dt}=0.}
\tag{5.3}
$$

A converging column has $\delta<0$, grows thicker, and increases its absolute vorticity in the same ratio, leaving $q$ unchanged. Equivalently, Kelvin's theorem conserves $(\zeta+f)\delta A$, while volume conservation fixes $h\delta A$; dividing the two gives (5.3). With a stationary uneven bottom, thickness is surface elevation minus bottom elevation, so topography can affect $q$ even beneath a rigid upper boundary. That case is excluded from the constant-depth model below. This layer $q$ is not the general three-dimensional potential vorticity of a stratified compressible atmosphere.

## Constant depth and the non-divergent BVE

**Result and motivation.** With constant layer thickness, potential-vorticity conservation reduces to advection of absolute vorticity. Pressure remains a constraint force under a rigid lid. [@Vallis2006, secs. 3.1.3, 4.4.2; @BarotropicNotes, pp. 1-2]

Impose a rigid lid, flat bottom, and a fixed thickness $h=H$ everywhere, with $H>0$ constant. Then (5.1) gives $\nabla_h\cdot\mathbf{u}=0$. The pressure under a rigid lid adjusts to maintain that constraint; it is not the constant surface pressure of the free-surface example. It would be inconsistent to put $h=H$ directly into every free-surface pressure term in (5.1) and conclude that all horizontal pressure gradients vanish.

Let $Q=\zeta+f$ be **normal absolute vorticity** ($\mathrm{s^{-1}}$). It differs by the constant factor $H$ from the layer potential vorticity $q$. The inviscid, unforced BVE is

[]{#law-bve-advection}
$$
\boxed{\partial_t\zeta+\mathbf{u}\cdot\nabla_h(\zeta+f)=0,
\qquad \nabla_h\cdot\mathbf{u}=0.}
\tag{5.4}
$$

It follows equally from (5.2) with $\delta=0$, or from circulation conservation on an area-preserving surface. There is no need to assume geostrophic balance in (5.4).

The restrictions used are a homogeneous fluid, two-dimensional tangent velocity, no thickness variation or topographic stretching, constant planetary rotation, no non-conservative forces, and horizontal non-divergence. They remove density-pressure production, vertical shear and tilting dynamics of a stratified layer, and vortex stretching associated with thickness changes. The resulting model supports horizontal eddy dynamics and Rossby waves. It does not prognose temperature, stratification, acoustic waves, or free-surface gravity waves.

Because $f$ varies in space, $D_hQ/Dt=0$ means

$$
\frac{D_h\zeta}{Dt}=-\mathbf{u}\cdot\nabla_h f.
$$

Time independence gives $\partial_tf=0$, not $D_hf/Dt=0$. This distinction corrects a misleading sentence on p. 2 of the supplied notes; their subsequent BVE retains the correct planetary-advection term.

## Chapter summary

- Layer thickness $h$ satisfies volume conservation (5.1). Horizontal convergence can coexist with three-dimensional incompressibility.
- Absolute vorticity obeys the stretching law (5.2). Layer potential vorticity $q=(\zeta+f)/h$ is materially conserved.
- A rigid lid, flat bottom, and fixed thickness enforce horizontal non-divergence. The pressure adjusts to impose that constraint.
- The non-divergent BVE (5.4) conserves $Q=\zeta+f$ on parcels. It is a two-dimensional dynamical model, not a complete thermodynamic atmosphere.

# The BVE on a rotating sphere

## Surface geometry and differential operators

**Result and motivation.** Longitude and latitude are angles, so physical derivatives need radius and cosine factors. The spherical BVE cannot be obtained by relabeling Cartesian coordinates. [@ArfkenWeber2005, secs. 2.1-2.5; @BarotropicNotes, sec. 1]

Let $S_a^2$ denote the sphere of radius $a$, with $0\leq\lambda<2\pi$ and $-\pi/2\leq\phi\leq\pi/2$. The tangent velocity is $\mathbf{u}=u\hat{\mathbf{e}}_\lambda+v\hat{\mathbf{e}}_\phi$. At fixed latitude, arc length is $a\cos\phi\,d\lambda$; meridional arc length is $a\,d\phi$. Therefore

[]{#law-metric}
$$
ds^2=a^2\cos^2\phi\,d\lambda^2+a^2d\phi^2,
\qquad dA=a^2\cos\phi\,d\phi\,d\lambda.
\tag{6.1}
$$

Here $ds$ is infinitesimal surface distance and $dA$ physical area. For a scalar $b$,

[]{#law-surface-operators}
$$
\begin{aligned}
\nabla_hb&=\hat{\mathbf{e}}_\lambda\frac{\partial_\lambda b}{a\cos\phi}
+\hat{\mathbf{e}}_\phi\frac{\partial_\phi b}{a},\\
\nabla_h\cdot\mathbf{u}&=\frac{\partial_\lambda u+\partial_\phi(v\cos\phi)}{a\cos\phi},\\
\zeta&=\frac{\partial_\lambda v-\partial_\phi(u\cos\phi)}{a\cos\phi},\\
\nabla_h^2b&=\frac{\partial_\lambda^2b}{a^2\cos^2\phi}
+\frac{1}{a^2\cos\phi}\partial_\phi(\cos\phi\,\partial_\phi b).
\end{aligned}\tag{6.2}
$$

The divergence follows from fluxes through the sides of a small latitude-longitude cell divided by its area. The curl follows from circulation around the same cell. Inserting the gradient into divergence gives the last formula, the **surface Laplacian** or **Laplace-Beltrami operator**. Its units are inverse length squared. The apparent singularities at $\cos\phi=0$ are coordinate singularities: physical fields must be smooth at the poles, rather than assigning arbitrary, longitude-dependent values there.

## Streamfunction, vorticity inversion, and the Jacobian

**Result and motivation.** A smooth non-divergent tangent field on the sphere is specified by one streamfunction, up to a constant. Recovering that streamfunction from vorticity closes the evolution. [@Vallis2006, sec. 4.2.1; @BarotropicNotes, pp. 1-2, 7-8]

Define the **streamfunction** $\psi$ ($\mathrm{m^2\,s^{-1}}$) by

[]{#law-streamfunction}
$$
\mathbf{u}=\hat{\mathbf{k}}\times\nabla_h\psi,
\qquad u=-\frac{1}{a}\partial_\phi\psi,
\qquad v=\frac{1}{a\cos\phi}\partial_\lambda\psi.
\tag{6.3}
$$

Substitution into (6.2) cancels the mixed derivatives in divergence and gives

[]{#law-inversion}
$$
\boxed{\zeta=\nabla_h^2\psi.}\tag{6.4}
$$

The velocity is tangent to contours of $\psi$, since $\mathbf{u}\cdot\nabla_h\psi=0$. These contours are instantaneous **streamlines**; they are parcel trajectories only in steady flow. For completeness, prescribe $d\psi=a\cos\phi\,v\,d\lambda-a u\,d\phi$. Non-divergence makes its integral around an infinitesimal cell zero, because $\partial_\phi(a\cos\phi\,v)+\partial_\lambda(au)=0$. By the surface Stokes theorem the integral vanishes around every closed loop bounding a surface; every closed loop on the sphere can be contracted without meeting a hole. Thus path integrals from a fixed point define a global single-valued $\psi$ up to a constant. Pole smoothness joins the coordinate charts without a physical singularity. Other domains need boundary and possible circulation information. In particular, constant mean velocity on a periodic plane is not recovered from periodic vorticity alone; here spherical topology avoids that undetermined harmonic flow.

Equation (6.4) is a **Poisson equation**. Integrating over the closed sphere gives the necessary compatibility condition $\int_{S_a^2}\zeta\,dA=0$. A smooth globally defined tangent velocity satisfies this by Stokes' theorem. The Laplacian annihilates constants, so $\psi$ is unique only after fixing a **gauge**, for example

[]{#law-gauge}
$$
\int_{S_a^2}\zeta\,dA=0,\qquad \int_{S_a^2}\psi\,dA=0.
\tag{6.5}
$$

For two scalars $A,B$, define their spherical **Jacobian**

[]{#law-jacobian}
$$
J(A,B)=\frac{\partial_\lambda A\,\partial_\phi B
-\partial_\phi A\,\partial_\lambda B}{a^2\cos\phi}.
\tag{6.6}
$$

Inserting (6.3) into $\mathbf{u}\cdot\nabla_hB$ gives exactly $J(\psi,B)$. The sign convention is fixed by eastward $u$ and northward $v$; reversing the streamfunction convention would change multiple signs together.

## Closed spherical equation and a sign check

**Result and motivation.** The BVE is nonlinear vorticity advection coupled to an elliptic inversion. Planetary rotation contributes an exact linear longitude derivative on the sphere. [@BarotropicNotes, eq. 11; @Vallis2006, sec. 4.4.2]

Combining (5.4) and (6.4)-(6.6), with $f=2\Omega\sin\phi$, gives

[]{#law-spherical-bve}
$$
\boxed{\partial_t\zeta+J(\psi,\zeta+f)=0,
\qquad \nabla_h^2\psi=\zeta.}\tag{6.7}
$$

Indeed $\partial_\phi f=2\Omega\cos\phi$ and $\partial_\lambda f=0$, so

$$
J(\psi,f)=\frac{2\Omega}{a^2}\partial_\lambda\psi,
\qquad
\partial_t\nabla_h^2\psi+J(\psi,\nabla_h^2\psi)
+\frac{2\Omega}{a^2}\partial_\lambda\psi=0.
$$

Every term in the vorticity equation has units $\mathrm{s^{-2}}$. Although $\psi$ appears, the nonlinearity is not a prescribed transport velocity: vorticity determines $\psi$, and $\psi$ determines the velocity advecting that same vorticity.

As a metric and sign check, choose a zonal solid rotation relative to the planet, $u=U_s\cos\phi$, $v=0$, with speed scale $U_s$. Then

$$
\psi=-aU_s\sin\phi,\qquad \zeta=\frac{2U_s}{a}\sin\phi.
$$

Both are smooth and have zero spherical mean. All fields are independent of longitude, so both Jacobians in (6.7) vanish: this is an inviscid steady solution. Omitting the cosine term in the curl would fail this check.

## Rossby waves from absolute-vorticity conservation

**Result and motivation.** A meridional displacement changes planetary vorticity; compensating relative spin produces propagating Rossby waves. Their phase propagates westward relative to a resting background. [@Vallis2006, sec. 5.7]

Use the local $\beta$-plane, where $u=-\partial_y\psi$, $v=\partial_x\psi$, $\zeta=\nabla_h^2\psi$, and $J(A,B)=A_xB_y-A_yB_x$. The BVE is

$$
\partial_t\nabla_h^2\psi+J(\psi,\nabla_h^2\psi)+\beta\partial_x\psi=0.
$$

Let a constant mean eastward velocity be $U$, and write $\psi=-Uy+\psi'$, where $\psi'$ is a small disturbance. The prime denotes a perturbation. Since $\nabla_h^2(-Uy)=0$, neglecting products of disturbance amplitudes gives

$$
(\partial_t+U\partial_x)\nabla_h^2\psi'+\beta\partial_x\psi'=0.
$$

Seek a mode $\psi'=\operatorname{Re}\{\Psi e^{i(k_xx+k_yy-\sigma t)}\}$, where $\Psi$ is constant complex amplitude, $k_x,k_y$ are wavenumbers, $\sigma$ angular frequency, and $\operatorname{Re}$ takes the real part. Put $K^2=k_x^2+k_y^2>0$. Inserting the mode gives $iK^2(\sigma-Uk_x)+i\beta k_x=0$, hence

[]{#law-rossby}
$$
\boxed{\sigma=Uk_x-\frac{\beta k_x}{k_x^2+k_y^2},
\qquad c_x=\frac{\sigma}{k_x}=U-\frac{\beta}{K^2}\quad(k_x\ne0).}
\tag{6.8}
$$

Here $c_x$ is zonal phase speed. For $\beta>0$, its intrinsic value $c_x-U$ is negative. Phase speed describes constant-phase lines, not the velocity of a parcel or necessarily the propagation of a localized wave packet. Shorter waves have smaller intrinsic zonal phase speed in magnitude. At $\beta=0$ and no background potential-vorticity gradient, the restoring term disappears. This result is a small-amplitude local-plane limit, not a replacement for the full spherical nonlinear equation.

## Chapter summary

- Sphere geometry sets the area element and all metric factors in (6.1)-(6.2). Pole smoothness replaces arbitrary polar grid values.
- The streamfunction convention (6.3) makes velocity non-divergent and gives $\zeta=\nabla_h^2\psi$. Zero-mean compatibility and a gauge are necessary for inversion.
- The spherical Jacobian is exactly non-divergent advection. The closed BVE is (6.7).
- Planetary advection is $2\Omega\partial_\lambda\psi/a^2$. The local linear limit gives the Rossby-wave dispersion relation (6.8).

# Invariants, turbulence, and eddy-driven flow

## Conserved vorticity distributions and kinetic energy

**Result and motivation.** Inviscid non-divergent advection preserves the distribution of absolute vorticity and the total kinetic energy. These are practical sign and geometry checks for any model. [@Vallis2006, secs. 3.6, 8.3; @BarotropicNotes, p. 3]

All integrals in this chapter are over the closed sphere unless another domain is stated. Let $G(Q)$ be any differentiable function of $Q=\zeta+f$. From $D_hQ/Dt=0$ and $\nabla_h\cdot\mathbf{u}=0$,

$$
\partial_tG(Q)+\nabla_h\cdot[\mathbf{u}G(Q)]=0.
$$

Integrating a surface divergence over the sphere gives zero. Thus

[]{#law-casimirs}
$$
\frac{d}{dt}\int_{S_a^2}G(Q)\,dA=0,
\qquad Z_a=\frac12\int_{S_a^2}Q^2\,dA=\text{constant}.
\tag{7.1}
$$

The integrals for arbitrary $G$ are often called **Casimir invariants**; here this term means conserved functionals of the advected scalar. $Z_a$ is absolute enstrophy, the integrated squared absolute vorticity divided by two. These are area-weighted integrals, not equally weighted latitude-longitude sums.

Define integrated kinetic energy per unit constant areal mass and **relative enstrophy** by

[]{#law-energy-enstrophy}
$$
E=\frac12\int_{S_a^2}|\mathbf{u}|^2\,dA
=-\frac12\int_{S_a^2}\psi\zeta\,dA,
\qquad Z=\frac12\int_{S_a^2}\zeta^2\,dA.
\tag{7.2}
$$

The equality for $E$ uses $|\mathbf{u}|=|\nabla_h\psi|$ and integration by parts. $E$ has units $\mathrm{m^4\,s^{-2}}$ and $Z$ has units $\mathrm{m^2\,s^{-2}}$. Dividing by $4\pi a^2$ gives surface-mean quantities; multiplying by the constant areal mass $\rho_0H$ gives physical total energy.

For smooth scalars $A,B,C$, integration by parts yields the cyclic Jacobian identity

$$
\int A J(B,C)\,dA=\int B J(C,A)\,dA=\int C J(A,B)\,dA.
$$

For example, integrate $A(\partial_\lambda B\,\partial_\phi C-\partial_\phi B\,\partial_\lambda C)$ by parts; the metric factor in $dA$ cancels the denominator in (6.6), mixed second derivatives cancel, longitude is periodic, and pole terms vanish for smooth fields. Since $J(\psi,\psi)=0$, this gives $\int\psi J(\psi,Q)\,dA=0$. Integration by parts also gives $\int A\nabla_h^2B\,dA=\int B\nabla_h^2A\,dA=-\int\nabla_hA\cdot\nabla_hB\,dA$. The symmetry under exchanging $A$ and $B$ is called **self-adjointness**. In particular, differentiating $\zeta=\nabla_h^2\psi$ lets the two terms in $d(\int\psi\zeta\,dA)/dt$ be made equal, so

$$
\dot E=-\int\psi\,\partial_t\zeta\,dA
=\int\psi J(\psi,Q)\,dA=0.
$$

The overdot means ordinary time derivative of a global quantity. Thus the pressure-free vorticity formulation still conserves kinetic energy.

Relative enstrophy has $\dot Z=-\int\zeta J(\psi,\zeta)\,dA-\int\zeta J(\psi,f)\,dA$. The first term vanishes by the cyclic identity. For the second, use $J(\psi,f)=2\Omega\partial_\lambda\psi/a^2$. If $I=\int(\nabla_h^2\psi)\partial_\lambda\psi\,dA$, self-adjointness and commutation of $\nabla_h^2$ with $\partial_\lambda$ give

$$
I=\int\psi\,\partial_\lambda\nabla_h^2\psi\,dA
=-\int(\partial_\lambda\psi)\nabla_h^2\psi\,dA=-I.
$$

Therefore $I=0$ and $\dot Z=0$ as well. This additional quadratic conservation uses the spherical planetary-vorticity profile. The general parcel invariants in (7.1) involve $Q$, not $\zeta$: higher relative-vorticity moments are not generally conserved when parcels cross latitude. This qualifies the statement about higher moments on p. 3 of the supplied notes.

## Scale transfer and why two sinks are useful

**Result and motivation.** Simultaneous energy and enstrophy conservation constrains nonlinear transfer between spatial scales. It motivates removing energy at large scales and enstrophy near the resolution limit, without making either transfer direction a theorem for every flow. [@Vallis2006, sec. 8.3; @BarotropicNotes, pp. 3-4]

For a Laplacian eigenmode with $-\nabla_h^2\psi=\kappa^2\psi$, $\kappa>0$ is an inverse length. Since vorticity adds two spatial derivatives while velocity adds one, the mode contributions satisfy $Z_\kappa=\kappa^2E_\kappa$. The harmonic construction in the next chapter makes this precise on the sphere. Enstrophy thus weights short scales more strongly than energy.

A simple three-scale exchange illustrates the constraint. Let $\kappa_1<\kappa_2<\kappa_3$, and suppose the middle scale loses energy $\Delta>0$, so $\delta E_2=-\Delta$. If the exchange conserves $E$ and $Z$,

$$
\delta E_1+\delta E_3=\Delta,
\qquad \kappa_1^2\delta E_1+\kappa_3^2\delta E_3=\kappa_2^2\Delta.
$$

Solving these two equations gives

[]{#law-transfer}
$$
\delta E_1=\frac{\kappa_3^2-\kappa_2^2}{\kappa_3^2-\kappa_1^2}\Delta,
\qquad
\delta E_3=\frac{\kappa_2^2-\kappa_1^2}{\kappa_3^2-\kappa_1^2}\Delta.
\tag{7.3}
$$

Both receivers gain energy. This calculation alone neither proves a cascade nor says which receiver gains more for arbitrary scale spacing. In forced, approximately homogeneous two-dimensional turbulence with separated forcing and dissipation scales, the standard statistical picture is a net **inverse energy transfer** toward larger scales and a **direct enstrophy transfer** toward smaller scales. A **cascade** means sustained transfer through a range of scales, not just one interaction. Rotation, boundaries, finite domains, and anisotropic forcing can modify this picture.

At finite resolution, unresolved enstrophy transfer motivates a short-scale sink. A large-scale sink prevents accumulation of transferred energy in the largest available modes during sustained forcing. Linear drag and hyperdiffusion serve these different purposes. Their use is a closure choice, not a derivation of molecular friction from the inviscid BVE.

## Eddy fluxes and mean jets

**Result and motivation.** Eddies can accelerate a mean current through momentum-flux convergence even when forcing has no imposed zonal-mean component. Random forcing need not produce a random-looking time mean. [@Vallis2006, sec. 12.1; @VallisEtAl2004, sec. 2]

Use a local plane periodic in $x$ with zonal period $L_x$. Define the **zonal mean** $\overline{b}(y,t)=L_x^{-1}\int_0^{L_x}b(x,y,t)\,dx$ and **eddy** departure $b'=b-\overline b$. Let $U=\overline u$. Mean continuity gives $\partial_y\overline v=0$; assume zero net meridional transport, so $\overline v=0$. For the inviscid momentum equation with linear drag $-r\mathbf{u}$ and applied horizontal acceleration $\mathbf{F}$, zonal averaging yields

[]{#law-meanjet}
$$
\partial_tU=-\partial_y\overline{u'v'}-rU+\overline{F_x}.
\tag{7.4}
$$

Here $r\geq0$ is the drag rate ($\mathrm{s^{-1}}$), and $\overline{u'v'}$ is the northward flux of eastward momentum per unit mass. To derive the flux term, use non-divergence to write $u\partial_xu+v\partial_yu=\partial_x(u^2)+\partial_y(uv)$. The $x$ derivative and mean pressure gradient average to zero; $f\overline v=0$. Decomposing $uv$ then leaves $\overline{u'v'}$.

Where the eddy momentum flux decreases northward, its convergence accelerates the mean eastward current. Eddies exchange momentum with the mean; they do not create net momentum through the nonlinear term in a closed periodic channel. Equation (7.4) is a planar teaching example. On the sphere, the corresponding eddy flux convergence includes $-(a\cos^2\phi)^{-1}\partial_\phi(\cos^2\phi\,\overline{u'v'})$; replacing $y$ with $a\phi$ alone misses the metric factor.

The competition between nonlinear transport and Rossby-wave propagation also suggests a scale [@Vallis2006, sec. 9.1.1]. At eddy size $L_e$, estimate a turnover rate $U_e/L_e$ and an intrinsic Rossby frequency of order $\beta L_e$, where $U_e$ is an eddy speed. Equating them gives the **Rhines scale** $L_\beta\sim\sqrt{U_e/\beta}$ for $\beta>0$. The symbol $\sim$ here means an order-of-magnitude balance. It suggests when wave effects can organize turbulence into anisotropic structures and jets; it does not uniquely predict jet spacing for the localized, damped spherical model.

## Chapter summary

- Area integrals of functions of absolute vorticity are ideal invariants. Absolute enstrophy is quadratic in $Q$.
- Kinetic energy $E=-\tfrac12\int\psi\zeta\,dA$ and relative enstrophy $Z=\tfrac12\int\zeta^2\,dA$ are also conserved by the ideal spherical BVE.
- $Z_\kappa=\kappa^2E_\kappa$ constrains transfers. The three-scale calculation (7.3) motivates, but does not prove, dual cascade behavior.
- Eddy momentum-flux convergence accelerates a mean jet. The Rhines scale estimates competition between advection and planetary Rossby waves.

# Spherical harmonics, inversion, and dissipation

## Harmonics as Laplacian eigenfunctions

**Result and motivation.** Spherical harmonics diagonalize the surface Laplacian. They make streamfunction inversion and scale-selective damping algebraic operations. [@ArfkenWeber2005, secs. 9.3, 12.3-12.6; @BarotropicNotes, sec. 3]

Define solid angle $d\omega=dA/a^2=\cos\phi\,d\phi\,d\lambda$; the lower-case $\omega$ in this measure is not the vorticity vector. A **spherical harmonic** $Y_\ell^m$ is a smooth angular function satisfying

[]{#law-harmonic-eigenvalue}
$$
\nabla_h^2Y_\ell^m=-\kappa_\ell^2Y_\ell^m,
\qquad \kappa_\ell^2=\frac{\ell(\ell+1)}{a^2},
\quad \ell=0,1,\ldots,\quad -\ell\leq m\leq\ell.
\tag{8.1}
$$

The nonnegative integer $\ell$ is **degree** or total wavenumber; the integer $m$ is **order** or zonal wavenumber. To obtain this structure, separate an angular eigenfunction as $Y=\Theta(\phi)e^{im\lambda}$. Periodicity in longitude forces integer $m$. Substitution into (6.2), followed by $\mu=\sin\phi$, gives

$$
\frac{d}{d\mu}\left[(1-\mu^2)\frac{d\Theta}{d\mu}\right]
+\left[a^2\kappa^2-\frac{m^2}{1-\mu^2}\right]\Theta=0.
$$

Regularity at both poles selects $a^2\kappa^2=\ell(\ell+1)$ and associated Legendre functions $P_\ell^m(\mu)$. This is an eigenvalue problem: allowed smooth functions occur only for particular eigenvalues. For $m\geq0$, an explicit convention is

$$
\begin{aligned}
P_\ell(\mu)&=\frac{1}{2^\ell\ell!}\frac{d^\ell}{d\mu^\ell}(\mu^2-1)^\ell,\\
P_\ell^m(\mu)&=(-1)^m(1-\mu^2)^{m/2}\frac{d^mP_\ell}{d\mu^m},\\
Y_\ell^m&=\left[\frac{2\ell+1}{4\pi}\frac{(\ell-m)!}{(\ell+m)!}\right]^{1/2}
P_\ell^m(\sin\phi)e^{im\lambda}.
\end{aligned}
$$

Here $n!$ denotes the product of integers from 1 to $n$, with $0!=1$. Negative orders are defined by $Y_\ell^{-m}=(-1)^m\overline{Y_\ell^m}$; an overbar on a complex quantity means complex conjugation, whereas an overbar on a flow field in Chapter 7 meant zonal averaging. This is the standard orthonormal, Condon-Shortley phase convention:

[]{#law-harmonic-expansion}
$$
\begin{aligned}
\int Y_\ell^m\overline{Y_{\ell'}^{m'}}\,d\omega&=\delta_{\ell\ell'}\delta_{mm'},\\
\zeta&=\sum_{\ell=0}^{\infty}\sum_{m=-\ell}^{\ell}\widehat\zeta_\ell^mY_\ell^m,
\qquad \widehat\zeta_\ell^m=\int\zeta\overline{Y_\ell^m}\,d\omega.
\end{aligned}\tag{8.2}
$$

The Kronecker deltas are 1 when their indices agree and 0 otherwise. A real field requires $\widehat\zeta_\ell^{-m}=(-1)^m\overline{\widehat\zeta_\ell^m}$. The supplied barotropic notes use a different normalization and phase pairing (their eqs. 15-17). Their coefficient values and conjugacy rule must be interpreted in their own convention; the physical field and eigenvalues are unchanged. In particular, the notes' constant harmonic is $1/\sqrt2$, whereas (8.2) uses $1/\sqrt{4\pi}$.

## Inversion and the spectral energy weights

**Result and motivation.** Nonconstant vorticity modes determine streamfunction modes uniquely. The constant mode cannot be inverted and must be absent from relative vorticity. [@BarotropicNotes, pp. 1, 7-8; @ArfkenWeber2005, secs. 10.4-10.5]

Insert the expansion (8.2) into $\nabla_h^2\psi=\zeta$ and match orthogonal coefficients:

[]{#law-spectral-inversion}
$$
\widehat\psi_\ell^m=-\frac{a^2}{\ell(\ell+1)}\widehat\zeta_\ell^m
\quad(\ell\geq1),\qquad
\widehat\zeta_0^0=0,\qquad\widehat\psi_0^0=0.
\tag{8.3}
$$

The last equality fixes the gauge, while the preceding zero is a compatibility condition. They are logically different. A constant added to $\psi$ changes no velocity. A constant added to relative vorticity cannot be the curl of a smooth globally defined tangent flow on the sphere.

Orthogonality gives **Parseval's identity**, $\int|\zeta|^2d\omega=\sum_{\ell,m}|\widehat\zeta_\ell^m|^2$. Since $dA=a^2d\omega$, (7.2) becomes

[]{#law-spectral-budgets}
$$
E=\frac{a^4}{2}\sum_{\ell\geq1,m}
\frac{|\widehat\zeta_\ell^m|^2}{\ell(\ell+1)},
\qquad
Z=\frac{a^2}{2}\sum_{\ell\geq1,m}|\widehat\zeta_\ell^m|^2.
\tag{8.4}
$$

Define $E_\ell,Z_\ell$ by the corresponding sums over $m$ at fixed $\ell$. Then $Z_\ell=\kappa_\ell^2E_\ell$, as used in (7.3). Larger $\ell$ means smaller horizontal structure; $a/\sqrt{\ell(\ell+1)}$ is an inverse-wavenumber length, not a unique wavelength or grid spacing.

## Truncation and evaluation of nonlinear transport

**Result and motivation.** A finite harmonic expansion defines the represented state, while a sufficiently fine transform grid evaluates the nonlinear term. These are different resolutions. [@BarotropicNotes, pp. 4-8]

**Triangular truncation** at degree $N$ retains $0\leq\ell\leq N$ and all $|m|\leq\ell$, often denoted T$N$. There are $(N+1)^2$ real degrees of freedom for a real scalar before imposing its mean constraint. Define $\mathcal{P}_N$ to be orthogonal projection onto these retained modes. The ideal projected equation is

$$
\partial_t\zeta_N=-\mathcal{P}_NJ(\psi_N,\zeta_N+f),
\qquad \nabla_h^2\psi_N=\zeta_N.
$$

The subscript $N$ denotes a truncated field. The nonlinear product produces degrees outside the retained set. One must compute its projection, rather than assume that the product is itself truncated.

A **pseudospectral** or spectral-transform method inverts vorticity in harmonic space, transforms to a longitude-latitude grid, forms velocity-vorticity products there, and transforms the resulting tendency back. Sampling too coarsely causes **aliasing**: unresolved product modes masquerade as retained modes. For the triangular spherical transform model in the notes, the quadratic de-aliasing requirements are

[]{#law-dealias}
$$
N_\lambda\geq3N+1,\qquad
N_\phi\geq\left\lceil\frac{3N+1}{2}\right\rceil.
\tag{8.5}
$$

Here $N_\lambda$ is the number of equally spaced longitudes, $N_\phi$ the number of Gaussian latitudes, and $\lceil x\rceil$ the smallest integer at least $x$. **Gaussian latitudes** are $\phi_j=\arcsin\mu_j$, where $\mu_j$ are roots of the Legendre polynomial $P_{N_\phi}$. Their weights $w_j>0$ give $\int_{-1}^{1}g(\mu)d\mu=\sum_jw_jg(\mu_j)$ for polynomial $g$ of degree at most $2N_\phi-1$. Since $d\omega=d\lambda\,d\mu$, this quadrature is adapted to the spherical transform.

In longitude, two factors with wavenumbers at most $N$ have product modes up to $2N$. Projecting onto a mode up to $N$ involves integration of a trigonometric polynomial with wavenumbers up to $3N$; more than $3N$ equally spaced points avoid spurious nonzero discrete averages. The latitude requirement in (8.5) is the spherical-transform counterpart derived in the supplied notes. T85 therefore admits $N_\lambda=256$, $N_\phi=128$. These conditions concern quadratic products; they do not guarantee that arbitrary localized functions, higher nonlinearities, or time integration are exact.

## Drag, hyperdiffusion, and their signs

**Result and motivation.** Dissipation should damp every retained nonconstant mode. Writing it with the nonnegative operator $-\nabla_h^2$ makes this sign transparent. [@BarotropicNotes, eq. 12 and pp. 3-4, 11]

Let $r\geq0$ be a linear drag rate, $p$ a positive integer diffusion order, and $\nu_p\geq0$ a hyperdiffusion coefficient ($\mathrm{m^{2p}\,s^{-1}}$). Define the vorticity dissipation operator

[]{#law-dissipation}
$$
\mathcal{D}(\zeta)=-r\zeta-\nu_p(-\nabla_h^2)^p\zeta.
\tag{8.6}
$$

For $p=1$, the second term is ordinary diffusion $+\nu_1\nabla_h^2\zeta$. For $p=2$, it is $-\nu_2\nabla_h^4\zeta$, called biharmonic diffusion. Its origin here is a small-scale model closure; it is not an exact substitute for unresolved three-dimensional turbulence. On each mode,

[]{#law-modal-damping}
$$
\partial_t\widehat\zeta_\ell^m\big|_{\mathcal D}
=-\gamma_\ell\widehat\zeta_\ell^m,
\qquad \gamma_\ell=r+\nu_p\kappa_\ell^{2p}\geq0.
\tag{8.7}
$$

A pure damped mode decays as $e^{-\gamma_\ell t}$, and its squared amplitude decays as $e^{-2\gamma_\ell t}$. Both energy and relative enstrophy decrease under this operator. Increasing $p$ concentrates damping near the high-degree end. An alternative specifies a cutoff damping rate $\gamma_*>0$ and sets $\nu_p=\gamma_*/\kappa_N^{2p}$, so the hyperdiffusive damping rate is $\gamma_*[\ell(\ell+1)/(N(N+1))]^p$. A cutoff damping rate has units $\mathrm{s^{-1}}$ and must not be confused with the dimensional $\nu_p$.

## Chapter summary

- Harmonics $Y_\ell^m$ are smooth Laplacian eigenfunctions with eigenvalues $-\ell(\ell+1)/a^2$. Normalization and phase conventions affect coefficients.
- Inversion is division by those eigenvalues for $\ell\geq1$. The zero vorticity mode is excluded; the zero streamfunction mode is a gauge.
- Spectral energy gives more weight to large spatial scales than enstrophy. Their exact weights are (8.4).
- T$N$ truncation and the transform grid are distinct. Adequate Gaussian and longitude sampling prevent quadratic aliasing under the stated transform assumptions.
- Linear drag and hyperdiffusion give nonnegative modal damping rates (8.7). Their coefficients have different units and scale dependence.

# Stochastic stirring and the closed forced model

## What a random forcing specifies

**Result and motivation.** Stochastic stirring is a statistical model for omitted eddy input, not a new conservation law. Its distribution, covariance, spatial structure, and memory must be specified separately. [@VallisEtAl2004, sec. 3 and appendix; @ArfkenWeber2005, secs. 19.1-19.2]

Let $S(\lambda,\phi,t)$ be an additive vorticity tendency, with units $\mathrm{s^{-2}}$. The **stochastically stirred, damped BVE** is

[]{#law-forced-bve}
$$
\boxed{\begin{aligned}
\partial_t\zeta+J(\psi,\zeta+2\Omega\sin\phi)
&=S-r\zeta-\nu_p(-\nabla_h^2)^p\zeta,\\
\nabla_h^2\psi&=\zeta,\qquad \int\zeta\,dA=\int\psi\,dA=0.
\end{aligned}}\tag{9.1}
$$

Initial vorticity, compatible forcing, the radius and rotation rate, drag and diffusion parameters, and a law for $S$ complete the model. Spatial smoothness and zero global-mean relative vorticity remain necessary. In particular, $\int S\,dA=0$ prevents the forcing from driving a noninvertible constant vorticity mode. A curl of a smooth globally defined horizontal force automatically has this property; a directly prescribed scalar forcing must enforce it.

A **random variable** takes values according to a specified probability law. $\mathbb{E}[X]$ denotes its ensemble mean, averaging over possible realizations. For real $X,Y$, define

$$
\operatorname{Var}(X)=\mathbb{E}[(X-\mathbb{E}X)^2],\qquad
\operatorname{Cov}(X,Y)=\mathbb{E}[(X-\mathbb{E}X)(Y-\mathbb{E}Y)].
$$

The square root of variance is standard deviation. Independence implies zero covariance when moments exist, but zero covariance does not generally imply independence. A realization is one sampled forcing history. A **stationary** process has statistics unchanged by shifting all times together; second-order stationarity requires only constant mean and covariance that depends on time lag. The **autocorrelation** is covariance divided by variance for a nonzero-variance stationary scalar process. A finite correlation time describes memory in the imposed forcing, not necessarily the memory of the fluid response.

## A finite-memory recurrence and its variance

**Result and motivation.** An autoregressive recurrence produces exponentially decaying time correlations. The innovation amplitude must include $\sqrt{1-\alpha^2}$ to keep the stationary variance fixed as the time step changes. [@VallisEtAl2004, appendix, eqs. A.6-A.8]

Consider one real forcing component $s^n$ at times $t_n=n\Delta t$, with time step $\Delta t>0$. Let $\tau>0$ be the desired memory time, $\sigma_s$ a specified stationary standard deviation, and $\xi^n$ independent identically distributed random variables, independent of the past, with mean zero and variance one. Define

[]{#law-ar1}
$$
s^{n+1}=\alpha s^n+\sigma_s\sqrt{1-\alpha^2}\,\xi^n,
\qquad \alpha=e^{-\Delta t/\tau}.
\tag{9.2}
$$

This is an **autoregressive process of order one**, abbreviated AR(1): the next value uses only the previous value and a fresh **innovation** $\xi^n$. The coefficient $\alpha$ is dimensionless and between zero and one. Here $s^n$ and $\sigma_s$ have units $\mathrm{s^{-2}}$, while $\xi^n$ is dimensionless.

Taking expectations gives $\mathbb{E}s^n=\alpha^n\mathbb{E}s^0$. Independence makes the cross term in the variance vanish, so if $V_n=\operatorname{Var}(s^n)$,

$$
V_{n+1}=\alpha^2V_n+\sigma_s^2(1-\alpha^2),\qquad
V_n=\alpha^{2n}V_0+\sigma_s^2(1-\alpha^{2n}).
$$

At stationarity $V_n=\sigma_s^2$. Iterating (9.2) over $k$ steps, future innovations have zero covariance with $s^n$, giving

[]{#law-ar-covariance}
$$
\operatorname{Cov}(s^{n+k},s^n)
=\sigma_s^2\alpha^{|k|}
=\sigma_s^2e^{-|k|\Delta t/\tau}.
\tag{9.3}
$$

The nonnegative integer $k$ counts lag steps; the absolute value extends the covariance symmetrically to negative lag. At elapsed lag $\tau$ the correlation is $e^{-1}$: $\tau$ is an **e-folding time**. Starting at $s^0=0$ produces a forcing spinup in its variance. For Gaussian innovations, drawing $s^0$ from the Gaussian law with mean zero and variance $\sigma_s^2$ gives stationary forcing immediately. A uniform-innovation recurrence has a different stationary distribution; matching initial variance alone does not make its full distribution stationary.

As a concrete variance check, choose $\alpha=1/2$. The innovation coefficient is $\sqrt{3}/2$ times $\sigma_s$, so one step preserves variance because $1/4+3/4=1$. Dropping the square root factor would instead give stationary variance $\sigma_s^2/(1-\alpha^2)$, changing the forcing when $\Delta t$ changes.

## Gaussian OU forcing and bounded innovations

**Result and motivation.** Gaussian innovations make (9.2) an exact sample of an Ornstein-Uhlenbeck process. Bounded uniform innovations can preserve the same mean and covariance while changing higher statistics. [@VallisEtAl2004, appendix; @ArfkenWeber2005, secs. 19.2, 19.5]

A Gaussian or normal law with mean zero and variance one has density $(2\pi)^{-1/2}e^{-x^2/2}$. A **Wiener process** $W_t$ has independent Gaussian increments with mean zero and variance equal to elapsed time. It has units $\mathrm{s^{1/2}}$ when $t$ is dimensional. Define the **Ornstein-Uhlenbeck (OU) process** through

[]{#law-ou}
$$
ds=-\frac{s}{\tau}\,dt+\sigma_s\sqrt{\frac{2}{\tau}}\,dW_t.
\tag{9.4}
$$

This notation is interpreted through a stochastic integral, not an ordinary time derivative of $W_t$. For the deterministic integrand used here, the integral is the mean-square limit of sums of the integrand times independent Wiener increments. Such an integral has zero mean and variance equal to the integral of the squared integrand, directly from independence and $\operatorname{Var}(\Delta W)=\Delta t$.

Multiply (9.4) by $e^{t/\tau}$ and integrate from $t$ to $t+\Delta t$:

$$
s(t+\Delta t)=e^{-\Delta t/\tau}s(t)
+\sigma_s\sqrt{\frac{2}{\tau}}
\int_t^{t+\Delta t}e^{-(t+\Delta t-u)/\tau}\,dW_u.
$$

The last term is Gaussian, independent of the past, and has variance

$$
\frac{2\sigma_s^2}{\tau}\int_t^{t+\Delta t}
e^{-2(t+\Delta t-u)/\tau}du
=\sigma_s^2(1-e^{-2\Delta t/\tau}).
$$

This recovers (9.2) with Gaussian $\xi^n$. It derives the exact sampled OU law, rather than a forward-Euler approximation to it.

For a uniformly distributed $\eta$ on $[-1,1]$, its density is $1/2$ there and zero elsewhere. Direct integration gives $\mathbb{E}\eta=0$, $\mathbb{E}\eta^2=\tfrac12\int_{-1}^{1}x^2dx=1/3$. Thus $\xi=\sqrt3\eta$ has unit variance. If the recurrence instead uses $A\sqrt{1-\alpha^2}\eta^n$, its stationary variance is $A^2/3$, not $A^2$. For independent real and imaginary components of a complex innovation, each uniform on $[-1,1]$, the pre-localization stationary mean square complex amplitude is $2A^2/3$. That statement concerns coefficient components, not the variance at a physical grid point after transforms and localization.

Ideal temporal **white noise** is the formal derivative $dW_t/dt$: it has no ordinary pointwise value and is defined by its time integrals, which are independent Wiener increments over disjoint intervals. Its intensity specifies increment variance per unit time. Small $\tau/\Delta t$ makes successive sampled forcing values nearly independent. That does **not** by itself define a finite-strength continuous white-noise forcing in the BVE. At fixed $\sigma_s^2$, OU covariance is $\sigma_s^2e^{-|t|/\tau}$, whose integral over all lags is $2\sigma_s^2\tau\to0$ as $\tau\to0$. Holding white-noise intensity fixed would require scaling $\sigma_s^2\tau$ to a nonzero constant. The distinction matters when comparing forcing amplitudes across correlation times.

## Spatial masks, localization, and covariance

**Result and motivation.** Spectral selection sets initial forcing scales, while multiplication by a spatial envelope localizes forcing and mixes those scales. Removing the global mean preserves vorticity invertibility. [@VallisEtAl2004, sec. 3; @BarotropicNotes, sec. 3]

Let $\mathbf{b}^n$ be a real vector collecting independent random coefficient components at step $n$, with zero mean and covariance matrix $\mathbf{C}_b=\mathbb{E}[\mathbf{b}^n(\mathbf{b}^n)^T]$. The superscript $T$ denotes matrix transpose. Complex coefficients can always be represented by their real and imaginary components in this vector. Let $\mathcal{M}$ select a prescribed band of harmonic modes, $\mathcal{T}$ synthesize a grid field from coefficients, and $L(\lambda,\phi)$ be a fixed dimensionless envelope. Let $\mathcal{P}_0$ remove the spherical mean. Let $\mathcal{A}$ analyze a grid field back into a real vector of retained spectral coefficient components. The combined linear map $\mathcal{L}$ therefore produces a coefficient-vector innovation proportional to

$$
\mathcal{L}\mathbf{b}^n
=\mathcal{A}\mathcal{P}_0\mathcal{P}_N\big[L\,\mathcal{T}\mathcal{M}\mathbf{b}^n\big].
$$

Grid quadrature and transform conventions are part of this map. With forcing amplitude $A$ ($\mathrm{s^{-2}}$), the vector or field recurrence can be written

[]{#law-spatial-ar}
$$
\mathbf{s}^{n+1}=\alpha\mathbf{s}^n
+A\sqrt{1-\alpha^2}\,\mathcal{L}\mathbf{b}^n,
\qquad
\mathbf{C}_s=A^2\mathcal{L}\mathbf{C}_b\mathcal{L}^{T}
\quad\text{at stationarity}.
\tag{9.5}
$$

Here $\mathbf{s}^n$ is the real vector of retained forcing coefficient components, $\mathbf{C}_s$ its covariance, and $\mathcal{L}^T$ the transpose in this real component representation. The result follows by the same variance recurrence as (9.2), now applied to each pair of components. It shows why $A$ alone does not determine pointwise root-mean-square forcing. The number of forced modes, normalization, innovation variance, envelope, projection, and mean removal all enter.

A Gaussian-shaped envelope in latitude and a localized enhancement in longitude can be written

$$
L(\lambda,\phi)=\exp\left[-\frac{(\phi-\phi_c)^2}{2w_\phi^2}\right]
\left\{1+B\exp\left[-\frac{d_{2\pi}(\lambda-\lambda_c)^2}{2w_\lambda^2}\right]\right\}.
$$

The centers are $\phi_c,\lambda_c$, the positive angular widths are $w_\phi,w_\lambda$, $B$ controls the longitudinal enhancement, and $d_{2\pi}$ wraps an angular difference into $[-\pi,\pi]$. All angles in this expression must use the same units. $B=0$ is zonally uniform in its envelope; it is not globally uniform because latitude dependence remains.

Multiplication by $L$ convolves harmonic coefficients, so the final forcing is not confined to the initially selected band. Nor does excluding initial $m=0$ coefficients guarantee a final zero zonal-mean component after a longitude-dependent envelope. Removing $\ell=0$ enforces zero *global* mean, a different condition. A sharply or imperfectly smooth envelope also adds high-degree content; finite spectral projection defines what the numerical model actually retains.

## Forced budgets, stationarity, and state information

**Result and motivation.** The stirring enters energy and enstrophy through correlations with the flow. Its amplitude is not an energy-input rate. Finite-memory forcing also carries information beyond the instantaneous vorticity field. [@VallisEtAl2004, secs. 2-3 and appendix; @Vallis2006, sec. 8.3]

For the colored-in-time forcing above, the forcing state is an ordinary time-dependent input to the vorticity equation; ordinary product-rule energy budgets apply. Set $\mathcal{D}$ as in (8.6). The ideal transport terms cancel as in Chapter 7, giving

[]{#law-forced-budgets}
$$
\begin{aligned}
\dot E&=-\int\psi S\,dA-2rE
-\nu_pa^2\sum_{\ell\geq1,m}\kappa_\ell^{2p-2}|\widehat\zeta_\ell^m|^2,\\
\dot Z&=\int\zeta S\,dA-2rZ
-\nu_pa^2\sum_{\ell\geq1,m}\kappa_\ell^{2p}|\widehat\zeta_\ell^m|^2.
\end{aligned}\tag{9.6}
$$

The energy forcing sign comes from $\dot E=-\int\psi\partial_t\zeta\,dA$; the enstrophy sign comes from $\dot Z=\int\zeta\partial_t\zeta\,dA$. The energy forcing integral has units $\mathrm{m^4\,s^{-3}}$. The coefficient amplitude $A$ instead has units $\mathrm{s^{-2}}$, so they cannot be identified. Zero ensemble-mean $S$ does not make the energy input zero: $\psi$ responds to $S$ and can correlate with it. An instantaneous realization need not inject positive energy at every time.

A **statistical steady state** has time-independent statistics after transient adjustment, even while individual fields continue evolving. If such a state exists with finite moments, ensemble averaging (9.6) balances mean forcing input against mean dissipation. These identities do not prove existence, uniqueness, or an adequate spinup duration. If the vorticity equation were instead driven directly by ideal temporal white noise, stochastic quadratic-variation terms would be needed in the mean budgets; (9.6) is stated for finite-memory forcing.

A process is **Markov** when its future probability law, conditional on its present state, does not need earlier states. The pair $(\zeta,\mathbf{s})$, together with fixed parameters, provides the physical state for a finite-memory stirring model; a time-discrete integrator may additionally need previous time levels. Vorticity alone generally does not: two equal vorticity fields accompanied by different stirring states have different immediate tendencies. Thus even perfect observations of $\zeta(t)$ alone need not specify a unique deterministic $\zeta(t+\Delta t)$. This is a consequence of the forcing model, separate from numerical error or chaotic sensitivity.

## Chapter summary

- The closed forced BVE is (9.1), with zero-mean vorticity, a streamfunction gauge, and a specified stirring law. The forcing units are vorticity per time.
- The AR(1) process (9.2) has stationary covariance (9.3). Its innovation normalization fixes variance as the time step changes.
- Gaussian innovations give exact OU samples. Uniform innovations have different higher moments and require explicit variance normalization.
- Spectral masks, localization, transform normalization, and global-mean removal determine the final forcing covariance (9.5).
- Energy and enstrophy budgets (9.6) involve flow-forcing correlations. Statistical balance is not a proof of stationarity. Finite-memory stirring is part of the dynamical state.

# Relating the theory to this repository

## Reading the implemented equation

**Result and motivation.** The repository evolves relative vorticity on a sphere, reconstructs a non-divergent wind, and adds localized, finite-memory stirring. Runtime configuration determines the numerical experiment; the equations do not determine one universal parameter set.

The evidence below is the local source inspected on 21 November 2026. Repository-specific facts in this chapter come from code, rather than the textbooks. The submodule has local changes, so its commit identifier alone is not a complete provenance record. Source file hashes are recorded in the accompanying build record.

The main call path is `sim/barotropic_stirring.py`, then Isca's `barotropic_dynamics.F90`, `stirring.F90`, and `spectral_damping.F90`. These files are linked in the directory README. The diagnostic called `vor` is $\zeta$. The internal diagnostic called `pv` is $\zeta+f$, not thickness-normalized shallow-water $q$ with variable $h$. Velocity and `stream` correspond to (6.3)-(6.4).

The wrapper requests T85 by default, with 128 Gaussian latitudes and 256 longitudes, and sets a 600 s atmospheric step. It sets diffusion order $p=2$, cutoff damping rate $1.157\times10^{-4}\ \mathrm{s^{-1}}$, and linear drag $r=1.929\times10^{-6}\ \mathrm{s^{-1}}$. These are source defaults in this wrapper, not a claim about every saved run. The associated drag time is $1/r\simeq6.00$ days and the cutoff hyperdiffusion time is about 2.40 hours. The configured `resolution_dependent` option implements the cutoff-rate form following (8.7); its `damping_coeff` is not a dimensional $\nu_2$.

The notes describe leapfrog stepping: $\zeta^{n+1}-\zeta^{n-1}=2\Delta t\,\mathcal{R}^n$ for an undamped tendency $\mathcal{R}^n$. That recurrence supports both a physical solution and an odd-even computational mode. A Robert-Asselin time filter suppresses the latter; implicit spectral damping controls fast decaying modes. In the inspected code, damping modifies the preexisting tendency before `stirring` adds its increment. Therefore the continuous equation (9.1) identifies modeled terms, but is not a complete algebraic description of the time-discrete update. No stability guarantee follows from a quoted default time step.

## Reading the stirring implementation

**Result and motivation.** The code implements the AR(1) covariance structure with bounded uniform innovations, followed by spatial localization and projection. Its amplitude is not a prescribed energy injection or pointwise standard deviation.

In `stirring.F90`, the factors `bstir` and `astir` are $\alpha=e^{-\Delta t/\tau}$ and $\sqrt{1-\alpha^2}$. The innovations are complex numbers whose real and imaginary parts are each drawn uniformly from $[-1,1]$ and multiplied by the configured amplitude. The default initial spectral mask uses stored indices $(m,n)$ with total degree $\ell=m+n$, requiring $m>3$ and $9<\ell<15$. It initially selects degrees 10 through 14 and positive orders 4 or greater. Reality is handled by the transform's coefficient storage convention.

The code transforms this innovation to grid space, multiplies by the fixed latitude-longitude envelope, transforms back, and sets the $(0,0)$ component to zero. It then updates `s_stir = bstir*s_stir + new_stirring`. This is the map order described by (9.5), with the actual finite transforms providing the projection. The spectral mask acts before localization. The final forcing can contain other degrees and orders, including $m=0$ when longitudinal modulation is used. The global mean remains removed.

The wrapper defaults are amplitude $A=10^{-10}\ \mathrm{s^{-2}}$, memory time $\tau=172800\ \mathrm{s}=2$ days, latitude center $45$ degrees, latitude width $12$ degrees, longitude center $180$ degrees, longitude width $45$ degrees, and enhancement $B=0.4$. The code evaluates envelope ratios in degrees; ratios agree with the radian expression when all centers and widths are converted consistently. The unlocalized coefficient variance per real component tends to $A^2/3$. Localization and transforms determine physical-space variance, so the wrapper amplitude cannot be read as a gridpoint root-mean-square forcing.

Fresh stirring starts with zero forcing state unless a restart is loaded. A restart stores the current forcing coefficients and random-generator state. Reproduction therefore needs the realized namelist, initial fields, forcing state or reproducible generator initialization, time stepping, code revision and patches, and transform convention. Matching only nominal amplitude and correlation time does not reproduce an individual trajectory. A daily time average of a diagnostic is also not an instantaneous BVE state: averaging and nonlinear advection do not commute.

## Chapter summary

- The local model matches the non-divergent spherical vorticity framework. `pv` denotes absolute vorticity in this implementation.
- The wrapper sets defaults, while saved configuration and restarts identify an experiment. The cutoff damping coefficient is a rate.
- Stirring uses uniform complex-component innovations, pre-localization spectral selection, grid-space localization, mean removal, and AR(1) memory.
- Continuous equations, the discrete update, instantaneous fields, and time-averaged diagnostics are different objects. Preserving these distinctions is necessary when interpreting simulations.

# Notation and source guide {.unnumbered}

## Core notation {.unnumbered}

**Result and motivation.** The same conventions apply throughout the derivation; source-specific alternatives require conversion.

| Symbol | Meaning and units |
|:---|:---|
| $t,\Delta t$ | Time and time step, $\mathrm{s}$ |
| $\mathbf{x},\mathbf{v}$ | Three-dimensional position, $\mathrm{m}$, and velocity, $\mathrm{m\,s^{-1}}$ |
| $\mathbf{u},u,v$ | Tangent velocity and its eastward and northward components, $\mathrm{m\,s^{-1}}$ |
| $\rho,p,\Phi$ | Density, $\mathrm{kg\,m^{-3}}$; pressure, $\mathrm{Pa}$; effective geopotential, $\mathrm{m^2\,s^{-2}}$ |
| $\boldsymbol{\Omega},f,\beta$ | Rotation vector, $\mathrm{s^{-1}}$; normal planetary vorticity, $\mathrm{s^{-1}}$; its local northward gradient, $\mathrm{m^{-1}\,s^{-1}}$ |
| $a,\lambda,\phi$ | Radius, $\mathrm{m}$; longitude and latitude, radians |
| $h,H$ | Layer thickness and fixed reference thickness, $\mathrm{m}$ |
| $\boldsymbol{\omega},\boldsymbol{\omega}_a$ | Relative and absolute vorticity vectors, $\mathrm{s^{-1}}$ |
| $\zeta,Q,q$ | Normal relative vorticity; normal absolute vorticity, both $\mathrm{s^{-1}}$; layer PV $Q/h$, $\mathrm{m^{-1}\,s^{-1}}$ |
| $\psi,J$ | Streamfunction, $\mathrm{m^2\,s^{-1}}$; spherical Jacobian (6.6) |
| $\ell,m,N$ | Harmonic degree, order, and truncation degree; dimensionless integers |
| $\kappa_\ell$ | Inverse-length wavenumber $\sqrt{\ell(\ell+1)}/a$, $\mathrm{m^{-1}}$ |
| $r,\nu_p,p$ | Drag rate, $\mathrm{s^{-1}}$; hyperdiffusivity, $\mathrm{m^{2p}\,s^{-1}}$; diffusion order (the symbol $p$ also denotes pressure outside diffusion formulas) |
| $S,A,\tau,\alpha$ | Vorticity forcing and its coefficient amplitude, $\mathrm{s^{-2}}$; correlation time, $\mathrm{s}$; AR persistence, dimensionless |
| $E,Z,Z_a$ | Area-integrated kinetic energy, relative enstrophy, and absolute enstrophy as in (7.1)-(7.2) |

## Source locations and limits {.unnumbered}

**Result and motivation.** Each derivation has a source locator, and extensions beyond the three requested PDFs are identified explicitly.

| Material | Primary source locations |
|:---|:---|
| Derivatives, operators, integral theorems | Arfken and Weber, secs. 1.6-1.12, 2.1-2.5 |
| Continuity, forces, incompressibility, energy | Vallis, secs. 1.1-1.4, 1.9-1.11 |
| Rotation, scaling, hydrostasy, geostrophy | Vallis, secs. 2.1-2.4, 2.7-2.9 |
| Layer thickness and potential vorticity | Vallis, secs. 3.1 and 3.6 |
| Vorticity, circulation, barotropic limit | Vallis, secs. 4.1-4.4; barotropic notes, pp. 1-3 |
| Rossby waves and turbulent transfer | Vallis, secs. 5.7, 8.3, 12.1 |
| Harmonics, inversion, transform model | Arfken and Weber, secs. 12.3-12.6; barotropic notes, pp. 4-8 |
| Hyperdiffusion and time stepping | Barotropic notes, pp. 3-4, 9, 11 |
| Random variables and normal law | Arfken and Weber, secs. 19.1-19.2, 19.5 |
| Finite-memory stirring and OU distinction | Vallis et al. (2004), sec. 3 and appendix, pp. 279-280 |
| Implementation and current defaults | Local code linked and hashed in the accompanying README and build record |

The barotropic notes' sentence equating the material derivatives of absolute and relative vorticity on p. 2 is not used: only their *partial time derivatives* agree. Their claim of a unique Poisson solution needs the compatibility and gauge conditions in (6.5). Their broad higher-moment statement is interpreted through (7.1); relative enstrophy has the additional spherical proof given above. These qualifications follow directly from the displayed equations, rather than an inferred attribution or an unverified correction list.

The unsigned barotropic PDF supplies no author or publication date on its pages. The bibliography therefore lists its title without inventing either. Stochastic forcing details are attributed to the supplementary local 2004 paper and code, not retroactively to those unsigned notes.

## Derivation checks {.unnumbered}

**Result and motivation.** These short reconstruction questions test the connections needed to read the forced equation. Their answers use only results derived above.

1. Why can an incompressible layer have changing absolute vorticity?
2. Why can $\partial_tf=0$ coexist with $D_hf/Dt\ne0$?
3. Why must the global-mean relative vorticity be zero on a sphere, while streamfunction mean can be chosen freely?
4. If $p=2$ and $\nu_2>0$, which sign of the fourth-derivative term damps a harmonic mode?
5. With uniform innovations on $[-1,1]$, is the coefficient amplitude $A$ the stationary standard deviation?
6. Why can two identical instantaneous vorticity fields evolve differently under colored stirring?

## Answers {.unnumbered}

**Result and motivation.** Each answer follows from a constraint or a budget, rather than a memorized name.

1. Three-dimensional incompressibility conserves column volume, not horizontal area. Horizontal convergence increases $h$; (5.2)-(5.3) increase $\zeta+f$ in proportion to $h$ while preserving $q$.
2. A parcel crosses a fixed spatial gradient: $D_hf/Dt=\mathbf{u}\cdot\nabla_h f$. On the local $\beta$-plane this is $\beta v$.
3. Integrating $\nabla_h^2\psi=\zeta$ on a closed sphere gives zero on the left. Adding a constant to $\psi$ changes neither its gradient nor its Laplacian; setting its mean fixes this freedom.
4. $-\nu_2\nabla_h^4\zeta$ gives modal tendency $-\nu_2\kappa_\ell^4\widehat\zeta_\ell^m$. The opposite sign grows modes.
5. No. The scalar recurrence gives variance $A^2/3$, hence standard deviation $A/\sqrt3$, before spatial mixing. Physical-space statistics also depend on transforms and localization.
6. Their current forcing states can differ, so their right-hand sides in (9.1) differ. A vorticity-only observation omits that state information.

To review, reconstruct (5.3), (6.7), and (9.3) without looking, then compare assumptions and signs with the derivations. Revisit any failed step after a delay; distinguish an omitted explanation from an algebra error before changing a formula.

# References {.unnumbered}

::: {#refs}
:::
