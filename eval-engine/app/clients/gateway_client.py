"""Client for the gateway's admin API (see gateway/internal/control)."""

import logging

import httpx

logger = logging.getLogger(__name__)


class GatewayClient:
    def __init__(self, admin_url: str) -> None:
        self._admin_url = admin_url.rstrip("/")

    def get_canary_weight(self) -> int:
        resp = httpx.get(f"{self._admin_url}/admin/traffic-split")
        resp.raise_for_status()
        return resp.json()["canary_weight"]

    def set_canary_weight(self, weight: int) -> None:
        resp = httpx.post(
            f"{self._admin_url}/admin/traffic-split",
            json={"canary_weight": weight},
        )
        resp.raise_for_status()
        logger.info("canary weight updated", extra={"canary_weight": weight})