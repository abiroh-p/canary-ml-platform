from app.api.deps import get_inference_service


def test_predict_returns_valid_response():
    service = get_inference_service()
    from app.schemas.prediction import PredictionRequest

    response = service.predict(PredictionRequest(features=[1.0, 2.0, 3.0, 4.0, 5.0]))

    assert isinstance(response.prediction, float)
    assert response.model_version_label == "stable"
    assert response.latency_ms > 0