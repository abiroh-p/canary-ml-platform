from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    eval_interval_seconds: int = 30
    gateway_admin_url: str = "http://localhost:8081"
    promote_psi_threshold: float = 0.1
    rollback_psi_threshold: float = 0.25
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()