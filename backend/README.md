# Backend

This directory contains the canonical FastAPI application. Run Python commands
here, not from the repository root, which still contains a legacy `app/` package.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Copy the example only on initial setup; preserve an existing `.env`. Set the database
URL and a generated secret. Provider key names are documented in `.env.example`.

```powershell
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API is at `/api/v1`, with Swagger documentation at `/docs`. All AI assistant
routes require a bearer token obtained from the existing login endpoint.

```powershell
python -m pytest -q
```

Tests isolate document/vector storage and disable live provider credentials before
loading the app. They do not require the local PostgreSQL database or incur AI usage.

Use one backend worker with the local NumPy index. For deployment, set
`ENVIRONMENT=production`, `DEBUG=false`, use a generated secret of at least 32
characters, and persist document/index directories. See
[the audit report](../docs/AI_ASSISTANT_AUDIT.md) for upgrade and production limits.
