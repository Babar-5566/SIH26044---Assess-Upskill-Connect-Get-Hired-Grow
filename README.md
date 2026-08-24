# SkillBridge AI Backend

FastAPI and PostgreSQL MVP backend for SkillBridge AI Phase 8 and Phase 9.

## Scope

Includes JWT authentication, bcrypt passwords, student profiles, skills, projects, certifications, achievements, internships, career interests, resumes, metadata, admin student views, Alembic migrations, seed data, Docker Compose, and tests.

Does not include AI recommendations, resume parsing, skill-gap analysis, employability prediction, matching, interviews, placement prediction, or analytics dashboards.

## Requirements

- Python 3.11+
- Docker Desktop with Docker Compose
- PostgreSQL 16 through Docker Compose

## Installation

Create a virtual environment, activate it, install dependencies, and copy the environment file:

`python -m venv .venv`

`.venv\Scripts\Activate.ps1`

`python -m pip install --upgrade pip`

`python -m pip install -r requirements.txt`

`Copy-Item .env.example .env`

If activation is blocked, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## Environment

`.env.example` contains local values for database URLs, JWT secret, token expiry, CORS, upload directory, and resume size. For production, set `DEBUG=false`, use a long random `SECRET_KEY`, secure database credentials, and restricted CORS origins.

## PostgreSQL

Start PostgreSQL with `docker compose up -d`. Check it with `docker ps` and `docker logs skillbridge-postgres`.

Local database: host `localhost`, port `5432`, database `skillbridge`, user `skillbridge`, password `skillbridge`.

## Migrations

Generate a migration with `alembic revision --autogenerate -m "phase 8 and phase 9 tables"`.

Apply migrations with `alembic upgrade head`.

Other commands: `alembic history` and `alembic downgrade -1`.

`alembic/env.py` reads settings, imports `app.models`, and uses `Base.metadata`.

## Seed Data

Run `python -m app.scripts.seed`.

Demo accounts:

- Admin: `admin@example.com` / `Admin@123`
- Student: `student@example.com` / `Student@123`

Use these credentials only for local development.

## Run the API

Run `uvicorn app.main:app --reload`.

- API: `http://127.0.0.1:8000/api/v1`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health: `http://127.0.0.1:8000/api/v1/health`

## Authentication

Register or log in to receive a JWT. Send it as `Authorization: Bearer <access_token>`.

Endpoints: `POST /api/v1/auth/register/student`, `POST /api/v1/auth/login`, and `GET /api/v1/auth/me`.

## Main API Areas

- Profile: `/api/v1/students/me`, `/completeness`, `/dashboard`
- Skills: `/api/v1/students/me/skills`
- Projects: `/api/v1/students/me/projects`
- Certifications: `/api/v1/students/me/certifications`
- Achievements: `/api/v1/students/me/achievements`
- Internships: `/api/v1/students/me/internships`
- Career interests: `/api/v1/students/me/career-interests`
- Resume: `/api/v1/students/me/resume`
- Metadata: `/api/v1/meta/skills`, `/api/v1/meta/career-roles`
- Admin: `/api/v1/admin/students`

## Response Format

Success responses use `{"success": true, "data": ...}`. Errors use `{"success": false, "error": {"code": ..., "message": ...}}`.

Common codes: `VALIDATION_ERROR`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `INTERNAL_ERROR`.

## Resume Uploads

Use multipart form data with field `file`. Allowed extensions are `.pdf`, `.doc`, and `.docx`. Maximum size is controlled by `MAX_RESUME_SIZE_MB`. Files are stored under `storage/resumes/{student_id}/{uuid}.{extension}`. A new upload deactivates the previous active resume.

## Testing

Create the test database with `docker exec -it skillbridge-postgres psql -U skillbridge -c "CREATE DATABASE skillbridge_test;"`.

Run all tests with `pytest -q`. Use `pytest -v` for verbose output or `pytest -q tests/test_auth.py` for one file.

## Useful Docker Commands

Stop the database with `docker compose down`.

Stop and delete local database data with `docker compose down -v`.

Open PostgreSQL with `docker exec -it skillbridge-postgres psql -U skillbridge -d skillbridge`.

## Troubleshooting

- PostgreSQL connection refused: run `docker compose up -d` and inspect `docker logs skillbridge-postgres`.
- Test database missing: run the database creation command above.
- Alembic model failure: confirm `alembic/env.py` imports `app.models` and sets `target_metadata = Base.metadata`.
- JWT 401: check bearer header, token expiry, `SECRET_KEY`, and active user status.
- Admin 403: the authenticated user must have role `ADMIN`.
- Resume failure: check extension, size, `UPLOAD_DIR`, and storage permissions.

## Security Notes

Password hashes are never returned. Passwords use bcrypt. JWTs expire and require valid `sub` and `exp` claims. Role-based access control protects routes. Students can access only their own records. Resume downloads validate the resolved path against `UPLOAD_DIR`. Never commit `.env`, secrets, or uploaded files.

## Production Checklist

- Set `DEBUG=false`.
- Use a strong unique `SECRET_KEY`.
- Use secure PostgreSQL credentials.
- Serve through HTTPS.
- Restrict CORS origins.
- Store resumes in private durable storage.
- Add reverse-proxy rate limiting.
- Rotate secrets and credentials regularly.
