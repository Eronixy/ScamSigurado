# ScamSigurado

ScamSigurado is a multimodal scam-detection web application for uploaded
screenshots. It is intended to help users assess a screenshot,
not to replace careful judgment or report complex social-engineering attacks.

## Architecture

```text
Next.js web UI -> Public FastAPI API -> Private FastAPI ML runtime
                           |
                     PostgreSQL records
```

| Area            | Location              | Responsibility                                                 |
| --------------- | --------------------- | -------------------------------------------------------------- |
| Product UI      | `apps/web`            | Next.js App Router upload, crop, status, and result experience |
| Public API      | `apps/api`            | Upload validation, result records, and ML orchestration        |
| ML runtime      | `services/ml-runtime` | OCR plus text and image model inference                        |
| Model artifacts | `models`              | Versioned model files loaded only by the ML runtime            |
| Legacy archive  | `legacy`              | Original Flask implementation retained for reference only      |

The default analysis configuration is Random Forest for text, VGG16 for image
classification, and a 70% text / 30% image weighting.

## Prerequisites

- Node.js 20.9+ with Corepack/pnpm
- Python 3.11 and [uv](https://docs.astral.sh/uv/)
- Docker Desktop or Docker Engine for the complete local stack

Tesseract OCR is installed automatically in the ML Docker image. Install it
locally only when running the ML runtime outside Docker.

## Run locally

The fastest way to start the complete application is Docker Compose:

```bash
docker compose up --build
```

This starts:

- Web UI: `http://localhost:3000`
- Public API and API docs: `http://localhost:8000` and `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`
- Private ML runtime: available only to the API container

To stop the stack, press `Ctrl+C`. To run it in the background, use
`docker compose up -d --build`.

### Run services individually

```bash
# Terminal 1: public API
cd apps/api
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: ML runtime
cd services/ml-runtime
uv sync
uv run uvicorn app.main:app --reload --port 8001

# Terminal 3: web UI
cd apps/web
pnpm install --frozen-lockfile
pnpm dev
```

Copy each service's `.env.example` file when overriding defaults. Never commit
real database URLs or other secrets.

## Verify changes

```bash
cd apps/web && pnpm lint && pnpm build
UV_CACHE_DIR=/tmp/scamsigurado-uv-cache uv run --project apps/api python -m compileall app migrations
UV_CACHE_DIR=/tmp/scamsigurado-uv-cache uv run --project services/ml-runtime python -m compileall app
```

For a manual smoke test, open the web app, upload a PNG or JPEG screenshot,
crop it if needed, then wait for the result page. The public API validates the
file type, contents, size, and image dimensions before it calls the ML runtime.

## Deployment

The showcase deployment uses Vercel for the website, one AWS EC2 instance for
Caddy + FastAPI + the private ML runtime, and Amazon RDS PostgreSQL for durable
records:

```text
Browser -> Vercel HTTPS -> /api rewrite -> EC2 Caddy -> API -> ML runtime
                                                   -> RDS PostgreSQL
```

No purchased domain is required; Vercel provides a `*.vercel.app` URL. The
detailed beginner-friendly instructions are in [DEPLOYMENT.md](DEPLOYMENT.md).

## Authors

- Irron Jovic Jun V. Brosoto
- Jezrielle Anne G. Padlan
- Julia Kyla C. Rustia
- Catherine C. Tabigne

## Usage notice

This project is for academic and research purposes only. Commercial use is not
permitted without prior consent.
