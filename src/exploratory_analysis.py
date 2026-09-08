"""
Exploratory data analysis and visualization for Quant AI Market Lab.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "adjusted_close.csv"

RESULTS_DIR = PROJECT_ROOT / "results"


def load_prices():
    """
    Load adjusted closing prices.
    """

    prices = pd.read_csv(
        RAW_DATA_PATH,
        index_col=0,
        parse_dates=True,
    )

    return prices


def normalize_prices(prices):
    """
    Normalize each asset so that its first observation equals 100.
    """

    normalized = 100 * prices / prices.iloc[0]

    return normalized


def plot_normalized_performance(normalized):
    """
    Plot normalized cross-asset performance and save the figure.
    """

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    ax = normalized.plot(
        figsize=(12, 7),
        linewidth=1.5,
    )

    ax.set_title("Normalized Cross-Asset Performance")
    ax.set_xlabel("Date")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(normalized.index.min(), normalized.index.max())
    ax.set_ylabel("Normalized Value (Start = 100)")
    ax.grid(True, alpha=0.3)

    figure_path = RESULTS_DIR / "normalized_asset_performance.png"

    plt.tight_layout()
    plt.savefig(
        figure_path,
        dpi=200,
        bbox_inches="tight",
    )

    print(f"Saved figure to: {figure_path}")

    plt.close()


if __name__ == "__main__":
    prices = load_prices()

    normalized = normalize_prices(prices)

    plot_normalized_performance(normalized)
