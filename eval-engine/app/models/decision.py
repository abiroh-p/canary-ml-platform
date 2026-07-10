"""Appends each evaluation decision as a JSON line for audit purposes."""

import json
from datetime import datetime, timezone
from pathlib import Path

from app.policy.evaluator import EvaluationResult


def log_decision(path: str, result: EvaluationResult, canary_weight_before: int, canary_weight_after: int) -> None:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decision": result.decision.value,
        "reason": result.reason,
        "psi": result.psi,
        "stable_p99_latency_ms": result.stable_p99_latency_ms,
        "canary_p99_latency_ms": result.canary_p99_latency_ms,
        "canary_error_rate": result.canary_error_rate,
        "canary_weight_before": canary_weight_before,
        "canary_weight_after": canary_weight_after,
    }
    with Path(path).open("a") as f:
        f.write(json.dumps(record) + "\n")