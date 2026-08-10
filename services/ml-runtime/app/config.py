from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def default_model_dir() -> Path:
    """Locate repository models locally and `/app/models` in the container."""
    config_file = Path(__file__).resolve()
    if len(config_file.parents) > 3:
        return config_file.parents[3] / "models"
    return config_file.parents[1] / "models"


class Settings(BaseSettings):
    """Configuration for the isolated inference service."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    model_dir: Path = Field(default_factory=default_model_dir)
    temp_dir: Path = Path("/tmp/scamsigurado-ml")
    max_upload_bytes: int = 10 * 1024 * 1024
    max_image_pixels: int = 25_000_000
    default_text_model: str = "rf"
    default_image_model: str = "vggnet"
    default_text_weight: float = 0.7
    default_image_weight: float = 0.3
    model_version: str = "model-set-1-training-aligned-v2"


@lru_cache
def get_settings() -> Settings:
    return Settings()
