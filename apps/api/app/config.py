from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the public API service."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = (
        "postgresql+psycopg://scamsigurado:scamsigurado@localhost:5432/scamsigurado"
    )
    ml_runtime_url: str = "http://localhost:8001"
    web_origins: str = "http://localhost:3000,http://localhost:3001"
    api_max_upload_bytes: int = 10 * 1024 * 1024
    api_temp_dir: Path = Path("/tmp/scamsigurado-api")
    ml_runtime_timeout_seconds: float = 90.0
    result_retention_days: int = 30

    @property
    def allowed_web_origins(self) -> list[str]:
        return [origin.strip() for origin in self.web_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
