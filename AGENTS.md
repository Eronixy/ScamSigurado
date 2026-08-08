# ScamSigurado Refactor Guidance

## Objective

Refactor the legacy Flask application into a small Next.js product UI, a public
FastAPI application API, and a private FastAPI ML runtime. PostgreSQL is the
system of record for application data. The ML runtime is deployed separately
from the UI and application API.

The user is the project overseer. Before beginning a new stage, report the
scope, the files expected to change, and any decision that would materially
change the product. Keep each stage independently runnable before continuing.

The detailed sequence and acceptance criteria live in `REFACTOR_PLAN.md`.

## Architecture Boundaries

- `apps/web/`: Next.js + TypeScript user interface. It calls public API
  endpoints only. It must not include model files, TensorFlow, OpenCV, or
  Tesseract.
- `apps/api/`: FastAPI application API. It validates requests, manages
  application data, accesses PostgreSQL and artifact storage, and calls the ML
  runtime through its private HTTP API.
- `services/ml-runtime/`: FastAPI inference service. It owns model loading,
  OCR, image/text inference, and optional explanation artifacts. It has no
  public ingress and does not write application records to PostgreSQL.
- PostgreSQL stores durable application records, not uploads, generated images,
  or ML model files.
- Object storage stores uploads and generated artifacts when cloud storage is
  introduced. Local development may use a replaceable local-storage adapter.

## Product Scope for the First Release

Keep the UI focused on one task: upload a screenshot and receive a clear scam
assessment.

- Keep: upload, analysis status, result, practical safety guidance, optional
  feedback.
- Remove from the new UI: public accuracy/scan/protected statistics, the Learn
  page, public model selectors/weights, and technical model details by default.
- Do not migrate a legacy page or feature merely because it exists. Confirm its
  user value first.
- Treat model selection and weighting as server configuration, not public UI
  controls.

## Engineering Rules

- Do not create baseline tests for the legacy engine and do not aim for exact
  behavioral parity with it. The legacy implementation is reference material,
  not a quality target.
- Do perform focused validation for new code: type/lint checks where configured,
  API schema validation, manual smoke flows, and service health checks.
- Keep the legacy Flask app available until the replacement flow is accepted.
  Do not delete or overwrite it as part of scaffolding work.
- Preserve unrelated working-tree changes, especially `templates/upload.html`,
  unless the user explicitly includes them in a task.
- Use UUID-controlled names for uploads; never trust a client filename as a
  storage path. Validate file size, type, image contents, and dimensions.
- Load ML models once at runtime startup. Run one ML worker initially because
  every worker can load a separate copy of the model set.
- Never use process-local queues for durable jobs or cross-container progress.
  Start with synchronous analysis; add Redis-backed jobs only when needed.
- Keep the ML runtime private. Only the application API may call it.
- Use `uv` and a `pyproject.toml` for each Python deployable service. The
  Next.js app uses the Node package manager selected for that app.
- Add migrations for every PostgreSQL schema change; do not rely on ad-hoc
  table creation in production.

## Completion Standards

At the end of each stage, report:

1. What changed and why.
2. Commands or manual flows used to verify it.
3. Known limitations and the proposed next stage.
4. Any decision requiring the overseer's approval.
