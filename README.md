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
