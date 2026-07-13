"""
Real metrics client backed by Prometheus PromQL queries (latency, error
rate) plus a network call to each model-server's /predictions/recent
endpoint (prediction scores for PSI).

NOTE: prediction_scores comes from a direct HTTP call to the model
server's in-memory recent-predictions buffer, not from Prometheus
(histograms don't retain raw values needed for PSI) and not from a
shared filesystem (that assumption broke on multi-node K8s — see
ADR-0004 and Step 41).
"""

import logging

import httpx

from app.clients.metrics_client import MetricsClient, ModelMetrics

logger = logging.getLogger(__name__)


class PrometheusMetricsClient(MetricsClient):
    def __init__(
        self,
        prometheus_url: str,
        stable_url: str,
        canary_url: str,
        window: str = "5m",
    ) -> None:
        self._base_url = prometheus_url.rstrip("/")
        self._window = window
        self._upstream_urls = {"stable": stable_url, "canary": canary_url}

    def _query(self, promql: str) -> float | None:
        try:
            resp = httpx.get(f"{self._base_url}/api/v1/query", params={"query": promql})
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.warning("prometheus query failed", extra={"error": str(e)})
            return None

        result = resp.json()["data"]["result"]
        if not result:
            return None
        value = float(result[0]["value"][1])
        if value != value:  # NaN check
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

        upstream_url = self._upstream_urls.get(model_version_label)
        prediction_scores: list[float] = []
        if upstream_url:
            try:
                resp = httpx.get(f"{upstream_url}/predictions/recent")
                resp.raise_for_status()
                prediction_scores = resp.json()["prediction_scores"]
            except httpx.HTTPError as e:
                logger.warning(
                    "failed to fetch recent predictions",
                    extra={"model_version_label": model_version_label, "error": str(e)},
                )

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
