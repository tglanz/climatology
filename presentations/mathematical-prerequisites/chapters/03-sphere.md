# Geometry and calculus on the sphere {#ch-sphere}

Why do uniform latitude weights and Cartesian derivative formulas fail on a sphere? Coordinate increments correspond to different physical lengths at different latitudes. We derive the metric factors first, then use length, flux, and circulation to construct the surface operators and streamfunction convention.

## Coordinates, metric factors, and area

Spherical coordinates have unequal physical scale factors. The area measure becomes uniform in sine of latitude, which explains Gaussian latitude weights. Sources: [@ArfkenWeber2005, Sections 2.1-2.2, 2.5].

::: {.tb-definition #obj-3-1}
**Definition 3.1 - Spherical and geographic coordinates**

Let $r>0$ be radius, $\theta\in[0,\pi]$ colatitude measured from the north pole, and $\lambda\in[0,2\pi)$ east longitude. Latitude is $\varphi=\pi/2-\theta$. Write

$$
\mathbf x=r(\sin\theta\cos\lambda,\sin\theta\sin\lambda,\cos\theta),
\qquad \mu=\cos\theta=\sin\varphi.
\tag{3.1}
$$
:::

::: {.tb-definition #obj-3-2}
**Definition 3.2 - Scale factors and orthonormal directions**

The unit vectors $\mathbf e_r,\mathbf e_\theta,\mathbf e_\lambda$ point toward increasing coordinates. The scale factor is $h_i=|\partial_{q_i}\mathbf x|$.
:::

::: {.tb-result #obj-3-3}
**Result 3.3 - Spherical distance and volume**

For the coordinate map (3.1), away from its coordinate singularities, the scale factors are $1,r,r\sin\theta$. Thus

$$
ds^2=dr^2+r^2d\theta^2+r^2\sin^2\theta\,d\lambda^2,
\qquad dV=r^2\sin\theta\,dr\,d\theta\,d\lambda.
\tag{3.2}
$$
:::

::: {.tb-proof}
**Proof of Result 3.3**

Differentiate (3.1) in $r,\theta,\lambda$. The resulting vectors are perpendicular and have lengths $1,r,r\sin\theta$. Their squared lengths give the distance formula; their product gives the positive volume factor. $\square$
:::

::: {.tb-definition #obj-3-4}
**Definition 3.4 - Sphere and solid-angle measure**

On the radius-$R$ sphere $S_R^2=\{\mathbf x:|\mathbf x|=R\}$, use solid angle $d\Omega=dA/R^2$.
:::

::: {.tb-result #obj-3-5}
**Result 3.5 - Surface area becomes uniform in sine of latitude**

For an integrable scalar $q$ on the radius-$R$ sphere,

$$
dA=R^2\sin\theta\,d\theta\,d\lambda
=R^2\cos\varphi\,d\varphi\,d\lambda,
\qquad
\int_{S_R^2}q\,dA=R^2\int_{-1}^1\int_0^{2\pi}q(\mu,\lambda)\,d\lambda\,d\mu.
\tag{3.3}
$$
:::

::: {.tb-proof}
**Proof of Result 3.5**

The last equality reverses the $\mu$ bounds to absorb $d\mu=-\sin\theta\,d\theta$. The integration uses positive area measure. $\square$
:::

::: {.tb-example #obj-3-6}
**Example 3.6 - Mean of sine-squared latitude**

The total area is $4\pi R^2$. For $q=\mu^2$, its global area mean is $\frac12\int_{-1}^1\mu^2\,d\mu=1/3$; equal weights on equally spaced latitudes would give a different average.
:::

::: {.tb-exercise #ex-3-1}
**Exercise 3.1 - Compute a spherical moment**

*Application.* Find the area mean of $\mu^4$ on a sphere, where $\mu=\sin\varphi$.
:::

## Tangent differential operators

Physical derivatives divide coordinate derivatives by arc lengths. These scale factors determine the spherical Laplacian and the correct signs of wind and vorticity. Sources: [@ArfkenWeber2005, Sections 2.2, 2.5].

::: {.tb-definition #obj-3-7}
**Definition 3.7 - Tangent gradient and physical components**

The surface gradient $\nabla_s q$ is tangent to the sphere and satisfies $dq=\nabla_s q\cdot d\mathbf x$ for tangent displacements. For $\mathbf F=F_\theta\mathbf e_\theta+F_\lambda\mathbf e_\lambda$, $F_\theta,F_\lambda$ are its physical components along the two tangent unit directions.
:::

::: {.tb-result #obj-3-8}
**Result 3.8 - Surface gradient, divergence, and radial curl**

For smooth scalars and tangent vector fields on $S_R^2$, with the physical components just defined,

$$
\begin{aligned}
\nabla_s q&=\frac{\mathbf e_\theta}{R}\partial_\theta q
+\frac{\mathbf e_\lambda}{R\sin\theta}\partial_\lambda q,\\
\nabla_s\cdot\mathbf F&=\frac{1}{R\sin\theta}
\left[\partial_\theta(\sin\theta F_\theta)+\partial_\lambda F_\lambda\right],\\
(\nabla\times\mathbf F)\cdot\mathbf e_r&=\frac{1}{R\sin\theta}
\left[\partial_\theta(\sin\theta F_\lambda)-\partial_\lambda F_\theta\right].
\end{aligned}
\tag{3.4}
$$
:::

::: {.tb-proof}
**Proof of Result 3.8**

The gradient follows by matching $dq$ to the physical line element. For flux and circulation use the same small spherical patch:

For the divergence formula, consider a small patch with sides $R\,d\theta$ and $R\sin\theta\,d\lambda$. The difference of meridional fluxes through its latitude edges is $R\partial_\theta(\sin\theta F_\theta)d\theta d\lambda$; the longitude edges contribute $R\partial_\lambda F_\lambda d\theta d\lambda$. Divide by patch area. Applying Stokes' theorem to the same patch yields the curl formula, with counterclockwise orientation viewed from outside. $\square$
:::

::: {.tb-definition #obj-3-9}
**Definition 3.9 - Laplace-Beltrami and angular operators**

The Laplace-Beltrami operator is the surface divergence of the surface gradient. Define $\Delta_\Omega=R^2\Delta_s$.
:::

::: {.tb-result #obj-3-10}
**Result 3.10 - Spherical scalar Laplacian**

For a smooth scalar $q$, the surface operator is

$$
\Delta_s q:=\nabla_s\cdot\nabla_s q
=\frac1{R^2}\left[\frac1{\sin\theta}\partial_\theta(\sin\theta\partial_\theta q)
+\frac1{\sin^2\theta}\partial_\lambda^2q\right].
\tag{3.5}
$$

In latitude or $\mu=\sin\varphi$,

$$
\Delta_s q=\frac1{R^2\cos\varphi}\partial_\varphi(\cos\varphi\partial_\varphi q)
+\frac1{R^2\cos^2\varphi}\partial_\lambda^2q
=\frac1{R^2}\left[\partial_\mu((1-\mu^2)\partial_\mu q)
+\frac{\partial_\lambda^2q}{1-\mu^2}\right].
\tag{3.6}
$$
:::

::: {.tb-proof}
**Proof of Result 3.10**

Substitute the gradient components from (3.4) into its divergence formula. Then use $\partial_\theta=-\sin\theta\,\partial_\mu$ and $\cos\varphi=\sin\theta$ to obtain the two coordinate forms. $\square$
:::

::: {.tb-remark #obj-3-11}
**Remark 3.11 - Intrinsic surface derivatives and physical radius**

In three-dimensional space, the full scalar Laplacian is $\Delta q=r^{-2}\partial_r(r^2\partial_rq)+r^{-2}\Delta_\Omega q$. Restricting to a surface and assuming radial independence are distinct operations; (3.5) is intrinsic to the surface. Its units are field units divided by $\mathrm m^2$.
:::

::: {.tb-exercise #ex-3-2}
**Exercise 3.2 - Check an eigenfunction before using harmonics**

*Application.* Apply (3.6) to $q=\mu$ and to $q=1$.
:::

## Regularity, streamfunction, and the closed surface

Poles are coordinate singularities, not physical edges. A smooth nondivergent tangent velocity on the sphere has a streamfunction whose mean is arbitrary. Sources: [@ArfkenWeber2005, Sections 1.16, 2.5, 12.11]; fluid application: [@Vallis2006, Sections 2.2, 4.5].

::: {.tb-remark #obj-3-12}
**Remark 3.12 - Pole regularity is geometric**

All longitudes at a pole describe one point. A smooth scalar has a unique value there; nonzero longitude Fourier orders must vanish at the poles with the behavior derived in Chapter 8. The local tangent basis itself depends on longitude, so smooth vector components need not be longitude-independent at a pole. Smoothness is a geometric condition, not a command to set all derivatives to zero.
:::

::: {.tb-definition #obj-3-13}
**Definition 3.13 - Streamfunction velocity**

For a smooth real streamfunction $\psi$ with units $\mathrm m^2\,\mathrm s^{-1}$, set $\mathbf u=\mathbf e_r\times\nabla_s\psi$. Let $u$ be eastward speed and $v$ northward speed, so $F_\lambda=u$ and $F_\theta=-v$.
:::

::: {.tb-result #obj-3-14}
**Result 3.14 - A streamfunction gives nondivergent flow**

For a smooth real streamfunction with velocity $\mathbf u=\mathbf e_r\times\nabla_s\psi$, the eastward and northward components and radial vorticity satisfy

$$
u=-\frac1R\partial_\varphi\psi,
\qquad v=\frac1{R\cos\varphi}\partial_\lambda\psi,
\qquad \nabla_s\cdot\mathbf u=0,
\qquad \zeta:=(\nabla\times\mathbf u)\cdot\mathbf e_r=\Delta_s\psi.
\tag{3.7}
$$
:::

::: {.tb-proof}
**Proof of Result 3.14**

To check divergence, substitute the first two expressions into $[\partial_\lambda u+\partial_\varphi(v\cos\varphi)]/(R\cos\varphi)$; the mixed partials cancel. Substituting into the radial curl yields (3.6). $\square$
:::

::: {.tb-remark #obj-3-15}
**Remark 3.15 - The undetermined mean and global representation**

Adding a spatial constant to $\psi$ changes neither speed nor vorticity. The converse for every smooth divergence-free tangent field on the whole sphere is justified by the potential decomposition in Section 8.4. Until then, (3.7) defines the velocity class considered. Domains with holes can require additional circulation modes.
:::

::: {.tb-result #obj-3-16}
**Result 3.16 - Integration by parts on a closed sphere**

For smooth real scalars $f,g$ on $S_R^2$,

$$
\int_{S_R^2}f\Delta_sg\,dA=-\int_{S_R^2}\nabla_sf\cdot\nabla_sg\,dA,
\qquad \int_{S_R^2}\Delta_sg\,dA=0.
\tag{3.8}
$$
:::

::: {.tb-proof}
**Proof of Result 3.16**

Integrate the surface divergence of $f\nabla_sg$ over the closed sphere. There is no external boundary, so its integral is zero. Expand the product divergence and rearrange. Set $f=1$ for the second identity. $\square$
:::

::: {.tb-remark #obj-3-17}
**Remark 3.17 - Poisson compatibility and coordinate cuts**

Here $f,g$ are smooth real scalars. The second identity uses $f=1$. Thus $\Delta_sg=h$ requires zero area integral of $h$. The coordinate cuts at longitude $0$ and the poles are not physical boundaries; periodicity and regularity cancel their apparent terms.
:::

::: {.tb-exercise #ex-3-3}
**Exercise 3.3 - Diagnose an incompatible vorticity field**

*Reasoning.* Can a globally smooth streamfunction satisfy $\Delta_s\psi=c$ for a nonzero spatial constant $c$?
:::

## Chapter summary

Colatitude $\theta$, latitude $\varphi$, and longitude $\lambda$ follow (3.1); $\mu=\sin\varphi$. Scale factors define distance, area, and differential operators. Area is uniform in $(\mu,\lambda)$, not $(\varphi,\lambda)$. The physical Laplace-Beltrami operator is $\Delta_s=R^{-2}\Delta_\Omega$. With the convention $\mathbf u=\mathbf e_r\times\nabla_s\psi$, vorticity is $\zeta=\Delta_s\psi$. The Laplacian has zero integral and a constant nullspace.

::: {.tb-exercise #ex-3-4}
**Exercise 3.4 - Connect the chapter results**

*Synthesis.* Verify $\Delta_s\mu=-2\mu/R^2$. If $\psi=A\sin\varphi$, find $u$, $v$, and $\zeta$, including their units.
:::
