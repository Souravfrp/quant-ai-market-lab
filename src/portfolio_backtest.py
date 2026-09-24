"""
Chronological minimum-variance portfolio backtesting.

Research experiment:
- Eight ETFs.
- Five historical covariance estimation methods.
- Long-only, fully invested portfolio.
- Monthly portfolio decisions.
- Next-session closing-price execution.
- Buy-and-hold between monthly rebalancing events.
- No transaction costs in the initial baseline.

Historical evaluation ends on April 30, 2026.
"""

from pathlib import Path

import cvxpy as cp
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

LOG_RETURNS_PATH = (
    PROJECT_ROOT / "data" / "processed" / "log_returns.csv"
)

HISTORICAL_CUTOFF = pd.Timestamp("2026-04-30")

INITIAL_CAPITAL = 100000.0

TRADING_DAYS_PER_YEAR = 252

COVARIANCE_METHODS = {
    "Rolling 252": 252,
    "Rolling 504": 504,
    "Rolling 756": 756,
    "Rolling 1008": 1008,
    "Expanding": None,
}


def load_simple_returns():
    """
    Load the existing daily log returns and convert
    them into daily simple returns.
    """

    log_returns = pd.read_csv(
        LOG_RETURNS_PATH,
        index_col=0,
        parse_dates=True,
    ).sort_index()

    returns = np.expm1(log_returns)

    historical = returns.loc[
        returns.index <= HISTORICAL_CUTOFF
    ].copy()

    if not historical.index.is_unique:
        raise RuntimeError(
            "Duplicate return dates detected."
        )

    if not historical.index.is_monotonic_increasing:
        raise RuntimeError(
            "Return dates are not chronological."
        )

    if not np.isfinite(
        historical.to_numpy()
    ).all():
        raise RuntimeError(
            "Non-finite return observations detected."
        )

    if not (historical > -1).all().all():
        raise RuntimeError(
            "Invalid simple returns detected."
        )

    if historical.shape[1] != 8:
        raise RuntimeError(
            "Expected eight ETF return series."
        )

    return historical


def get_monthly_decision_dates(historical):
    """
    Identify the final observed trading date
    of each eligible historical month.
    """

    eligible = historical.iloc[1008:]

    monthly_dates = (
        eligible.groupby(
            eligible.index.to_period("M")
        )
        .apply(
            lambda group: group.index[-1]
        )
    )

    if len(monthly_dates) != 88:
        raise RuntimeError(
            "Unexpected number of monthly decision dates."
        )

    # The final April 2026 decision cannot be
    # executed within the historical evaluation period.

    decision_dates = pd.DatetimeIndex(
        monthly_dates.iloc[:-1].to_numpy()
    )

    return decision_dates


def optimize_portfolio(history, window_length):
    """
    Solve the long-only minimum-variance problem
    using covariance estimated from historical
    simple returns.
    """

    if window_length is None:
        estimation_data = history
    else:
        estimation_data = history.tail(window_length)

    sigma = estimation_data.cov().to_numpy()

    if not np.isfinite(sigma).all():
        raise RuntimeError(
            "Non-finite covariance matrix."
        )

    if not np.allclose(
        sigma,
        sigma.T,
        atol=1e-12,
    ):
        raise RuntimeError(
            "Covariance matrix is not symmetric."
        )

    if np.linalg.eigvalsh(sigma).min() < -1e-12:
        raise RuntimeError(
            "Covariance matrix is not positive semidefinite."
        )

    n_assets = history.shape[1]

    weights_variable = cp.Variable(n_assets)

    problem = cp.Problem(
        cp.Minimize(
            cp.quad_form(
                weights_variable,
                sigma,
            )
        ),
        [
            cp.sum(weights_variable) == 1,
            weights_variable >= 0,
        ],
    )

    problem.solve(
        solver="OSQP",
        eps_abs=1e-9,
        eps_rel=1e-9,
        max_iter=100000,
    )

    if problem.status != cp.OPTIMAL:
        raise RuntimeError(
            f"Optimization failed: {problem.status}"
        )

    weights = np.asarray(
        weights_variable.value
    ).ravel()

    if not np.isfinite(weights).all():
        raise RuntimeError(
            "Non-finite portfolio weights."
        )

    if (
        abs(weights.sum() - 1) > 1e-7
        or weights.min() < -1e-7
    ):
        raise RuntimeError(
            "Portfolio constraints violated."
        )

    # Remove numerical negative-zero residuals.

    weights = np.maximum(weights, 0.0)

    weights = weights / weights.sum()

    return weights


def run_backtest(
    historical,
    decision_dates,
    window_length,
):
    """
    Simulate monthly portfolio rebalancing.

    A signal is generated after the decision-date
    close and executed at the following session's
    closing price.

    Existing holdings earn their daily returns
    before the next allocation is executed.

    Transaction costs are excluded.
    """

    dates = historical.index

    n_assets = historical.shape[1]

    asset_values = np.zeros(
        n_assets,
        dtype=float,
    )

    cash = INITIAL_CAPITAL

    pending_weights = None

    execution_date = None

    records = []

    trades = []

    for position, date in enumerate(dates):

        if date < decision_dates[0]:
            continue

        daily_returns = historical.loc[
            date
        ].to_numpy(dtype=float)

        # Existing holdings earn the current
        # trading day's returns.

        asset_values *= 1.0 + daily_returns

        # Execute the pending allocation
        # at the current session's close.

        if execution_date == date:

            if pending_weights is None:
                raise RuntimeError(
                    "Missing pending portfolio weights."
                )

            total_value = (
                asset_values.sum() + cash
            )

            old_weights = (
                asset_values / total_value
            )

            turnover = np.abs(
                pending_weights - old_weights
            ).sum()

            asset_values = (
                total_value * pending_weights
            )

            cash = 0.0

            trades.append({
                "Execution date": date,
                "Turnover": turnover,
                "Portfolio value": total_value,
            })

            pending_weights = None

            execution_date = None

        # Generate a new portfolio signal
        # using historical information through today.

        if date in decision_dates:

            history = historical.loc[:date]

            pending_weights = optimize_portfolio(
                history,
                window_length,
            )

            next_position = position + 1

            if next_position >= len(dates):
                raise RuntimeError(
                    "No subsequent execution date."
                )

            execution_date = dates[next_position]

            if execution_date <= date:
                raise RuntimeError(
                    "Invalid execution chronology."
                )

        total_value = (
            asset_values.sum() + cash
        )

        records.append({
            "Date": date,
            "Portfolio value": total_value,
        })

    equity = pd.DataFrame(
        records
    ).set_index("Date")

    trades = pd.DataFrame(trades)

    if len(trades) != len(decision_dates):
        raise RuntimeError(
            "Unexpected number of portfolio executions."
        )

    if pending_weights is not None:
        raise RuntimeError(
            "An unexecuted portfolio signal remains."
        )

    first_execution = trades[
        "Execution date"
    ].iloc[0]

    equity = equity.loc[
        equity.index >= first_execution
    ]

    daily_portfolio_returns = (
        equity["Portfolio value"]
        .pct_change()
        .dropna()
    )

    if not np.isfinite(
        daily_portfolio_returns
    ).all():
        raise RuntimeError(
            "Non-finite portfolio returns."
        )

    return (
        equity,
        daily_portfolio_returns,
        trades,
    )


def summarize_backtest(
    method,
    equity,
    daily_returns,
    trades,
):
    """
    Calculate historical portfolio performance
    and trading statistics.
    """

    final_capital = equity[
        "Portfolio value"
    ].iloc[-1]

    total_return = (
        final_capital / INITIAL_CAPITAL - 1
    )

    realized_volatility = (
        daily_returns.std(ddof=1)
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )

    running_peak = equity[
        "Portfolio value"
    ].cummax()

    drawdown = (
        equity["Portfolio value"]
        / running_peak
        - 1
    )

    maximum_drawdown = drawdown.min()

    rebalancing_turnover = (
        trades["Turnover"].iloc[1:].sum()
    )

    return {
        "Method": method,
        "Final capital": final_capital,
        "Total return": total_return,
        "Annualized volatility": realized_volatility,
        "Maximum drawdown": maximum_drawdown,
        "Rebalancing turnover": rebalancing_turnover,
        "Executions": len(trades),
    }


def main():

    historical = load_simple_returns()

    decision_dates = get_monthly_decision_dates(
        historical
    )

    print(
        "Historical cutoff:",
        HISTORICAL_CUTOFF.date(),
    )

    print(
        "First decision date:",
        decision_dates[0].date(),
    )

    print(
        "Last evaluated decision date:",
        decision_dates[-1].date(),
    )

    print(
        "Monthly decisions:",
        len(decision_dates),
    )

    results = []

    for method, window_length in COVARIANCE_METHODS.items():

        equity, daily_returns, trades = run_backtest(
            historical,
            decision_dates,
            window_length,
        )

        result = summarize_backtest(
            method,
            equity,
            daily_returns,
            trades,
        )

        results.append(result)

        print(f"\n{method}")

        print(
            "First execution:",
            trades["Execution date"].iloc[0].date(),
        )

        print(
            "Final execution:",
            trades["Execution date"].iloc[-1].date(),
        )

        print(
            "Daily evaluation returns:",
            len(daily_returns),
        )

        print(
            f"Final capital: ₹{result['Final capital']:,.2f}"
        )

        print(
            f"Total return: {result['Total return']:.4%}"
        )

        print(
            "Annualized realized volatility:",
            f"{result['Annualized volatility']:.4%}",
        )

        print(
            "Maximum drawdown:",
            f"{result['Maximum drawdown']:.4%}",
        )

        print(
            "Cumulative rebalancing turnover:",
            f"{result['Rebalancing turnover']:.6f}",
        )

    comparison = pd.DataFrame(results)

    print("\nFINAL COMPARISON")

    print(
        comparison.to_string(
            index=False,
            float_format=lambda x: f"{x:.6f}",
        )
    )

    print(
        "\nPASS: All five historical portfolio "
        "simulations completed."
    )


if __name__ == "__main__":
    main()
