"""
Application configuration.

All configuration for the model server is defined here as a single,
typed Settings object, sourced from environment variables (or a local
.env file during development — see .env.example).

No other module should read os.environ directly. If a new piece of
config is needed, add a field here first.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed, validated application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unrelated env vars present in the environment
    )

    # --- Server ---
    model_server_port: int = 8001

    # --- Model identity ---
    # Human-readable label for this running instance (e.g. "stable", "canary").
    # Not used for routing logic here — the model server itself is
    # canary-agnostic per ADR-0002. This exists so predictions can be
    # tagged with which instance produced them, once prediction logging
    # is built (see ADR-0004).
    model_version_label: str = "stable"

    # --- Model loading ---
    # Local filesystem path to the model artifact this instance loads at
    # startup. Will be supplemented by an MLflow registry URI in a later
    # step (see models/loader.py once it exists).
    model_path: str = "./artifacts/model.joblib"

    # --- Logging ---
    log_level: str = "INFO"

    prediction_log_path: str = "./logs/predictions.jsonl"

@lru_cache
def get_settings() -> Settings:
    """
    Return the cached Settings instance.

    Using lru_cache ensures environment variables are read and validated
    exactly once per process, and every caller across the app shares the
    same Settings object. This also makes Settings injectable via
    FastAPI's Depends() mechanism, which we'll use once routes exist —
    tests can then override this dependency without touching real
    environment variables.
    """
    return Settings()