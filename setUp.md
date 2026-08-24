# SkillBridge AI Backend Setup

Ei guide-ta Phase 8 backend foundation ebong Phase 9 student module run korar jonno.

## Requirements

- Python 3.11+
- Docker Desktop
- Docker Compose

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Jodi PowerShell activation block kore:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Start PostgreSQL

```powershell
docker compose up -d
docker ps
```

Local database: `localhost:5432`, database `skillbridge`, user `skillbridge`, password `skillbridge`.

## Migrations and Seed

```powershell
alembic upgrade head
python -m app.scripts.seed
```

Model change korle:

```powershell
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

Demo accounts:

- Admin: `admin@example.com` / `Admin@123`
- Student: `student@example.com` / `Student@123`

## Run API

```powershell
uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000/api/v1`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health: `http://127.0.0.1:8000/api/v1/health`

## Test Database and Tests

```powershell
docker exec -it skillbridge-postgres psql -U skillbridge -c "CREATE DATABASE skillbridge_test;"
pytest -q
```

## Resume Storage

Resume files are stored at `storage/resumes/{student_id}/{uuid}.{extension}`. Allowed extensions are `pdf`, `doc`, and `docx`. Maximum size is controlled by `MAX_RESUME_SIZE_MB`.

## Stop Services

```powershell
docker compose down
```

`docker compose down -v` also deletes the local PostgreSQL volume and its data.
