import logging
import tempfile
import uuid
from io import BytesIO
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from app.config import Settings
from app.inference.detector import AnalysisOptions, ScamDetector
from app.inference.model_loader import ModelRegistry, ModelUnavailableError
from app.schemas import AnalysisResponse, RuntimeStatus

logger = logging.getLogger(__name__)
router = APIRouter(tags=["runtime"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
ALLOWED_FORMATS = {"JPEG": ".jpg", "PNG": ".png"}


def _runtime_status(request: Request) -> RuntimeStatus:
    settings: Settings = request.app.state.settings
    registry: ModelRegistry = request.app.state.model_registry
    return RuntimeStatus(
        status="ok" if registry.is_ready else "not_ready",
        model_version=settings.model_version,
        available_text_models=sorted(registry.text_models),
        available_image_models=sorted(registry.image_models),
    )


@router.get("/health", response_model=RuntimeStatus)
def health(request: Request) -> RuntimeStatus:
    """Liveness endpoint; a model-loading problem does not make the process dead."""
    return _runtime_status(request)


@router.get("/ready", response_model=RuntimeStatus)
def ready(request: Request):
    """Readiness endpoint; it requires a vectorizer plus text and image models."""
    response = _runtime_status(request)
    if response.status == "ok":
        return response
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=response.model_dump())


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    request: Request,
    file: Annotated[UploadFile, File(description="PNG or JPEG screenshot")],
    text_model: Annotated[str | None, Form()] = None,
    image_model: Annotated[str | None, Form()] = None,
    text_weight: Annotated[float | None, Form()] = None,
    image_weight: Annotated[float | None, Form()] = None,
) -> AnalysisResponse:
    """Analyze one screenshot synchronously for use by the application API."""
    settings: Settings = request.app.state.settings
    registry: ModelRegistry = request.app.state.model_registry
    if not registry.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The ML runtime is not ready",
        )

    temporary_path = await _persist_validated_upload(file, settings)
    try:
        options = AnalysisOptions(
            text_model=text_model or settings.default_text_model,
            image_model=image_model or settings.default_image_model,
            text_weight=text_weight if text_weight is not None else settings.default_text_weight,
            image_weight=image_weight if image_weight is not None else settings.default_image_weight,
        )
        result = ScamDetector(registry).analyze(temporary_path, options)
        return AnalysisResponse(**result, model_version=settings.model_version)
    except (ModelUnavailableError, ValueError) as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
    except HTTPException:
        raise
    except Exception as error:  # pragma: no cover - depends on model/runtime failures
        logger.exception("Screenshot analysis failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Screenshot analysis failed",
        ) from error
    finally:
        temporary_path.unlink(missing_ok=True)


async def _persist_validated_upload(file: UploadFile, settings: Settings) -> Path:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PNG and JPEG screenshots are accepted",
        )

    payload = await file.read(settings.max_upload_bytes + 1)
    if len(payload) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The screenshot exceeds the upload size limit",
        )
    if not payload:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="The upload is empty")

    try:
        Image.MAX_IMAGE_PIXELS = settings.max_image_pixels
        with Image.open(BytesIO(payload)) as image:
            image.verify()
        with Image.open(BytesIO(payload)) as image:
            if image.width * image.height > settings.max_image_pixels:
                raise ValueError("The screenshot dimensions are too large")
            suffix = ALLOWED_FORMATS.get(image.format)
    except (UnidentifiedImageError, ValueError, OSError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The upload is not a valid PNG or JPEG screenshot",
        ) from error

    if suffix is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PNG and JPEG screenshots are accepted",
        )

    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}{suffix}"
    path = settings.temp_dir / filename
    path.write_bytes(payload)
    return path
