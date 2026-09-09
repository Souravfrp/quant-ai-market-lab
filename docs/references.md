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


## Attribution Principle

External ideas, datasets, software, documentation, and adapted
implementations are acknowledged where appropriate. Mathematical
derivations, modeling choices, experiments, validation, interpretation,
and project-specific implementation are documented separately as part of
the project's own quantitative research workflow.
