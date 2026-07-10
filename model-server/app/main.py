"""
FastAPI application entrypoint.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.deps import get_inference_service
from app.api.routes import health, predict
from app.core.config import get_settings
from prometheus_client import make_asgi_app
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("starting up", extra={"model_version_label": settings.model_version_label})

    get_inference_service()  # forces model load now, not on first request

    yield

    logger.info("shutting down")


app = FastAPI(title="model-server", lifespan=lifespan)

app.include_router(health.router)
app.include_router(predict.router)
app.mount("/metrics", make_asgi_app())