# SkillBridge AI Backend

Backend foundation for SkillBridge AI, an Academia-Industry collaboration and employability platform.

This repository covers the assigned phases:

- Phase 8: Backend Foundation
- Phase 9: Student Module
- Phase 21: Employment Outcome Tracking
- Phase 22: AI Layer with Gemini primary and OpenRouter fallback
- Phase 23: Recommendation Engine foundation

The design is modular so future phases can add models, schemas, services, and routers without rewriting authentication or student ownership rules.

## Implemented Phases

### Phase 8: Backend Foundation

- FastAPI with `/api/v1` prefix
- PostgreSQL 16 with synchronous SQLAlchemy 2.x
- Alembic migrations and model discovery
- Pydantic v2 validation
- Standard JSON success and error responses
- JWT bearer authentication with expiry
- Bcrypt password hashing
- Role-based access control
- Audit log service boundary
- Shared database and pagination dependencies

### Phase 9: Student Module

- Student registration, login, and current-user endpoint
- Student profile and completeness score
- Student dashboard
- Skills with proficiency and score
- Projects, certifications, achievements, and internships
- Preferred career roles
- Resume upload, replacement, metadata, and download
- Admin student list and details

### Phase 21: Employment Outcome Tracking

The `employment_outcomes` table and student-owned endpoints track employment status, company, job title, employment type, joining date, ending date, salary, and notes.

```text
GET   /api/v1/students/me/outcomes
POST  /api/v1/students/me/outcomes
PATCH /api/v1/students/me/outcomes/{outcome_id}
```

### Phase 22: AI Layer

The `ai_executions` table provides an auditable provider-independent AI boundary. It stores feature, provider, model, input, output, status, errors, and timestamps.

Provider order:

```text
Gemini primary -> retry -> OpenRouter fallback -> retry -> rule-based fallback
```

Provider keys remain server-side. If no provider key exists, the application remains usable through deterministic fallback recommendations.

### Phase 23: Recommendation Engine

The `recommendations` table stores normalized career, learning, project, internship, and job recommendations with title, reason, priority, source, context, status, and expiry.

```text
GET   /api/v1/students/me/recommendations
POST  /api/v1/students/me/recommendations/generate
PATCH /api/v1/students/me/recommendations/{recommendation_id}/status
```

## Architecture

```text
FastAPI Router
    -> Auth and Role Dependencies
    -> Domain Service
    -> SQLAlchemy Model
    -> PostgreSQL
    -> Standard JSON Response
```

AI flow:

```text
Student Context -> AIExecution(PENDING) -> Gemini -> OpenRouter -> JSON validation -> Recommendations
```

PostgreSQL is the only required data service. Uploaded resume/document bytes are stored in PostgreSQL `student_documents.file_data` (`BYTEA`/`LargeBinary`). The application does not write uploaded documents to the filesystem.

Detailed design documents:

- `docs/phase_integration_map.md`
- `docs/phase_21_23_architecture.md`
- `docs/ai_provider_setup.md`

## Technology Stack

- Python 3.11+
- FastAPI
- PostgreSQL 16
- SQLAlchemy 2.x
- Alembic
- Pydantic v2 and pydantic-settings
- python-jose JWT
- passlib and bcrypt
- pytest and httpx

## Installation

Docker is not required. Install PostgreSQL 16 locally or use a managed PostgreSQL instance.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Create PostgreSQL databases named `skillbridge` and `skillbridge_test`, then update `.env` if your credentials differ.

## Environment Variables

```env
DATABASE_URL=postgresql+psycopg://skillbridge:skillbridge@localhost:5432/skillbridge
TEST_DATABASE_URL=postgresql+psycopg://skillbridge:skillbridge@localhost:5432/skillbridge_test
SECRET_KEY=change-this-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
MAX_RESUME_SIZE_MB=5
AI_PROVIDER=gemini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openai/gpt-4o-mini
AI_TIMEOUT_SECONDS=20
AI_MAX_RETRIES=2
```

Never commit real API keys or production secrets.

## Database Migrations

```powershell
alembic revision --autogenerate -m "phase 8 9 21 22 23 tables"
alembic upgrade head
alembic history
```

Current migration head: `0002_phase_21_23_and_db_files`.

## Seed Demo Data

```powershell
python -m app.scripts.seed
```

Local demo accounts:

- Student: `student.test@gmail.com` / `student@123`
- Admin: `admin.test@example.com` / `admin@123`
- Industry admin: `industry.admin.test@example.com` / `industry@123`
- Recruiter: `recruiter.test@example.com` / `recruiter@123`
- Institution admin: `institution.admin.test@example.com` / `institution@123`
- Faculty: `faculty.test@example.com` / `faculty@123`
- Mentor: `mentor.test@example.com` / `mentor@123`

## Run the API

```powershell
uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000/api/v1`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health: `http://127.0.0.1:8000/api/v1/health`

## Authentication

Register or log in to receive a JWT. Use it with:

```text
Authorization: Bearer <access_token>
```

JWT claims include `sub`, role, issue time, and expiration. Password hashes are never returned.

## Main API Areas

- Authentication: `/api/v1/auth/*`
- Student profile: `/api/v1/students/me`
- Skills: `/api/v1/students/me/skills`
- Projects: `/api/v1/students/me/projects`
- Certifications: `/api/v1/students/me/certifications`
- Achievements: `/api/v1/students/me/achievements`
- Internships: `/api/v1/students/me/internships`
- Career interests: `/api/v1/students/me/career-interests`
- Resume: `/api/v1/students/me/resume`
- Outcomes: `/api/v1/students/me/outcomes`
- Recommendations: `/api/v1/students/me/recommendations`
- Metadata: `/api/v1/meta/skills`, `/api/v1/meta/career-roles`
- Admin: `/api/v1/admin/students`

## Response Format

Success: `{"success": true, "data": {}}`

Error: `{"success": false, "error": {"code": "UNAUTHORIZED", "message": "Unauthorized"}}`

Common codes: `VALIDATION_ERROR`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, and `INTERNAL_ERROR`.

## AI Provider Setup

Gemini is primary and OpenRouter is fallback. Add keys only to the backend `.env` file. The recommendation endpoint remains usable without keys through rule-based fallback.

## Testing

Create the separate PostgreSQL test database, then run:

```powershell
pytest -q
pytest -v
```

Tests cover health, authentication guards, architecture metadata, provider failover, and student route behavior. Full database tests require PostgreSQL to be running.

## Security and Reliability

- Passwords use bcrypt.
- JWT signature and expiry are validated.
- Invalid token subjects and inactive users are rejected.
- Role-based access control protects routes.
- Students can access only their own records.
- Document binary data is not exposed in metadata responses.
- Provider API keys stay server-side.
- AI failures are recorded and use deterministic fallback.
- Authorization, validation, ownership, and workflow rules remain non-AI.

## Future Phase Compatibility

Future phases can add independent modules for skill intelligence, career intelligence, learning, internships, jobs, assessments, interviews, dashboards, analytics, deployment, monitoring, and scalability. Existing authentication, ownership, outcome, AI execution, and recommendation boundaries are designed to remain stable.

## Troubleshooting

- PostgreSQL connection refused: start PostgreSQL and verify `DATABASE_URL`.
- Database missing: create `skillbridge` and `skillbridge_test`.
- Migration failure: confirm `alembic/env.py` imports `app.models` and uses `Base.metadata`.
- JWT 401: check bearer header, expiry, `SECRET_KEY`, and active user status.
- Admin 403: the user must have role `ADMIN`.
- Resume failure: check extension, size, and PostgreSQL availability.
- AI fallback: configure `GEMINI_API_KEY` and optionally `OPENROUTER_API_KEY`.
