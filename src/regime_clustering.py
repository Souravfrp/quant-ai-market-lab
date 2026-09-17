"""
Baseline KMeans analysis for market-condition features.

This module treats KMeans as a geometric baseline rather than assuming
that its clusters are genuine persistent market regimes.
"""

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
