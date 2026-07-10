"""
Population Stability Index (PSI) between two score distributions.
See docs/adr/0004-psi-drift-detection.md for the reasoning.
"""

import numpy as np

_EPSILON = 1e-6


def calculate_psi(expected: list[float], actual: list[float], bins: int = 10) -> float:
    """
    expected: stable model's prediction scores (the reference distribution)
    actual: canary model's prediction scores
    """
    if len(expected) == 0 or len(actual) == 0:
        raise ValueError("both distributions must be non-empty")

    expected_arr = np.array(expected)
    actual_arr = np.array(actual)

    quantiles = np.linspace(0, 100, bins + 1)
    bin_edges = np.percentile(expected_arr, quantiles)
    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    expected_counts, _ = np.histogram(expected_arr, bins=bin_edges)
    actual_counts, _ = np.histogram(actual_arr, bins=bin_edges)

    expected_pct = expected_counts / len(expected_arr)
    actual_pct = actual_counts / len(actual_arr)

    expected_pct = np.clip(expected_pct, _EPSILON, None)
    actual_pct = np.clip(actual_pct, _EPSILON, None)

    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return float(psi)