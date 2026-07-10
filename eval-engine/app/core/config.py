from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    eval_interval_seconds: int = 30
    gateway_admin_url: str = "http://localhost:8081"
    promote_psi_threshold: float = 0.1
    rollback_psi_threshold: float = 0.25
    log_level: str = "INFO"
    max_latency_ratio: float = 1.5
    max_error_rate: float = 0.05
    canary_step_percent: int = 10
    eval_stub_scenario: str = "healthy"  # healthy | degraded
    decision_log_path: str = "./decisions.jsonl"


@lru_cache
def get_settings() -> Settings:
    return Settings()