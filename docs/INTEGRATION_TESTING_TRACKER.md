# Integration Testing Tracker

Single source of truth for integration testing. Update after every test; do not record secrets.

## 1. Environment & Infrastructure

- Backend: FastAPI + SQLAlchemy + Alembic
- Database: Supabase PostgreSQL
- Frontend: React + Vite
- API documentation/testing: Swagger (`/docs`)
- Migration head: `0011_notification_delivery`
- Supabase migration: **Applied successfully**
- Current database revision: `0011_notification_delivery`
- Public schema: **Created successfully**

## 2. Automated Validation

| Area | Command | Result |
| --- | --- | --- |
| Backend | `python -m pytest -q` | ✅ 39 passed |
| Backend | `python -m compileall app` | ✅ Passed |
| Alembic | `alembic heads` | ✅ `0011_notification_delivery` |
| Frontend | `npm.cmd install` | ✅ Passed |
| Frontend | `npm.cmd run build` | ✅ Passed |
| Migration SQL | `alembic upgrade head --sql` | ✅ Passed |

Warnings: one existing Starlette/httpx deprecation warning; no functional failure recorded.

## 3. Live Supabase Integration

### Authentication

Tested through Swagger against the real Supabase database.

- Student registration → ✅ Passed
- Duplicate email detection → ✅ Passed (`409`)
- Student login → ✅ Passed
- Bearer token authorization → ✅ Passed
- Authenticated `/students/me` → ✅ Passed

### Student Profile

- GET profile → ✅ Passed
- PATCH profile → ✅ Passed
- Data persisted in Supabase → ✅ Confirmed

### Skills

- Create, list, update, delete → ✅ Passed
- Persistence → ✅ Confirmed

### Projects

- Create, list, update, delete → ✅ Passed
- URL persistence → ✅ Passed

Bug fixed: Pydantic `AnyUrl` values are normalized to strings before SQLAlchemy persistence.

### Certifications

- Create, list, update, delete → ✅ Passed

### Achievements

- Create, list, update, delete → ✅ Passed

### Internships

- Create, list, update, delete → ✅ Passed

### Resume

- Upload → ⏳ Not yet tested
- Replace → ⏳ Not yet tested
- Download → ⏳ Not yet tested
- Metadata/API response validation → ⏳ Not yet tested

## 4. Remaining Testing Order

1. Resume upload/replace/download
2. Preferred roles
3. Learning plans
4. Recommendations and skill gaps
5. Assessments
6. Interviews
7. Internship/application workflows
8. Jobs/opportunities
9. Mentorship
10. Employment outcomes
11. Organizations and memberships
12. Dashboards
13. Notifications
14. Role-based authorization
15. Cross-user data isolation
16. Complete frontend browser workflows

For each test record: **Endpoint → Request → Expected → Actual → Database verification → Status → Bug/fix reference**.

## 5. Testing Rules

- Never mark an untested feature as working.
- Distinguish automated, Swagger/API, and browser tests.
- Record real bugs and fixes.
- Verify important mutations in Supabase.
- Test success and failure cases: `401`, `403`, `404`, `409`, `422`.
- Test authorization and cross-user isolation.
- Never store passwords, JWTs, API keys, or other secrets here.
