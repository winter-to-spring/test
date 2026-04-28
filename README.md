# test
## Scaffolds (skeleton files for Phase 1 mission)

The following file paths are pre-created as placeholders. The Phase 1 autopilot
mission should FILL IN their content rather than re-create the files:

- service-backend/pyproject.toml
- service-backend/Dockerfile
- service-backend/.env.example
- service-backend/app/__init__.py
- service-frontend/package.json
- service-frontend/tsconfig.json
- service-frontend/Dockerfile
- service-frontend/next.config.mjs
- service-frontend/postcss.config.mjs
- infra/docker-compose.yml
- scripts/seed_slack.sh

Tasks the mission still creates net-new (under their respective paths):
- service-backend/app/main.py (FastAPI app)
- service-backend/app/db.py (SQLAlchemy session)
- service-backend/app/models.py (Notification model)
- service-backend/app/slack_verify.py (signature verifier)
- service-backend/tests/test_*.py (pytest)
- service-frontend/src/app/dashboard/page.tsx + supporting components

## Phase 2 scaffolds (added 2026-04-29)

Phase 2 (AI triage + worker + SSE) extends Phase 1 with:

- service-backend/app/services/triage_graph.py
- service-backend/app/worker/__init__.py
- service-backend/app/worker/main.py
- service-backend/migrations/001_add_triage_columns.sql

Phase 2 also creates net-new (no skeleton):
- service-backend/app/services/__init__.py
- service-backend/app/sse.py (SSE endpoint)
- Tests for classify / summarize / worker E2E / SSE
