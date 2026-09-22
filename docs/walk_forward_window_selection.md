# Walk-forward training-window selection

## Research question

Does retaining all available historical training data, using a fixed
rolling window, or selecting a window from past forecast errors produce
different five-day SPY RMS-risk forecasting results?

The training-window length is treated as an experimental choice rather
than assumed to be optimal.

## Experimental design

- Forecast dates: 2019-02-08 through 2026-04-23.
- Forecast target: RMS of SPY daily log returns over the next five
  trading days.
- Features: daily SPY log return, trailing 20-day SPY volatility,
  and same-day cross-asset return dispersion.
- Ridge alpha: 1.
- Models refitted on the first eligible forecast date of each month.
- Candidate training histories: the most recent 252, 504, 756, or
  1008 eligible examples, or all eligible examples (expanding).
- A training example is eligible only after its complete five-day
  target is observable at the refit date.

## Adaptive selection

At each monthly selection date, the algorithm calculates the MAE of
each candidate method using its most recent 252 completed forecasts.
It selects the candidate with the lowest historical MAE, breaking
exact ties by a fixed candidate order.

The first adaptive selection is 2020-03-02. Earlier candidate
forecasts supply its initial performance history.

The selected candidate supplies forecasts for the following monthly
block. Outcomes from that block are not used to select its method.

## Common-date evaluation

All six methods were evaluated on the same 1545 forecast dates,
2020-03-02 through 2026-04-23.

| Method | MAE | RMSE | Mean forecast error |
| --- | ---: | ---: | ---: |
| Rolling 252 | 0.004086 | 0.007246 | +0.000315 |
| Rolling 504 | 0.003781 | 0.006737 | +0.000098 |
| Rolling 756 | 0.003799 | 0.006668 | +0.000239 |
| Rolling 1008 | 0.003813 | 0.006693 | +0.000155 |
| Expanding | 0.003676 | 0.006511 | -0.000325 |
| Adaptive | 0.003715 | 0.006625 | -0.000198 |

The expanding-window method had lower aggregate MAE and RMSE than
the adaptive method during this evaluation. The experiment does not
establish that either method will perform better in future periods.

## Limitations

The five-day targets overlap, so neighboring forecast errors are
dependent. No statistical uncertainty interval has yet been
calculated for the differences between methods.

The candidate windows, monthly refitting, alpha, and 252-forecast
selection history are experimental design choices; this experiment
does not establish that they are optimal.

Historical evaluation results, including the later part of this
period, have been inspected during project development. These dates
must not be described as an untouched independent test.

The experiment forecasts future RMS risk, not return direction or
trading profitability.

## Reproduction

Generate the candidate forecasts using
`src/walk_forward_comparison.py`, then run:

`python -m src.walk_forward_evaluation`

The evaluation reads `results/walk_forward_forecasts.csv`.
