# Legacy Flask Archive

This directory preserves the original Flask/Jinja implementation of
ScamSigurado for historical reference. It is not part of the current local or
production deployment path.

The active application is split into:

- `apps/web` — Next.js user interface
- `apps/api` — public FastAPI application API
- `services/ml-runtime` — private FastAPI inference service

Do not deploy `legacy/app.py`, its Dockerfile, or its Procfile alongside the
current services. The model files remain in the repository-level `models/`
directory because the current ML runtime loads them.
