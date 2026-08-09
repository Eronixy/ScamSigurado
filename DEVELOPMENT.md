# Development Setup

The legacy Flask application remains available while the replacement services
are built. The commands below apply to the new architecture only.

## Prerequisites

- Python 3.11
- [uv](https://docs.astral.sh/uv/)
- Node.js 20.9 or newer and Corepack/pnpm (Node.js 24 LTS was used for the
  current web build)
- Docker Desktop or Docker Engine for the complete local stack
- Tesseract OCR for running the ML service outside Docker

## Run the Services Individually

Application API:

```bash
cd apps/api
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

ML runtime:

```bash
cd services/ml-runtime
uv sync
uv run uvicorn app.main:app --reload --port 8001
```

The ML runtime reads the existing repository `models/` directory by default.
Set `ML_MODEL_DIR` if models are stored elsewhere. Its internal endpoints are
available under `/internal/v1`; do not expose that service directly in a cloud
deployment.

Web scaffold:

```bash
cd apps/web
pnpm install --frozen-lockfile
pnpm dev
```

The web app submits to `NEXT_PUBLIC_API_URL` (default: `http://localhost:8000`)
and redirects to a result URL after a successful analysis. For the complete
upload-to-result flow, run PostgreSQL, the API, and ML runtime as well; Docker
Compose is the simplest option.

The API permits `http://localhost:3000` and `http://localhost:3001` by default.
Set `WEB_ORIGINS` to a comma-separated list when your frontend runs elsewhere.

When Docker starts the complete stack, the API waits for the ML runtime's
readiness check before becoming available. The ML runtime can take a short time
to load its models on the first start.

## Run the Local Stack

```bash
docker compose up --build
```

The Compose file provides the web app on port 3000, the public API on port
8000, PostgreSQL on port 5432, and an internal-only ML runtime. PostgreSQL is
included now for the Stage 3 schema and migration work; the API does not yet
persist data to it.

## Current Validation

The new API and ML runtime both expose `/health` and `/ready`. The ML endpoint
is `POST /internal/v1/analyze` and accepts a PNG or JPEG multipart field named
`file`. It validates file type, content, byte size, and image dimensions before
creating a UUID-based temporary file.

The public API stores completed analysis results for 30 days by default but
does not persist source screenshots. Set `RESULT_RETENTION_DAYS` to change the
result window. PostgreSQL schema changes are applied with:

```bash
cd apps/api
uv run alembic upgrade head
```

Once PostgreSQL and the ML runtime are running, submit a screenshot through the
public API rather than calling the ML service directly:

```bash
curl -F "file=@/absolute/path/to/screenshot.png" \
  http://localhost:8000/v1/analyses
```

Retrieve that result with `GET /v1/analyses/{analysis_id}`. The FastAPI docs at
`http://localhost:8000/docs` also describe feedback and scam-report endpoints.
