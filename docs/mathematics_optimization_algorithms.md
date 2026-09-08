# Mathematics, Optimization, and Algorithms

This document records the mathematical formulations, optimization viewpoints,
algorithmic reasoning, and computational decisions used throughout the
Quant AI Market Lab project.

The goal is to connect theoretical ideas with reproducible quantitative
implementation.

---

## 1. Market Data Representation

Let there be \(n\) assets observed over \(T\) trading dates.

The adjusted-price data are represented as a matrix

$$
P =
\begin{pmatrix}
P_{1,1} & P_{2,1} & \cdots & P_{n,1} \\
P_{1,2} & P_{2,2} & \cdots & P_{n,2} \\
\vdots & \vdots & \ddots & \vdots \\
P_{1,T} & P_{2,T} & \cdots & P_{n,T}
\end{pmatrix}
\in \mathbb{R}^{T \times n}.
$$

For the current project,

$$
T = 2932,
\qquad
n = 8.
$$

The eight assets represent multiple market exposures rather than a single
asset class. This allows later analysis of cross-asset dependence,
covariance structure, principal components, market regimes, and portfolio
optimization.

### Data validation

Before statistical modeling, the data pipeline verifies:

1. the downloaded dataset is non-empty,
2. all requested assets are present,
3. the number of observations and assets is recorded,
4. missing observations are checked explicitly.

The current dataset satisfies

$$
N_{\mathrm{missing},i} = 0
\qquad
\text{for every asset } i.
$$

### Algorithmic viewpoint

If \(n\) assets are requested, checking whether every requested asset is
present requires a scan over the asset universe.

At the asset level, this validation is approximately

$$
O(n).
$$

Operations performed over the entire price matrix generally scale with the
number of stored observations,

$$
O(Tn).
$$

### Optimization viewpoint

No optimization problem is solved during the data-ingestion stage.

The purpose of this stage is to construct and validate the numerical input
that will later generate quantities such as the estimated covariance matrix

$$
\hat{\Sigma},
$$

which will subsequently appear in convex portfolio-optimization problems.


---

## 2. Return Transformation

Financial price levels are transformed into returns before statistical
modeling.

For asset \(i\), the one-period simple return is

$$
R_{i,t}
=
\frac{P_{i,t}}{P_{i,t-1}} - 1.
$$

The corresponding logarithmic return is

$$
r_{i,t}
=
\log\left(\frac{P_{i,t}}{P_{i,t-1}}\right)
=
\log P_{i,t} - \log P_{i,t-1}.
$$

Simple and logarithmic returns satisfy the exact identity

$$
r_{i,t} = \log(1 + R_{i,t}).
$$

This identity is used in the implementation as a numerical consistency
check.

### Temporal additivity of log returns

Log returns are additive across consecutive time periods. For example,

$$
\sum_{t=1}^{k} r_{i,t}
=
\log\left(\frac{P_{i,k}}{P_{i,0}}\right).
$$

This property is useful in quantitative time-series analysis.

### Return matrix

For each trading date, the cross-asset log-return vector is

$$
r_t =
\begin{pmatrix}
r_{1,t} \\
r_{2,t} \\
\vdots \\
r_{n,t}
\end{pmatrix}
\in \mathbb{R}^{n}.
$$

The validated price dataset contains 2932 observations for 8 assets.
Because a one-period return requires both a current and previous price,
the resulting return matrices contain

$$
2932 - 1 = 2931
$$

observations.

Therefore,

$$
R_{\mathrm{simple}},
R_{\log}
\in
\mathbb{R}^{2931 \times 8}.
$$

### Numerical validation

The implementation verifies that:

1. the return matrices are non-empty,
2. no missing values remain,
3. all values are finite,
4. simple and logarithmic returns satisfy their mathematical relationship
   within a numerical tolerance.

The consistency condition is

$$
\max_{i,t}
\left|
\log(1 + R_{i,t}) - r_{i,t}
\right|
\leq 10^{-12}.
$$

The observed calculation satisfies this condition.

### Algorithmic viewpoint

Computing returns requires processing each observation for every asset.
For \(T\) dates and \(n\) assets, the computational work is approximately

$$
O(Tn).
$$

### Statistical viewpoint

The return observations will be used to estimate quantities such as the
sample mean vector

$$
\hat{\mu}
=
\frac{1}{T}
\sum_{t=1}^{T} r_t
$$

and sample covariance matrix

$$
\hat{\Sigma}
=
\frac{1}{T-1}
\sum_{t=1}^{T}
(r_t-\hat{\mu})(r_t-\hat{\mu})^\top.
$$

These quantities connect the preprocessing stage to exploratory analysis,
PCA, risk measurement, and portfolio construction.

### Optimization viewpoint

No optimization problem is solved during return computation.

However, the estimated covariance matrix derived from these returns will
later enter portfolio-risk objectives such as

$$
w^\top \hat{\Sigma} w,
$$

where \(w\) denotes the vector of portfolio weights.

## 3. Historical Volatility Estimation

### Problem

For each asset, estimate the historical variability of daily log returns
and express that risk measure on an annualized scale.

Let \(r_{i,t}\) denote the daily log return of asset \(i\) on return
observation \(t\), with \(T_R = 2931\) return observations in the current
dataset.

### Mathematical formulation

The sample mean return of asset \(i\) is

$$
\bar{r}_i
=
\frac{1}{T_R}
\sum_{t=1}^{T_R} r_{i,t}.
$$

The sample daily volatility is the sample standard deviation

$$
s_i
=
\sqrt{
\frac{1}{T_R-1}
\sum_{t=1}^{T_R}
(r_{i,t}-\bar{r}_i)^2
}.
$$

Using the conventional approximation of 252 trading days per year,
daily volatility is annualized as

$$
\hat{\sigma}_{i,\mathrm{annual}}
=
\sqrt{252}\,s_i.
$$

The square-root-of-time scaling follows from variance additivity under
appropriate assumptions. It is an annualization convention and does not
assert that real financial returns are perfectly independent or
identically distributed.

### Algorithmic viewpoint

For \(n\) assets and \(T_R\) return observations, computing the sample
standard deviation for every asset requires processing the return matrix
and has time complexity \(O(T_R n)\).

### Optimization viewpoint

No optimization problem is solved in this stage. The volatility estimates
are descriptive risk statistics. Later portfolio optimization will use the
full covariance structure rather than individual asset volatilities alone.

### Empirical result

For the current sample, the estimated annualized historical volatilities
range from approximately 14.8% for TLT to 40.5% for USO. These values
describe historical return dispersion over the sample period and should
not be interpreted as forecasts of future risk.

## 4. Cross-Asset Correlation Analysis

### Problem

Individual asset volatility describes the variability of each return
series separately, but portfolio risk also depends on how different
assets move together.

For the current universe of \(n=8\) assets, pairwise dependence is
measured using the Pearson correlation coefficient.

### Mathematical formulation

For assets \(i\) and \(j\), the sample correlation is

$$
\rho_{ij}
=
\frac{\operatorname{Cov}(r_i,r_j)}
{s_i s_j},
$$

where \(s_i\) and \(s_j\) are the sample standard deviations of the
corresponding daily log-return series.

The complete correlation matrix is

$$
C = [\rho_{ij}]_{i,j=1}^{n}.
$$

For the current asset universe,

$$
C \in \mathbb{R}^{8 \times 8}.
$$

A valid correlation matrix satisfies

$$
\rho_{ii}=1
$$

for every asset and

$$
\rho_{ij}=\rho_{ji},
$$

so that

$$
C=C^\top.
$$

Each correlation coefficient lies in the interval

$$
-1 \leq \rho_{ij} \leq 1.
$$

### Numerical validation

The computed matrix has shape \(8\times8\).

The maximum observed symmetry error was

$$
\max_{i,j} |\rho_{ij}-\rho_{ji}| = 0,
$$

and the maximum diagonal error was also zero.

The observed correlation values ranged from approximately \(-0.203\)
to \(1.000\), including the unit diagonal.

### Algorithmic viewpoint

Computing all pairwise correlations requires estimating relationships
between approximately \(n^2\) pairs of assets across \(T_R\) return
observations.

The resulting time complexity is approximately

$$
O(T_R n^2).
$$

The correlation matrix itself requires

$$
O(n^2)
$$

storage.

### Financial interpretation

The strongest observed correlation between two distinct assets is
approximately \(0.932\) between SPY and QQQ, indicating strong historical
linear co-movement in their daily returns.

TLT exhibits mildly negative correlations with several equity exposures,
while GLD has relatively low correlations with many of the equity ETFs.

These relationships illustrate the statistical basis of diversification:
portfolio risk depends not only on individual asset volatility but also
on cross-asset dependence.

Correlation does not imply causation, and historical correlations are not
guaranteed to remain stable across future market regimes.

### Optimization viewpoint

The correlation analysis is descriptive and does not itself solve an
optimization problem.

However, correlations are closely related to the covariance matrix.
If \(D\) is the diagonal matrix of asset standard deviations, then

$$
\Sigma = D C D.
$$

Portfolio variance can subsequently be written as

$$
\sigma_p^2
=
w^\top \Sigma w,
$$

where \(w\) is the portfolio-weight vector.

Thus, cross-asset dependence provides a direct mathematical bridge from
exploratory analysis to portfolio optimization.
