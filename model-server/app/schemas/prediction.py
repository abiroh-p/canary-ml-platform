"""
Request/response contracts for the prediction API.

These schemas define the model server's external HTTP contract. They are
intentionally generic (a numeric feature vector in, a numeric prediction
out) rather than tied to any one model's named features — this service
is designed to serve whatever model is configured via Settings.model_path
(see core/config.py), including different models for stable vs. canary.
"""

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Input payload for a single prediction request."""

    features: list[float] = Field(
        ...,
        min_length=1,
        description="Numeric feature vector, in the order the loaded model expects.",
    )


class PredictionResponse(BaseModel):
    """Output payload for a single prediction."""

    prediction: float = Field(
        ...,
        description="The model's raw output for the given input.",
    )
    model_version_label: str = Field(
        ...,
        description=(
            "Which running instance produced this prediction (e.g. "
            "'stable' or 'canary'). Set from Settings.model_version_label."
        ),
    )
    latency_ms: float = Field(
        ...,
        description="Time taken to run inference, in milliseconds.",
    )


class HealthResponse(BaseModel):
    """Response for the /health endpoint."""

    status: str = Field(default="ok", description="Liveness/readiness status.")
    model_version_label: str = Field(
        ...,
        description="Which instance this health check is reporting for.",
    )