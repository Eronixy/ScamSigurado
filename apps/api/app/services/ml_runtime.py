from pathlib import Path
from typing import Any

import httpx

from app.config import Settings


class MLRuntimeUnavailableError(RuntimeError):
    """Raised when the private ML service cannot complete an analysis."""


class MLRuntimeRequestError(RuntimeError):
    """Raised when the ML service rejects a client upload."""


class MLRuntimeClient:
    def __init__(self, settings: Settings):
        self.base_url = settings.ml_runtime_url.rstrip("/")
        self.timeout = settings.ml_runtime_timeout_seconds

    def analyze(
        self, upload_path: Path, content_type: str | None, options: dict[str, Any]
    ) -> dict[str, Any]:
        headers = {"content-type": content_type or "application/octet-stream"}
        try:
            with upload_path.open("rb") as uploaded_file:
                response = httpx.post(
                    f"{self.base_url}/internal/v1/analyze",
                    files={"file": ("screenshot", uploaded_file, headers["content-type"])},
                    data=options,
                    timeout=self.timeout,
                )
            if 400 <= response.status_code < 500:
                raise MLRuntimeRequestError("The screenshot could not be processed")
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise MLRuntimeUnavailableError("The ML runtime could not analyze the screenshot") from error
