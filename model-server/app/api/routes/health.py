from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.prediction import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(model_version_label=settings.model_version_label)