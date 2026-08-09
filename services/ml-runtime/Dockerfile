FROM ghcr.io/astral-sh/uv:0.12.3 AS uv

FROM python:3.11-slim

COPY --from=uv /uv /uvx /bin/
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY services/ml-runtime/pyproject.toml services/ml-runtime/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY services/ml-runtime/app ./app
COPY models ./models

ENV PATH="/app/.venv/bin:$PATH" \
    TF_CPP_MIN_LOG_LEVEL=2 \
    ML_MODEL_DIR=/app/models
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
