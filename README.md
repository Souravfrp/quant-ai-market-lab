# Quant AI Market Lab

An ongoing quantitative research project exploring cross-asset market data through statistical analysis, numerical linear algebra, predictive risk modeling, convex portfolio optimization, and reproducible computational methods.

> **Project Status:** Active development. Completed research includes market-data validation, return analysis, covariance estimation, PCA, market-regime analysis, SPY risk forecasting, chronological walk-forward evaluation, portfolio optimization, historical backtesting, benchmark comparisons, transaction-cost analysis, and subperiod robustness testing.

## Motivation

This project develops an end-to-end quantitative research workflow from historical market data to mathematically formulated and computationally validated analysis.

The project develops cross-asset return and risk analysis, market-regime models, predictive risk forecasts, and historical minimum-variance portfolio experiments. Mathematical formulations, algorithmic considerations, numerical validation, and limitations are documented alongside the implementation.

## Asset Universe

The analysis currently uses eight exchange-traded funds (ETFs) representing different market exposures:

- SPY — U.S. large-cap equities
- QQQ — Nasdaq-100 equities
- IWM — U.S. small-cap equities
- TLT — long-term U.S. Treasury bonds
- GLD — gold
- USO — oil-futures exposure
- EEM — emerging-market equities
- VNQ — U.S. real estate

The data-ingestion configuration requests observations from `2015-01-01` through `2026-09-01`. The validated dataset currently contains observed trading dates from `2015-01-02` through `2026-08-31`.

## Completed Work

### 1. Market Data Pipeline

- Historical adjusted-price data acquisition
- Cross-asset dataset validation
- Missing-value and finite-value checks
- Local raw-data storage separated from version-controlled source code

### 2. Return Transformation

Both simple and logarithmic returns are computed and numerically validated.

For prices $P_t$,

$$
R_t = \frac{P_t}{P_{t-1}} - 1,
$$

and

$$
r_t = \log\left(\frac{P_t}{P_{t-1}}\right).
$$

The implementation verifies the relationship

$$
r_t = \log(1+R_t)
$$

within numerical tolerance.

### 3. Exploratory Cross-Asset Analysis

Implemented analyses include:

- normalized historical asset performance
- annualized historical volatility
- cross-asset return correlations
- numerical validation of correlation-matrix properties

![Normalized Asset Performance](results/normalized_asset_performance.png)

![Annualized Volatility](results/annualized_volatility.png)

![Cross-Asset Correlation Matrix](results/correlation_matrix.png)

### 4. Covariance Analysis

The sample covariance matrix of log returns is constructed and numerically checked for symmetry and positive semidefinite structure.

For a portfolio-weight vector $w$, portfolio return variance is represented by

$$
\mathrm{Var}(r_p)=w^\top\Sigma w.
$$

This covariance structure supports the minimum-variance portfolio optimization implemented in the project.

### 5. Principal Component Analysis

PCA is applied to standardized cross-asset log returns to study dominant directions of historical co-movement.

In the current sample:

- PC1 explains approximately **50.53%** of standardized return variation.
- The first two components explain approximately **66.93%**.
- The first three components explain approximately **79.01%**.

The implementation validates eigenvector orthogonality, eigenvalue/trace consistency, and the explained-variance ratio.

![PCA Explained Variance](results/pca_explained_variance.png)

![PCA Component Weights](results/pca_loadings.png)

The first component is interpreted cautiously as a broad equity/risk co-movement direction in this historical sample rather than as a causal economic factor.


## Market-Regime Analysis

### Temporal Research Split

For later predictive experiments, the return observations are divided chronologically at `2026-04-30`.

The historical period contains **2,847 return observations**, while the later May-August 2026 period contains **84 observations**.

Because the later period has already been inspected during project development, it is treated as a **fixed-cutoff temporal or pseudo-out-of-sample evaluation period**, rather than being described as a completely untouched holdout.

### Regime Features

The baseline market-condition vector is

$$
x_t =
\begin{pmatrix}
r_{\mathrm{SPY},t} \\
\sigma_{\mathrm{SPY},t}^{(20)} \\
d_t
\end{pmatrix},
$$

where the three coordinates are:

- SPY daily log return
- backward-looking 20-trading-day SPY volatility
- daily cross-asset return dispersion across the eight ETFs

Before clustering, the geometry of this three-dimensional feature space was inspected through pairwise projections.

![Return vs Volatility](results/regime_return_vs_volatility.png)

![Return vs Cross-Asset Dispersion](results/regime_return_vs_dispersion.png)

![Volatility vs Cross-Asset Dispersion](results/regime_volatility_vs_dispersion.png)

The observations form a dense central region with asymmetric tails rather than obviously separated compact groups. Therefore, clustering is treated as a baseline statistical partition rather than evidence that naturally separated economic regimes necessarily exist.

### KMeans Baseline

Because the three features have different numerical scales, they are standardized before KMeans is fitted.

For $K$ clusters, KMeans minimizes

$$
\sum_{k=1}^{K}
\sum_{z_t \in C_k}
\|z_t-\mu_k\|_2^2.
$$

Candidate values from $K=2$ through $K=8$ were compared using inertia, silhouette score, cluster sizes, and initialization stability.

Among these candidates, $K=2$ produced the largest silhouette score. The resulting baseline contains:

- **Cluster 0:** 309 observations (approximately **10.93%**)
- **Cluster 1:** 2,519 observations (approximately **89.07%**)

The smaller cluster has, on average, more negative SPY returns, higher recent SPY volatility, and higher cross-asset dispersion. These are described as **stress-like statistical characteristics**, not as proof of a causal economic regime.

![KMeans Return vs Volatility](results/kmeans_return_vs_volatility.png)

![KMeans Return vs Dispersion](results/kmeans_return_vs_dispersion.png)

![KMeans Volatility vs Dispersion](results/kmeans_volatility_vs_dispersion.png)

The plot colors identify Cluster 0 and Cluster 1, while the `X` markers identify the KMeans centroids.

### 3-D Geometric Comparison

The same KMeans assignments can also be viewed simultaneously in the original financial coordinates and in the standardized coordinates used during model fitting.

![KMeans Original vs Standardized 3D Geometry](results/kmeans_3d_comparison.png)

The left panel preserves the original financial units. The right panel shows the standardized feature space in which KMeans computes Euclidean distances and includes the equal-distance decision plane between the two centroids. Axis limits use the 1st-99th percentile range for visualization only; all 2,828 historical observations remain part of model fitting.

### Temporal Diagnostics

KMeans uses feature-space geometry but does not use chronological dependence while fitting. The cluster assignments were therefore examined afterward through time.

![KMeans Cluster Timeline](results/kmeans_cluster_timeline.png)

The larger cluster is substantially more persistent, while the smaller cluster often occurs in shorter bursts.

This is an important limitation rather than something to hide: it motivates comparison with a temporal latent-state model such as a Hidden Markov Model (HMM).

The current KMeans result is therefore treated as a **reproducible geometric baseline**, not as evidence that the market has exactly two genuine persistent regimes.

### Hidden Markov Model Temporal Analysis

The same three standardized market-condition features were then modeled
with Gaussian Hidden Markov Models (HMMs), which explicitly represent
latent state persistence and transition probabilities through time.

A two-state full-covariance HMM was first used as a simple temporal
baseline. Its decoded historical states contained **1,853** and **975**
observations, with expected durations of approximately **61.1** and
**32.1 trading observations**.

The two-state HMM changed decoded state **54 times** over the historical
sequence, compared with **348 KMeans cluster switches**. This is not
treated as evidence that the HMM is automatically superior because
temporal persistence is built directly into the HMM transition structure.

For more detailed interpretation, a **three-state full-covariance
Gaussian HMM** was retained as the primary specification. Its decoded
historical state proportions are approximately:

- **48.69%** — lower-volatility / lower-dispersion conditions
- **38.72%** — intermediate-volatility / intermediate-dispersion conditions
- **12.59%** — higher-volatility / higher-dispersion, stress-like conditions

The corresponding expected durations are approximately **45.6**,
**24.7**, and **13.5 trading observations**.

Candidate HMMs with two through six states and both diagonal and full
covariance structures were compared using multiple initializations,
likelihood, AIC/BIC, chronological validation, rolling-origin validation,
Viterbi occupancy, and posterior state probabilities.

Higher-state models continued to improve likelihood but increasingly
introduced small or period-specific latent components. The three-state
full-covariance model is therefore retained as a **parsimonious and
interpretable specification**, not as evidence that financial markets
contain exactly three true regimes.

The later May-August 2026 period was used for fixed-cutoff temporal
evaluation of the retained HMM. Because this period has already been
examined during project development, its results are treated as
retrospective pseudo-out-of-sample evidence rather than as an
untouched holdout.


## Mathematical and Algorithmic Documentation

The repository includes a dedicated technical document covering:

- data and return representations
- statistical estimators
- volatility and dependence measures
- covariance-matrix properties
- PCA formulation and eigendecomposition
- numerical validation
- computational complexity
- scalability considerations
- predictive-modeling and look-ahead-bias caveats

See:

`docs/mathematics_optimization_algorithms.md`

For example, covariance construction for $T_R$ return observations and $n$ assets scales approximately as

$$
O(T_R n^2),
$$

while a full dense eigendecomposition scales approximately as

$$
O(n^3).
$$

For the current eight-asset universe these computations are small, but the documentation discusses why algorithmic choices become more important as the asset universe grows.

## Repository Structure

```text
quant-ai-market-lab/
├── data/
│   ├── raw/        # local, ignored by Git
│   └── processed/  # local, ignored by Git
├── docs/
│   ├── hmm_fixed_cutoff_evaluation.md
│   ├── mathematics_optimization_algorithms.md
│   ├── portfolio_mathematics_and_validation.md
│   ├── portfolio_robustness_findings.md
│   ├── references.md
│   ├── ridge_alpha_validation.md
│   ├── ridge_risk_forecasting.md
│   ├── risk_forecasting_baselines.md
│   └── walk_forward_window_selection.md
├── models/         # local model artifacts
├── notebooks/
├── results/
├── src/
│   ├── adaptive_window_selection.py
│   ├── april_2020_ridge_diagnostic.py
│   ├── compute_returns.py
│   ├── download_data.py
│   ├── exploratory_analysis.py
│   ├── later_forecast_plot.py
│   ├── later_walk_forward_comparison.py
│   ├── later_walk_forward_evaluation.py
│   ├── pca_analysis.py
│   ├── portfolio_backtest.py
│   ├── portfolio_benchmarks.py
│   ├── portfolio_optimization.py
│   ├── portfolio_risk_visualization.py
│   ├── portfolio_robustness.py
│   ├── portfolio_visualization.py
│   ├── regime_clustering.py
│   ├── regime_features.py
│   ├── regime_hmm.py
│   ├── regime_hmm_evaluation.py
│   ├── ridge_alpha_validation.py
│   ├── ridge_risk_forecasting.py
│   ├── risk_forecast_comparison.py
│   ├── risk_forecasting.py
│   ├── risk_full_history_plot.py
│   ├── temporal_split.py
│   ├── walk_forward_comparison.py
│   ├── walk_forward_dates.py
│   ├── walk_forward_evaluation.py
│   └── walk_forward_ridge.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Reproducibility

Development environment:

- Python 3.12
- Conda environment: `quant-ai`

The current Python dependency snapshot is stored in:

`requirements.txt`

Raw and processed market datasets are intentionally excluded from Git version control. The data-ingestion scripts provide the computational route for reconstructing the analysis dataset from the documented data source.

## Completed Research and Remaining Development

The completed research includes market-data validation, return and
covariance analysis, PCA, market-regime modeling, SPY risk forecasting,
chronological walk-forward evaluation, minimum-variance portfolio
optimization, historical backtesting, benchmark comparisons,
transaction-cost analysis, and subperiod robustness testing.

The portfolio methodology, execution assumptions, validation checks,
historical results, and limitations are documented in:

`docs/portfolio_mathematics_and_validation.md`

The subperiod findings are documented in:

`docs/portfolio_robustness_findings.md`

The remaining development tasks are:

1. add model explainability where appropriate
2. investigate additional predictive-model alternatives, with
   chronological validation
3. add local generative-AI-assisted quantitative reporting
4. develop an interactive Streamlit research dashboard
5. complete the documentation, reproducibility, and validation audit

These remaining components will be described as completed only after
their implementations and validations have been added to the repository.

## Research and Validation Principles

The project emphasizes:

- mathematical formulation before implementation
- numerical validation of computed quantities
- explicit distinction between descriptive and predictive analysis
- prevention of look-ahead leakage in future predictive experiments
- computational-complexity and scalability analysis where relevant
- reproducible source code and version history
- transparent documentation of data sources, external methods, and limitations

## References and Attribution

Data sources, mathematical references, software documentation, and external methods used during development are recorded in:

`docs/references.md`

## Current Scope and Limitations

The project includes descriptive market analysis, historical risk-forecasting experiments, and retrospective portfolio backtests. These results depend on the selected data, models, evaluation periods, and execution assumptions. They do not establish future predictive performance or a profitable live trading strategy and should not be interpreted as investment advice.

PCA currently uses the full historical sample and is therefore treated as descriptive analysis. Any future predictive or backtesting use of dimensionality reduction will require fitting transformations using only information available at the relevant historical time.
