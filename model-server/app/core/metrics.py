"""Prometheus metrics definitions. Import and use these, never
instantiate duplicate metrics elsewhere."""

from prometheus_client import Counter, Histogram

PREDICTION_LATENCY = Histogram(
    "model_server_prediction_latency_ms",
    "Prediction latency in milliseconds",
    labelnames=["model_version_label"],
    buckets=(5, 10, 25, 50, 100, 250, 500, 1000),
)

PREDICTION_REQUESTS_TOTAL = Counter(
    "model_server_predictions_total",
    "Total prediction requests",
    labelnames=["model_version_label", "status"],
)