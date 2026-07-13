from fastapi import APIRouter, Depends

from app.api.deps import get_inference_service
from app.services.inference import InferenceService

router = APIRouter()


@router.get("/predictions/recent")
def recent_predictions(service: InferenceService = Depends(get_inference_service)) -> dict:
    return {"prediction_scores": service.prediction_logger.get_recent()}