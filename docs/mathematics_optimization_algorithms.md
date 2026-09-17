# Mathematics, Optimization, and Algorithms

This document records the mathematical formulations, optimization viewpoints,
algorithmic reasoning, and computational decisions used throughout the
Quant AI Market Lab project.

The goal is to connect theoretical ideas with reproducible quantitative
implementation.

---

## 1. Market Data Representation

Let there be $n$ assets observed over $T_P$ trading dates, where $T_P$
denotes the number of price observations.
The adjusted-price data are represented as a matrix

$$
P =
\begin{pmatrix}
P_{1,1} & P_{2,1} & \cdots & P_{n,1} \\
P_{1,2} & P_{2,2} & \cdots & P_{n,2} \\
\vdots & \vdots & \ddots & \vdots \\
P_{1,T_P} & P_{2,T_P} & \cdots & P_{n,T_P}
\end{pmatrix}
\in \mathbb{R}^{T_P \times n}.
$$

For the current project,

$$
T_P = 2932,
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

If $n$ assets are requested, checking whether every requested asset is
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

For asset $i$, the one-period simple return is

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

The validated price dataset contains $T_P=2932$ price observations for
$n=8$ assets. Because a one-period return requires both a current and previous price, define the number of return observations as

$$
T_R = T_P - 1 = 2931.
$$


Therefore,

$$
R_{\mathrm{simple}},
R_{\log}
\in
\mathbb{R}^{T_R \times n}
=
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


For $T_P$ price observations and $n$ assets, the computational work is approximately

$$
O(T_P n).
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

where $w$ denotes the vector of portfolio weights.

## 3. Historical Volatility Estimation

### Problem

For each asset, estimate the historical variability of daily log returns
and express that risk measure on an annualized scale.

Let $r_{i,t}$ denote the daily log return of asset $i$ on return
observation $t$, with $T_R = 2931$ return observations in the current
dataset.

### Mathematical formulation

The sample mean return of asset $i$ is

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

For $n$ assets and $T_R$ return observations, computing the sample
standard deviation for every asset requires processing the return matrix
and has time complexity $O(T_R n)$.

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

For the current universe of $n=8$ assets, pairwise dependence is
measured using the Pearson correlation coefficient.

### Mathematical formulation

For assets $i$ and $j$, the sample correlation is

$$
\rho_{ij}
=
\frac{\operatorname{Cov}(r_i,r_j)}
{s_i s_j},
$$

where $s_i$ and $s_j$ are the sample standard deviations of the
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

The computed matrix has shape $8\times8$.

The maximum observed symmetry error was

$$
\max_{i,j} |\rho_{ij}-\rho_{ji}| = 0,
$$

and the maximum diagonal error was also zero.

The observed correlation values ranged from approximately $-0.203$
to $1.000$, including the unit diagonal.

### Algorithmic viewpoint

Computing all pairwise correlations requires estimating relationships
between approximately $n^2$ pairs of assets across $T_R$ return
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
approximately $0.932$ between SPY and QQQ, indicating strong historical
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
If $D$ is the diagonal matrix of asset standard deviations, then

$$
\Sigma = D C D.
$$

Portfolio variance can subsequently be written as

$$
\sigma_p^2
=
w^\top \Sigma w,
$$

where $w$ is the portfolio-weight vector.

Thus, cross-asset dependence provides a direct mathematical bridge from
exploratory analysis to portfolio optimization.
---

## 5. Covariance Matrix and Positive Semidefiniteness

### Problem

Correlation measures standardized dependence, but portfolio risk depends on both
cross-asset dependence and the individual scales of asset returns. Therefore,
the covariance matrix is required for later portfolio optimization.

### Mathematical Formulation

Let $X \in \mathbb{R}^{T_R \times n}$ denote the log-return matrix, where
$T_R$ is the number of return observations and $n$ is the number of assets.

After centering each asset return series, let $X_c$ denote the centered
return matrix. The sample covariance matrix is

$$
\hat{\Sigma}
=
\frac{1}{T_R-1}X_c^\top X_c.
$$

The covariance matrix is symmetric:

$$
\hat{\Sigma}=\hat{\Sigma}^\top.
$$

For every vector $x \in \mathbb{R}^n$,

$$
x^\top \hat{\Sigma}x
=
\frac{1}{T_R-1}\|X_cx\|_2^2
\geq 0.
$$

Therefore, $\hat{\Sigma}$ is positive semidefinite.

For the current dataset, the minimum eigenvalue was numerically

$$
\lambda_{\min}(\hat{\Sigma})
\approx 5.019\times10^{-6}>0,
$$

so the estimated covariance matrix is positive definite for this sample.

If $D$ is the diagonal matrix of sample standard deviations and $C$ is the
sample correlation matrix, then

$$
\hat{\Sigma}=DCD.
$$

The numerical reconstruction error in this identity was approximately

$$
5.421\times10^{-19},
$$

which is consistent with floating-point numerical precision.

### Optimization Viewpoint

For a portfolio-weight vector $w$, portfolio variance is

$$
w^\top\hat{\Sigma}w.
$$

Because $\hat{\Sigma}$ is positive semidefinite, this is a convex quadratic
function of $w$. This covariance structure will therefore become the risk
term in the later portfolio-optimization stage.

### Algorithmic Complexity

For $T_R$ return observations and $n$ assets, constructing the covariance
matrix requires approximately $O(T_R n^2)$ arithmetic operations and
$O(n^2)$ storage.
---

## 6. Principal Component Analysis of Standardized Returns

### Problem

The eight asset-return series are correlated, so their movements contain
redundant information. Principal Component Analysis (PCA) constructs
orthogonal directions that summarize the dominant linear variation in the
cross-asset return system.

Because the assets have substantially different volatility scales, PCA is
performed on standardized log returns rather than directly on the raw
covariance matrix. This prevents a high-volatility asset from dominating a
principal component solely because of its scale.

### Standardization

For asset $i$ at time $t$, define

$$
z_{t,i}
=
\frac{r_{t,i}-\bar{r}_i}{s_i},
$$

where $\bar{r}_i$ is the sample mean and $s_i$ is the sample standard
deviation of asset $i$.

The resulting standardized-return matrix $Z$ has approximately zero column
means and unit sample standard deviations.

Therefore,

$$
\operatorname{Cov}(Z)
=
\operatorname{Corr}(R),
$$

up to floating-point numerical precision.

In the implementation, the maximum absolute difference between these two
matrices was

$$
3.775\times10^{-15}.
$$

Thus, the PCA performed here can equivalently be interpreted as PCA on the
sample correlation matrix.

### Optimization Formulation

Let $C$ denote the covariance matrix of the standardized returns, which is
equivalently the sample correlation matrix of the original returns.

The first principal component direction solves

$$
\max_{v\in\mathbb{R}^n}
\quad
v^\top C v
$$

subject to

$$
v^\top v=1.
$$

This asks for the unit-length direction having maximum sample variance.

The Lagrangian is

$$
\mathcal{L}(v,\lambda)
=
v^\top C v
-
\lambda(v^\top v-1).
$$

Differentiating with respect to $v$ gives the first-order condition

$$
2Cv-2\lambda v=0,
$$

and therefore

$$
Cv=\lambda v.
$$

Hence, the principal-component directions are eigenvectors of $C$, and the
corresponding eigenvalues measure the variance captured along those
directions.

The first principal component corresponds to the largest eigenvalue.
Subsequent components solve the same variance-maximization problem subject
also to orthogonality with the previously selected component directions.

### Explained Variance

If

$$
\lambda_1\geq\lambda_2\geq\cdots\geq\lambda_n,
$$

then the explained-variance ratio of component $k$ is

$$
\mathrm{EVR}_k
=
\frac{\lambda_k}
{\sum_{j=1}^{n}\lambda_j}.
$$

For the current eight-asset dataset:

- PC1 explains approximately $50.53\%$ of standardized variance.
- PC1--PC2 cumulatively explain approximately $66.93\%$.
- PC1--PC3 cumulatively explain approximately $79.01\%$.

Thus, three orthogonal directions summarize approximately $79\%$ of the
sample's standardized cross-asset variation.

### Component-Weight Interpretation

The first component has relatively large same-sign coefficients for SPY,
QQQ, IWM, EEM, and VNQ. It therefore represents a broad equity/risk
co-movement direction in this sample.

The second component has its largest absolute coefficients in TLT and GLD,
while the equity coefficients are comparatively small. It captures a
different cross-asset direction dominated by bond and gold behavior.

The third component is dominated by USO and, to a lesser extent, GLD,
indicating a commodity-related direction in the sample.

These interpretations are statistical rather than causal. PCA identifies
directions of linear variation; it does not establish economic causation.

The overall sign of an eigenvector is arbitrary: if $v$ is an eigenvector,
then $-v$ represents the same principal-component direction. Therefore,
interpretation focuses on relative signs and coefficient magnitudes rather
than the absolute orientation of an eigenvector.

### Numerical Validation

The implementation validates that:

- the eigenvectors are orthonormal;
- the sum of the eigenvalues equals the trace of the PCA matrix;
- the explained-variance ratios sum to one.

Observed numerical errors were approximately

$$
\max |V^\top V-I|
=
6.661\times10^{-16},
$$

and

$$
\left|
\sum_i\lambda_i-\operatorname{tr}(C)
\right|
=
8.882\times10^{-16}.
$$

These values are consistent with floating-point numerical precision.

### Algorithm

The PCA implementation:

1. standardizes each asset's log-return series;
2. constructs the covariance matrix of the standardized returns;
3. computes the symmetric eigendecomposition using `numpy.linalg.eigh`;
4. sorts eigenvalues and eigenvectors in descending eigenvalue order;
5. computes explained-variance ratios;
6. validates orthogonality and trace preservation;
7. extracts the first three component directions for interpretation and
   visualization.

### Computational Complexity

Constructing the standardized covariance matrix requires approximately

$$
O(T_R n^2)
$$

operations.

The eigendecomposition of the resulting symmetric $n\times n$ matrix
requires approximately

$$
O(n^3)
$$

operations, with $O(n^2)$ matrix storage.

For this project, $n=8$, so the eigendecomposition is computationally small.
The same formulation, however, makes the scaling behavior explicit for larger
asset universes.



### Scalability and Computational Perspective

For the current universe of only $n=8$ assets, the direct covariance and
eigendecomposition approach is entirely appropriate. Introducing a more
complicated algorithm here would add unnecessary implementation complexity
without a meaningful computational benefit.

The complexity analysis becomes important when considering a substantially
larger asset universe. Covariance construction scales approximately as

$$
O(T_R n^2),
$$

while a full dense eigendecomposition scales approximately as

$$
O(n^3).
$$

Thus, increasing the number of assets can make both computation and
$O(n^2)$ matrix storage significantly more expensive.

If only the leading $k$ principal components are required, with
$k \ll n$, computing the complete eigendecomposition may perform more work
than necessary. For sufficiently large problems, iterative or truncated
methods can target only the dominant components rather than computing every
eigenpair.

This illustrates an algorithmic principle used throughout the project:
the mathematically correct formulation is considered together with its
computational cost, and more scalable alternatives are considered when the
problem size makes them necessary. Optimization of computation should be
motivated by an actual bottleneck rather than added solely for complexity.


### Predictive-Modeling Caveat

The current PCA is descriptive and uses the full historical sample. If PCA is
later used as part of a predictive model or backtest, the standardization
parameters and PCA directions must be estimated using only information
available at that historical time. Fitting them on future observations would
introduce look-ahead bias.

## 7. Market-Regime Feature Construction and Geometric Interpretation

### Research Question

Before choosing a clustering algorithm, I first need to define what I mean by
the "market condition" observed on a particular trading day.

The question is:

> Do the statistical characteristics of the eight ETF market exposures exhibit
> distinguishable states over time?

I do not begin by assuming that a particular clustering method will discover
genuine economic regimes. The first step is instead to construct a small set of
interpretable variables that describe different aspects of market behavior.

For each trading day $t$, I represent the market condition by the feature
vector

$$
x_t =
\begin{pmatrix}
r_{\mathrm{SPY},t} \\
\sigma_{\mathrm{SPY},t}^{(20)} \\
d_t
\end{pmatrix}.
$$

The three coordinates describe:

1. the daily SPY log return, representing broad-equity market movement;

2. the trailing 20-day volatility of SPY, representing the recent magnitude of
   market fluctuations;

3. the cross-asset dispersion of the eight ETF returns on that day, representing
   how differently the assets are moving from one another.


### Geometric Interpretation

The feature construction gives a geometric way to think about the problem.

Each trading day is represented by one point in a three-dimensional feature
space. The three coordinate axes correspond to return, recent volatility, and
cross-asset dispersion.

Therefore, instead of initially asking an algorithm to assign a regime label, I
can first inspect the geometry of the resulting point cloud.

If market conditions naturally form well-separated groups, the point cloud
should contain corresponding geometric structure. If the observations instead
form one continuous cloud with tails or outliers, a clustering algorithm may
still divide the observations, but those divisions should not automatically be
interpreted as genuine persistent market regimes.

This distinction is important because clustering algorithms can produce a
partition even when the underlying data do not contain naturally separated
groups.

### Construction of the Three Features

#### 1. Daily Broad-Market Return

The first coordinate is the SPY daily log return,

$$
r_{\mathrm{SPY},t}
=
\log\left(
\frac{P_{\mathrm{SPY},t}}
{P_{\mathrm{SPY},t-1}}
\right).
$$

SPY is used here as a simple and interpretable proxy for broad U.S. equity
market movement. A positive value represents an upward daily movement and a
negative value represents a downward daily movement.

This is not the only possible choice. Alternatives include an equal-weighted
return across the eight ETFs or a PCA-based common-market factor. I use SPY for
the initial baseline because its interpretation is direct and it does not
require estimating an additional model.

If a PCA score is later used as a predictive feature, the PCA transformation
must be fitted using historical data only. Using the previously computed
full-sample PCA directions would introduce future information into the
historical experiment.


#### 2. Trailing 20-Day Volatility

The second coordinate measures the recent variability of SPY returns.

For a window of $w=20$ trading days,

$$
\sigma_{\mathrm{SPY},t}^{(20)}
=
\sqrt{
\frac{1}{w-1}
\sum_{j=0}^{w-1}
\left(
r_{\mathrm{SPY},t-j}
-
\bar r_t^{(20)}
\right)^2
},
$$

where

$$
\bar r_t^{(20)}
=
\frac{1}{w}
\sum_{j=0}^{w-1}
r_{\mathrm{SPY},t-j}.
$$

The window is backward-looking: the feature at time $t$ uses observations
from $t-19$ through $t$, and therefore does not use future returns.

The first 19 observations cannot have a complete 20-day window. They are
therefore unavailable by construction rather than being treated as data
errors.

The 20-day window is a simple baseline corresponding approximately to one
trading month. It is not assumed to be an optimal volatility estimator.
Possible alternatives include other rolling-window lengths, exponentially
weighted volatility, or conditional-volatility models such as GARCH. Such
alternatives should be compared only when there is a clear modeling reason
rather than chosen because they produce visually cleaner regimes.


#### 3. Daily Cross-Asset Dispersion

The third coordinate measures how differently the eight ETF returns behave on
the same trading day.

For $n=8$ assets, first define the cross-sectional mean return

$$
\bar r_t
=
\frac{1}{n}
\sum_{i=1}^{n} r_{i,t}.
$$

The daily cross-asset dispersion is then

$$
d_t
=
\sqrt{
\frac{1}{n-1}
\sum_{i=1}^{n}
\left(
r_{i,t}-\bar r_t
\right)^2
}.
$$

Geometrically, consider the eight-dimensional return vector

$$
r_t =
(r_{1,t},\ldots,r_{n,t})^\top.
$$

The vector

$$
\bar r_t \mathbf{1}
$$

represents the point on the common-movement line where all assets have the
same return.

More precisely, define the one-dimensional common-movement subspace

$$
L=\{c\mathbf{1}:c\in\mathbb{R}\}.
$$

The vector

$$
\bar r_t\mathbf{1}
$$

is the orthogonal projection of $r_t$ onto $L$.

From the definition of $d_t$,

$$
\left\|
r_t-\bar r_t\mathbf{1}
\right\|_2^2
=
(n-1)d_t^2.
$$

Therefore,

$$
d_t
=
\frac{1}{\sqrt{n-1}}
\left\|
r_t-\bar r_t\mathbf{1}
\right\|_2.
$$

For the current universe of $n=8$ ETFs,

$$
\left\|
r_t-\bar r_t\mathbf{1}
\right\|_2
=
\sqrt{7}\,d_t.
$$

Thus, daily cross-asset dispersion has an exact geometric interpretation as a
scaled Euclidean distance from the common-movement subspace.

This is different from correlation. Dispersion is a cross-sectional quantity
computed for one trading day, whereas correlation measures statistical
co-movement between return series over multiple observations.


### Causality and Timing of the Features

All three baseline features are constructed using information available no
later than trading day $t$. No observation from $t+1$ or later is required.

The interpretation nevertheless depends on when the model is intended to be
used. Because the day-$t$ return and dispersion are known only after the
relevant day-$t$ prices are observed, these features describe the market
condition at or after that observation time. They can subsequently be used as
inputs for a next-period forecasting experiment, provided the temporal
ordering is preserved.

## 8. Feature Standardization Before KMeans

### Why Standardization Is Necessary

KMeans is based on Euclidean distances between observations and cluster
centroids. Therefore, the numerical scale of each coordinate directly affects
the geometry seen by the algorithm.

For two feature vectors $x$ and $y$,

$$
\|x-y\|_2^2
=
\sum_{j=1}^{d}(x_j-y_j)^2.
$$

A feature with a substantially larger numerical scale can contribute more to
this distance simply because of its units. This would implicitly give that
coordinate greater influence on the clustering.

To place the three regime features on comparable scales, each feature is
standardized using

$$
z_{t,j}
=
\frac{x_{t,j}-\mu_j}{s_j},
$$

where $\mu_j$ is the historical mean of feature $j$, and $s_j$ is its
historical standard deviation.

After standardization, each coordinate is centered near zero and has unit
variance on the data used to fit the transformation.


### Geometric Interpretation

Standardization changes the coordinate system in which distances are measured.

Subtracting the mean translates the point cloud so that its center is near the
origin. Dividing each coordinate by its standard deviation rescales the axes so
that one unit along each standardized axis represents approximately one
standard deviation of movement in that feature.

This is a diagonal affine transformation of the original feature space. It does
not make the features statistically independent and it does not remove their
correlations.

For example, the historical 20-day SPY volatility and cross-asset dispersion
have a positive sample correlation of approximately $0.529$. Standardizing
the two variables changes their units but does not remove this relationship.


### Historical-Only Fitting

The scaling parameters must respect the temporal structure of the experiment.

The mean and standard deviation used by the scaler are estimated from the
historical feature sample only. When later observations are evaluated, they
must be transformed using these frozen historical parameters rather than
refitting the scaler on the later period.

In symbolic form, if

$$
\mu_j^{\mathrm{hist}}
\quad\text{and}\quad
s_j^{\mathrm{hist}}
$$

are estimated from the historical period, then a later observation is
transformed as

$$
z_{t,j}^{\mathrm{later}}
=
\frac{
x_{t,j}^{\mathrm{later}}-\mu_j^{\mathrm{hist}}
}{
s_j^{\mathrm{hist}}
}.
$$

Using information from the later evaluation period to determine the scaling
parameters would leak future information into the model-development process.


### Numerical Validation

For the historical regime-feature matrix, the standardized feature means were
numerically close to zero,

$$
(-1.22\times10^{-17},
 -1.11\times10^{-16},
 -2.84\times10^{-16}),
$$

and the population standard deviations were

$$
(1,1,1).
$$

The very small deviations of the means from exactly zero are expected
floating-point effects rather than modeling errors.

The implementation also explicitly rejects non-finite feature values before
fitting the scaler and checks that the transformed values remain finite.

## 9. KMeans as a Geometric Baseline

### Objective

After standardization, each trading day is represented by a point

$$
z_t \in \mathbb{R}^3.
$$

For a chosen number of clusters $K$, KMeans seeks cluster assignments
$C_1,\ldots,C_K$ and centroids $\mu_1,\ldots,\mu_K$ that minimize the
within-cluster sum of squared Euclidean distances:

$$
\min_{C_1,\ldots,C_K,\mu_1,\ldots,\mu_K}
\sum_{k=1}^{K}
\sum_{z_t\in C_k}
\|z_t-\mu_k\|_2^2.
$$

In scikit-learn this objective value is reported as `inertia_`.

The objective gives KMeans a direct geometric interpretation: observations
assigned to the same cluster should lie relatively close to a common centroid.


### Assignment Step and Voronoi Geometry

For fixed centroids, each observation is assigned to its nearest centroid:

$$
c(t)
=
\arg\min_{k\in\{1,\ldots,K\}}
\|z_t-\mu_k\|_2^2.
$$

Geometrically, the centroids divide feature space into Voronoi cells. Each
Voronoi cell contains the points that are closer to one centroid than to any
other centroid.

For two centroids, the boundary between their cells is a hyperplane consisting
of points that are equally distant from the two centroids.

Therefore, KMeans produces a piecewise-linear geometric partition of the
standardized feature space.


### Why the Centroid Is the Mean

Suppose the observations assigned to one cluster are

$$
z_1,\ldots,z_m.
$$

For fixed cluster membership, KMeans chooses the centroid $\mu$ by minimizing

$$
f(\mu)
=
\sum_{i=1}^{m}\|z_i-\mu\|_2^2.
$$

Differentiating with respect to $\mu$,

$$
\nabla_\mu f(\mu)
=
2m\mu
-
2\sum_{i=1}^{m}z_i.
$$

Setting the gradient equal to zero gives

$$
\mu
=
\frac{1}{m}
\sum_{i=1}^{m}z_i.
$$

The Hessian is

$$
\nabla_\mu^2 f(\mu)=2mI,
$$

which is positive definite for a nonempty cluster. Therefore, the arithmetic
mean is the unique minimizer of the squared-distance objective for that fixed
cluster.

This explains mathematically why the KMeans centroid-update step uses the
within-cluster mean.


### Alternating Algorithm

KMeans alternates between two operations:

1. Assignment: assign every observation to its nearest current centroid.

2. Update: replace each centroid by the arithmetic mean of the observations
   currently assigned to that cluster.

Each step does not increase the KMeans objective. Because there are finitely
many possible cluster assignments, the procedure eventually reaches a stable
partition under the usual finite-data setting.

This does not imply that KMeans finds the globally optimal partition. The final
solution can depend on the initial centroids because the optimization problem
is non-convex.


### Initialization

The implementation uses `k-means++` initialization rather than selecting all
initial centroids uniformly at random.

The purpose of `k-means++` is to spread the initial centroids through the data
more carefully, reducing the chance of starting with several centroids in the
same dense region.

The implementation also uses

`n_init = 20`

so that multiple initializations are tried and the solution with the smallest
KMeans objective is retained.

A fixed `random_state` is used for reproducibility. Reproducibility does not
remove initialization sensitivity, so the final partition is also compared
across several different random seeds.


### Computational Complexity

Let

- $N$ be the number of observations,
- $K$ the number of clusters,
- $d$ the feature dimension,
- $I$ the number of KMeans iterations.

A standard assignment step computes distances from approximately every
observation to every centroid, requiring roughly

$$
O(NKd)
$$

operations per iteration.

Over $I$ iterations, one run therefore has approximate complexity

$$
O(NKdI).
$$

If several initializations are performed, this cost is multiplied by the
number of initializations.

In the current experiment,

$$
N=2828,\qquad d=3,
$$

and only small candidate values of $K$ are considered. The computational
cost is therefore small. The complexity becomes more relevant for much larger
datasets, higher-dimensional feature spaces, or large numbers of repeated
initializations.


### What KMeans Does Not Model

KMeans uses the geometry of the feature vectors but does not use the
chronological ordering of the observations.

For example, it treats two feature vectors with identical coordinates in the
same way whether they occurred on consecutive trading days or several years
apart.

Therefore, KMeans can identify geometrically similar market conditions, but it
does not directly model:

- state persistence through time;
- transition probabilities between states;
- probabilistic uncertainty about state membership;
- different covariance shapes for different states.

For this reason, the KMeans result is treated as a baseline partition rather
than immediate evidence of genuine persistent market regimes.

## 10. KMeans Model Diagnostics and Empirical Findings

### Why Inertia Alone Cannot Select the Number of Clusters

The KMeans objective, or inertia, is

$$
J_K
=
\sum_{k=1}^{K}
\sum_{z_t\in C_k}
\|z_t-\mu_k\|_2^2.
$$

As the number of clusters increases, inertia cannot increase, because a model
with more centroids has at least as much flexibility as a model with fewer
centroids.

Therefore, choosing the value of $K$ with the smallest inertia would
automatically favor larger values of $K$. Inertia must instead be interpreted
together with other diagnostics and the structure of the resulting clusters.


### Silhouette Score

For an observation $i$, let

$$
a(i)
$$

be its average distance to observations in its own cluster, and let

$$
b(i)
$$

be the smallest average distance from $i$ to observations in another
cluster.

The silhouette value is

$$
s(i)
=
\frac{b(i)-a(i)}
{\max\{a(i),b(i)\}}.
$$

Its value lies between $-1$ and $1$.

Values closer to $1$ indicate that an observation is relatively well
separated from neighboring clusters. Values near zero indicate overlap near a
cluster boundary, while negative values can indicate that an observation may
be closer, on average, to another cluster.

The overall silhouette score is the average of $s(i)$ across observations.

A high silhouette score is evidence of geometric separation under the chosen
distance and feature representation. It is not proof that the clusters are
economically meaningful market regimes.


### Candidate Values of K

I evaluated

$$
K=2,\ldots,8
$$

on the standardized historical feature matrix.

The observed diagnostics were:

| K | Inertia | Silhouette | Cluster sizes |
|---:|---:|---:|---|
| 2 | 6293.477 | 0.5624 | 309, 2519 |
| 3 | 4943.018 | 0.4116 | 2208, 33, 587 |
| 4 | 3888.653 | 0.3968 | 509, 1846, 441, 32 |
| 5 | 3433.518 | 0.3938 | 1831, 435, 21, 530, 11 |
| 6 | 3064.706 | 0.3166 | 465, 1548, 159, 625, 10, 21 |
| 7 | 2757.822 | 0.3027 | 171, 1398, 289, 557, 21, 382, 10 |
| 8 | 2526.448 | 0.2921 | 510, 154, 1227, 20, 248, 10, 542, 117 |

Among these candidate values, $K=2$ produced the largest silhouette score.

For larger values of $K$, several very small clusters appeared. Together
with the previously inspected feature-space geometry, this suggests that some
additional centroids may be isolating relatively unusual tail observations
rather than revealing a large number of clearly separated, persistent market
states.

For this reason, $K=2$ is retained as a baseline partition for further
diagnostics. This is not a claim that the market has exactly two true regimes.


### Interpretation of the Two Centroids

After transforming the standardized centroids back into the original feature
units, the two cluster centers were approximately:

| Feature | Cluster 0 | Cluster 1 |
|---|---:|---:|
| SPY daily log return | -0.009342 | 0.001725 |
| SPY 20-day daily volatility | 0.018999 | 0.008184 |
| Cross-asset dispersion | 0.022333 | 0.008783 |

Cluster 0 therefore contains, on average, observations with more negative SPY
returns, higher recent volatility, and higher cross-asset dispersion.

Cluster 1 contains observations with, on average, mildly positive SPY returns,
lower volatility, and lower dispersion.

These descriptions are empirical characteristics of the clusters. The
numerical labels 0 and 1 have no intrinsic economic meaning, and I do not
hard-code semantic regime names into the algorithm.


### Initialization Stability and Adjusted Rand Index

Because KMeans is sensitive to initialization, I repeated the $K=2$
experiment across several random seeds.

To compare two partitions while ignoring arbitrary permutations of the cluster
labels, I use the Adjusted Rand Index (ARI).

ARI compares whether pairs of observations are grouped together or separately
in two different partitions and adjusts the comparison for agreement expected
by chance.

A value of

$$
\mathrm{ARI}=1
$$

means that the two partitions are identical up to a permutation of cluster
labels.

Across the tested seeds, almost all solutions had ARI equal to $1$ relative
to the reference solution. One seed produced

$$
\mathrm{ARI}\approx0.993261,
$$

with only a very small difference in the partition.

Therefore, the observed $K=2$ partition is highly stable with respect to the
tested KMeans initializations.

This stability addresses one computational concern, but it does not establish
that the clusters correspond to true economic regimes.


### Temporal Diagnostics

Although KMeans does not use time ordering during fitting, I examine the
resulting labels afterward to determine whether the geometric clusters also
show temporal persistence.

For consecutive observations, define the empirical transition count

$$
N_{ij}
=
\#\{t:c_t=i,\;c_{t+1}=j\}.
$$

The corresponding empirical transition probability is

$$
\widehat P_{ij}
=
\frac{N_{ij}}
{\sum_j N_{ij}}.
$$

For the $K=2$ baseline, the transition matrix was approximately

$$
\widehat P
=
\begin{pmatrix}
0.436893 & 0.563107 \\
0.069102 & 0.930898
\end{pmatrix}.
$$

The complete historical feature sequence contained 348 cluster switches, giving
a switch rate of approximately

$$
12.31\%.
$$

The run-length diagnostics were:

| Cluster | Number of runs | Mean run length | Median | Maximum |
|---|---:|---:|---:|---:|
| 0 | 174 | 1.776 | 1 | 44 |
| 1 | 175 | 14.394 | 3 | 295 |

Cluster 1 is relatively persistent, with an estimated self-transition
probability of approximately $0.931$.

Cluster 0 is substantially less persistent. Its median run length is only one
trading day, even though a few longer episodes occur.


### What the Baseline Result Supports

The KMeans experiment supports the conclusion that the selected feature space
contains a reproducible geometric separation between a large lower-volatility,
lower-dispersion group and a smaller group associated with more negative
returns, higher volatility, and higher dispersion.

However, the temporal diagnostics show that the smaller group is frequently
short-lived.

Therefore, I interpret KMeans as identifying different geometric market
conditions rather than claiming that it has established two persistent latent
economic regimes.


### Limitations and Reasonable Alternatives

KMeans has several limitations for this problem.

It uses squared Euclidean distance, so extreme observations can exert a strong
influence on centroids. The feature-space plots contain tails and unusual
stress observations, so this sensitivity is relevant.

KMeans also favors centroid-based geometric partitions and does not explicitly
represent clusters with different covariance structures.

Most importantly, it ignores temporal dependence while fitting the clusters.

Reasonable alternatives include:

- a Gaussian Mixture Model, which can represent probabilistic membership and
  different ellipsoidal covariance structures;

- a Hidden Markov Model, which can explicitly represent latent states and
  transition probabilities through time;

- alternative feature representations or scaling methods when justified by the
  statistical properties of the data.

These alternatives should not be adopted simply because they are more
sophisticated. They should be compared against the KMeans baseline using
consistent historical information and clearly defined diagnostics.



### 3-D Geometry and the KMeans Decision Boundary

The regime feature vector has three coordinates,

$$
x_t =
\begin{pmatrix}
r_{\mathrm{SPY},t} \\
\sigma_{\mathrm{SPY},t}^{(20)} \\
d_t
\end{pmatrix}.
$$

Therefore, each trading date can be viewed geometrically as one point in a
three-dimensional feature space.

The three coordinates have different numerical scales. KMeans is therefore
not fitted directly to the original financial coordinates. Each feature is
standardized using historical-sample statistics,

$$
z_{t,j}
=
\frac{x_{t,j}-\mu_j}{s_j},
$$

where $\mu_j$ and $s_j$ are respectively the fitted mean and scale of feature
$j$.

Standardization changes the coordinate system but not the identity of an
observation. The original-coordinate and standardized-coordinate panels in
the 3-D comparison figure therefore show the same trading dates and the same
final cluster assignments.

This distinction matters because KMeans minimizes squared Euclidean distances
in the standardized feature space. Consequently, the standardized panel
shows the geometry that is directly relevant to the clustering objective.

For the $K=2$ baseline, let the standardized centroids be $c_0$ and $c_1$.
A point $z$ lies on the KMeans decision boundary when it is equally distant
from the two centroids,

$$
\|z-c_0\|_2^2
=
\|z-c_1\|_2^2.
$$

Expanding both sides gives

$$
z^\top z
-2c_0^\top z
+\|c_0\|_2^2
=
z^\top z
-2c_1^\top z
+\|c_1\|_2^2.
$$

The common $z^\top z$ terms cancel, leaving

$$
2(c_1-c_0)^\top z
=
\|c_1\|_2^2-\|c_0\|_2^2.
$$

This is the equation of a plane in three dimensions. Geometrically, it is
the perpendicular-bisector plane separating the two KMeans Voronoi regions.

The 3-D comparison figure displays this plane only in standardized
coordinates because that is the space in which the KMeans distance
calculation is performed.

For readability, the plotted axes use the 1st-99th percentile range of each
feature. This is only a visualization choice. KMeans is fitted using all
2,828 historical feature observations, including observations outside the
displayed axis limits. In the current figure, 138 observations fall outside
at least one displayed axis limit; they are not removed from model fitting.

The centroid coordinates are also written directly on the figure. This makes
it possible to compare both their financial interpretation in the original
coordinates and their geometric position in standardized coordinates.

### Motivation for the Next Experiment

The KMeans result creates a specific next research question:

> If temporal state transitions are modeled explicitly, do the inferred market
> states become more coherent and persistent without sacrificing interpretability?

This provides a methodological reason to investigate a Hidden Markov Model
rather than adding it only as a more advanced algorithm.

The later May-August period remains outside this model-development comparison.
Feature choices, scaling rules, and model decisions should be developed using
the historical period before the later temporal evaluation is used.
