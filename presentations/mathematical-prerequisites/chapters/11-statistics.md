# Probability, averages, and climatological estimates {#ch-statistics}

What does an average estimated from a simulation mean? Spatial integration, time averaging, and ensemble expectation are distinct operations. We introduce their probability assumptions, derive the effect of serial dependence on an estimated mean, and identify what a quadratic prediction objective can recover.

## Random variables, expectation, and covariance

Probability distinguishes an ensemble average from one observed realization. Covariance measures the dependence that determines uncertainty in averages. Sources: [@ArfkenWeber2005, Sections 19.1-19.2, 19.5-19.6].

::: {.tb-definition #obj-11-1}
**Definition 11.1 - Probability space and a random variable**

A probability space consists of possible outcomes, a collection of events, and a probability measure $P$ assigning nonnegative probabilities, total probability one, and countably additive probabilities for disjoint events (the probability of a countable disjoint union is the sum of the probabilities). A real random variable $X$ is a measurable function of an outcome. A realization is one observed value. If $X$ has density $p_X(x)$, probabilities and expectations satisfy

$$
P(X\in A)=\int_Ap_X(x)dx,\quad \int_{\mathbb R}p_Xdx=1,
\qquad \mathbb E[g(X)]=\int_{\mathbb R}g(x)p_X(x)dx.
\tag{11.1}
$$
:::

::: {.tb-definition #obj-11-2}
**Definition 11.2 - Mean, variance, covariance, and correlation**

For a discrete variable, replace the integral by a sum over values weighted by their probabilities. Expectations require the stated moment to exist. Define mean $m_X=\mathbb E X$, variance $\sigma_X^2=\mathbb E[(X-m_X)^2]$, and covariance $\operatorname{Cov}(X,Y)=\mathbb E[(X-m_X)(Y-m_Y)]$. Variance has squared units; standard deviation $\sigma_X$ has the variable's units. For nonzero standard deviations, correlation is $\operatorname{Corr}(X,Y)=\operatorname{Cov}(X,Y)/(\sigma_X\sigma_Y)$ and lies in $[-1,1]$ by Cauchy-Schwarz.
:::

::: {.tb-definition #obj-11-3}
**Definition 11.3 - Independence**

Independence means the joint probabilities factor for all events concerning the two variables. It implies zero covariance when second moments exist, but the reverse is false.
:::

::: {.tb-counterexample #obj-11-4}
**Counterexample 11.4 - Uncorrelated variables can be dependent**

For a variable $X$ uniform on $[-1,1]$, let $Y=X^2$. Symmetry gives $\operatorname{Cov}(X,Y)=\mathbb E X^3-\mathbb E X\mathbb E X^2=0$, yet $Y$ is determined by $X$.
:::

::: {.tb-definition #obj-11-5}
**Definition 11.5 - Gaussian distribution and its extra assumption**

A Gaussian (normal) variable has density $p_X(x)=(2\pi\sigma_X^2)^{-1/2}\exp[-(x-m_X)^2/(2\sigma_X^2)]$ when $\sigma_X>0$. Normality is an additional distributional assumption, not a consequence of having a mean and variance.
:::

::: {.tb-result #obj-11-6}
**Result 11.6 - Independent means and the central limit theorem (quoted)**

For independent identically distributed samples with variance $0<\sigma_X^2<\infty$, the sample mean has variance $\sigma_X^2/N$. The central limit theorem gives an asymptotically Gaussian standardized mean under these assumptions; correlated time samples need additional hypotheses. [@ArfkenWeber2005, Sections 19.5-19.6].
:::

::: {.tb-exercise #ex-11-1}
**Exercise 11.1 - Scale a random variable**

*Application.* If $Y=3X+2$ with finite second moments, express its mean and variance in terms of those of $X$.
:::

## Spatial, temporal, and ensemble means

The integration measure and sampling mechanism define an average. Spatial, temporal, and ensemble means answer different questions. Sources: [@ArfkenWeber2005, Sections 19.2, 19.6]; fluid averaging and correlation: [@Vallis2006, Sections 8.1, 10.2].

::: {.tb-definition #obj-11-7}
**Definition 11.7 - Ensemble, time, and area means**

For a field $q(\mathbf x,t,\omega)$, $\omega$ labels a random outcome, not wave frequency in this chapter. An ensemble mean is $\mathbb E[q(\mathbf x,t,\omega)]$ at fixed position and time. A time mean of one realization over duration $T$ is $\overline q_T(\mathbf x)=T^{-1}\int_0^Tq(\mathbf x,t,\omega)dt$. A global spatial mean is $\langle q\rangle_A$ from Chapter 10. None equals the others by definition.
:::

::: {.tb-definition #obj-11-8}
**Definition 11.8 - Stationarity and observable ergodicity**

A time series is weakly stationary if its mean is time-independent, its variance is finite and constant, and its covariance depends only on lag. Strict stationarity means all finite joint distributions are invariant under a common time shift. Ergodicity, for an observable, means its long-time average equals the corresponding ensemble expectation almost surely (with probability one), under an invariant distribution. Stationarity alone does not guarantee this property.
:::

::: {.tb-counterexample #obj-11-9}
**Counterexample 11.9 - A stationary trajectory with a random time mean**

For example, $X(t)=B$ with one random constant $B$ for an entire trajectory is stationary, but its time mean is the realized $B$, not generally $\mathbb EB$.
:::

::: {.tb-remark #obj-11-10}
**Remark 11.10 - Finite-time climate estimates and spin-up**

A finite-time climatological estimate can retain initial-state transients, sampling variability, and slow fluctuations. Excluding an initial adjustment interval (spin-up) is a modeling decision whose adequacy requires diagnostics; it is not a theorem that any fixed exclusion time yields equilibrium. Independent simulations and adjacent windows of one simulation are not interchangeable sampling units.
:::

::: {.tb-exercise #ex-11-2}
**Exercise 11.2 - Name the missing averaging assumption**

*Reasoning.* A time series has constant ensemble mean and covariance depending only on lag. Does that prove its long-time mean equals the ensemble mean? Explain with the random-constant example.
:::

## Autocorrelation and uncertainty of a mean

Positive serial correlation reduces the information in a fixed number of time samples. The variance of a mean follows from all pairwise covariances. Sources: [@ArfkenWeber2005, Section 19.6]; time-correlation interpretation: [@Vallis2006, Section 10.2].

::: {.tb-assumption #obj-11-11}
**Assumption 11.11 - Equally spaced stationary samples**

Let $X_1,\ldots,X_N$ be equally spaced weakly stationary samples with variance $\sigma^2>0$. Define autocorrelation at integer lag $k$ by $\rho_k=\operatorname{Cov}(X_j,X_{j+k})/\sigma^2$, independent of $j$.
:::

::: {.tb-result #obj-11-12}
**Result 11.12 - Variance of a correlated sample mean**

For $\overline X=N^{-1}\sum_{j=1}^NX_j$ under the preceding assumptions,

$$
\begin{aligned}
\operatorname{Var}(\overline X)
&=\frac1{N^2}\sum_{i,j}\operatorname{Cov}(X_i,X_j)\\
&=\frac{\sigma^2}{N}\left[1+2\sum_{k=1}^{N-1}\left(1-\frac{k}{N}\right)\rho_k\right].
\end{aligned}
\tag{11.2}
$$
:::

::: {.tb-proof}
**Proof of Result 11.12**

Expand the centered sum before taking expectation to obtain the double covariance sum. There are $N$ diagonal terms and $N-k$ pairs at each positive lag $k$, with the same number at negative lag. Substituting $\operatorname{Cov}(X_j,X_{j+k})=\sigma^2\rho_k$ gives (11.2). $\square$
:::

::: {.tb-definition #obj-11-13}
**Definition 11.13 - Variance-equivalent effective sample count**

There are $N-k$ pairs at each positive lag and the same number at negative lag, explaining the factor two. Define $N_{\rm eff}=N/[1+2\sum_{k=1}^{N-1}(1-k/N)\rho_k]$ when the denominator is positive; then $\operatorname{Var}(\overline X)=\sigma^2/N_{\rm eff}$. This is a variance-equivalent sample count, not literally a count of independent observations. Negative correlation can make it exceed $N$.
:::

::: {.tb-example #obj-11-14}
**Example 11.14 - Geometric serial correlation**

For $\rho_k=r^k$, $|r|<1$, and $N$ long relative to the correlation decay, the bracket approaches $(1+r)/(1-r)$. With $r=0.8$, $N_{\rm eff}\approx N/9$. If correlations are estimated from a short series, the estimated effective count is itself uncertain. A decorrelation formula does not establish stationarity or supply independent replicas.
:::

::: {.tb-exercise #ex-11-3}
**Exercise 11.3 - Use negative correlation**

*Interpretation.* For a long series with $\rho_k=r^k$ and $r=-1/2$, what is the approximate ratio $N_{\rm eff}/N$? Does this denote a literal count of independent observations?
:::

## Squared-error prediction and normalization

The conditional mean minimizes expected squared error. This identifies the target of a quadratic loss but does not establish optimality for a relative-error loss. Sources: [@ArfkenWeber2005, Sections 19.2, 19.6]; projection argument follows Chapter 4.

::: {.tb-definition #obj-11-15}
**Definition 11.15 - Conditional mean and conditional variance**

For predictor information $X$ and square-integrable scalar target $Y$, the conditional expectation $m(X)=\mathbb E[Y\mid X]$ is the mean given that information; it is characterized by $\mathbb E[(Y-m(X))h(X)]=0$ for suitable functions $h$. For a square-integrable predictor $a(X)$, the conditional variance is $\operatorname{Var}(Y\mid X)=\mathbb E[(Y-m(X))^2\mid X]$.
:::

::: {.tb-result #obj-11-16}
**Result 11.16 - The conditional mean minimizes quadratic risk**

Let $Y$ and the predictor $a(X)$ have finite second moments. For $m(X)=\mathbb E[Y\mid X]$,

$$
\mathbb E[(Y-a(X))^2\mid X]
=\operatorname{Var}(Y\mid X)+[m(X)-a(X)]^2.
\tag{11.3}
$$

Consequently $a(X)=m(X)$ minimizes expected squared error.
:::

::: {.tb-proof}
**Proof of Result 11.16**

Expand $Y-a=(Y-m)+(m-a)$; the cross term vanishes conditionally. This proves the optimum. It extends to a fixed weighted quadratic norm on finite-dimensional profiles by summing the component identities. It does not automatically extend to $\mathbb E[\|Y-a\|/\|Y\|]$, whose weighting and unsquared norm differ. Also, variability between targets with the same external configuration need not be irreducible when the predictor sees extra state information. $\square$
:::

::: {.tb-definition #obj-11-17}
**Definition 11.17 - Affine normalization for learning**

For a scalar training variable $x$, a mean $m$, standard deviation $s$, and small positive $\epsilon$ in the same units as $x$, affine normalization is $z=(x-m)/(s+\epsilon)$, with inverse $x=(s+\epsilon)z+m$. Fit these scales on training data only to avoid using held-out information. Equal sample weights for a numerical scaling convention need not coincide with physical area weights for a climatological mean. One changes coordinates for learning; the other defines an observable.
:::

::: {.tb-exercise #ex-11-4}
**Exercise 11.4 - Invert a normalization**

*Application.* If $z=(x-m)/(s+\epsilon)$, derive the inverse and state what dimensions $\epsilon$ must have.
:::

## Chapter summary

Probability assigns weights to outcomes; expectation, variance, and covariance depend on that distribution. Zero covariance does not imply independence. Ensemble, time, zonal, and area averages are different operators. Stationarity is time-shift invariance of specified statistics; ergodicity is an additional long-time averaging property. Equation (11.2) gives exact sample-mean variance from autocorrelations. The conditional mean minimizes quadratic risk by (11.3). Normalization and physical averaging need separate definitions.

::: {.tb-exercise #ex-11-5}
**Exercise 11.5 - Connect the chapter results**

*Synthesis.* Can ten overlapping windows from one run be assumed independent? For $r=0.8$, how many variance-equivalent samples do $900$ long-series samples supply approximately? Why does predicting the conditional mean not remove conditional variance?
:::
