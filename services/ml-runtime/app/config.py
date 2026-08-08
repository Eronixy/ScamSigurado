from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the isolated inference service."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    model_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[3] / "models"
    )
    temp_dir: Path = Path("/tmp/scamsigurado-ml")
    max_upload_bytes: int = 10 * 1024 * 1024
    max_image_pixels: int = 25_000_000
    default_text_model: str = "svm"
    default_image_model: str = "efficientnet"
    default_text_weight: float = 0.6
    default_image_weight: float = 0.4
    model_version: str = "legacy-model-set-1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
