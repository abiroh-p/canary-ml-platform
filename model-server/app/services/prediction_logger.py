"""
Appends prediction scores to a local JSONL file for audit purposes, and
keeps a small in-memory ring buffer of recent scores for the
/predictions/recent endpoint (see ADR-0004 and Step 41 — this replaces
the shared-filesystem assumption that doesn't hold on multi-node K8s).
"""

import json
import logging
import threading
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class PredictionLogger:
    def __init__(self, log_path: str, model_version_label: str, buffer_size: int = 500) -> None:
        self._path = Path(log_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._model_version_label = model_version_label
        self._lock = threading.Lock()
        self._recent = deque(maxlen=buffer_size)

    def log(self, prediction: float) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model_version_label": self._model_version_label,
            "prediction": prediction,
        }
        with self._lock:
            self._recent.append(prediction)
            try:
                with self._path.open("a") as f:
                    f.write(json.dumps(record) + "\n")
            except OSError as e:
                logger.error("failed to log prediction", extra={"error": str(e)})

    def get_recent(self) -> list[float]:
        with self._lock:
            return list(self._recent)