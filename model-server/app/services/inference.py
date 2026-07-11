"""
Inference business logic. Framework-agnostic — no FastAPI imports here,
so it's testable with plain Pytest and reusable outside HTTP if needed.
"""

import logging
import time

from app.core.metrics import PREDICTION_LATENCY, PREDICTION_REQUESTS_TOTAL
from app.models.loader import ModelLoader
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_logger import PredictionLogger

logger = logging.getLogger(__name__)


class InferenceService:
    """Wraps a loaded model and produces PredictionResponse objects."""

    def __init__(
        self,
        loader: ModelLoader,
        model_version_label: str,
        prediction_logger: PredictionLogger,
    ) -> None:
        self._model = loader.load()
        self._model_version_label = model_version_label
        self._prediction_logger = prediction_logger

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        start = time.perf_counter()
        try:
            raw_prediction = self._model.predict([request.features])[0]
            status = "success"
        except Exception:
            status = "error"
            PREDICTION_REQUESTS_TOTAL.labels(
                model_version_label=self._model_version_label, status=status
            ).inc()
            raise

        latency_ms = (time.perf_counter() - start) * 1000

        self._prediction_logger.log(float(raw_prediction))

        PREDICTION_LATENCY.labels(model_version_label=self._model_version_label).observe(latency_ms)
        PREDICTION_REQUESTS_TOTAL.labels(
            model_version_label=self._model_version_label, status=status
        ).inc()

        logger.info(
            "prediction served",
            extra={
                "model_version_label": self._model_version_label,
                "latency_ms": round(latency_ms, 3),
            },
        )

        return PredictionResponse(
            prediction=float(raw_prediction),
            model_version_label=self._model_version_label,
            latency_ms=latency_ms,
        )
