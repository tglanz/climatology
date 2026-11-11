# Gaussian and equiangular grids

A geographic grid specifies where a field is sampled on the sphere. In a
latitude-longitude array, each row corresponds to a latitude and each column
to a longitude. Array shape alone does not identify those coordinates.

The grid matters when transforming fields into spherical harmonics, computing
global averages, weighting errors, and plotting results.

## Latitude placement

An **equiangular grid** uses a constant latitude spacing in degrees. Endpoint
placement is a separate choice: a grid can include the poles or use points
between them. The pinned harmonic library's `equiangular` transform includes
both poles.

A **Gaussian grid** chooses latitudes for Gauss-Legendre quadrature, a numerical
integration rule. Let $H$ be the total number of latitude rows, $\phi_j$ a
latitude, and $P_H$ the Legendre polynomial of degree $H$. Its nodes satisfy

$$
P_H(\mu_j) = 0, \qquad \mu_j = \sin\phi_j.
$$

These latitudes are nearly, but not exactly, equally spaced. They are symmetric
about the equator and exclude the poles. With even $H$, they also exclude the
equator. ECMWF denotes the number of latitudes per hemisphere by $N$, so
$H = 2N$. See
[ECMWF's Gaussian grids reference](https://confluence.ecmwf.int/pages/viewpage.action?pageId=50039496)
and its [current version](https://confluence.ecmwf.int/spaces/FCST/pages/49415103/Gaussian%2Bgrids).

For four latitude rows:

| Grid | Latitudes in degrees, south to north |
|---|---|
| Gaussian | Approximately -59.4, -19.9, 19.9, 59.4 |
| Equiangular including poles | -90, -30, 30, 90 |

Gaussian latitude placement does not specify the longitude layout. A **full
Gaussian grid** uses the same number of equally spaced longitudes on every row.
A **reduced Gaussian grid** uses fewer longitude points near the poles, reducing
the crowding caused by shrinking latitude circles. Both use Gaussian latitudes.
[ECMWF](https://confluence.ecmwf.int/spaces/FCST/pages/49415103/Gaussian%2Bgrids)
describes these layouts.

## Integration weights

Grid points come with an integration rule. Let $R$ be the sphere's radius and
$\lambda$ longitude. With angles in radians, the area element is

$$
dA = R^2 \cos\phi\,d\phi\,d\lambda
   = R^2\,d\mu\,d\lambda.
$$

For equally spaced latitudes, cosine weights approximate the area represented
by each row. Gaussian quadrature instead supplies weights $q_j$ for integration
in $\mu = \sin\phi$. For a zonal-mean profile $f(\phi)$, its global area mean is
approximated by

$$
\langle f\rangle \approx
\frac{\sum_{j=1}^{H} q_j f(\phi_j)}{\sum_{j=1}^{H} q_j}.
$$

The Gaussian weights already account for the change of variable. Multiplying
them by another cosine factor changes the integration rule. The same weights
can define area-weighted profile errors; see [norms](norms.md).

Isca computes Gaussian nodes and weights in
[`compute_gaussian`](../submodules/isca/src/atmos_spectral/tools/gauss_and_legendre.F90)
and uses those weights to construct latitude cell boundaries in
[`transforms.F90`](../submodules/isca/src/atmos_spectral/tools/transforms.F90).

## Current project behavior

Isca output uses a full Gaussian grid. A checked T85 output file has shape
$128 \times 256$ in latitude and longitude. Its latitudes run from approximately
-88.93 to 88.93 degrees, south to north, and match the 128-node Gauss-Legendre
latitudes.

The [model builder](../ml/src/ml/training/model.py) uses the actual coordinates
for positional features. Every SFNO spherical convolution uses Gaussian
transforms. The installed transform expects north-to-south rows; the adapter
reverses the supported south-to-north Isca inputs around each convolution.
Output profiles retain the input latitude order.

[Spatial diagnostics](../ml/src/ml/diagnostics/spatial.py), convergence, spectra,
and profile errors use the same Gaussian quadrature owner.
Prepared data and checkpoints save coordinates and input units.
Evaluation checks this identity and uses those coordinates in metrics and plots.
Unsupported grids and inconsistent units fail explicitly.

Spectral truncation specifies which harmonic modes are retained. It is distinct
from the geographic grid on which fields are sampled; see
[spectral truncation](spectral-truncation.md).
