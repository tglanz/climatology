# Table of Contents

1. **A Sphere Is Not a Flat Image.** Fields, coordinates, distances, cell areas, and area-weighted averages. Why a rectangular array needs spherical geometry.
2. **Waves Around a Latitude Circle.** Repeating patterns, sine and cosine waves, wave size and position, complex numbers as pairs of real numbers, and the one-dimensional Fourier transform along longitude.
3. **Patterns from South to North.** Why latitude is not another repeating direction. Polynomials, weighted comparisons of patterns, Legendre polynomials, and associated Legendre polynomials: latitude shapes matched to a chosen longitude wave.
4. **Spherical Harmonic Transforms.** Spherical harmonics as whole-sphere wave patterns. The spherical harmonic transform (SHT) measures their mixing amounts; the inverse SHT rebuilds the field. Sampling, retained waves, and false patterns caused by insufficient samples.
5. **Describing Moving Fluid.** Velocity as speed with direction, local fluid spin called vorticity, change across space, and change over time. Streamfunction: one field that specifies horizontal flow with no local spreading or gathering.
6. **The Barotropic Vorticity Equation on a Sphere.** A model of horizontal fluid motion without resolved vertical structure. Rotation of the planet, transport of spin, friction, and the numerical steps that advance the simulated state.
7. **Stochastic Stirring.** Random forcing: externally supplied changes that sustain motion. Random draws, forcing strength, memory over time, selected wave sizes, latitude localization, and repeatable experiments.
8. **Learning Maps Between Fields: The FNO.** Neural networks as adjustable computations fitted to examples. Operators as maps between whole functions. The Fourier Neural Operator (FNO): learned mixing of Fourier wave components, combined with local computations.
9. **Learning on the Sphere: The SFNO.** The Spherical Fourier Neural Operator (SFNO) uses spherical harmonics for its global computation. Coordinates, channel mixing, retained waves, output profiles, and limits of physical guarantees.
10. **From Simulation Output to Learning Examples.** Preprocessing: validate coordinates and units, select time windows, build long-time average targets, separate training and held-out simulations, and rescale values using training data.
11. **Training and Loss Functions.** A loss is a numerical penalty for prediction error. Follow one group of examples through prediction, loss, parameter updates, validation, stopping, and saved model state.
12. **Evaluation and the Complete Pipeline.** Return predictions to physical units, compare with reference predictions, weight errors by area, distinguish windows from simulations, quantify variation between repeated runs, and trace data through the entire system.

# Chapter 1: A Sphere Is Not a Flat Image

## The Problem

Imagine storing the temperature of Earth's surface in a rectangular array. Each row contains measurements along one east-west circle. Each column follows a north-south line. The array looks like an image, so it is tempting to process it as an ordinary image.

That resemblance hides three physical facts. East-west circles shrink toward the poles. The first and last longitude columns meet on the globe. At either pole, all longitude labels identify the same point.

A calculation can therefore have the correct array shape and the wrong physical meaning. A three-column neighborhood covers a larger east-west distance near the equator than near a pole. An average over all array entries gives every entry equal influence, even when entries represent unequal areas. Adding zeros outside the left and right edges introduces an artificial boundary through a connected ocean or atmosphere.

These are failures of flat-image assumptions. A latitude-longitude grid remains a valid way to store and calculate spherical fields when its geometry is handled explicitly. The codebase uses such grids throughout its simulation and learning pipeline.

A **field** assigns a physical value to every location in a region. A temperature map is a field. A **scalar field** assigns one number at each location. Temperature is a scalar; horizontal wind needs both an eastward and a northward component, meaning two numbers measured along specified directions. This chapter uses scalar fields so that geometry can be understood before direction-dependent quantities.

A computer stores only finitely many measurements of a field. A **sample** is a value at one chosen location. A **grid** specifies those locations and how they are arranged. An **array** stores the sampled numbers in a chosen order. Coordinates attach physical locations to those array positions.

By the end of this chapter, you should be able to explain why identical array shapes can describe different physical grids, choose the right kind of average, and recognize why latitude and longitude require different treatment.

## The Intuition

### Wrap the image around a globe

Draw a checkerboard on a rectangular sheet and wrap its left and right edges together. You obtain a cylinder. To make a sphere, you must also gather the entire top edge into one point and the entire bottom edge into another.

The gathering explains the crowding near the poles. Squares on the sheet cannot remain equal-size squares on the sphere. Each row still has the same number of entries, but the physical circle holding those entries gets smaller.

**Latitude** measures how far north or south a location lies, as an angle from the equator. The equator is the circle halfway between the poles. It has latitude zero. The North Pole has latitude 90 degrees; the South Pole has latitude minus 90 degrees.

**Longitude** measures the east-west angle around the rotation axis relative to a chosen reference line. A full turn is 360 degrees. Longitude zero and longitude 360 degrees identify the same line.

The **radius** of a sphere is the distance from its center to its surface. We approximate Earth as a smooth sphere with a constant radius. This chapter ignores mountains and the small difference between Earth's equatorial and polar radii.

The mental picture is now concrete: latitude chooses a ring; longitude chooses a position around that ring.

### Separate a location from its label

Suppose a row contains samples at longitudes zero, 90, 180, and 270 degrees. The next sample after 270 degrees would return to zero. Storing 360 degrees as a fifth independent location would count the starting location twice.

A direction that returns to its starting point is **periodic**. Longitude is periodic. The apparent seam between the array's left and right sides comes from the coordinate labels, not from a break in the physical surface.

Latitude does not wrap in the same way. Moving north reaches the North Pole, not the South Pole. Continuing across the North Pole moves down a different longitude. Joining the top array row directly to the bottom row creates a connection absent from the sphere.

This distinction will determine which wave patterns are suitable in the next chapters.

### Count surface area rather than storage slots

Imagine two narrow surface patches spanning the same changes in latitude and longitude. Put one at the equator and the other at 60 degrees north. The northern patch has about half the area because its east-west width is about half as large.

If the equatorial patch has temperature departure zero and the northern patch has temperature departure ten, an average of their two numbers gives five. Here **temperature departure** means temperature minus a fixed reference temperature, measured in degrees Celsius.

An average representing their combined surface area should give the equatorial patch twice the influence. That average is about 3.33 degrees Celsius. It answers a different question from the unweighted value of five.

This two-patch example concerns those patches only. It is not a two-point estimate of the whole globe.

## The Mechanism

### 1. Attach coordinates and units before calculating

A **unit** states what a number measures, such as kilometers, seconds, or degrees Celsius. The number 30 does not identify a physical angle until we know whether its unit is degrees or radians.

A **radian** measures angle by dividing distance along a circle by that circle's radius. A full turn contains twice $\pi$ radians. The constant $\pi$ is a circle's circumference divided by its diameter, approximately 3.14159. Thus, 180 degrees and $\pi$ radians describe the same half-turn.

The distance and area equations below require angles in radians. Data files in this project store latitude and longitude in degrees. A program must convert those values before passing them to trigonometric functions that expect radians.

We will write latitude as $\varphi$, longitude as $\lambda$, and sphere radius as $R$. These symbols label physical quantities; their values do not depend on array storage order.

### 2. Account for shrinking east-west circles

The **cosine** of latitude, written $\cos\varphi$, gives the radius of that latitude circle as a fraction of the sphere's radius. The fraction is one at the equator, one-half at 60 degrees north or south, and zero at either pole.

The **sine** of latitude, written $\sin\varphi$, gives the location's signed height above the equatorial plane as a fraction of the sphere's radius. It is zero at the equator, one at the North Pole, and minus one at the South Pole. We will use it to describe the area between two latitude circles.

For a sphere with radius 6,371 kilometers, a one-degree eastward step along the equator travels about 111.2 kilometers. The same longitude step at 60 degrees north travels about 55.6 kilometers along that latitude circle. A one-degree northward step travels about 111.2 kilometers along a north-south circle at either location.

A fixed number of array columns therefore does not describe a fixed physical distance. This matters whenever a calculation compares neighboring values or interprets the size of a spatial pattern.

### 3. Treat the seam and poles as geometry

For longitude, a neighbor lookup past the final column returns to the first column. This is often called **periodic boundary handling**: lookups continue around a repeating direction.

At a pole, every longitude label denotes the same physical point. A continuous scalar field, meaning a field without jumps between arbitrarily close locations, must approach one value there regardless of the approach longitude. Different temperatures assigned to the same pole would describe an inconsistent field.

Avoiding samples exactly at the poles removes duplicate pole entries from the array. It does not remove shrinking circles or the requirement that the underlying field fit together on the sphere.

### 4. Distinguish two latitude sampling rules

An **equiangular grid** places latitude rows at equal angular intervals. Whether it includes the poles is a separate choice. Its equal angular spacing does not create equal-area cells.

A **Gaussian grid** chooses latitude rows together with numerical weights for adding up values over the sphere accurately. This weighted summation rule is called **Gaussian quadrature**. Quadrature means estimating an accumulated quantity from selected samples and weights. The mathematical construction of these locations belongs to Chapter 3; here we need their operational meaning.

A **full Gaussian grid** uses the same number of equally spaced longitude samples on every latitude row. It still has a rectangular array and still crowds samples toward the poles. It is the grid supported by the project's current ML code. A **reduced Gaussian grid** uses fewer longitude samples on shorter latitude circles; the project's rectangular-grid reader does not support that layout.

These definitions follow the [ECMWF grid reference](https://confluence.ecmwf.int/spaces/FCST/pages/49415103/Gaussian%2Bgrids). Gaussian quadrature's mathematical accuracy depends on the sampled functions; it is not an exact summation rule for every possible field. See [NIST's quadrature reference](https://dlmf.nist.gov/3.5#v).

For four latitude rows, the layouts differ visibly:

| Row order, south to north | Gaussian latitude | Equiangular latitude, including poles |
|-------------------------------|--------------------------:|------------------------------------:|
| First | About -59.4 degrees | -90 degrees |
| Second | About -19.9 degrees | -30 degrees |
| Third | About 19.9 degrees | 30 degrees |
| Fourth | About 59.4 degrees | 90 degrees |

Both layouts can hold an array with four rows. Assigning the wrong latitude labels to the stored numbers changes their physical locations. It does not convert one sampled field into the other.

### 5. Use weights matched to the sampling rule

An **area-weighted average** gives each value influence according to the surface area it represents. On a fine equiangular grid, row weights proportional to the cosine of latitude approximate this influence. Exact cell areas can instead be calculated from the cell boundaries.

A Gaussian grid supplies its own quadrature weights. After rescaling those weights so their sum is one, each is the row's contribution to a global average. Those weights already include the spherical area treatment. Multiplying them by another cosine changes the calculation and generally gives the wrong result.

Quadrature weights should be understood as integration weights, not automatically as the physical areas of arbitrary cells drawn halfway between sampling locations. They are selected together with the Gaussian sampling locations.

Within one latitude row of a full Gaussian grid, all longitude samples have equal influence because they are equally spaced around the same circle. Therefore, average longitude first, then combine latitude rows with their Gaussian weights. A **zonal mean** is this average around a latitude circle; a **profile** stores one value per latitude.

### 6. Separate sampling from representation

Sampling specifies where values are stored. **Representation** specifies how a field is described. One representation lists sampled values. Another describes a field by mixing fixed spatial patterns in measured amounts.

A sound recording offers a concrete comparison. You can list microphone readings over time, or describe the recording by how much of each repeating tone it contains. For a field on a sphere, the corresponding patterns vary over the surface. A **spectral representation** describes a field using the mixing amounts of such wave patterns.

Changing representation does not repair incorrect coordinates. It also cannot recover arbitrary detail that the samples never captured. The useful question is which patterns respect the sphere and can be distinguished by the available samples. Chapter 2 begins with waves around one latitude circle.

\newpage

## Reading the Math

### Distance along coordinate directions

Picture a step east along a latitude circle, followed by a step north along a north-south circle. Use $\Delta$ to mean a finite change, so $\Delta\lambda$ is a longitude change and $\Delta\varphi$ is a latitude change. Call the eastward path length $\Delta x$ and the northward path length $\Delta y$.

For positive steps along these paths:

$$
\Delta x = R\cos\varphi\,\Delta\lambda,
\qquad
\Delta y = R\,\Delta\varphi.
$$

**Symbol-by-Symbol**

| Symbol or notation | Meaning |
|------------------------|--------------------------------------------------------|
| $R$ | Sphere radius, in a chosen length unit such as kilometers. |
| $\varphi$ | Latitude of the eastward path, in radians. |
| $\lambda$ | Longitude, in radians; it appears here inside its change $\Delta\lambda$. |
| $\Delta$ | A finite change in the quantity that follows it. It is not a multiplier. |
| $x$, $y$ inside $\Delta x$, $\Delta y$ | Labels for eastward and northward path distance, respectively. These are not global flat coordinates. |
| $\Delta x$, $\Delta y$ | The two path lengths, in the same length unit as $R$. |
| $\Delta\lambda$, $\Delta\varphi$ | The positive angle steps, in radians. |
| $\cos\varphi$ | The shrinking factor for the latitude circle. |
| $=$ | Both sides describe the same quantity. |
| Adjacent factors and thin spaces | Multiplication. For example, radius times angle gives a distance. |
| Comma and extra spacing | Separate the two statements; neither performs a calculation. |

**Plain-English Translation:** The same longitude step covers less ground near a pole, while a latitude step follows a circle with the sphere's full radius.

These are lengths along the specified coordinate paths. The eastward path is not generally the shortest route between its endpoints. For very small patches, treating the two lengths as the sides of a flat rectangle provides a local approximation to area.

\newpage

### Area of a finite surface patch

Now draw a patch bounded by two latitude circles and two longitude lines. Let its southern boundary be $\varphi_{\mathrm S}$ and its northern boundary be $\varphi_{\mathrm N}$. Let $A$ denote its surface area. The letters $\mathrm S$ and $\mathrm N$ are labels for south and north, not quantities to multiply.

The longitude width $\Delta\lambda$ is positive and measured across the intended patch, continuing across the longitude seam when needed. The exact area on our ideal sphere is:

$$
A = R^2\,\Delta\lambda\,
\bigl(\sin\varphi_{\mathrm N}-\sin\varphi_{\mathrm S}\bigr).
$$

**Symbol-by-Symbol**

| Symbol or notation | Meaning |
|------------------------|--------------------------------------------------------|
| $A$ | Patch area, in square length units. |
| $R$ | Sphere radius, in length units. |
| Superscript $2$ in $R^2$ | Square the radius: multiply it by itself. |
| $\Delta\lambda$ | Positive longitude width in radians; $\Delta$ means finite change and $\lambda$ labels longitude. |
| $\varphi$ | Latitude in radians. |
| Subscripts $\mathrm N$, $\mathrm S$ | Select the northern or southern patch boundary. |
| $\varphi_{\mathrm N}$, $\varphi_{\mathrm S}$ | The latitude values of those boundaries. |
| $\sin$ | Sine: the signed height fraction defined above. |
| $-$ | Subtract the southern height fraction from the northern one. |
| Parentheses | Group the subtraction so it is evaluated as one factor. |
| $=$ | Exact equality under the stated spherical assumption. |
| Adjacent factors and thin spaces | Multiplication of squared radius, angle width, and height-fraction difference. |

**Plain-English Translation:** A patch's area is determined by its longitude width and by how much of the sphere's north-south height its latitude boundaries span.

No calculus is needed to use this formula. Near the equator, a small latitude interval spans a larger change in height fraction than an equally wide angular interval near a pole. That is the area difference the flat image conceals.

\newpage

### A global average on the project's grid

Imagine taking the average around each latitude circle and then giving each circle its prescribed Gaussian influence. This is the computation implemented by the project's area-mean function.

Let $f$ be the scalar field being averaged. Let $H$ count latitude rows and $W$ count longitude columns. Let $j$ select a row and $k$ select a column, both starting at zero as in Python. Write $f_{jk}$ for the stored value at that row and column. Let $w_j$ be the positive Gaussian row weight, rescaled so all row weights sum to one. Finally, use $\langle f\rangle_A$ to name the whole-sphere area average.

$$
\langle f\rangle_A
\approx
\sum_{j=0}^{H-1} w_j
\left[\frac{1}{W}\sum_{k=0}^{W-1} f_{jk}\right].
$$

**Symbol-by-Symbol**

| Symbol or notation | Meaning |
|------------------------|--------------------------------------------------------|
| $f$ | Scalar field, with its physical unit. |
| $\langle f\rangle_A$ | The field's area average over the sphere, with the same unit as $f$. Angle brackets mean averaging; subscript $A$ labels area weighting. |
| $\approx$ | Approximately equals: finite samples need not capture every feature of the continuous field. |
| $H$, $W$ | Total latitude row count and longitude column count. |
| $j$, $k$ | Integer row and column selectors. |
| $\sum$ | Add the following expression for each indicated selector value. |
| $j=0$ below the first sum | Start with row zero; $=$ assigns the starting value here. |
| $H-1$ above the first sum | End with the last row. The minus sign subtracts one because numbering starts at zero. This upper label is not an exponent. |
| $k=0$ and $W-1$ on the second sum | Start with column zero and end with the last column. Again, the upper label is a limit, not a power. |
| $w_j$ | Normalized Gaussian weight for row $j$, with no physical unit. The subscript selects a row. |
| $f_{jk}$ | Field value selected by row $j$ and column $k$. Its subscripts are selectors, not multiplication. |
| $1/W$ | Divide the longitude sum by the number of columns to obtain its arithmetic mean. |
| Square brackets | Group the longitude average before multiplying by the row weight. |
| Adjacent factors | Multiply each row's average by that row's weight. |

**Plain-English Translation:** Average equally spaced samples around each latitude circle, then combine those row averages using the Gaussian weights appropriate to the sphere.

The right-hand side defines the computer's weighted sum exactly, apart from arithmetic rounding. The approximation sign concerns its agreement with the underlying continuous field's true surface average.

All weights are positive and sum to one. Consequently, a constant field retains its value, and the computed mean lies between the smallest and largest sampled values. These are useful checks, although passing them alone does not establish that the coordinates or weights are correct.

\newpage

## Code Connection

### What an array shape tells you

A **tensor** is a numerical array with named or understood axes. Here an **axis** is one direction of indexing, such as latitude or longitude. Shape records the length of each axis; it does not record its physical meaning.

For one scalar snapshot, shape `(H, W)` means latitude first and longitude second. The symbols `H` and `W` have the same meanings as in the averaging equation. A snapshot is the sampled field at one time.

The prepared learning inputs have shape `(B, K*V, H, W)`. Here `B` counts examples processed together, called a batch; `K` counts snapshots in one input window; and `V` counts physical input variables. A window is a consecutive collection of snapshots. The asterisk means multiplication. The `K*V` axis stores a separate **channel**, or stack of spatial values, for every time-variable pair.

The targets have shape `(B, C, H)`, where `C` counts requested output variables. Each target is a profile produced by averaging a variable over a configured time interval and around longitude. A **target** is the reference answer used to fit or assess the model. These targets estimate long-time average behavior rather than the next full global snapshot.

The sample construction is owned by [simulation loading](../../ml/src/ml/data/simulation_data.py); the [preprocessing contract](../../docs/pre-processing.md) describes its axes and averaging intervals. Later chapters explain how examples and targets become a learning task.

\newpage

### Follow a four-row example through real functions

The following field assigns temperature departure ten to the outer two Gaussian rows and zero to the inner two rows. Each row repeats its value at four longitudes. This is a small sampled example, not an observed climate record.

```python
import numpy as np

from ml.diagnostics.grid import GaussianGrid
from ml.diagnostics.spatial import area_mean

latitudes = np.array([-59.444408, -19.875719,
                       19.875719,  59.444408])
longitudes = np.array([0.0, 90.0, 180.0, 270.0])
grid = GaussianGrid(latitudes, longitudes)

field = np.array([
    [10.0, 10.0, 10.0, 10.0],
    [ 0.0,  0.0,  0.0,  0.0],
    [ 0.0,  0.0,  0.0,  0.0],
    [10.0, 10.0, 10.0, 10.0],
])

print(field.mean())
print(area_mean(field, grid.latitudes))
```

Run the example from the repository root using the project's Python environment:

```sh
uv run --project ml --group train python your_example.py
```

`your_example.py` means a file in which you save the example. The import name `np` is a short name for NumPy, the numerical-array library. `np.array` creates arrays from the listed numbers. `GaussianGrid` checks the supplied coordinates and attaches the correct row weights. `field.mean()` averages all 16 entries equally. `area_mean` first averages longitude and then applies Gaussian latitude weights.

The first result is **5.0**. The second is approximately **3.47855** degrees Celsius. Each outer row receives about 0.17393 of the total weight; each inner row receives about 0.32607. The high-valued rows therefore contribute less than their share of array entries.

These weights belong to this four-row Gaussian rule. They are not the approximate cosine weights of the earlier equator-and-60-degrees patch example. The differing answers describe different sampled regions and averaging rules.

\newpage

### Where the geometry lives

The code keeps each responsibility explicit:

| Source | Responsibility relevant to this chapter |
|------------------------|--------------------------------------------------------|
| [Grid definitions](../../ml/src/ml/diagnostics/grid.py) | `GaussianGrid` validates Gaussian latitude coordinates, equally spaced longitudes covering one turn without a duplicate endpoint, and row order. `gaussian_latitude_weights` returns normalized weights in that order. |
| [Spatial calculations](../../ml/src/ml/diagnostics/spatial.py) | `area_mean` applies the weighted average. `zonal_mean` averages the final longitude axis. |
| [Model construction](../../ml/src/ml/training/model.py) | `CoordinateEmbedding` attaches coordinate information to model inputs. `GaussianSphericalConv` selects the Gaussian transform grid and reverses latitude rows around the library call. |
| [Error calculations](../../ml/src/ml/diagnostics/errors.py) | Profile error functions use Gaussian latitude weights so that the error calculation respects represented surface area. |

The transform library expects latitude rows running north to south. The supported Isca inputs run south to north. The adapter reverses them before the transform calculation and reverses the result afterward. A reversed array has the same shape; without consistent coordinate handling, north and south can be exchanged silently. The transform itself is developed in Chapter 4.

An unweighted average is still appropriate when the intended question concerns array entries or equally spaced samples along one latitude circle. For example, the project's training-data rescaling uses an unweighted convention to set numerical scales. That convention is a different operation from estimating a physical surface average; see [the normalization and metric conventions](../../docs/norms.md).

Before interpreting a spatial calculation, identify its coordinates, units, axis order, and weighting rule. Array shape cannot supply any of those on its own.

## Sanity Check

**Question:** A programmer adds a second copy of every sample in the outermost northern Gaussian row and then takes an unweighted average over the enlarged list. No new physical region was sampled. Should the estimated global temperature change? Explain what happened to that row's influence and how an area-aware calculation should treat the copies.

Attempt the question before reading the answer.

**Answer:** The physical area average should not change. The unweighted calculation increases the copied row's influence because it counts entries rather than represented area. If that row differs from the previous unweighted mean, the reported value moves toward the row's value. An area-aware calculation keeps the row's total weight fixed, either by removing the duplicates or splitting its original weight between them. The project's grid format expects a rectangular full grid with unique longitude samples, so the enlarged list should be corrected before calling its grid-based functions.

For later review, cover the answer and explain the failure again without using the formula. Revisit the coordinate and weight definitions if the explanation depends only on counting array slots.
