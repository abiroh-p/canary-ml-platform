"""
Model loading abstraction.

ModelLoader defines the interface; LocalFileModelLoader is the current
implementation. An MLflowRegistryModelLoader will be added later without
changing this interface or anything in services/inference.py.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
import logging

import joblib

logger = logging.getLogger(__name__)


class ModelLoader(ABC):
    """Interface for anything that can produce a loaded model object."""

    @abstractmethod
    def load(self) -> Any:
        """Return a loaded model object with a .predict() method."""
        raise NotImplementedError


class LocalFileModelLoader(ModelLoader):
    """Loads a joblib-serialized scikit-learn model from a local path."""

    def __init__(self, model_path: str) -> None:
        self._model_path = Path(model_path)

    def load(self) -> Any:
        if not self._model_path.exists():
            raise FileNotFoundError(
                f"Model artifact not found at {self._model_path}. "
                "Train a placeholder model first (see training/) or check MODEL_PATH."
            )
        logger.info("loading model", extra={"model_path": str(self._model_path)})
        return joblib.load(self._model_path)