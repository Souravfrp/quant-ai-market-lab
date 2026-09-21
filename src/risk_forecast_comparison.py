"""Compare five-day SPY risk forecasts on historical validation."""

import pandas as pd

from src.temporal_split import CUTOFF_DATE, load_log_returns
from src.regime_features import construct_regime_features
from src.risk_forecasting import (
    construct_risk_target,
    split_forecasting_dates,
    constant_risk_baseline,
    rolling_rms_baseline,
)
from src.ridge_risk_forecasting import fit_predict_ridge


def build_validation_comparison():
    """Return date-aligned actual risk and baseline forecasts."""

    returns = load_log_returns()
    spy = returns["SPY"]
    features = construct_regime_features(returns)
    target = construct_risk_target(spy)

    train, validation, _ = split_forecasting_dates(
        spy, features.index, target, CUTOFF_DATE
    )

    _, ridge = fit_predict_ridge(
        features, target, train, validation, alpha=1.0
    )

    comparison = pd.DataFrame({
        "actual": target.loc[validation],
        "constant": constant_risk_baseline(
            target, train, validation
        ),
        "rolling_20d": rolling_rms_baseline(
            spy, validation
        ),
        "ridge": ridge,
    })

    if comparison.isna().any().any():
        raise ValueError("Comparison contains missing values.")

    return comparison

def plot_validation_forecast_comparison(comparison):
    """Plot historical validation forecasts against realized risk."""
    import matplotlib.pyplot as plt
    from pathlib import Path

    fig, ax = plt.subplots(figsize=(12, 6))

    for column, label in [
        ("actual", "Actual five-day RMS"),
        ("constant", "Training-average baseline"),
        ("rolling_20d", "Rolling 20-day RMS"),
        ("ridge", "Ridge, alpha=1"),
    ]:
        ax.plot(comparison.index, comparison[column], label=label)

    ax.set(
        title=(
            "SPY five-day risk: historical validation\n"
            "Forecast dates: 2024-01-23 to 2026-04-23"
        ),
        xlabel="Forecast date",
        ylabel="Daily-return RMS",
    )
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()

    output = Path("results/risk_forecast_validation_comparison.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return output

if __name__ == "__main__":
    comparison = build_validation_comparison()
    output = plot_validation_forecast_comparison(comparison)

    print("\nFive-day risk forecast comparison")
    print("--------------------------------")
    print("Validation dates:", len(comparison))
    print("First date:", comparison.index.min())
    print("Last date:", comparison.index.max())
    print("Columns:", list(comparison.columns))

    for column in ["constant", "rolling_20d", "ridge"]:
        errors = comparison[column] - comparison["actual"]
        mae = errors.abs().mean()
        rmse = (errors.pow(2).mean()) ** 0.5
        print(f"{column}: MAE={mae:.6f}, RMSE={rmse:.6f}")

    print("Saved figure:", output)
