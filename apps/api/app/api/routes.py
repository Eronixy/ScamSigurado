from sqlalchemy import text
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.schemas import ServiceStatus

router = APIRouter(tags=["service"])


def _status(request: Request) -> ServiceStatus:
    settings = request.app.state.settings
    return ServiceStatus(
        status="ok",
        service="scamsigurado-api",
        environment=settings.app_env,
    )


@router.get("/health", response_model=ServiceStatus)
def health(request: Request) -> ServiceStatus:
    """Liveness endpoint; it has no dependency on PostgreSQL yet."""
    return _status(request)


@router.get("/ready", response_model=ServiceStatus)
def ready(request: Request) -> ServiceStatus:
    """Readiness endpoint; verifies that PostgreSQL can accept a query."""
    try:
        with request.app.state.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        response = _status(request)
        return JSONResponse(status_code=503, content={**response.model_dump(), "status": "not_ready"})
    return _status(request)
