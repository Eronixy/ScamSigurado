import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.v1.routes import router as v1_router
from app.config import get_settings
from app.db import create_database_engine, create_session_factory
from app.services.ml_runtime import MLRuntimeClient
from app.storage import EphemeralUploadStore


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="ScamSigurado Application API",
        version="0.1.0",
        docs_url="/docs" if settings.app_env != "production" else None,
        redoc_url=None,
    )
    application.state.settings = settings
    application.state.engine = create_database_engine(settings)
    application.state.session_factory = create_session_factory(application.state.engine)
    application.state.upload_store = EphemeralUploadStore(settings)
    application.state.ml_runtime_client = MLRuntimeClient(settings)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_web_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )

    @application.middleware("http")
    async def add_request_id(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        return response

    application.include_router(router)
    application.include_router(v1_router)
    return application


app = create_app()
