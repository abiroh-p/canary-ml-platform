"""
Real metrics client backed by Prometheus PromQL queries (latency, error
rate) plus local JSONL prediction logs (prediction scores for PSI).

NOTE: prediction_scores comes from the model-server's prediction log
files, not Prometheus — histograms don't retain raw values needed for
PSI. See ADR-0004 and Step 30 notes for the shared-filesystem
assumption this currently relies on.
"""

import logging

import httpx

from app.clients.metrics_client import MetricsClient, ModelMetrics
from app.clients.prediction_log_reader import read_recent_scores

logger = logging.getLogger(__name__)


class PrometheusMetricsClient(MetricsClient):
    def __init__(
        self,
        prometheus_url: str,
        stable_log_path: str,
        canary_log_path: str,
        window: str = "5m",
    ) -> None:
        self._base_url = prometheus_url.rstrip("/")
        self._window = window
        self._log_paths = {"stable": stable_log_path, "canary": canary_log_path}

    def _query(self, promql: str) -> float | None:
        resp = httpx.get(f"{self._base_url}/api/v1/query", params={"query": promql})
        resp.raise_for_status()
        result = resp.json()["data"]["result"]
        if not result:
            return None
        value = float(result[0]["value"][1])
        if value != value:  # NaN check (NaN != NaN is always True)
            return None
        return value

    def get_metrics(self, model_version_label: str) -> ModelMetrics:
        p99_query = (
            f'histogram_quantile(0.99, rate('
            f'model_server_prediction_latency_ms_bucket{{model_version_label="{model_version_label}"}}[{self._window}]))'
        )
        error_query = (
            f'rate(model_server_predictions_total{{model_version_label="{model_version_label}", status="error"}}[{self._window}])'
            f' / rate(model_server_predictions_total{{model_version_label="{model_version_label}"}}[{self._window}])'
        )

        p99 = self._query(p99_query)
        error_rate = self._query(error_query)

        if p99 is None:
            logger.warning("no latency data yet", extra={"model_version_label": model_version_label})
            p99 = 0.0
        if error_rate is None:
            error_rate = 0.0

        log_path = self._log_paths.get(model_version_label)
        prediction_scores = read_recent_scores(log_path) if log_path else []

        if not prediction_scores:
            logger.warning(
                "no prediction scores available yet",
                extra={"model_version_label": model_version_label},
            )

        return ModelMetrics(
            p99_latency_ms=p99,
            error_rate=error_rate,
            prediction_scores=prediction_scores,
        )
