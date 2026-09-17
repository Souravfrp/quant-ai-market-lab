"""
Baseline KMeans analysis for market-condition features.

This module treats KMeans as a geometric baseline rather than assuming
that its clusters are genuine persistent market regimes.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

from src.regime_features import construct_regime_features
from src.temporal_split import (
    load_log_returns,
    temporal_split,
    validate_returns,
)

MIN_CLUSTERS = 2
MAX_CLUSTERS = 8
BASELINE_CLUSTERS = 2
N_INIT = 20
RANDOM_STATE = 42


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

def standardize_features(features):
    """
    Standardize each feature using statistics fitted on historical data.
    """
    feature_values = features.to_numpy()

    if not np.isfinite(feature_values).all():
        raise ValueError(
            "Input features contain non-finite values."
        )

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    if not np.isfinite(scaled_features).all():
        raise ValueError(
            "Standardized features contain non-finite values."
        )

    return scaled_features, scaler

def evaluate_candidate_clusters(scaled_features):
    """
    Evaluate candidate KMeans partitions using inertia and silhouette score.
    """
    diagnostics = []

    for k in range(MIN_CLUSTERS, MAX_CLUSTERS + 1):
        model = KMeans(
            n_clusters=k,
            init="k-means++",
            n_init=N_INIT,
            random_state=RANDOM_STATE,
        )

        labels = model.fit_predict(scaled_features)

        diagnostics.append(
            {
                "k": k,
                "inertia": model.inertia_,
                "silhouette": silhouette_score(
                    scaled_features,
                    labels,
                ),
                "cluster_sizes": np.bincount(
                    labels,
                    minlength=k,
                ).tolist(),
            }
        )

    return diagnostics


def fit_baseline_kmeans(scaled_features):
    """
    Fit the selected K=2 baseline partition.
    """
    model = KMeans(
        n_clusters=BASELINE_CLUSTERS,
        init="k-means++",
        n_init=N_INIT,
        random_state=RANDOM_STATE,
    )

    labels = model.fit_predict(scaled_features)

    return model, labels

def plot_cluster_geometry(features, labels, centroids):
    """
    Visualize the KMeans partition in the original feature coordinates.

    Points are colored by cluster assignment and cluster centroids are
    marked separately. These plots are diagnostic views of the KMeans
    partition, not evidence that the clusters are true market regimes.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    centroid_frame = pd.DataFrame(
        centroids,
        columns=features.columns,
    )

    pairs = [
        (
            "spy_return",
            "spy_volatility_20d",
            "SPY Return vs 20-Day Volatility",
            "kmeans_return_vs_volatility.png",
        ),
        (
            "spy_return",
            "cross_asset_dispersion",
            "SPY Return vs Cross-Asset Dispersion",
            "kmeans_return_vs_dispersion.png",
        ),
        (
            "spy_volatility_20d",
            "cross_asset_dispersion",
            "20-Day Volatility vs Cross-Asset Dispersion",
            "kmeans_volatility_vs_dispersion.png",
        ),
    ]

    for x_column, y_column, title, filename in pairs:
        plt.figure(figsize=(8, 6))

        for cluster in range(BASELINE_CLUSTERS):
            cluster_mask = labels == cluster

            plt.scatter(
                features.loc[cluster_mask, x_column],
                features.loc[cluster_mask, y_column],
                alpha=0.45,
                s=16,
                label=f"Cluster {cluster}",
            )

        plt.scatter(
            centroid_frame[x_column],
            centroid_frame[y_column],
            marker="X",
            s=180,
            edgecolors="black",
            linewidths=1.2,
            label="KMeans centroids",
        )

        plt.xlabel(x_column.replace("_", " ").title())
        plt.ylabel(y_column.replace("_", " ").title())
        plt.title(f"KMeans Baseline: {title}")
        plt.legend()
        plt.grid(alpha=0.25)
        plt.tight_layout()

        output_path = RESULTS_DIR / filename
        plt.savefig(output_path, dpi=160)
        plt.close()

        print("Saved:", output_path)

def plot_cluster_timeline(labels, index):
    """
    Plot KMeans cluster assignments through historical time.

    This is a post-clustering temporal diagnostic. KMeans itself does not
    use chronological ordering when assigning observations to clusters.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    regimes = pd.Series(
        labels,
        index=index,
        name="cluster",
    )

    plt.figure(figsize=(12, 3))

    for cluster in range(BASELINE_CLUSTERS):
        cluster_mask = regimes == cluster

        plt.scatter(
            regimes.index[cluster_mask],
            regimes.loc[cluster_mask],
            s=10,
            alpha=0.7,
            label=f"Cluster {cluster}",
        )

    plt.yticks(
        range(BASELINE_CLUSTERS),
        [f"Cluster {k}" for k in range(BASELINE_CLUSTERS)],
    )
    plt.xlabel("Date")
    plt.ylabel("KMeans cluster")
    plt.title("KMeans Baseline Cluster Assignments Through Time")
    plt.legend()
    plt.grid(axis="x", alpha=0.25)
    plt.tight_layout()

    output_path = RESULTS_DIR / "kmeans_cluster_timeline.png"
    plt.savefig(output_path, dpi=160)
    plt.close()

    print("Saved:", output_path)


def temporal_diagnostics(labels, index):
    """
    Measure persistence and transitions of consecutive KMeans labels.

    These statistics diagnose temporal behavior after clustering.
    KMeans itself does not use time ordering.
    """
    regimes = pd.Series(
        labels,
        index=index,
        name="cluster",
    )

    switches = int(
        (
            regimes.iloc[1:].to_numpy()
            != regimes.iloc[:-1].to_numpy()
        ).sum()
    )

    run_id = regimes.ne(regimes.shift()).cumsum()

    runs = pd.DataFrame(
        {
            "cluster": regimes.groupby(run_id).first().to_numpy(),
            "length": regimes.groupby(run_id).size().to_numpy(),
        }
    )

    previous = regimes.iloc[:-1].to_numpy()
    current = regimes.iloc[1:].to_numpy()

    transition_counts = pd.crosstab(
        pd.Series(previous, name="from"),
        pd.Series(current, name="to"),
    )

    transition_probabilities = transition_counts.div(
        transition_counts.sum(axis=1),
        axis=0,
    )

    return (
        switches,
        runs,
        transition_counts,
        transition_probabilities,
    )


def initialization_stability(scaled_features):
    """
    Compare K=2 solutions across several random seeds.
    """
    seeds = [0, 1, 2, 3, 4, 10, 42, 100, 2026]
    solutions = {}
    diagnostics = []

    for seed in seeds:
        model = KMeans(
            n_clusters=BASELINE_CLUSTERS,
            init="k-means++",
            n_init=N_INIT,
            random_state=seed,
        )

        labels = model.fit_predict(scaled_features)
        solutions[seed] = labels

        diagnostics.append(
            {
                "seed": seed,
                "inertia": model.inertia_,
                "cluster_sizes": np.bincount(
                    labels,
                    minlength=BASELINE_CLUSTERS,
                ).tolist(),
            }
        )

    reference = solutions[RANDOM_STATE]

    for result in diagnostics:
        result["ari_vs_reference"] = adjusted_rand_score(
            reference,
            solutions[result["seed"]],
        )

    return diagnostics

if __name__ == "__main__":
    returns = load_log_returns()
    validate_returns(returns)

    historical, _ = temporal_split(returns)
    features = construct_regime_features(historical)

    scaled_features, scaler = standardize_features(features)

    print("Candidate KMeans diagnostics")
    print("----------------------------")

    diagnostics = evaluate_candidate_clusters(
        scaled_features
    )

    for result in diagnostics:
        print(
            f"K={result['k']}: "
            f"inertia={result['inertia']:.3f}, "
            f"silhouette={result['silhouette']:.4f}, "
            f"sizes={result['cluster_sizes']}"
        )

    model, labels = fit_baseline_kmeans(
        scaled_features
    )

    centroids = scaler.inverse_transform(
        model.cluster_centers_
    )

    plot_cluster_geometry(
        features,
        labels,
        centroids,
    )

    plot_cluster_timeline(
        labels,
        features.index,
    )

    print("\nK=2 baseline centroids")
    print("----------------------")

    for cluster, centroid in enumerate(centroids):
        print(f"\nCluster {cluster}")
        for feature_name, value in zip(
            features.columns,
            centroid,
        ):
            print(f"  {feature_name}: {value:.6f}")

    (
        switches,
        runs,
        transition_counts,
        transition_probabilities,
    ) = temporal_diagnostics(
        labels,
        features.index,
    )

    print("\nTemporal diagnostics")
    print("--------------------")
    print("Number of regime switches:", switches)
    print(
        "Switch rate:",
        f"{100 * switches / (len(labels) - 1):.2f}%"
    )

    print("\nRun-length statistics:")
    print(
        runs.groupby("cluster")["length"]
        .agg(["count", "mean", "median", "max"])
    )

    print("\nTransition counts:")
    print(transition_counts)

    print("\nTransition probabilities:")
    print(transition_probabilities)

    stability = initialization_stability(
        scaled_features
    )

    print("\nInitialization stability")
    print("------------------------")

    for result in stability:
        print(
            f"seed={result['seed']:4d}, "
            f"inertia={result['inertia']:.6f}, "
            f"sizes={result['cluster_sizes']}, "
            f"ARI={result['ari_vs_reference']:.6f}"
        )
