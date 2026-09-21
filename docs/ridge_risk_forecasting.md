# Five-day SPY risk forecasting: provisional Ridge model

## Research question

Does combining current market features improve forecasts
of SPY's future five-trading-day daily-return RMS compared
with our constant and rolling-RMS baselines?

The target and chronological dates are defined in
`docs/risk_forecasting_baselines.md`.

## Why Ridge regression?

Ridge provides an interpretable multivariable benchmark.
Its L2 penalty can reduce coefficient sensitivity when
features are correlated. Its fitting objective is a
convex quadratic optimization problem.

This is an initial trained model, not a claim that a
linear model is the correct description of market risk.

## Inputs and fitting

Features: current SPY log return, SPY 20-day rolling
sample volatility, and cross-asset return dispersion.

The feature scaler and Ridge coefficients are fitted
on the 2,253 internal training examples only.

The regularization setting `alpha=1.0` is provisional;
it has not been selected through hyperparameter tuning.

## Historical validation

Validation starts on 2024-01-23 and contains 565
forecast dates.

| Method | MAE | RMSE | Mean error |
| --- | ---: | ---: | ---: |
| Constant baseline | 0.003597 | 0.005924 | +0.000617 |
| Rolling 20-day RMS | 0.003613 | 0.006217 | +0.000511 |
| Provisional Ridge | 0.003201 | 0.005386 | +0.000167 |

Ridge had lower MAE and RMSE than both baselines in
this historical validation period. This observation
does not establish performance in other periods.

The 565 validation forecasts were nonnegative.

## Limitations and next questions

Five-day target windows overlap, so neighboring forecast
errors are dependent. The features may be correlated,
and fitted coefficients should not be interpreted as
causal effects.

Ridge does not enforce nonnegative predictions generally,
even though this validation run produced none.

We have not selected an optimal regularization strength
or evaluated this Ridge model on the later May-August 2026
period. That later period has already been inspected
during earlier baseline analysis and is not an untouched
holdout. It must not be used to choose model settings.

Run: `python -m src.ridge_risk_forecasting`
