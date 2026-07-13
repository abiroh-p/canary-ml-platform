"""
Promote/hold/rollback decision policy. Combines PSI drift with latency
and error-rate checks against the stable baseline.
"""

import logging
from dataclasses import dataclass
from enum import Enum

from app.clients.metrics_client import MetricsClient
from app.policy.psi import calculate_psi

logger = logging.getLogger(__name__)


class Decision(str, Enum):
    PROMOTE = "promote"
    HOLD = "hold"
    ROLLBACK = "rollback"


@dataclass
class EvaluationResult:
    decision: Decision
    psi: float
    stable_p99_latency_ms: float
    canary_p99_latency_ms: float
    canary_error_rate: float
    reason: str


class Evaluator:
    def __init__(
        self,
        metrics_client: MetricsClient,
        promote_psi_threshold: float,
        rollback_psi_threshold: float,
        max_latency_ratio: float = 1.5,
        max_error_rate: float = 0.05,
    ) -> None:
        self._metrics_client = metrics_client
        self._promote_psi_threshold = promote_psi_threshold
        self._rollback_psi_threshold = rollback_psi_threshold
        self._max_latency_ratio = max_latency_ratio
        self._max_error_rate = max_error_rate

    def evaluate(self) -> EvaluationResult:
        stable = self._metrics_client.get_metrics("stable")
        canary = self._metrics_client.get_metrics("canary")

        if not stable.prediction_scores or not canary.prediction_scores:
            logger.warning(
                "insufficient prediction data for PSI, holding",
                extra={
                    "stable_count": len(stable.prediction_scores),
                    "canary_count": len(canary.prediction_scores),
                },
            )
            return EvaluationResult(
                decision=Decision.HOLD,
                psi=0.0,
                stable_p99_latency_ms=stable.p99_latency_ms,
                canary_p99_latency_ms=canary.p99_latency_ms,
                canary_error_rate=canary.error_rate,
                reason="insufficient prediction data for PSI",
            )

        psi = calculate_psi(stable.prediction_scores, canary.prediction_scores)
        latency_ratio = canary.p99_latency_ms / max(stable.p99_latency_ms, 1e-6)

        if canary.error_rate > self._max_error_rate:
            decision, reason = Decision.ROLLBACK, f"error_rate {canary.error_rate} exceeds max {self._max_error_rate}"
        elif latency_ratio > self._max_latency_ratio:
            decision, reason = Decision.ROLLBACK, f"latency_ratio {latency_ratio:.2f} exceeds max {self._max_latency_ratio}"
        elif psi > self._rollback_psi_threshold:
            decision, reason = Decision.ROLLBACK, f"psi {psi:.4f} exceeds rollback threshold {self._rollback_psi_threshold}"
        elif psi > self._promote_psi_threshold:
            decision, reason = Decision.HOLD, f"psi {psi:.4f} between promote and rollback thresholds"
        else:
            decision, reason = Decision.PROMOTE, f"psi {psi:.4f} below promote threshold {self._promote_psi_threshold}"

        logger.info("evaluation complete", extra={
            "decision": decision.value, "psi": psi, "latency_ratio": latency_ratio,
            "canary_error_rate": canary.error_rate, "reason": reason,
        })

        return EvaluationResult(
            decision=decision, psi=psi,
            stable_p99_latency_ms=stable.p99_latency_ms,
            canary_p99_latency_ms=canary.p99_latency_ms,
            canary_error_rate=canary.error_rate,
            reason=reason,
        )
