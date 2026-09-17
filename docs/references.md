# References and Data Sources

This document records external data sources, software libraries, papers,
documentation, and methodological references used in Quant AI Market Lab.

References are added as they are actually used in the project.

## Market Data

### Yahoo Finance / yfinance

Historical market data used in the project are retrieved programmatically
through the open-source `yfinance` Python package.

- yfinance documentation:
  https://ranaroussi.github.io/yfinance/

- yfinance source repository:
  https://github.com/ranaroussi/yfinance

The project uses `yfinance.download()` to retrieve historical market data
for the selected cross-asset universe.

`yfinance` is not affiliated with or endorsed by Yahoo. Usage of downloaded
market data is subject to the applicable provider terms. The data in this
repository are used for research, educational, and portfolio-demonstration
purposes.

## Software

The project uses open-source Python libraries including NumPy, pandas,
SciPy, scikit-learn, statsmodels, XGBoost, SHAP, CVXPY, hmmlearn,
matplotlib, and Streamlit.

Specific methodological references will be added in later sections when
the corresponding techniques are introduced.


## Principal Component Analysis

### Methodological Reference

The PCA formulation, including variance-maximizing orthogonal directions,
eigendecomposition, and explained variance, is supported by:

- Jolliffe, I. T., and Cadima, J. (2016).
  "Principal component analysis: a review and recent developments."
  *Philosophical Transactions of the Royal Society A*,
  374(2065), 20150202.
  DOI: 10.1098/rsta.2015.0202

### Numerical Implementation

The PCA implementation uses symmetric eigendecomposition through
`numpy.linalg.eigh`. This routine is appropriate for real symmetric matrices
such as covariance and correlation matrices.

- NumPy documentation: `numpy.linalg.eigh`
  https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigh.html


## Market-Regime Baseline: Standardization and KMeans

### Feature Standardization

The regime-feature matrix is standardized before Euclidean-distance-based
KMeans clustering so that differences in numerical scale do not cause one
feature to dominate the distance calculation.

The implementation uses `sklearn.preprocessing.StandardScaler`.

- scikit-learn documentation: `StandardScaler`
  https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html

### KMeans Clustering

KMeans is used as a geometric baseline for partitioning the standardized
market-condition feature space. The project does not assume that the
resulting clusters are automatically genuine or persistent market regimes.

The implementation uses `sklearn.cluster.KMeans` with `k-means++`
initialization, multiple initializations, and a fixed random state for
reproducibility.

- scikit-learn documentation: `KMeans`
  https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html

The initialization strategy is based on:

- Arthur, D., and Vassilvitskii, S. (2007).
  "k-means++: The Advantages of Careful Seeding."
  Proceedings of the Eighteenth Annual ACM-SIAM Symposium on Discrete
  Algorithms (SODA), pp. 1027-1035.

### Cluster Diagnostics

Candidate cluster counts are compared using the silhouette score.
Initialization stability of the selected baseline partition is checked
using the Adjusted Rand Index (ARI).

- scikit-learn documentation: `silhouette_score`
  https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html

- scikit-learn documentation: `adjusted_rand_score`
  https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html


## Attribution Principle

External ideas, datasets, software, documentation, and adapted
implementations are acknowledged where appropriate. Mathematical
derivations, modeling choices, experiments, validation, interpretation,
and project-specific implementation are documented separately as part of
the project's own quantitative research workflow.
