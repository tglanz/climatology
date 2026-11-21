# Table of Contents

1. **Fields and Geometry on a Sphere.** Coordinates and physical locations; local directions, distance, and area; continuity at the seam and poles; integration, averages, and inner products; Gaussian sampling; the difference between a field and its samples.
2. **Fourier Analysis Around a Latitude Circle.** Repeating waves; amplitude and position; complex numbers as two-component bookkeeping; orthogonality, projection, and Fourier coefficients; discrete transforms, sampling limits, and inverse reconstruction.
3. **Latitude Patterns and Associated Legendre Polynomials.** Why latitude is not periodic; polynomials and weighted orthogonality; Legendre polynomials, Gaussian quadrature, pole behavior, and the latitude functions associated with each longitude wave.
4. **Spherical Harmonics and Their Transforms.** Whole-sphere patterns; degree and order; normalization and real-field symmetry; spherical harmonic analysis and synthesis; truncation, array layout, and contamination from unresolved products.
5. **The Mathematics of Horizontal Fluid Motion.** Velocity and circulation; spatial and temporal derivatives; divergence, vorticity, and streamfunction; the spherical gradient and Laplacian; recovering velocity from a scalar description of spin.
6. **The Barotropic Vorticity Equation.** The physical assumptions of a horizontal model; planetary rotation; transport of absolute vorticity; forcing and dissipation; conservation statements and their limits; the simulation's numerical update.
7. **Stochastic Stirring.** Random variables, means, variance, and correlation; forcing strength and memory; selected spatial scales and geographic localization; seeds, repeated simulations, and the statistics of sustained motion.
8. **Neural Operators and the FNO.** Functions, samples, and learned maps; channels and learned parameters; local and global computations; the Fourier Neural Operator (FNO); nonlinearities, finite retained spectra, and resolution dependence.
9. **The SFNO in This Repository.** The Spherical Fourier Neural Operator (SFNO); spherical transforms and learned spectral weights; coordinate features, latitude order, and grid contracts; field, profile, and Legendre output heads; properties the architecture does and does not enforce.
10. **Constructing the Learning Problem.** Simulation records and units; initial adjustment and empirical convergence checks; input windows and finite-time average targets; configuration-level data splits; normalization, metadata, and information leakage.
11. **Training and Objectives.** A complete prediction and parameter-update cycle; squared error and relative norms; area weighting; batches, validation, stopping, and checkpoints; normalized objectives versus physical-unit errors.
12. **Evaluation and the Complete Project.** Model loading and reconstruction of the data contract; physical-unit predictions; reference predictors; window and simulation aggregation; variation between repeated runs; diagnosing what the model learned and what the evidence cannot establish.

\newpage

# Chapter 1: Fields and Geometry on a Sphere

## The Problem

Consider a program that receives an array of atmospheric measurements. Its final two axes have lengths 128 and 256. The first temptation is to treat this as a small image: rows are vertical, columns are horizontal, and neighboring entries represent equally spaced pieces of the world.

The array alone establishes none of these physical facts. Its rows might be ordered from south to north or north to south. Its longitude samples might include both ends of a repeating interval, thereby storing one location twice. Its latitude rows might be equally spaced in angle, or chosen according to a numerical integration rule. Its entries might represent temperature, wind, or local fluid spin. Correct arithmetic applied to the wrong interpretation can produce a plausible map and an incorrect scientific conclusion.

The central task of this chapter is to distinguish three objects that a computer often stores together:

- The **physical field**: a quantity assigned to every location on a surface.
- The **coordinate description**: the labels used to identify those locations.
- The **sampled representation**: the finite collection of numbers stored in an array.

A temperature field assigns one temperature to each location. A **scalar** is a quantity described by one number once its unit is specified; temperature is an example. A **scalar field** assigns such a quantity throughout a region. A **vector** also includes direction. Horizontal wind requires two directional components, such as eastward and northward speed. This chapter develops scalar fields and the geometry needed to interpret those components later.

A **unit** identifies what a number measures: meters for length, seconds for duration, and kelvin for absolute temperature. A difference between two temperatures can be measured in kelvin or degrees Celsius with the same numerical value. A number without a unit is **dimensionless**. Angles in radians and the normalized weights used below are dimensionless, although their meanings remain distinct.

A **function** is a rule that returns an output for each allowed input. A field can therefore be described by a function whose inputs identify a location. A **sample** is one evaluation of this rule. A **grid** specifies a collection of sample locations. An **array** stores the resulting values in an indexing order. The grid and array must remain associated; their relationship cannot be recovered from shape alone.

These distinctions matter throughout the project. The simulation evolves fluid motion on a sphere. The learning model receives sampled fields and predicts latitude-dependent averages. The error calculation must compare predictions using the correct physical weighting. A mistake in the geometry can enter all three stages without causing an array-shape error.

By the end of the chapter, you should be able to calculate distances and areas, distinguish a coordinate singularity from a physical irregularity, interpret an area integral, construct a weighted comparison between fields, and explain what finite sampling can and cannot establish. These are the prerequisites for understanding why longitude waves and latitude patterns are treated differently.

## The Intuition

### A coordinate map is an address system

Imagine painting a temperature pattern on a globe and then drawing latitude and longitude lines over the paint. Redrawing the reference longitude changes the addresses. It does not move the paint. Reversing the order in which a program stores latitude rows changes the data layout. It does not turn the Northern Hemisphere into the Southern Hemisphere.

A valid coordinate description must assign the same physical temperature whenever two coordinate labels identify the same location. Longitude zero and longitude 360 degrees describe the same line. At the North Pole, every longitude describes the same point. The numerical function must respect these identifications.

There is a useful software analogy. Several keys may refer to the same underlying object. Updating the object through one key must be consistent with reading it through another. A seam discontinuity is a failure of this consistency, not evidence for a physical wall in the atmosphere.

### The sphere is curved, but a sufficiently small neighborhood looks flat

Stand on a smooth globe with a ruler. Directly beneath your feet, the ruler lies in a plane that touches the surface. This is the **tangent plane**. It approximates the surface near the contact point. The approximation improves as the neighborhood becomes smaller.

The tangent plane contains local east and north directions. A third direction points outward from the globe. These three directions are mutually perpendicular, but their orientations in ordinary three-dimensional space change as you move over the sphere.

A small eastward step is measured along a latitude circle. Near a pole, that circle is short. A fixed longitude change therefore produces a shorter physical displacement there than at the equator. The coordinate angle did not shrink; the circle on which it is measured did.

This is why a numerical difference divided by a longitude increment is not yet a physical rate of change per meter. A length conversion is still required. The same conversion will later appear in the fluid equations.

### Averaging is a question about what receives equal influence

Suppose one thermometer represents a large region near the equator and another represents a small region near a pole. Averaging their two readings equally answers a question about the two thermometers. Averaging them in proportion to represented area answers a question about the surface.

Neither arithmetic operation is meaningless. They estimate different quantities. The scientific mistake is to perform the first operation while interpreting the result as the second.

For a global field, an area average can be pictured as selecting a point uniformly from the surface and asking for the average value observed over many such selections. Uniformly selecting a latitude angle does not select points uniformly over the surface: narrow latitude bands near a pole contain less area.

This distinction also changes error measurement. If prediction errors are large only in a small polar region, a physical surface error should account for the region's size. Counting its oversampled array entries equally can give it excessive influence.

### A stored picture is not the complete field

Four thermometers around a circle can all read zero while the temperature rises and falls between them. A computer that receives only those four values cannot determine whether the true field is zero everywhere or contains an unsampled pattern.

This ambiguity is **aliasing**: distinct continuous patterns produce indistinguishable samples. To reconstruct a field from samples, one must restrict the permitted patterns or accept uncertainty between observations. A transform does not remove that requirement.

The forthcoming spectral methods make the permitted patterns explicit. Their mathematical usefulness rests on the geometry and weighted comparisons developed here.

## The Mechanism

### 1.1 Establish a spherical model and an angle convention

We approximate Earth by a smooth sphere of constant radius, denoted by $R$. A **radius** is the distance from the center to the surface. This model ignores topography and Earth's small departure from a sphere. Those assumptions match this project's simulation of horizontal flow without resolved vertical structure, called its barotropic model. They are not a statement that Earth's real surface is exactly spherical.

Choose three fixed perpendicular axes through the center. Call the coordinates along them $x$, $y$, and $z$. Choose the positive $z$ axis to point toward the North Pole. Choose the positive $x$ axis to meet the equator at the reference longitude. The positive $y$ axis then meets the equator 90 degrees east of that reference. Coordinates measured along fixed perpendicular axes are called **Cartesian coordinates**.

**Latitude**, denoted by $\varphi$, is the angle north or south of the equatorial plane. It ranges from minus 90 degrees to plus 90 degrees. **Longitude**, denoted by $\lambda$, is the angle around the rotation axis measured eastward from the reference line. We usually store it from zero up to, but excluding, 360 degrees.

A **radian** measures angle by the length traveled around a circle divided by the circle's radius. The constant $\pi$ is a circle's circumference divided by its diameter, approximately 3.14159. One complete turn is 360 degrees or twice $\pi$ radians. The trigonometric and calculus formulas in this chapter take radian arguments.

The **cosine** and **sine** of an angle describe the horizontal and vertical coordinates, respectively, of a point one unit from the origin on a plane circle. For latitude, cosine gives the radius of the latitude circle as a fraction of $R$; sine gives height above the equatorial plane as a fraction of $R$. For longitude, they split the latitude circle's radius into its fixed $x$ and $y$ components.

Some references measure the north-south angle downward from the North Pole. That angle is **colatitude**, denoted by $\theta$. Latitude and colatitude describe the same location with different zero points and opposite directions of increase. Mixing their conventions changes signs and exchanges sine with cosine. We will state which convention every formula uses.

### 1.2 Distinguish physical points from coordinate pairs

At an ordinary location away from the poles and the chosen longitude seam, a pair of latitude and longitude values identifies one point uniquely. Around the seam, two longitude labels separated by a full turn identify the same point. At either pole, an entire circle of longitude labels identifies one point.

A coordinate description that is locally unambiguous is called a **chart**. Latitude and longitude provide a useful chart away from the poles, but they cannot provide one globally unambiguous rectangular address system for the whole sphere. The poles are **coordinate singularities**: the address system loses its ability to distinguish directions there. The physical surface remains smooth.

A **continuous field** has no jumps between physically nearby points. More precisely, requesting a sufficiently small change in its value must be achievable by restricting attention to a sufficiently small physical neighborhood. This definition uses distance on the surface, not the numerical difference between coordinate labels. Longitudes just below 360 degrees and just above zero describe nearby points.

Continuity requires matching values across the longitude seam and a unique limiting value at each pole. Smoothness demands more. A **differentiable field** has a consistent local linear rate of change: close to a point, its variation is approximated by a slope in each tangent direction. A **smooth field** has continuous derivatives of all orders. This stronger property is useful because repeated differentiation occurs in the fluid equations and in spectral analysis.

A field can be continuous at a pole and still have a cusp there. A pattern's **amplitude** is the scale of its variation. Making its longitude-dependent amplitude shrink to zero is necessary for continuity, but it does not by itself establish differentiability. We will examine a concrete example in Section 1.13.

### 1.3 Understand local vectors before differential operators

A vector can be stored as an ordered list of components along specified axes. The **dot product** of two real vectors multiplies corresponding components and adds the results. It measures alignment as well as size. The dot product of a vector with itself is its squared length. Taking the nonnegative square root gives its length, also called its **norm**.

A **unit vector** has length one and indicates direction without setting a physical magnitude. **Orthogonal** vectors have zero dot product; geometrically, they are perpendicular. An **orthonormal** collection consists of mutually perpendicular unit vectors.

At a nonpolar point, local east, local north, and the outward radial direction form an orthonormal collection. We denote them by $\mathbf e_{\mathrm E}$, $\mathbf e_{\mathrm N}$, and $\mathbf e_{\mathrm R}$. Bold type identifies a vector. Subscripts $\mathrm E$, $\mathrm N$, and $\mathrm R$ label directions; they are not numbers or quantities to multiply.

A velocity component of ten meters per second eastward refers to the local east vector at the location where the wind is measured. Reusing the same component at another location does not mean reusing the same fixed three-dimensional direction. This is one reason vector fields need additional care beyond scalar fields.

### 1.4 Learn what an infinitesimal calculation is claiming

A finite change, written with $\Delta$, compares two separated values. An **infinitesimal displacement**, written with $d$, describes the leading behavior as that separation becomes arbitrarily small. It is a tool for local geometry, not a claim that a computer stores infinitely small numbers.

A **derivative** measures the limiting ratio of a change in output to a change in input. A **partial derivative** varies one input while holding the others fixed. We write $\partial$ in a partial derivative to emphasize this restriction. A **limit** records the value approached as an increment is made arbitrarily small, when that value exists.

The **gradient** of a scalar field is a tangent vector pointing in the direction of fastest local increase. Its length is the increase per unit physical distance in that direction. A temperature gradient therefore has units of temperature per meter. An angular partial derivative has units of temperature per radian and must be converted using the local length associated with that angle.

These definitions introduce the operations needed to read the local formulas. They do not require a derivation of multivariable calculus. The conventions agree with the [NIST treatment of partial derivatives and coordinate systems](https://dlmf.nist.gov/1.5).

### 1.5 Distinguish a path length from a shortest surface distance

A route along a latitude circle is a particular path. It is generally not the shortest surface route between its endpoints. A **great circle** is the intersection of the sphere with a plane passing through its center. The shorter great-circle arc gives the shortest surface distance between distinct nonopposite points. Such a shortest path is called a **geodesic**.

A plane through the equator passes through the center, so the equator is a great circle. A plane through a northern latitude circle generally misses the center, so that circle is smaller. Two points on the same northern latitude can be connected more directly by a path that bows toward the pole.

This distinction matters when interpreting grid spacing. Neighboring points separated by a very small longitude increment have nearly the same coordinate-path and geodesic distances to leading order. For long separations, the difference can be substantial. A local formula should not be extended to an arbitrary global distance without checking its assumptions.

### 1.6 Build accumulated quantities from local pieces

An **integral** adds contributions from arbitrarily small pieces of a continuous region. For surface area, each piece contributes its area. For a field, each piece contributes its value multiplied by its area. A **surface integral** performs this accumulation over a surface.

An area element, written $dA$, represents the infinitesimal surface patch used in this accumulation. Its expression depends on the coordinate labels. The physical area does not. The factor converting a coordinate rectangle into physical area is sometimes called an **area Jacobian**. Here it accounts for radius and the shrinking of latitude circles.

A **mean**, or average, divides a total accumulated quantity by the size of the region over which it was accumulated. A surface mean of temperature is therefore an area integral of temperature divided by the total area. The sphere's radius cancels from this average when the same angular temperature pattern is considered on spheres of different radii.

A useful alternative coordinate is the signed height fraction, denoted by $\mu$. It is the sine of latitude and ranges from minus one at the South Pole to one at the North Pole. Equal intervals of this height fraction correspond to equal-area complete latitude belts. Equal latitude-angle intervals do not.

Changing from latitude to height fraction is a **change of variables**. It leaves the physical accumulated quantity unchanged while simplifying its coordinate expression. This change of variables explains the particular Gaussian quadrature used in the repository.

### 1.7 Compare whole fields, not just individual values

Two ordinary vectors can be compared by a dot product. Two real scalar fields can be compared by multiplying their values at each location and taking an area average. This operation is an **inner product** of fields. It tells us whether their positive and negative patterns tend to align after surface area is taken into account.

The norm associated with this inner product is the square root of the area mean of the squared field. It is a **root mean square**, abbreviated RMS. Squaring prevents positive and negative values from canceling. The RMS of an error field is a global measure of error magnitude.

Two nonzero fields are called **orthogonal** when their inner product is zero. This does not mean their colored regions never overlap. It means their signed product cancels when averaged with the specified weighting. Changing the weighting can change which fields are orthogonal.

A **projection** measures how much of a chosen pattern is present in a field. For one pattern, it selects the multiplying coefficient that minimizes the mean squared residual. A **residual** is what remains after subtracting the chosen approximation. Several mutually orthogonal patterns can be measured without their coefficients interfering with one another. This is the mathematical idea behind the transforms developed in Chapters 2-4.

All fields in the present chapter are real-valued. A real number is an ordinary signed number on the number line. Chapter 2 will extend the bookkeeping to complex numbers and explain the corresponding adjustment to the inner product.

### 1.8 Replace continuous accumulation by a controlled numerical rule

A computer cannot evaluate an arbitrary continuous field at every point. **Quadrature** estimates an integral from finitely many samples and numerical weights. A weight specifies how much a sample contributes to that particular integration rule.

An equiangular grid places rows at equal angular latitude intervals. A Gaussian grid chooses particular latitude locations and accompanying weights. **Gauss-Legendre quadrature** is the rule that integrates polynomials in the height fraction accurately with no additional weighting function on the interval from minus one to one.

A **polynomial** is a finite sum of nonnegative whole-number powers of its input multiplied by coefficients. Its **degree** is the highest power with a nonzero coefficient. Gaussian quadrature with a given number of latitude nodes is exact, apart from arithmetic rounding, for polynomials through degree twice the node count minus one. Exactness for one polynomial does not imply exactness for its square, which can have twice the degree. The [NIST quadrature reference](https://dlmf.nist.gov/3.5#v) states the general rule.

A **node** is a sampling location. The Gaussian nodes and their weights are selected together. The weights are not automatically the areas of cells drawn halfway between the nodes. A finite-volume scheme, which stores averages over physical cells, and a Gaussian quadrature scheme, which weights point samples, are distinct numerical constructions.

The project's **full Gaussian grid** has the same number of equally spaced longitudes on every latitude row. A **reduced Gaussian grid** decreases the number of longitude samples toward the poles. Both use Gaussian latitude placement, but only the first naturally fits the rectangular spatial array supported by this project's ML reader. See the [ECMWF grid descriptions](https://confluence.ecmwf.int/spaces/FCST/pages/49415103/Gaussian%2Bgrids).

### 1.9 State the information lost by sampling

Sampling is a map from a function to a finite array. Many different functions can map to the same array. A **reconstruction** is a rule that selects a function from those samples, usually by restricting the permitted patterns.

A **basis** is a collection of patterns from which the permitted functions can be constructed uniquely by taking weighted sums. The multiplying numbers are **coefficients**. A **mode** is one such pattern, usually labeled according to its spatial structure. A **spectral representation** stores the coefficients of wave-like modes rather than only local sampled values.

A finite set of retained modes describes a restricted class of fields. Removing modes outside that set is **truncation**. Increasing the number of sample points while leaving the retained set unchanged can improve numerical calculations without expanding the represented physical detail. Increasing the retained set without enough samples can make distinct patterns indistinguishable.

The geometric grid, the retained representation, and the accuracy of a numerical integration rule are therefore separate choices. Their compatibility will become a central concern in the spherical harmonic transform. We begin by putting the continuous geometry and its discrete approximation on a precise footing.

## Reading the Math

The right-hand labels identify equations for later reference. They are reference numbers, not factors in the calculations. All trigonometric arguments in the equations are in radians unless a degree label explicitly says otherwise.

### 1.10 Coordinates, units, and the embedded sphere

**Begin with a marked angle.** A 90-degree turn is one quarter of a full circle. The same angle is half of $\pi$ radians. To keep units visible, let $a_{\mathrm{deg}}$ denote the numerical angle in degrees and $a_{\mathrm{rad}}$ the numerical angle in radians. Colatitude $\theta$ is measured downward from the North Pole, whereas latitude $\varphi$ is measured upward from the equator.

$$
a_{\mathrm{rad}}=\frac{\pi}{180}\,a_{\mathrm{deg}},
\qquad
\theta=\frac{\pi}{2}-\varphi.
\tag{1.1}
$$

**Symbol-by-Symbol**

- $a$: the angle being expressed; subscripts $\mathrm{deg}$ and $\mathrm{rad}$ select its degree and radian numerical values.
- $\pi$: circumference divided by diameter; 180 is the number of degrees in a half-turn, and 2 divides a half-turn into a quarter-turn.
- $\theta$: colatitude in radians. $\varphi$: latitude in radians.
- $=$ means equality; the fraction bars mean division; adjacency means multiplication; $-$ subtracts latitude from a quarter-turn. The comma and spacing separate the two statements.

**Plain-English Translation:** Convert angle units before calculation, and measure north-south position from the correct reference direction.

A degree-to-radian error is not a small rounding error. Passing 60 directly to a cosine function that expects radians means asking for the cosine of an angle larger than nine complete turns. The expected latitude-circle radius fraction is one-half; the mistaken answer is negative. A negative geometric radius is a warning that the interpretation has already failed.

**Now locate the point in three-dimensional space.** Let $\mathbf r$ be the position vector from the sphere's center to a surface point. Its three components are the Cartesian coordinates $x$, $y$, and $z$ defined earlier. The horizontal circle has radius $R\cos\varphi$; longitude divides that horizontal radius between the $x$ and $y$ axes.

$$
\mathbf r(\varphi,\lambda)
=(x,y,z)
=R\bigl(\cos\varphi\cos\lambda,
        \cos\varphi\sin\lambda,
        \sin\varphi\bigr),
\qquad x^2+y^2+z^2=R^2.
\tag{1.2}
$$

**Symbol-by-Symbol**

- $\mathbf r$: a vector, indicated by bold type; the parentheses after it specify the latitude and longitude at which it is evaluated.
- $\varphi$, $\lambda$: latitude and longitude in radians. $R$: sphere radius in length units.
- $x$, $y$, $z$: fixed-axis position components, in the same length units as $R$.
- $\sin$, $\cos$: sine and cosine. A parenthesized three-entry list is an ordered vector of components; commas separate its entries.
- Superscript $2$ means squaring; $+$ adds squared components; $=$ means equality. Multiplication is written by adjacency; multiplying a vector by $R$ multiplies each component by $R$.

**Plain-English Translation:** Latitude and longitude label a point whose distance from the center is always the prescribed sphere radius.

At the equator and reference longitude, the position lies entirely on the positive $x$ axis. At the equator and 90 degrees east, it lies on the positive $y$ axis. At the North Pole, the horizontal components vanish and only the positive $z$ component remains. These three cases are inexpensive checks of any coordinate-conversion function.

The final equality is a geometric constraint. It states that the surface is two-dimensional even though it is described using three Cartesian components. Two coordinates can vary independently; the radius fixes the remaining freedom.

### 1.11 Continuity, periodicity, and pole identifications

**Follow one painted mark across the seam.** A full longitude turn returns to the same location. At a pole, turning around the longitude circle never changes the physical location at all. Let $f$ be a scalar field and let $f_{\mathrm N}$ and $f_{\mathrm S}$ denote its unique north and south pole values. The coordinate function must satisfy:

$$
\begin{aligned}
f(\varphi,\lambda+2\pi)&=f(\varphi,\lambda),\\
f\left(\frac{\pi}{2},\lambda\right)&=f_{\mathrm N},
&f\left(-\frac{\pi}{2},\lambda\right)&=f_{\mathrm S}.
\end{aligned}
\tag{1.3}
$$

**Symbol-by-Symbol**

- $f$: the scalar field; $f(\varphi,\lambda)$ means its value at the stated latitude and longitude.
- $\varphi$, $\lambda$: latitude and longitude. $\pi$: the circle constant; $2\pi$ is one full turn, and $\pi/2$ is a quarter-turn.
- $f_{\mathrm N}$, $f_{\mathrm S}$: single physical pole values; the subscripts label north and south, and neither depends on longitude.
- $+$ adds one full turn; the leading $-$ selects the southern latitude; fractions divide; $=$ requires equal physical values. Parentheses group function inputs; commas separate them.

**Plain-English Translation:** Different coordinate addresses for the same point must return the same scalar value.

These equalities state necessary identifications. Continuity additionally requires that values approaching a pole tend to the pole value regardless of approach direction. Merely filling the final array row with a constant while the preceding rows approach incompatible values does not repair the field.

For a smooth field, the matching across the longitude seam also applies to its derivatives. A map with identical endpoint values but mismatched slopes still contains a physical crease. This matters to spectral representations because differentiation magnifies irregular behavior and makes additional short-scale patterns necessary to describe it.

Avoiding samples exactly at the poles is a useful numerical design choice, but it does not remove the underlying consistency requirement. The function represented by those samples must still be a function on the sphere.

### 1.12 Local length, the metric, and global distance

**Put two perpendicular rulers on the surface.** One lies along a latitude circle and one points north. Their directions in fixed Cartesian coordinates are given by unit vectors $\mathbf e_{\mathrm E}$ and $\mathbf e_{\mathrm N}$; the outward unit vector is $\mathbf e_{\mathrm R}$.

$$
\begin{aligned}
\mathbf e_{\mathrm E}&=(-\sin\lambda,\ \cos\lambda,\ 0),\\
\mathbf e_{\mathrm N}&=(-\sin\varphi\cos\lambda,
                       -\sin\varphi\sin\lambda,
                        \cos\varphi),\\
\mathbf e_{\mathrm R}&=(\cos\varphi\cos\lambda,
                        \cos\varphi\sin\lambda,
                        \sin\varphi).
\end{aligned}
\tag{1.4}
$$

**Symbol-by-Symbol**

- Bold $\mathbf e$ denotes a direction vector; subscripts $\mathrm E$, $\mathrm N$, and $\mathrm R$ select east, north, and radial outward directions.
- $\varphi$, $\lambda$: latitude and longitude; $\sin$ and $\cos$: sine and cosine.
- Each three-entry list gives components along fixed $x$, $y$, and $z$ axes. Zero means no component along that axis.
- Leading $-$ reverses a component; adjacency multiplies; $=$ specifies the vector. Commas separate components.

**Plain-English Translation:** Local east and north rotate through three-dimensional space as the observer moves over the sphere.

For example, at the equator and reference longitude, local east points along positive $y$, local north along positive $z$, and outward along positive $x$. The dot product of each pair is zero and each vector has length one. These checks establish the local orthonormal frame away from the poles. At a pole, the formulas depend on an arbitrary longitude label, revealing the absence of a unique east direction there.

**Convert the two rulers into a distance rule.** Write $ds$ for infinitesimal path length, $d\varphi$ for a small north-south angular displacement, and $d\lambda$ for a small east-west angular displacement. Because the local directions are perpendicular, their squared lengths add:

$$
ds^2=R^2\,d\varphi^2+R^2\cos^2\varphi\,d\lambda^2.
\tag{1.5}
$$

**Symbol-by-Symbol**

- $ds$: infinitesimal physical path length. The $d$ marks a local differential quantity, not multiplication by a separate variable.
- $R$: radius; $d\varphi$, $d\lambda$: infinitesimal latitude and longitude changes in radians.
- $\cos\varphi$: latitude-circle shrinking factor; $\cos^2\varphi$ means the square of that cosine.
- Superscript $2$ squares the indicated length or increment. $+$ adds perpendicular squared lengths; $=$ states the local distance rule; adjacent factors multiply.

**Plain-English Translation:** North-south and east-west angular changes contribute different physical lengths, and their perpendicular contributions combine by the ordinary right-triangle rule.

This rule is the sphere's **metric** in latitude-longitude coordinates: it specifies physical length from coordinate displacement. The metric does not assert that a finite spherical patch is exactly flat. It gives the leading local behavior from which curved-path lengths are accumulated.

For a finite eastward motion that stays at fixed latitude, the corresponding arc length is radius times longitude change, using the latitude-circle radius. At Earth's approximate radius of 6,371 kilometers, one degree along the equator spans about 111.195 kilometers. At 60 degrees north the same angular longitude increment spans about 55.597 kilometers. One degree of northward displacement along a meridian spans about 111.195 kilometers at both locations.

A three-by-three array neighborhood therefore covers different physical shapes at different latitudes. A translation of a pattern by one array column is not generally the same physical displacement everywhere. A flat-image operation can still be useful as a numerical component, but its geometric interpretation must be justified.

![A meridional cross-section and a small coordinate patch. The latitude circle shrinks as its height increases; the two local coordinate directions have different physical scale factors.](figures/geometry.png){width=95%}

**Now compare widely separated points.** Let $\gamma$ be the central angle between their radial vectors. Let $d_{12}$ be the shorter surface distance between point 1 and point 2. The inverse cosine function, written $\arccos$, returns the angle between zero and $\pi$ whose cosine is the supplied value.

$$
\begin{aligned}
\cos\gamma
&=\frac{\mathbf r_1\cdot\mathbf r_2}{R^2}
=\sin\varphi_1\sin\varphi_2
 +\cos\varphi_1\cos\varphi_2\cos(\lambda_2-\lambda_1),\\
d_{12}&=R\,\arccos(\cos\gamma).
\end{aligned}
\tag{1.6}
$$

**Symbol-by-Symbol**

- $\gamma$: central angle, selected between zero and $\pi$ radians. $d_{12}$: shorter great-circle distance, with the subscript labeling the two points.
- $\mathbf r_1$, $\mathbf r_2$: position vectors of the two surface points. Subscripts 1 and 2 select points throughout the equation.
- $\varphi_1$, $\varphi_2$, $\lambda_1$, $\lambda_2$: their latitudes and longitudes. $R$: common sphere radius.
- $\cdot$: vector dot product, the sum of products of corresponding Cartesian components.
- $\sin$, $\cos$: trigonometric functions; $\arccos$: inverse cosine. Parentheses group the longitude difference or a function's input.
- $R^2$: squared radius; fraction bar: division; $+$ and $-$: addition and subtraction; adjacency: multiplication; $=$: equality.

**Plain-English Translation:** Compare the two outward directions to obtain their angular separation, then convert that angle into the shorter surface distance.

Take two points at 60 degrees north separated by 90 degrees of longitude. Their radial dot product divided by squared radius is 0.75. The shorter great-circle distance is about 4,604.5 kilometers. The route along their latitude circle is about 5,003.8 kilometers. Both are valid lengths, but they describe different routes.

In floating-point arithmetic, which stores numbers to finite precision, a computed normalized dot product can lie slightly outside the interval from minus one to one. Clipping that computed argument to the permitted interval prevents a spurious inverse-cosine failure. For very close points, inverse cosine also loses relative precision because its argument is extremely close to one. Numerical geodesic libraries use more stable equivalent formulations in that regime. Neither issue changes the geometry.

### 1.13 Derivatives, physical slopes, and regularity at a pole

**Measure a slope by shortening the ruler.** Suppose we vary longitude while holding latitude fixed. Let $h$ denote the longitude increment in radians. The angular partial derivative records the limiting change per angular increment:

$$
\frac{\partial f}{\partial\lambda}(\varphi,\lambda)
=\lim_{h\to0}
\frac{f(\varphi,\lambda+h)-f(\varphi,\lambda)}{h}.
\tag{1.7}
$$

**Symbol-by-Symbol**

- $f$: scalar field; $\varphi$, $\lambda$: latitude and longitude at the evaluation point.
- $\partial f/\partial\lambda$: partial derivative with respect to longitude while latitude is fixed; $\partial$ marks the one-input variation.
- $h$: angular increment. $\lim_{h\to0}$ means the limiting value as $h$ approaches zero from either sign.
- $f(\varphi,\lambda+h)$: field value at the shifted longitude. Parentheses contain inputs; commas separate them.
- $+$ shifts longitude; $-$ forms the field difference; the fraction divides by the angular increment; $=$ asserts that the limit defines the derivative when the limit exists.

**Plain-English Translation:** Compare nearby values while varying only longitude, and ask what change per angular step remains as the step becomes arbitrarily small.

A computer usually approximates a derivative using a finite increment. Shrinking that increment first reduces the error caused by a finite step, but eventually subtraction of nearly equal stored numbers magnifies rounding error. A valid mathematical limit is therefore not a prescription to choose the smallest representable numerical step.

**Convert an angular slope into a physical gradient.** The northward physical distance per latitude increment is $R$. The eastward distance per longitude increment is $R\cos\varphi$. Divide the corresponding angular slopes by these lengths and attach the correct local directions:

$$
\nabla_{\!S}f
=\mathbf e_{\mathrm N}\frac{1}{R}\frac{\partial f}{\partial\varphi}
 +\mathbf e_{\mathrm E}\frac{1}{R\cos\varphi}
                            \frac{\partial f}{\partial\lambda}.
\tag{1.8}
$$

**Symbol-by-Symbol**

- $\nabla_{\!S}$: surface-gradient operator; $\nabla$ denotes a spatial rate-of-change operation and subscript $S$ restricts it to the spherical surface.
- $f$: scalar field. $\varphi$, $\lambda$: latitude and longitude; $R$: radius; $\cos\varphi$: latitude-circle radius fraction.
- $\mathbf e_{\mathrm N}$, $\mathbf e_{\mathrm E}$: local north and east unit vectors; subscripts label directions.
- $\partial f/\partial\varphi$, $\partial f/\partial\lambda$: angular partial derivatives, holding the other angle fixed.
- Fractions divide slopes by physical length factors; adjacency multiplies vectors by scalar components; $+$ adds the two directional contributions; $=$ specifies the gradient.

**Plain-English Translation:** A physical slope is an angular slope divided by the physical distance represented by that angle, resolved into local north and east components.

Away from the poles, the formula is directly usable. At a pole, the east direction is undefined and its denominator vanishes. For a smooth physical field, this coordinate expression must be interpreted by limits or replaced by a nonsingular coordinate description. A divergent intermediate factor alone does not prove that the physical field has an infinite gradient.

A useful example is the normalized height field. Its value is sine of latitude. Its northward slope is cosine of latitude divided by radius, and its eastward slope is zero. The physical gradient tends to zero at both poles. A formula containing a potentially vanishing denominator can therefore describe a perfectly regular field when its numerator vanishes appropriately.

**Compare three proposed longitude-dependent patterns.** Let $b$ label a bad pole behavior, $c$ label a continuous but nonsmooth behavior, and $s$ label a smooth behavior. These are labels, not multiplying variables. Consider dimensionless fields:

$$
\begin{aligned}
f_b(\varphi,\lambda)&=\cos\lambda,\\
f_c(\varphi,\lambda)&=\cos\varphi\cos(2\lambda),\\
f_s(\varphi,\lambda)&=\cos^2\varphi\cos(2\lambda)
                    =\frac{x^2-y^2}{R^2}.
\end{aligned}
\tag{1.9}
$$

**Symbol-by-Symbol**

- $f_b$, $f_c$, $f_s$: the three fields; their subscripts label the cases just described.
- $\varphi$, $\lambda$: latitude and longitude; $x$, $y$: Cartesian coordinates; $R$: radius.
- $\cos$: cosine; $2\lambda$ means twice the longitude. Superscript $2$ squares its quantity, including the cosine in $\cos^2\varphi$.
- The fraction divides by squared radius, making the field dimensionless. $-$ subtracts squared coordinates; adjacency multiplies; $=$ identifies equal representations of the same field.

**Plain-English Translation:** Longitude variation needs an appropriate latitude-dependent amplitude to fit smoothly together at a pole.

The first field is unacceptable as a continuous scalar field at the pole. Approaching along longitude zero gives one; approaching along longitude 180 degrees gives minus one. The two paths reach the same point with incompatible limiting values.

The second field approaches zero from every direction because its amplitude is bounded by the latitude cosine. It is continuous when assigned zero at a pole. Nevertheless, along a straight local path through the North Pole in the fixed $x$ direction, it behaves like the absolute value of horizontal displacement divided by radius. Its graph has a cusp. The slope on one side of the pole has the opposite sign to the slope on the other, so there is no differentiable local linear description.

The third field is a polynomial in the fixed Cartesian coordinates divided by a constant. That expression stays smooth at the pole. In the same cross-pole direction it behaves quadratically, with a slope tending to zero. This demonstrates why continuity alone is too weak a criterion for fields that will be differentiated repeatedly.

![Restrictions of the three fields to a path through the North Pole. A jump has no unique pole value, an absolute-value shape has a cusp, and the quadratic shape is smooth. The horizontal axis is signed Cartesian displacement divided by radius.](figures/polar-regularity.png){width=100%}

Spherical harmonics will supply latitude-longitude combinations that satisfy the required pole behavior as complete patterns. The restriction is geometric; it is not an optional cosmetic treatment applied after performing a transform.

### 1.14 Surface area and the height-fraction coordinate

**Cover a small patch with the two local rulers.** Its leading north-south length is radius times latitude increment. Its leading east-west length includes the cosine shrinking factor. Their product gives the physical area element.

Write $\mu$ for signed height divided by radius. The relation between height fraction and latitude, together with the area element, is:

$$
\mu=\sin\varphi,
\qquad d\mu=\cos\varphi\,d\varphi,
\qquad dA=R^2\cos\varphi\,d\varphi\,d\lambda
        =R^2\,d\mu\,d\lambda.
\tag{1.10}
$$

**Symbol-by-Symbol**

- $\mu$: dimensionless signed height fraction; $\varphi$: latitude; $\lambda$: longitude; $R$: radius.
- $d\mu$, $d\varphi$, $d\lambda$: infinitesimal increments. $dA$: infinitesimal surface area, with units of squared length.
- $\sin$, $\cos$: sine and cosine. The relation for $d\mu$ expresses the local slope of sine.
- Superscript $2$ squares the radius; adjacency multiplies increments and scale factors; $=$ relates equivalent descriptions. Commas and spacing separate statements.

**Plain-English Translation:** The shrinking of latitude circles appears as a cosine in latitude coordinates and is already absorbed when signed height fraction is used instead.

The sphere's area Jacobian in latitude-longitude coordinates is therefore squared radius times latitude cosine. This factor is nonnegative over the allowed latitude range. At either pole it vanishes because the whole longitude coordinate line collapses to a point.

The alternative height coordinate explains a less obvious geometric fact. A complete belt between two horizontal planes has area proportional to the planes' height separation, meaning a fixed constant times that separation, regardless of whether the belt is near the equator or a pole. A narrower circumference near the pole is offset by a longer sloping surface distance for the same height increment.

This statement does not say that equal-height samples are equally spaced along the curved surface. It says their complete intervening belts have equal areas. Sampling location, path length, and represented area remain distinct.

**Use a finite patch before trusting a local approximation.** Let the southern and northern latitude boundaries be $\varphi_{\mathrm S}$ and $\varphi_{\mathrm N}$, and let its positive longitude width be $\Delta\lambda$. Let $A_{\mathrm{cell}}$ denote its exact spherical area. The label $\mathrm{cell}$ identifies a bounded region rather than an infinitesimal piece.

$$
A_{\mathrm{cell}}
=R^2\Delta\lambda
 \bigl(\sin\varphi_{\mathrm N}-\sin\varphi_{\mathrm S}\bigr).
\tag{1.11}
$$

**Symbol-by-Symbol**

- $A_{\mathrm{cell}}$: finite patch area; subscript $\mathrm{cell}$ labels the quantity.
- $R$: radius; superscript $2$: square the radius.
- $\Delta\lambda$: positive longitude width in radians; $\Delta$ denotes a finite change and $\lambda$ longitude.
- $\varphi_{\mathrm N}$, $\varphi_{\mathrm S}$: northern and southern latitude boundaries; subscripts select the boundaries.
- $\sin$: sine; $-$ subtracts the two height fractions; parentheses group that difference; adjacency multiplies; $=$ states exact equality for the ideal sphere.

**Plain-English Translation:** A finite patch's area is its longitude width times its signed-height span, multiplied by squared radius.

If the longitude interval crosses zero, its width must be interpreted along the intended patch. A cell from 359 degrees to one degree east spans two degrees, not minus 358 degrees. Coordinate arithmetic needs the periodic interpretation before being used in a physical formula.

For a one-degree-wide cell centered at the equator with latitude boundaries half a degree north and south, the area on a 6,371-kilometer sphere is about 12,364 square kilometers. Centering the same angular cell at 60 degrees north gives about 6,182 square kilometers. The exact ratio is one-half for these symmetric latitude boundaries. The corresponding rectangular distance-product approximation is close because the cells are narrow.

For a cell spanning a very broad latitude interval, a cosine evaluated only at its center can be a poor area approximation. Formula (1.11) removes that ambiguity when actual cell boundaries are available.

**Accumulate all longitudes over a polar cap.** Let $\varphi_0$ be its southern boundary and $A_{\mathrm{cap}}$ the area extending northward to the North Pole. Let $A_S$ denote the area of the entire spherical surface; subscript $S$ labels the surface.

$$
A_{\mathrm{cap}}=2\pi R^2(1-\sin\varphi_0),
\qquad A_S=4\pi R^2.
\tag{1.12}
$$

**Symbol-by-Symbol**

- $A_{\mathrm{cap}}$: north polar cap area; $A_S$: whole-sphere area. Subscripts identify the regions.
- $\varphi_0$: cap boundary latitude; subscript zero labels this chosen boundary, not a zero latitude value.
- $R$: radius; $\pi$: circle constant; $\sin$: sine.
- $R^2$: squared radius; 1 is the North Pole's height fraction. $-$ subtracts the lower boundary fraction; parentheses group the difference; adjacency multiplies; $=$ states equality.

**Plain-English Translation:** A cap occupies the fraction of the sphere determined by its height span, and the entire surface has area four times the area of a radius-sized planar disk.

The region north of 60 degrees occupies about 6.70 percent of the whole sphere. A latitude range covering one-sixth of the full pole-to-pole angular range therefore does not occupy one-sixth of the area. This provides a quantitative check on polar weighting.

### 1.15 Integrals, zonal means, and global means

**Imagine accumulating field value times physical area.** Let $\mathcal S$ name the spherical surface. The symbol $\int$ denotes an integral. A subscript giving a region tells us where to accumulate; lower and upper bounds give the beginning and end of a coordinate interval. Let $\overline f$ denote an average over longitude at fixed latitude, called the zonal mean.

$$
\overline f(\varphi)
=\frac{1}{2\pi}\int_0^{2\pi}f(\varphi,\lambda)\,d\lambda.
\tag{1.13}
$$

**Symbol-by-Symbol**

- $f$: scalar field; $\overline f$: its zonal mean. The overbar signifies this longitude average.
- $\varphi$: fixed latitude; $\lambda$: longitude variable over which accumulation occurs.
- $\int_0^{2\pi}$: integrate through one full longitude turn; $d\lambda$ identifies its infinitesimal increment.
- $2\pi$: total angular width of that turn. The fraction divides the integral by this width; $=$ defines the mean. Parentheses specify function inputs; commas separate them.

**Plain-English Translation:** At each latitude, accumulate the field around its complete circle and divide by one full turn to obtain one representative value.

No cosine appears inside this fixed-latitude average. Every equal longitude interval on the same circle has the same physical length and represents the same fraction of that circle. The cosine becomes necessary when different latitude circles are combined to represent area.

A profile is a field of one latitude argument, such as this zonal mean. Averaging over longitude removes information about where the original field was high or low around each circle. Two very different global maps can have the same zonal-mean profile. This is intentional when the learning target is a persistent latitude-dependent circulation rather than a full instantaneous map.

**Now average the whole sphere.** Let $\langle f\rangle_A$ denote the surface-area mean, with subscript $A$ identifying the averaging measure. Using either latitude or height fraction gives:

$$
\begin{aligned}
\langle f\rangle_A
&=\frac{1}{4\pi R^2}\int_{\mathcal S} f\,dA\\
&=\frac{1}{4\pi}\int_0^{2\pi}\int_{-\pi/2}^{\pi/2}
 f(\varphi,\lambda)\cos\varphi\,d\varphi\,d\lambda\\
&=\frac12\int_{-1}^{1}\overline f(\arcsin\mu)\,d\mu.
\end{aligned}
\tag{1.14}
$$

**Symbol-by-Symbol**

- $\langle f\rangle_A$: global area mean; angle brackets indicate averaging and subscript $A$ labels area weighting.
- $f$: scalar field; $\mathcal S$: the spherical surface; $R$: radius; $dA$: physical area element.
- $\varphi$, $\lambda$: latitude and longitude; $\mu$: signed height fraction. $\overline f$: zonal mean from (1.13).
- $\arcsin$: inverse sine returning latitude between minus $\pi/2$ and plus $\pi/2$ from its height fraction.
- $\int_{\mathcal S}$: integrate over the surface. The two coordinate integrals accumulate all latitudes and longitudes. The final integral accumulates height fraction from minus one to one.
- $d\varphi$, $d\lambda$, $d\mu$: the corresponding infinitesimal increments; $\cos\varphi$: latitude-area factor.
- $\pi$: circle constant; superscript $2$: squaring; negative lower bounds select the southern or negative end. Fractions divide by total area or coordinate width; adjacent factors multiply; $=$ connects equivalent continuous means.

**Plain-English Translation:** A global mean averages the field by physical surface area, which is equivalent to averaging its zonal mean uniformly in signed height fraction.

Each line describes the same quantity. The first is independent of the coordinate labels. The second shows explicitly why uniform latitude-angle averaging is generally wrong. The third exposes the integration interval used by the Gaussian latitude rule.

A constant field retains its value under every line because the total weight is one. A field that is positive in the north and equally negative at mirrored southern locations has zero global mean. The radius cancels because both the weighted total and the whole-sphere area increase with squared radius. None of these facts makes the mean a sufficient description of the field's variability.

**Worked example: the squared height fraction.** Consider a dimensionless field whose value is the square of height fraction. It is zero at the equator, one at both poles, and unchanged around longitude. Uniform averaging in height fraction gives one-third. Uniform averaging in latitude angle instead gives one-half. Both values can be evaluated accurately, but only the former is its surface-area mean.

**Evaluate that integral once by hand.** An **antiderivative** of a function is another function whose slope equals the original function. For squared height, cubed height divided by three is an antiderivative: its slope is squared height. The rule connecting slopes and accumulated quantities says to evaluate an antiderivative at the upper bound and subtract its value at the lower bound. This is the fundamental theorem of calculus; see [NIST's definite-integral conventions](https://dlmf.nist.gov/1.4#v).

$$
\frac12\int_{-1}^{1}\mu^2\,d\mu
=\frac12\left[\frac{\mu^3}{3}\right]_{-1}^{1}
=\frac12\left(\frac13-\left(-\frac13\right)\right)
=\frac13.
\tag{1.15}
$$

**Symbol-by-Symbol**

- $\mu$: height fraction; $d\mu$: its infinitesimal increment; $\int_{-1}^{1}$: accumulate from the South Pole's height fraction to the North Pole's.
- $\mu^2$: squared height, the field being averaged. $\mu^3/3$: cubed height divided by three, its antiderivative.
- Square brackets with lower label $-1$ and upper label $1$: evaluate the bracketed function at the upper bound and subtract its value at the lower bound. These labels are bounds, not powers.
- Superscripts $2$ and $3$ mean powers. A leading minus sign marks a negative value; the subtraction between fractions forms upper value minus lower value.
- One-half normalizes the accumulated value by the interval width of two; fractions divide; parentheses group the negative lower-bound value; adjacency multiplies; $=$ connects equal values of the same average.

**Plain-English Translation:** Accumulate squared height across the full height interval, then divide by that interval's width to obtain the area mean of one-third.

The negative lower-bound value is worth keeping visible. The accumulated integral is two-thirds, because subtracting minus one-third adds one-third. The mean is then half that total. This calculation makes the reference value reproducible without requiring a general course in integration techniques.

The difference remains when the sample count becomes arbitrarily large. It is a bias in the chosen measure, not a shortage of points. Adding data does not repair an integral taken with the wrong weighting.

### 1.16 Inner products and the size of a whole field

**Compare two maps by multiplying corresponding values.** Let $f$ and $g$ be real scalar fields with finite integrals of their squared values. The notation $(f,g)_A$ will denote their normalized area inner product. The norm $\|f\|_A$ is its associated RMS magnitude.

$$
(f,g)_A=\frac{1}{4\pi R^2}\int_{\mathcal S}f\,g\,dA,
\qquad
\|f\|_A=\sqrt{(f,f)_A}.
\tag{1.16}
$$

**Symbol-by-Symbol**

- $f$, $g$: real scalar fields. $(f,g)_A$: their inner product; parentheses here denote a paired operation, not a location. Subscript $A$ specifies normalized area weighting.
- $\|f\|_A$: the field's area RMS norm; paired vertical bars denote norm, not absolute value at one point.
- $\mathcal S$: spherical surface; $R$: radius; $dA$: area element; $\int_{\mathcal S}$: integrate over that surface.
- $\pi$: circle constant; $R^2$: squared radius. The fraction divides by total area; adjacent $f\,g$ multiplies values at the same point.
- $\sqrt{\phantom{x}}$: nonnegative square root; $(f,f)_A$ pairs the field with itself; $=$ defines the two operations.

**Plain-English Translation:** Compare spatial patterns by their area-averaged product, and measure a field's magnitude by the square root of its mean squared value.

If $f$ and $g$ both have temperature units, the inner product has squared-temperature units. The norm has temperature units. This dimensional check is useful when comparing a physical error norm with a dimensionless normalized training objective.

This inner product is linear in either input when the other is fixed: the contribution from a sum of fields is the sum of their contributions, and constant multipliers can be taken outside the integral. It is symmetric because multiplication of real values is symmetric. Its self-product is nonnegative because squares are nonnegative.

There is one qualification. Changing assigned values only at isolated points, such as the two poles, does not change an area integral because those points have zero surface area. For a continuous field, however, a nonzero value requires nonzero values in a surrounding neighborhood. Its norm can therefore vanish only if the field vanishes everywhere. The smooth-field examples in this chapter satisfy this stronger interpretation.

The qualification matters conceptually: integral measurements describe the field up to what the chosen measure can detect. A single assigned value at a pole has zero influence on an area integral, yet incompatible limits near that pole still destroy continuity. Averaging and regularity test different properties.

**Measure prediction error with a controlled meaning.** Let $p$ be a predicted field and $t$ a reference field with the same physical units. Let $e$ denote their difference, and let $E$ denote its area RMS magnitude:

$$
e=p-t,
\qquad E=\|e\|_A=\sqrt{\langle(p-t)^2\rangle_A}.
\tag{1.17}
$$

**Symbol-by-Symbol**

- $p$: prediction; $t$: reference field. The letter $t$ labels the target here, not time. $e$: signed error; $E$: one nonnegative error magnitude.
- $\|\cdot\|_A$: area RMS norm; the centered dot marks the place of an input, not multiplication. $\langle\cdot\rangle_A$: global area mean.
- $-$ subtracts matching values at the same location; parentheses group this difference; superscript $2$ squares it; $\sqrt{\phantom{x}}$ takes the nonnegative square root; $=$ states the definitions.

**Plain-English Translation:** Subtract the reference map from the prediction, square the local discrepancies, average them over physical area, and return to the original units by taking a square root.

A signed mean error can vanish while this RMS error is large. For example, errors of equal magnitude and opposite sign in two equal-area hemispheres cancel in the mean but reinforce after squaring. The choice of summary must match the scientific question.

An absolute RMS value also cannot be compared directly across targets with different units. Wind error in meters per second and vorticity error in inverse seconds require separate interpretation. **Vorticity** measures local fluid spin; inverse seconds means a rate measured per second. Comparing these different quantities requires an explicit choice of scales that removes their physical units, a process called **nondimensionalization**. The later loss-function chapter will distinguish these physical comparisons from the channel scaling used during learning.

### 1.17 Moments, orthogonality, and measuring a pattern coefficient

**Use simple north-south patterns as exact reference cases.** A **moment** is an average of a chosen power of a variable. Let $M_n$ be the surface mean of the $n$th power of height fraction, where $n$ is a nonnegative integer. An even integer is divisible by two; an odd integer is not. Since height fraction is uniform under the normalized area measure after longitude averaging:

$$
M_n=\frac12\int_{-1}^{1}\mu^n\,d\mu
=\begin{cases}
0,&n\text{ odd},\\[2pt]
\dfrac{1}{n+1},&n\text{ even}.
\end{cases}
\tag{1.18}
$$

**Symbol-by-Symbol**

- $M_n$: normalized surface moment; subscript $n$ labels the power being averaged.
- $\mu$: height fraction; $n$: a nonnegative integer; superscript $n$ means repeated multiplication, with power zero defined as one here.
- $\int_{-1}^{1}$: accumulation over the full height interval; $d\mu$: its increment; one-half divides by interval width two.
- The brace chooses the appropriate case according to whether $n$ is odd or even. Zero is the exact odd-moment result; $1/(n+1)$ is the even-moment result.
- $+$ adds one to the power in the denominator; fractions divide; $=$ gives equivalent moment descriptions.

**Plain-English Translation:** North-south antisymmetric powers cancel, while even powers have known positive area averages that can check any grid-weighting implementation.

The first few values are one, zero, one-third, zero, and one-fifth. These are independent scientific oracles: their values come from the continuous geometry, not from the code being checked. A test based on them can detect a wrong latitude measure even if an implementation agrees with its own duplicated formula.

The constant pattern and the signed-height pattern are orthogonal. Their product is the signed-height pattern, whose mean is zero. The squared norm of the constant pattern is one; the squared norm of the signed-height pattern is one-third. Orthogonality therefore does not imply equal size. **Normalization** rescales each pattern to a chosen size, often unit norm.

**Fit one spatial pattern to an observed map.** Let $g$ be a chosen nonzero pattern and let $a$ be its multiplying coefficient. Write $\widehat f$ for the approximation consisting of that coefficient times the pattern. The hat marks an approximation, not a transform in this chapter. The coefficient minimizing the area mean squared residual is:

$$
a=\frac{(f,g)_A}{(g,g)_A},
\qquad \widehat f=a\,g,
\qquad (f-\widehat f,g)_A=0.
\tag{1.19}
$$

**Symbol-by-Symbol**

- $f$: field being approximated; $g$: selected nonzero pattern; $a$: scalar multiplying coefficient.
- $\widehat f$: approximate field; the hat means approximation.
- $(\cdot,\cdot)_A$: normalized area inner product; the two centered dots mark its input positions. $(g,g)_A$ is the pattern's positive squared norm.
- $f-\widehat f$: residual field. The final zero says its inner product with the selected pattern vanishes.
- Fraction bar: divide alignment by squared pattern size; adjacency: multiplication; $-$: subtraction; $=$: equality. Parentheses pair whole fields, with comma separating the two inputs.

**Plain-English Translation:** Measure alignment with the chosen pattern, correct for the pattern's size, and leave behind a residual containing no further component along that pattern.

The denominator prevents a change in the arbitrary pattern normalization from changing the fitted physical approximation. Doubling the pattern halves its coefficient, leaving the product unchanged. Treating a coefficient as an absolute physical amount without knowing the pattern normalization is therefore ambiguous.

For a concrete map, start with a uniform value of two and add three times the signed-height pattern. Its mean is two. Its best coefficient along the signed-height pattern is three because the constant contribution is orthogonal to that pattern. In the coefficient formula, the numerator is one and the denominator is one-third; their ratio is three. Its residual after subtracting the height component is the uniform map of two. Combining the constant and height patterns reconstructs the original field exactly.

No long minimization proof is needed to interpret the result. If a residual still aligned with the chosen pattern, increasing or decreasing that pattern's coefficient would remove some squared error. At the best coefficient, no such aligned residual remains. The same principle will measure Fourier and spherical harmonic coefficients.

### 1.18 Quadrature: what the Gaussian rule promises

**Replace a smooth integral by selected measurements.** Let $g$ now denote a real function of height fraction only. Let $H$ be the number of latitude nodes, $\mu_j$ the node selected by row index $j$, and $q_j$ its unnormalized Gaussian weight. Number rows from zero. The quadrature rule and its normalized weights are:

$$
\int_{-1}^{1}g(\mu)\,d\mu
\approx\sum_{j=0}^{H-1}q_jg(\mu_j),
\qquad
w_j=\frac{q_j}{2},
\qquad
\sum_{j=0}^{H-1}w_j=1.
\tag{1.20}
$$

**Symbol-by-Symbol**

- $g$: a function of height fraction; $\mu$: integration variable; $\mu_j$: the node at row $j$.
- $H$: total node count; $j$: integer row index. $\sum_{j=0}^{H-1}$ adds terms from zero through the last row; the upper expression is a summation limit, not a power.
- $q_j$: Gaussian integral weight; $w_j$: normalized area-mean row weight. Their subscripts select nodes.
- $\int_{-1}^{1}$: integrate over the height interval; $d\mu$: its increment. $g(\mu_j)$ evaluates the function at one node.
- $\approx$: approximation for a general integrable function. $=$: exact rule definitions or identities, subject to numerical rounding in implementation.
- Division by 2 normalizes by interval width; $-$ in $H-1$ subtracts one for zero-based indexing; adjacent factors multiply. The final 1 is the total normalized weight.

**Plain-English Translation:** Approximate the height integral with a weighted sum, and divide the integral weights by two to obtain weights for a normalized whole-sphere mean.

The approximation becomes an equality for every polynomial through degree twice $H$ minus one, assuming exact mathematical nodes and weights. This is an exactness statement about a specified function class. It does not assert exactness for every smooth function, every discontinuous function, or every product built from individually representable fields.

The Gaussian nodes are the zeros of a particular degree-$H$ polynomial in the Legendre family. A **zero** is an input where a function's value vanishes. Legendre polynomials form a family orthogonal under the unweighted height integral. Chapter 3 develops their construction and explains why their zeros produce this integration rule; see [NIST's definition of classical orthogonal polynomials](https://dlmf.nist.gov/18.3).

For the present purpose, the mathematical contract of the rule is sufficient: known nodes, positive weights, the correct total weight, and polynomial exactness through a known degree. This is stronger than choosing rows because they look evenly spaced on a map.

**Work the two-node rule completely.** Symmetry suggests two opposite height nodes with equal weights. Requiring the constant and squared-height averages to be correct places them at opposite inverse-square-root-of-three heights:

$$
\mu_0=-\frac{1}{\sqrt3},
\qquad \mu_1=\frac{1}{\sqrt3},
\qquad q_0=q_1=1,
\qquad w_0=w_1=\frac12.
\tag{1.21}
$$

**Symbol-by-Symbol**

- $\mu_0$, $\mu_1$: the southern and northern height nodes; subscripts zero and one label the two rows.
- $q_0$, $q_1$: corresponding integral weights; $w_0$, $w_1$: corresponding normalized mean weights.
- $\sqrt3$: positive square root of three; a leading $-$ selects the southern node.
- Fractions divide; $=$ specifies equal values. The numerical weights 1 and one-half refer to integration over an interval of width two and its normalized average, respectively.

**Plain-English Translation:** Two symmetric samples at carefully chosen heights reproduce all height-polynomial averages through cubic degree.

The latitudes are approximately minus 35.2644 degrees and plus 35.2644 degrees. Neither the equator nor the poles is sampled. The constant average is correct because the mean weights sum to one. Odd powers cancel by symmetry. Both sampled squared heights are one-third, so the squared-height average is correct. These observations account for degrees zero through three without a long algebraic proof.

The fourth-power average is not correct: both sampled fourth powers are one-ninth, whereas the true mean is one-fifth. A field proportional to squared height therefore has an exactly integrated mean on this two-node rule but an incorrectly integrated mean square. Computing energy-like quantities and squared losses can require greater resolution than computing the mean of the field itself.

If a polynomial basis includes powers through degree $D$, products of two such patterns can reach degree twice $D$. At least $D+1$ Gaussian latitude nodes are sufficient for those polynomial products. This statement concerns the latitude integration of polynomial products. Longitude sampling and nonpolynomial associated latitude factors require their own analysis in later chapters.

### 1.19 From a full grid to a discrete field inner product

**Lay equally spaced marks around each latitude circle.** Let $W$ count longitude columns and let $k$ select one of them. Let $\lambda_0$ be the first longitude. A full repeating grid contains one turn without duplicating its endpoint:

$$
\lambda_k=\lambda_0+\frac{2\pi k}{W},
\qquad k=0,1,\ldots,W-1.
\tag{1.22}
$$

**Symbol-by-Symbol**

- $\lambda_k$: longitude at column $k$; $\lambda_0$: the chosen first longitude; the subscripts select columns.
- $W$: longitude sample count; $k$: integer column index.
- $\pi$: circle constant; $2\pi/W$: spacing in radians. Multiplying by $k$ gives the angular offset from the first sample.
- $+$ adds that offset; the fraction divides a turn into $W$ intervals; $=$ specifies the grid and index values. $\ldots$ continues the integer sequence through $W-1$; $-$ subtracts one for zero-based indexing.

**Plain-English Translation:** Divide a repeating circle into equal intervals and store one sample per interval without storing the starting point twice.

With four columns and a zero starting longitude, the samples are zero, 90, 180, and 270 degrees. Including 360 degrees as a fifth independent entry would overweight the reference meridian in an unweighted longitude average. A plotting tool may temporarily copy the initial column to close a visible map seam, but that copied column must not be treated as a new physical observation during analysis.

**Combine longitude averaging with Gaussian latitude integration.** Let $f_{jk}$ be the sample at latitude row $j$ and longitude column $k$. Let $g_{jk}$ be a second field on the identical grid. Write $\langle f\rangle_h$ for the discrete area mean and $(f,g)_h$ for the discrete inner product. The subscript $h$ labels the sampled calculation; it is not the increment from (1.7).

$$
\begin{aligned}
\langle f\rangle_h
 &=\sum_{j=0}^{H-1}\sum_{k=0}^{W-1}\frac{w_j}{W}\,f_{jk},\\
(f,g)_h
 &=\sum_{j=0}^{H-1}\sum_{k=0}^{W-1}\frac{w_j}{W}\,f_{jk}g_{jk},
\qquad \|f\|_h=\sqrt{(f,f)_h}.
\end{aligned}
\tag{1.23}
$$

**Symbol-by-Symbol**

- $f_{jk}$, $g_{jk}$: field samples at row $j$ and column $k$; the paired subscripts are selectors, not multiplication.
- $H$, $W$: row and column counts; $j$, $k$: their zero-based indices. The two summation symbols add over all indicated rows and columns.
- $w_j$: positive normalized Gaussian row weight; $w_j/W$: that row's weight split equally among its longitude columns.
- $\langle f\rangle_h$: discrete mean; $(f,g)_h$: discrete inner product; $\|f\|_h$: discrete RMS norm. Subscript $h$ denotes the grid calculation.
- Upper summation labels $H-1$ and $W-1$ are terminal indices, not powers. $\sqrt{\phantom{x}}$ takes a nonnegative square root; fractions divide; adjacent factors multiply; $=$ defines the discrete quantities.

**Plain-English Translation:** Give each sample its latitude rule's share of surface influence, split uniformly across longitude, and use the same weights when comparing or measuring fields.

The equality signs define operations on arrays exactly, apart from arithmetic rounding. Their agreement with continuous quantities is a separate accuracy question. A constant field is integrated correctly. Reversing both the latitude coordinates and corresponding data rows leaves the result unchanged. Reversing only the data rows changes the represented field; symmetric row weights can conceal that mistake in a global mean.

Because all weights are positive, the discrete self-product vanishes only when every stored entry vanishes. Nevertheless, a nonzero continuous field can vanish at every sample. The discrete norm is a norm of the array, not an unconditional detector of every possible continuous pattern.

**A concrete field that disappears between columns.** Let $u$ denote a dimensionless example field with four longitude oscillations and an amplitude that vanishes smoothly at the poles. Sample it at the four longitudes just listed:

$$
u(\varphi,\lambda)=\cos^4\varphi\sin(4\lambda),
\qquad
u(\varphi,\lambda_k)=0
\quad(k=0,1,2,3;\ W=4,\ \lambda_0=0).
\tag{1.24}
$$

**Symbol-by-Symbol**

- $u$: the example scalar field; $\varphi$, $\lambda$: latitude and longitude; $\lambda_k$: longitude sample from (1.22).
- $\cos^4\varphi$: fourth power of the latitude cosine; $\sin(4\lambda)$: sine of four times longitude.
- $k$: column index; $W$: column count; $\lambda_0$: first longitude. The values in parentheses specify this four-column example.
- $=$ gives the field definition and its sampled values; zero is exact in mathematical arithmetic. Adjacency multiplies factors; commas and semicolon separate conditions.

**Plain-English Translation:** A smooth nonzero whole-sphere pattern can produce an all-zero array when its longitude variation is missed by the sampling locations.

In (1.24), the field symbol is $u$; it is unrelated to the height coordinate $\mu$. At longitude 22.5 degrees on the equator, the field reaches one, despite every sampled column being zero. In Cartesian form it is proportional to the product of $x$, $y$, and their squared-coordinate difference, divided by the fourth power of radius, so the example is smooth on the sphere. Its nonzero continuous RMS is approximately 0.45075; the four-column sampled RMS is zero.

The amplitude's latitude factor prevents the example from relying on an invalid pole discontinuity. Sampling ambiguity remains even when the physical field is smooth. Chapter 2 will quantify how many samples are needed for a specified set of longitude waves; Chapter 4 will combine that restriction with latitude sampling.

### 1.20 Why multiplying Gaussian weights by cosine is a different problem

**Return to the squared-height field.** Its correct area mean is one-third. Gaussian weights already approximate a uniform integral in height fraction. Multiplying them by the latitude cosine inserts an extra factor proportional to the radius of a latitude circle. Renormalizing these altered weights makes their sum one again, but it does not restore the original measure.

Let $M_{\mathrm{extra}}$ denote the limiting average produced by this extra factor. In height coordinates the cosine equals the nonnegative square root of one minus squared height, giving:

$$
M_{\mathrm{extra}}
=\frac{\displaystyle\int_{-1}^{1}\mu^2\sqrt{1-\mu^2}\,d\mu}
       {\displaystyle\int_{-1}^{1}\sqrt{1-\mu^2}\,d\mu}
=\frac14.
\tag{1.25}
$$

**Symbol-by-Symbol**

- $M_{\mathrm{extra}}$: the mean under the altered weighting; its subscript labels the extra latitude factor.
- $\mu$: height fraction; $\mu^2$: its square, the field being averaged.
- $\sqrt{1-\mu^2}$: latitude cosine written in height coordinates; the square root is nonnegative on the allowed interval.
- The integrals run from minus one to one; $d\mu$ is the height increment. The numerator weights the field; the denominator normalizes the altered weights.
- Superscript $2$: square; $-$: subtraction; fraction bars: division; adjacency: multiplication; $=$: the limiting value of this different normalized integral. One-quarter is not the true area mean of the chosen field.

**Plain-English Translation:** An extra cosine systematically changes the question being averaged and biases this field's limiting mean from one-third to one-quarter.

The denominator ensures that a constant field still passes the constant-field test. Symmetry ensures that odd height powers still average to zero. A wrong rule can therefore pass two reasonable checks. The squared-height moment detects the error because it is sensitive to how influence is distributed between high and low latitudes.

Equal weighting of Gaussian row entries also converges to a different average. As the Gaussian node count increases, their latitude angles become approximately uniformly distributed, so this unweighted squared-height average approaches one-half. Neither incorrect rule is repaired by increasing the number of latitude rows.

![Numerical estimates of the squared-height mean as the Gaussian latitude count increases. Correct Gaussian weighting gives one-third; equal-entry weighting approaches one-half; an extra cosine approaches one-quarter. These are differences in measure, not random errors.](figures/weighting-bias.png){width=95%}

There are settings in which cosine weighting is appropriate. On a sufficiently fine equiangular latitude grid it approximates the spherical area Jacobian. The error is not the presence of a cosine symbol by itself. The error is failing to match the integration weight to the coordinate variable and sampling rule actually used.

\newpage

## Code Connection

### 1.21 The stored scientific object

A **tensor** is a numerical array whose axes have specified meanings. Its **shape** lists the lengths of those axes. One sampled scalar field on a full grid has shape `(H, W)`: latitude first, longitude second. The symbols `H` and `W` have the same meanings as in (1.23).

One number per entry is not a complete data contract. A **data contract** specifies what a producer promises and what a consumer must check. For a sampled physical field, it includes coordinate values, axis order, units, and the meaning of each variable. A file with the correct shape but different latitudes violates the physical contract even if every entry is finite.

The repository's current contract is explicit. [GaussianGrid](../../ml/src/ml/diagnostics/grid.py) accepts latitude coordinates matching the Gaussian rule within a numerical tolerance and accepts either latitude orientation. It checks that longitudes have the uniform spacing implied by one complete turn without a duplicate endpoint. It preserves the input coordinate order and returns normalized weights in that order.

A **tolerance** is a permitted small numerical discrepancy. Here latitude comparisons allow an absolute difference of 0.00005 degrees. This accommodates stored numerical precision; it is not permission to relabel a visibly different sampling layout as Gaussian. `np.allclose` in the implementation performs this approximate numerical comparison. It does not interpolate the data.

**Interpolation** estimates values at new locations from values at existing locations. Attaching different coordinate labels to unchanged numbers is not interpolation. A real change of grid must include a method for estimating the field at the new nodes and an assessment of what that method preserves or distorts.

The distinction is consequential when loading data produced by another simulator. An array with the expected row and column counts can still represent an unsupported grid. Rejecting it is preferable to silently applying the wrong transform and weights.

### 1.22 A reproducible check against continuous answers

The following examples can be run consecutively in one Python file. Their source is also executable through the textbook's build script. NumPy, imported under the short name `np`, supplies numerical arrays and elementary functions. The functions `area_mean` and `area_l2_norm` are the repository implementations being checked.

First construct actual Gaussian coordinates, rather than copying a rounded list of latitude values. `leggauss` returns height nodes and integral weights. `arcsin` converts height fraction to latitude angle in radians, and `rad2deg` converts those angles to the degree coordinates expected by `GaussianGrid`. `arange` creates zero-based consecutive indices. The helper `make_grid` gives this construction one reusable owner within the examples.

```python
import numpy as np

from ml.diagnostics.grid import GaussianGrid
from ml.diagnostics.spatial import area_mean, area_l2_norm


def make_grid(height, width):
    nodes, _ = np.polynomial.legendre.leggauss(height)
    latitudes = np.rad2deg(np.arcsin(nodes))
    longitudes = np.arange(width) * (360.0 / width)
    return GaussianGrid(latitudes, longitudes)


grid = make_grid(4, 8)
mu = np.sin(np.deg2rad(grid.latitudes))
field = np.repeat((mu**2)[:, None], 8, axis=1)

assert np.isclose(grid.weights.sum(), 1.0)
assert np.isclose(area_mean(field, grid.latitudes), 1 / 3)
assert np.isclose(
    area_l2_norm(field, grid.latitudes), np.sqrt(1 / 5)
)
assert np.isclose(
    area_mean(field[::-1], grid.latitudes[::-1]), 1 / 3
)
print("Squared-height mean:", area_mean(field, grid.latitudes))
print("Squared-height RMS:", area_l2_norm(field, grid.latitudes))
```

The double asterisk in Python raises a number to a power. The expression `[:, None]` keeps all latitude entries and adds a one-entry longitude axis; `repeat` copies them to eight columns. This creates a field independent of longitude, not eight independent physical variables. `axis=1` selects the newly created column axis. `[::-1]` reverses an axis. Both coordinates and field rows are reversed together in the final check.

`assert` stops the program if its condition fails. `isclose` permits small arithmetic rounding differences. Its purpose here is to compare the computation with independently known continuous answers, not to establish symbolic equality of floating-point representations.

The expected mean is one-third and the expected RMS is approximately 0.447214. The RMS uses the fourth height moment because the field itself is squared height. Four Gaussian rows integrate that fourth-degree polynomial exactly within rounding. Replacing the normalized Gaussian weights with an extra cosine changes the mean and causes this check to fail.

There is an important limit to the reversal check. Reversing the field alone also leaves its global mean unchanged because the Gaussian weights are symmetric about the equator. A scalar global average cannot verify geographical orientation. Coordinate identity and explicit latitude-dependent comparisons are still required. A passing numerical invariant proves only the property it actually measures.

### 1.23 Recover a pattern coefficient with the same weighting

Continue with the same grid and height coordinates. The next example constructs the field described after (1.19): a constant part of two and a height-pattern coefficient of three. `dot` computes the vector dot product of matching row entries; here its first input is the row-weight vector, so it performs the discrete weighted accumulation.

```python
pattern = mu
observed = 2.0 + 3.0 * pattern
weights = grid.weights

coefficient = (
    np.dot(weights, observed * pattern)
    / np.dot(weights, pattern * pattern)
)
residual = observed - coefficient * pattern

assert np.isclose(coefficient, 3.0)
assert np.allclose(residual, 2.0)
assert np.isclose(np.dot(weights, residual * pattern), 0.0)
print("Recovered height coefficient:", coefficient)
```

This is a small transform: a complete sampled profile is reduced to the coefficient of one chosen pattern. Its mathematical content is projection, not a property unique to neural networks. The same operation becomes a full transform when performed for a suitable collection of patterns.

The denominator is the pattern's squared size. Omitting it would return one instead of three in this example because the height pattern's squared norm is one-third. That error can be hidden when a library uses unit-normalized basis functions internally. A coefficient's meaning cannot be transferred between normalization conventions without checking their scale factors.

The repository's `legendre_basis` function in [grid.py](../../ml/src/ml/diagnostics/grid.py) constructs latitude basis values with a specific normalization under the saved Gaussian weights. Its [Legendre output head](../../ml/src/ml/training/model.py) uses weighted latitude projections before producing output coefficients and rebuilding a profile. Chapter 3 develops the underlying patterns; Chapter 9 follows the learned computation. The present example supplies the projection operation those implementations rely on.

### 1.24 Demonstrate an undetectable sampled pattern

The next example evaluates (1.24) on two grids. The helper `hidden_field` accepts an actual validated grid and evaluates the same continuous expression at its nodes. `meshgrid` constructs all latitude-longitude combinations. The argument `indexing="ij"` makes the first input vary along the first output axis, preserving latitude-first storage.

```python
def hidden_field(grid):
    latitude, longitude = np.meshgrid(
        np.deg2rad(grid.latitudes),
        np.deg2rad(grid.longitudes),
        indexing="ij",
    )
    return np.cos(latitude)**4 * np.sin(4 * longitude)


coarse = make_grid(8, 4)
fine = make_grid(8, 64)
coarse_values = hidden_field(coarse)
fine_values = hidden_field(fine)

coarse_rms = area_l2_norm(coarse_values, coarse.latitudes)
fine_rms = area_l2_norm(fine_values, fine.latitudes)

assert coarse_rms < 1e-14
assert np.isclose(fine_rms, np.sqrt(64 / 315))
print("Four-column RMS:", coarse_rms)
print("64-column RMS:", fine_rms)
```

The coarse result is approximately zero, with tiny nonzero values caused by evaluating sine at finite-precision representations of multiples of $\pi$. The fine result is approximately 0.450749. The different arrays sample the same smooth mathematical field. The larger result did not arise because the field changed; the finer longitude sampling detected a pattern that the coarse grid missed.

The reference RMS can be checked without trusting the sampling implementation. Squaring the longitude sine gives an average of one-half around a full turn. Squaring the latitude factor gives the fourth power of one minus squared height. Expanding that finite polynomial and using the moments in (1.18) gives a total mean square of 64 divided by 315. Taking its square root gives the stated result. This is a short interpretation of the reference calculation, not an assumption that a dense numerical grid is automatically exact.

Run all three examples from the repository root with:

```sh
uv run --project ml --group train --group vis \
  python presentations/textboox/build.py --check
```

The script executes these Markdown examples, checks additional numerical values quoted in the text, and prints the results. It does not start a simulation, train a model, or change experiment data.

### 1.25 Follow the geometry into the ML pipeline

A **machine-learning model** is an adjustable computation fitted from examples. An **input** is what it receives; a **target** is the reference answer used during fitting or assessment. A **channel** is a separately identified variable or feature stored alongside others at the same spatial locations. A **batch** is a collection of examples processed together.

The prepared input arrays have shape `(B, K*V, H, W)`. Here `B` counts examples in a batch, `K` counts snapshots in one input time window, `V` counts physical input variables, `H` counts latitude rows, and `W` counts longitude columns. The asterisk denotes multiplication. A **snapshot** is one saved state; a **window** is a selected consecutive collection of snapshots. Time and variable identity are packed into separate channels. Two snapshots of three variables produce six input channels, not a six-times-larger geographic surface.

Target arrays have shape `(B, C, H)`, where `C` counts output variables. They contain one latitude profile per output variable and example. The target is built from a configured average over time and longitude. It describes a finite trajectory's average behavior, not the next full instantaneous map. A **trajectory** is the sequence of simulated states through time. Its finite average is an estimate, not a guarantee about an infinitely long simulation.

The ownership is visible in the source:

| Source | What it owns |
|------------------------|--------------------------------------------------------|
| [Simulation loading](../../ml/src/ml/data/simulation_data.py) | Reading the physical record, coordinate and unit checks, time-window selection, and construction of target profiles. |
| [Grid definitions](../../ml/src/ml/diagnostics/grid.py) | Gaussian coordinate validation, normalized row weights, coordinate identity, and the normalized latitude basis. |
| [Spatial diagnostics](../../ml/src/ml/diagnostics/spatial.py) | Longitude means, global area means, and area RMS norms. |
| [Model construction](../../ml/src/ml/training/model.py) | Attaching coordinates to inputs, selecting Gaussian transforms, adapting latitude order, and constructing the output head. |
| [Error calculations](../../ml/src/ml/diagnostics/errors.py) | Comparing predictions and references with explicit shape checks and the appropriate latitude weights. |

The table is a map of responsibilities, not a requirement to memorize filenames. The reusable reasoning is that data identity, numerical geometry, model computation, and error interpretation have separate owners and must agree.

The model's `CoordinateEmbedding` attaches latitude and longitude information to the inputs. It uses the actual saved coordinates, rescaled numerically. This makes location available to the learned computation. It does not turn an ordinary angular difference into physical distance, and a raw longitude coordinate still jumps at the chosen seam. Coordinate features do not by themselves guarantee every physical symmetry.

The spherical transform library expects latitude order running north to south. Supported Isca input runs south to north. `GaussianSphericalConv` reverses rows before its transform-based calculation and reverses the output afterward. This is an adaptation of storage convention, not a physical reflection of the predicted circulation. The mathematical transform is developed in Chapter 4.

An **output head** is the final part of a model that converts its internal features into requested predictions. The repository offers a full-field head followed by longitude averaging, a profile head that averages intermediate features around longitude before the final mapping, and a Legendre head that predicts latitude-pattern coefficients. All retain the same need for coordinates and normalization. Their statistical and physical differences require the neural-operator chapters; they cannot be inferred from output shape alone.

The word normalization has two distinct uses that must not be confused. **Basis normalization** sets the sizes of spatial patterns under an inner product. **Data normalization** shifts and rescales numerical channels to facilitate training. The repository's data-normalization statistics use an unweighted sampling convention; its physical error diagnostics use Gaussian area weights. These operations answer different questions and are documented in [the norms and normalization conventions](../../docs/norms.md).

The scientific discipline is to state the quantity being computed before choosing the numerical reduction. A mean over entries, a mean over longitude, a mean over area, and a mean over repeated simulations can all be reasonable. They become interchangeable only under additional conditions that must be checked.

## Sanity Check

**Question:** A model's prediction and reference agree at every point of a coarse full Gaussian grid, so their Gaussian-weighted discrete RMS error is zero. A programmer concludes that the two smooth physical fields must agree everywhere on the sphere. Is that conclusion justified, and what information would be needed to justify it?

Attempt the question before reading the answer.

**Answer:** Zero discrete RMS error establishes equality of the stored arrays because all grid weights are positive. It does not establish equality between samples. Equation (1.24) supplies a counterexample: the zero field and a nonzero smooth field agree at all four sampled longitudes. Correct Gaussian latitude weights cannot recover longitude information that was never observed.

To justify equality of the continuous fields, one would need an additional restriction on their permitted patterns and enough independent samples to identify every field in that restricted class. For example, a specified finite set of wave patterns can admit unique reconstruction when the sampling rule resolves all of them. Chapters 2-4 establish the corresponding conditions for Fourier and spherical harmonic representations.

The field, coordinates, sampling rule, and permitted representation must therefore be considered together. A successful array comparison is evidence about the sampled learning problem. Its interpretation as a statement about the physical sphere requires the mathematical assumptions that connect the two.
