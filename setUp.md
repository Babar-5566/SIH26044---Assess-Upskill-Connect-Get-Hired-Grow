# SkillBridge AI Backend Setup

Ei guide-ta Phase 8 backend foundation ebong Phase 9 student module run korar jonno.

## Requirements

- Python 3.11+
- PostgreSQL 16 locally or a managed PostgreSQL instance

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

Docker is not required. Install PostgreSQL 16 locally or use a managed PostgreSQL service. Create a `skillbridge` database and set `DATABASE_URL` in `.env`.

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

Create a separate PostgreSQL database named `skillbridge_test`, then run:

```powershell
pytest -q
```

## Resume Storage

Resume binary data is stored in PostgreSQL in the `student_documents.file_data` column. Allowed extensions are `pdf`, `doc`, and `docx`. Maximum size is controlled by `MAX_RESUME_SIZE_MB`.
