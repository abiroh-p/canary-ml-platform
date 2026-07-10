from fastapi import APIRouter, Depends

from app.api.deps import get_inference_service
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.inference import InferenceService

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict(
    request: PredictionRequest,
    service: InferenceService = Depends(get_inference_service),
) -> PredictionResponse:
    return service.predict(request)