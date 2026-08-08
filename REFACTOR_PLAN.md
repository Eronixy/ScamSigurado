# ScamSigurado Refactor Plan

## Intent

Replace the legacy all-in-one Flask/Jinja application incrementally. The
project will become a focused screenshot scam-checking product with a Next.js
frontend, a FastAPI application API, PostgreSQL, and an independently deployed
ML runtime.

This plan deliberately does **not** include baseline tests or strict output
parity with the legacy detector. Its quality bar is the new product flow,
validation, reliability boundaries, and clear user-facing results.

## Target Layout

```text
apps/
  web/                         # Next.js UI
  api/                         # Public FastAPI API
services/
  ml-runtime/                  # Private FastAPI inference service
packages/
  contracts/                   # Generated/shared API types, if useful
docker-compose.yml             # Local integration environment
```

The current empty `apps/api/web/` folder is not the desired web-app location;
the frontend belongs at `apps/web/`. It can be removed when the scaffold is
normalized without touching the legacy application.

## Stage 1 — Establish the New Service Foundations

**Status: complete (local Docker verification deferred because Docker is not
installed in this workspace).**

**Goal:** Make the new structure runnable without changing the user-facing
legacy application.

- Add `pyproject.toml` and `uv.lock` for `apps/api` and `services/ml-runtime`.
- Add minimal FastAPI applications with `/health` and `/ready` endpoints.
- Add configuration classes and environment examples. Secrets must stay out of
  source control.
- Create the Next.js TypeScript/Tailwind app in `apps/web/`.
- Add initial local Docker Compose service definitions, but do not include
  cloud credentials or deployment actions.

**Acceptance:** Each new service can start independently and reports healthy.

**Decision recorded:** Use `pnpm` for the Next.js app. The local environment
must provide Node.js 20.9+ and Corepack/pnpm before the frontend can be built.

## Stage 2 — Extract and Expose ML Inference

**Status: complete.**

**Goal:** Make the detector available as a private HTTP service.

- Move model registry/loading, OCR/text processing, image processing,
  heuristics, and Grad-CAM into focused ML-runtime modules.
- Load models at FastAPI lifespan startup; expose model/runtime readiness
  separately from simple liveness.
- Create `POST /internal/v1/analyze` with Pydantic request/response schemas.
- Start synchronously: receive an image and return the completed result.
- Retain explanation artifacts only where they are useful to the intended
  results experience; do not return large base64 images as a long-term API
  format.
- Validate uploads and clean temporary files safely.

**Acceptance:** A manual request to the private endpoint produces a valid
analysis result and leaves no unexpected temporary files.

**Overseer decision:** Confirm which result explanations remain visible:
flagged phrases/URLs only (recommended), or also image/Grad-CAM artifacts.

**Current default:** The runtime returns extracted text, flagged URLs/keywords,
and feature signals. Grad-CAM is retained as an internal artifact generator but
is not included in the HTTP response or new UI scope.

## Stage 3 — Build the Application API and PostgreSQL Persistence

**Status: complete (local PostgreSQL integration requires Docker or a running
PostgreSQL instance).**

**Goal:** Introduce the durable public application boundary.

- Add PostgreSQL configuration, SQLAlchemy models, and Alembic migrations.
- Store analyses, feedback, reports, timestamps, result status, model version,
  and artifact references in PostgreSQL.
- Add storage abstraction: local development storage first, cloud object
  storage implementation when a provider is selected.
- Implement public endpoints:
  - `POST /v1/analyses`
  - `GET /v1/analyses/{analysis_id}`
  - `POST /v1/feedback`
  - `POST /v1/reports`
- Have the API call the ML runtime through private networking/configuration.
- Add CORS rules for the Next.js origin and basic request/error logging.

**Acceptance:** Upload → API → ML runtime → saved PostgreSQL analysis →
retrieved result works locally.

**Decision recorded:** The first release permits anonymous analyses. Source
screenshots are processed ephemerally and deleted after the ML call. Result
records are available for 30 days by default; set `RESULT_RETENTION_DAYS` to
change that policy.

## Stage 4 — Rebuild the UI as a Focused Next.js Flow

**Status: complete.**

**Goal:** Replace the cluttered multi-page Jinja UI with a small, clear flow.

- Build a landing/upload screen, upload/analysis progress state, and results
  page keyed by an analysis ID.
- Present plain-language assessment, confidence, detected signals, safety
  recommendations, and optional feedback.
- Move language/theme only if they remain product requirements; do not recreate
  the legacy settings page by default.
- Remove the legacy Learn page, public aggregate stats, model controls, and
  technical metrics from the new navigation.
- Use generated API types or a maintained typed client based on the FastAPI
  OpenAPI schema.

**Acceptance:** A user can complete the entire core flow without using Flask
pages, browser session storage for result transfer, or knowledge of models.

**Overseer decision:** Review the new information architecture and result copy
before the UI replaces the legacy experience.

## Stage 5 — Integrate and Containerize Locally

**Goal:** Make the replacement system reproducible on a developer machine.

- Finalize Dockerfiles for web, API, and ML runtime.
- Run web, API, ML runtime, PostgreSQL, and any selected local storage service
  through Docker Compose.
- Ensure the API and ML runtime do not expose unnecessary public ports in the
  production-oriented configuration.
- Document setup, environment variables, migration commands, and manual smoke
  checks using `uv`.

**Acceptance:** A clean local setup can start the whole stack and complete a
manual upload-to-result flow.

## Stage 6 — Cloud Readiness and Deployment

**Goal:** Prepare a safe, economical cloud deployment after a provider is
chosen.

- Host Next.js on a CDN/managed web platform.
- Deploy API and ML runtime as separately scalable containers; keep the ML
  service private.
- Use managed PostgreSQL and object storage; configure backups and retention.
- Add secrets management, request IDs, rate limits, monitoring/error tracking,
  and CI checks for builds and migrations.
- Add Redis-backed asynchronous jobs and progress events only if synchronous
  analysis latency makes them necessary.

**Acceptance:** Staging deployment has private ML networking, managed data
services, health checks, and documented rollback steps.

**Overseer decision:** Select cloud provider, deployment regions, budget,
domain, and data/privacy requirements before any external deployment.

## Stage 7 — Retire the Legacy Application

**Goal:** Remove obsolete Flask/Jinja implementation only after acceptance.

- Confirm feature and data migration is complete.
- Archive or remove unused templates, static scripts, legacy Docker/Procfile,
  and legacy dependencies in a deliberate final change.
- Update the README to describe only the supported architecture.

**Acceptance:** The new stack is the sole documented and running application;
the legacy code is removed only with overseer approval.
