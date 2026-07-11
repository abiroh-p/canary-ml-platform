"""
Appends prediction scores to a local JSONL file for later PSI computation
by the eval engine. See ADR-0004 for why this exists separately from
Prometheus (histograms don't retain raw values).

Known limitation: file-per-instance, not safe across multiple replicas
of the same model version. Acceptable at this project's scope.
"""

import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class PredictionLogger:
    def __init__(self, log_path: str, model_version_label: str) -> None:
        self._path = Path(log_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._model_version_label = model_version_label
        self._lock = threading.Lock()

    def log(self, prediction: float) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model_version_label": self._model_version_label,
            "prediction": prediction,
        }
        # Lock guards concurrent writes from multiple in-flight requests
        # (uvicorn can handle requests concurrently even in a single
        # worker via async), preventing interleaved/corrupted JSON lines.
        with self._lock:
            try:
                with self._path.open("a") as f:
                    f.write(json.dumps(record) + "\n")
            except OSError as e:
                # Never let logging failures break a prediction response.
                logger.error("failed to log prediction", extra={"error": str(e)})