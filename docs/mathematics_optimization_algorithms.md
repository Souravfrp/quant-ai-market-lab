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

