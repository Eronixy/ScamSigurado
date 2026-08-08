import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.config import Settings, get_settings
from app.inference.model_loader import ModelRegistry


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings: Settings = application.state.settings
    registry = ModelRegistry(settings.model_dir)
    registry.load()
    application.state.model_registry = registry
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=logging.INFO)
    application = FastAPI(
        title="ScamSigurado ML Runtime",
        version="0.1.0",
        docs_url="/docs" if settings.app_env != "production" else None,
        redoc_url=None,
        lifespan=lifespan,
    )
    application.state.settings = settings
    application.include_router(router, prefix="/internal/v1")
    return application


app = create_app()
