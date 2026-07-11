"""
Reads recent prediction scores from a model server's JSONL prediction
log (see model-server/app/services/prediction_logger.py).

Known limitation: assumes a shared filesystem between eval-engine and
model-server (true in this local/dev setup, not true once each runs in
its own container/pod — see Step 30 notes).
"""

import json
import logging
from collections import deque
from pathlib import Path

logger = logging.getLogger(__name__)


def read_recent_scores(log_path: str, max_lines: int = 500) -> list[float]:
    """Return up to the last max_lines prediction values from the log file."""
    path = Path(log_path)
    if not path.exists():
        logger.warning("prediction log not found", extra={"log_path": log_path})
        return []

    # deque with maxlen efficiently keeps only the last N lines while
    # reading the whole file once, without loading everything into a list.
    recent_lines = deque(maxlen=max_lines)
    with path.open() as f:
        for line in f:
            recent_lines.append(line)

    scores = []
    for line in recent_lines:
        try:
            record = json.loads(line)
            scores.append(float(record["prediction"]))
        except (json.JSONDecodeError, KeyError, ValueError):
            continue  # skip malformed lines rather than crash the whole read

    return scores