"""Eval engine entrypoint: runs the evaluation loop on a fixed interval."""

import logging
import time

from app.clients.gateway_client import GatewayClient
from app.clients.metrics_client import ModelMetrics, StubMetricsClient
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.models.decision import log_decision
from app.policy.evaluator import Decision, Evaluator

logger = logging.getLogger(__name__)


def build_evaluator(settings) -> Evaluator:
    # TODO: replace StubMetricsClient with a real PrometheusMetricsClient
    # once monitoring/ is built.
    if settings.eval_stub_scenario == "degraded":
        canary_metrics = ModelMetrics(
            p99_latency_ms=55.0,
            error_rate=0.15,  # exceeds max_error_rate (0.05) -> forces rollback
            prediction_scores=[0.12] * 100,
        )
    else:
        canary_metrics = ModelMetrics(p99_latency_ms=55.0, error_rate=0.01, prediction_scores=[0.12] * 100)

    stub = StubMetricsClient({
        "stable": ModelMetrics(p99_latency_ms=50.0, error_rate=0.01, prediction_scores=[0.1] * 100),
        "canary": canary_metrics,
    })
    return Evaluator(
        metrics_client=stub,
        promote_psi_threshold=settings.promote_psi_threshold,
        rollback_psi_threshold=settings.rollback_psi_threshold,
        max_latency_ratio=settings.max_latency_ratio,
        max_error_rate=settings.max_error_rate,
    )


def apply_decision(gateway: GatewayClient, decision: Decision, step: int) -> tuple[int, int]:
    before = gateway.get_canary_weight()

    if decision == Decision.PROMOTE:
        after = min(before + step, 100)
    elif decision == Decision.ROLLBACK:
        after = 0
    else:
        after = before

    if after != before:
        gateway.set_canary_weight(after)

    return before, after


def run_loop() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    gateway = GatewayClient(settings.gateway_admin_url)
    evaluator = build_evaluator(settings)

    logger.info("eval engine started", extra={"interval_seconds": settings.eval_interval_seconds})

    while True:
        result = evaluator.evaluate()
        before, after = apply_decision(gateway, result.decision, settings.canary_step_percent)
        log_decision(settings.decision_log_path, result, before, after)

        logger.info("cycle complete", extra={"canary_weight_before": before, "canary_weight_after": after})
        time.sleep(settings.eval_interval_seconds)


if __name__ == "__main__":
    run_loop()