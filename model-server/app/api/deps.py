"""
FastAPI dependency providers. Routes should get everything (settings,
services) through these, never by constructing objects inline.
"""

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.models.loader import LocalFileModelLoader
from app.services.inference import InferenceService


@lru_cache
def get_inference_service() -> InferenceService:
    settings: Settings = get_settings()
    loader = LocalFileModelLoader(model_path=settings.model_path)
    return InferenceService(loader=loader, model_version_label=settings.model_version_label)