# What my models can answer, and their limitations

I use Quant AI Market Lab to study historical market structure, forecast SPY return magnitude, and evaluate minimum-variance portfolio methods. I want to distinguish the questions each method addresses from conclusions the experiment does not support. This document covers the original project only.

## Questions, outputs and boundaries

| Question | What I can report from this project | What I cannot conclude |
|---|---|---|
| How did the eight ETFs move together? | Historical return, covariance and correlation estimates for the selected sample. | That the same relationships will persist or establish economic causation. |
| Which directions explain common variation? | PCA loadings and explained variance in standardized historical returns. | That components are proven economic factors or forecasts of future returns. Full-sample PCA is descriptive. |
| Can observations be grouped into different market conditions? | A reproducible KMeans partition of the chosen feature space. | That the market has exactly that many true regimes, or that clusters capture temporal persistence. |
| How does a temporal model describe market conditions? | Gaussian HMM state parameters, transition estimates and filtered probabilities in the documented fixed-cutoff evaluation. | Verified economic regimes or a forecast made before the date's return when filtering uses that observed return. |
| How large might SPY's next five daily returns be? | Five-return RMS forecasts from the documented baselines, Ridge and Random Forest experiments. | Return direction, a daily price path, or a guarantee of the predicted magnitude. |
| Which risk model had smaller errors in the studied period? | Matched historical errors under the recorded chronological validation and walk-forward rules. | A universally best model, an untouched holdout result, or persistent superiority in future markets. |
| Which features did the fitted models rely on? | Standardized Ridge coefficients and Random Forest permutation importance under the documented fitting and validation procedure. | Causal effects, or that a weak permutation importance means a feature is economically irrelevant. |
| Which allocations minimize estimated portfolio variance? | Long-only, fully invested minimum-variance weights for the chosen covariance estimate and constraints. | Maximum expected return, maximum Sharpe ratio, or the allocation with the best future realized outcome. |
| How did the portfolio methods perform historically? | Retrospective wealth, risk, turnover, benchmark and cost comparisons under the stated execution conventions. | Profitable live trading, exact executable fills, or that inspected historical results form an untouched forward test. |
| Were the portfolio findings stable across time and assumptions? | Recorded subperiod comparisons, covariance-window comparisons and transaction-cost sensitivity. | Robustness to every regime, liquidity shock, cost model or future sample. |
| Which ETF will outperform in the future? | This is not established by the SPY RMS forecasts or historical portfolio study. | A validated prospective ranking of ETF returns. |
| What is the probability of a crash or a specified loss? | No separately validated tail-risk forecast or calibrated interval is established here. | Reliable crash probabilities, Value at Risk or Expected Shortfall merely from an RMS prediction or fitted regime distribution. |

## Why RMS cannot answer market direction

For daily log returns, my five-return risk target is

$$
y_t=\sqrt{\frac{1}{5}\sum_{j=1}^{5}r_{t+j}^{2}}.
$$

Five returns of +1% and five returns of -1% both have RMS 1%. Their directions differ, but squaring removes the sign. This is daily return magnitude over five observations, not the cumulative five-day return.

RMS includes the mean component:

$$
\mathrm{RMS}^2=\mathrm{SD}_{\mathrm{population}}^2+\overline r^2.
$$

I therefore distinguish the zero-centered RMS target from the rolling sample standard deviation used as a feature.

## What my evidence supports

The later May–August 2026 SPY period was examined during development. I describe it as pseudo-out-of-sample rather than an untouched holdout. Chronological fitting and model selection restrict information at each forecast origin, but they do not erase the fact that the evaluation period was previously inspected.

Adjacent five-day targets share returns, so neighboring forecast errors are dependent. I do not treat the number of daily forecasts as the same number of independent experiments. Smaller measured MAE or RMSE alone does not establish statistical significance or future superiority.

The fixed-cutoff HMM uses a historical scaler and fitted model, but its filtered probabilities incorporate each evaluation date's observed returns. These are descriptions conditional on observations available through that date. Later-period likelihood and historical fitting likelihood are not interchangeable forecasting scores.

The portfolio comparison is retrospective and separate from the May–August SPY forecast study. The optimizer minimizes estimated variance. The historical terminal wealth of a strategy is not a reason to claim that it solved a return-maximization problem or will deliver the best future performance.

## Assumptions I keep visible

- **Data:** results depend on the ETF universe, dates and vendor-adjusted prices. A later download may contain revisions; exact reproduction requires identifying the saved input vintage.
- **Transformations:** full-sample PCA is descriptive. Any predictive use of scaling or PCA must estimate those transformations using only the information available at the historical origin.
- **Model form:** KMeans uses Euclidean geometry; Gaussian HMMs impose distribution and state-transition assumptions; Ridge is linear in its features; Random Forest performance depends on the tested settings and sample.
- **Selection:** the recorded candidate grids and covariance-window comparisons do not establish global optimality. I do not choose a portfolio window solely because it achieved the largest inspected terminal wealth.
- **Execution:** backtest outcomes depend on the documented next-session-close convention, rebalancing, proportional costs and other accounting assumptions. Sensitivity checks cover the tested scenarios.
- **Validation:** numerical and timing checks establish particular implementation properties. They do not certify economic causality or market predictability.

## What I would need before making stronger claims

A stronger performance claim would require a frozen procedure evaluated on genuinely later observations, with matched targets and dependence-aware uncertainty assessment. A directional or ETF-ranking claim would require different targets and a separately validated forecasting experiment. Tail-loss claims would need a validated predictive distribution or calibrated risk model. A live-profitability claim would require a trading rule and realistic execution, costs, liquidity and risk controls.

I can report what the implemented methods computed, how I evaluated them and where they failed or differed. I keep claims about future performance within the evidence actually available.

## Supporting documentation

- [Mathematical formulations and algorithmic reasoning](mathematics_optimization_algorithms.md).
- [Risk forecasting baselines](risk_forecasting_baselines.md).
- [Ridge forecasting](ridge_risk_forecasting.md) and [alpha validation](ridge_alpha_validation.md).
- [Random Forest forecasting and interpretation](random_forest_risk_forecasting.md).
- [Walk-forward window selection](walk_forward_window_selection.md).
- [Fixed-cutoff HMM evaluation](hmm_fixed_cutoff_evaluation.md).
- [Portfolio mathematics, execution and validation](portfolio_mathematics_and_validation.md).
- [Portfolio subperiod findings](portfolio_robustness_findings.md).
