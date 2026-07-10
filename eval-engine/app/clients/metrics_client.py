"""
Metrics source abstraction. StubMetricsClient returns caller-controlled
fake data now; a PrometheusMetricsClient implementing the same interface
will replace it later without changing policy/evaluator.py.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ModelMetrics:
    p99_latency_ms: float
    error_rate: float
    prediction_scores: list[float]


class MetricsClient(ABC):
    @abstractmethod
    def get_metrics(self, model_version_label: str) -> ModelMetrics:
        raise NotImplementedError


class StubMetricsClient(MetricsClient):
    """Returns fixed, caller-supplied metrics per label. Testing only."""

    def __init__(self, fixed_metrics: dict[str, ModelMetrics]) -> None:
        self._fixed_metrics = fixed_metrics

    def get_metrics(self, model_version_label: str) -> ModelMetrics:
        if model_version_label not in self._fixed_metrics:
            raise KeyError(f"no stubbed metrics for {model_version_label}")
        return self._fixed_metrics[model_version_label]