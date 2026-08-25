# Phase 0: Integration Foundation

This repository is being integrated from the `NIRUPAM-PAL`, `ibran`, and `justin`
branches. Phase 0 establishes the target layout and operational conventions only.

## Target layout

- `backend/`: canonical Python/FastAPI application (added in later phases)
- `frontend/`: canonical React application (added in later phases)
- `database/`: database documentation and supporting assets
- `docs/`: architecture, API, audit, AI, and phase documentation

## Runtime conventions

- Backend default URL: `http://localhost:8000`
- Frontend default URL: `http://localhost:5173`
- Secrets are supplied through untracked `.env` files.
- PostgreSQL schema changes will use Alembic once the canonical backend is imported.
- Phase 0 deliberately contains no application models, routes, migrations, or feature code.

## Branch preservation

The source branches remain available as remote-tracking refs. Integration will use
selective file/commit transplantation in later phases rather than whole-branch merges.
