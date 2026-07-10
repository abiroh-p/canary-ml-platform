"""
Inference business logic. Framework-agnostic — no FastAPI imports here,
so it's testable with plain Pytest and reusable outside HTTP if needed.
"""

import logging
import time

from app.models.loader import ModelLoader
from app.schemas.prediction import PredictionRequest, PredictionResponse

logger = logging.getLogger(__name__)


class InferenceService:
    """Wraps a loaded model and produces PredictionResponse objects."""

    def __init__(self, loader: ModelLoader, model_version_label: str) -> None:
        self._model = loader.load()
        self._model_version_label = model_version_label

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        start = time.perf_counter()
        raw_prediction = self._model.predict([request.features])[0]
        latency_ms = (time.perf_counter() - start) * 1000

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