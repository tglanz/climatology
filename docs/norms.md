# Norms

## Latitude-weighted relative L2 (relL2)

Primary metric throughout evaluation. For a predicted profile $\hat{y}$ and truth $y$, both of shape $(H,)$:

$$\text{relL2}(\hat{y}, y) = \sqrt{\frac{\sum_h w_h (\hat{y}_h - y_h)^2}{\sum_h w_h y_h^2}}$$

where $w_h = \cos(\phi_h)$ and $\phi_h$ is the latitude of grid row $h$. The cosine weighting corrects for the over-representation of polar grid cells in a regular lat-lon grid. A value of 1.0 is equivalent to the zero predictor; 0.0 is a perfect prediction.

## Latitude-weighted RMSE

Used where an absolute error in physical units (m/s) is more interpretable than a relative quantity:

$$\text{RMSE}(\hat{y}, y) = \sqrt{\frac{\sum_h w_h (\hat{y}_h - y_h)^2}{\sum_h w_h}}$$

Same weights as relL2. The denominator is the sum of weights rather than the weighted signal energy, so the result is in m/s rather than dimensionless. Prefer relL2 when comparing across forcing configurations with different jet magnitudes.

## Normalized parameter distance

Used for the nearest-training-config baseline. For a configuration with parameter vector $p$ and a training configuration $p'$, both normalized by the observed range of each parameter across all available configurations:

$$d(p, p') = \left\| \frac{p - p'}{\text{range}} \right\|_2$$

Normalization ensures parameters with different physical scales contribute equally.

---

## Appendix: cosine latitude weights

We use the area weight of $w_h = \cos(\phi_h)$ for a row $h$ in lat-lon grids.

### Area element on the sphere

On a sphere of radius $R$, the infinitesimal area element in spherical coordinates is

$$dA = R^2 \cos\phi \, d\phi \, d\lambda$$

where $\phi \in [-\pi/2, \pi/2]$ is latitude and $\lambda \in [0, 2\pi)$ is longitude. The $\cos\phi$ factor is the distance from the rotation axis: near the equator a longitude step $d\lambda$ spans a large arc; near the poles the same $d\lambda$ spans almost nothing.

### Discrete grid

A regular lat-lon grid partitions the sphere into cells with uniform spacing $\Delta\phi$ in latitude and $\Delta\lambda$ in longitude. The area of the cell at latitude $\phi_h$ is

$$A_h = R^2 \cos(\phi_h) \, \Delta\phi \, \Delta\lambda$$

Since $R$, $\Delta\phi$, $\Delta\lambda$ are the same for every cell, the area is proportional to $\cos(\phi_h)$ alone:

$$A_h \propto \cos(\phi_h)$$

### Area-weighted global mean

The true global mean of a field $f$ is

$$\langle f \rangle = \frac{\iint f \, dA}{\iint dA}$$

For a zonal-mean profile $y_h$ (already averaged over longitude), the longitude integral just contributes a factor of $2\pi$ and cancels between numerator and denominator. The discrete approximation is

$$\langle y \rangle = \frac{\sum_h y_h A_h}{\sum_h A_h} = \frac{\sum_h y_h \cos(\phi_h)}{\sum_h \cos(\phi_h)}$$

This is exactly $\sum_h w_h y_h / \sum_h w_h$ with $w_h = \cos(\phi_h)$.

### Consequence for error metrics

Replacing the flat sum with the area-weighted sum in relL2 and RMSE ensures that errors at high latitudes, which affect a small fraction of the atmosphere, are penalized proportionally to the area they represent rather than to the number of grid rows they happen to occupy.
