import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import Settings


class EphemeralUploadStore:
    """Short-lived local storage behind the future object-storage boundary."""

    def __init__(self, settings: Settings):
        self.max_upload_bytes = settings.api_max_upload_bytes
        self.temp_dir = settings.api_temp_dir

    async def save(self, upload: UploadFile) -> Path:
        payload = await upload.read(self.max_upload_bytes + 1)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The upload is empty",
            )
        if len(payload) > self.max_upload_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="The screenshot exceeds the upload size limit",
            )

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        path = self.temp_dir / f"{uuid.uuid4()}.upload"
        path.write_bytes(payload)
        return path
