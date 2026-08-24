# Phase Integration Map

This backend is intentionally organized around stable ownership boundaries so phases can be added incrementally.

## Current Assigned Scope

### Phase 8: Backend Foundation

Owns application startup, settings, PostgreSQL session, SQLAlchemy metadata, Alembic, standard responses, exception handling, JWT security, password hashing, role checks, audit logging, and shared utilities.

### Phase 9: Student Module

Owns users with the `STUDENT` role, student profile, student-owned skills, projects, certifications, achievements, internships, career interests, and database-backed documents.

### Phase 21: Employment Outcome Tracking

Owns `employment_outcomes`. It references `users.id` and does not alter the student profile schema. Future placement and employment modules can append outcomes without coupling to recommendation or AI code.

### Phase 22: AI Layer

Owns `ai_executions` and the AI service boundary. An execution records what feature ran, which provider/model was used, input/output JSON, status, errors, and timestamps. Provider adapters can be added later without changing routes or database ownership.

### Phase 23: Recommendation Engine

Owns `recommendations` and recommendation service functions. Recommendations reference a student, contain a normalized type/title/reason/priority/source/context/status, and can expire. The source can be `RULE_BASED` now and an AI provider later.

## Future Phase Connections

- Phases 10–12 can read `student_skills`, `career_roles`, `student_preferred_roles`, `ai_executions`, and write `recommendations`.
- Phases 13–14 can add internship/job tables and use the same student ownership and recommendation patterns.
- Phase 15 can analyze the database-backed `student_documents.file_data` without changing document ownership.
- Phases 16–17 can create assessment/interview records and optionally record AI work in `ai_executions`.
- Phases 18–20 and 24 can aggregate existing tables through read-only services and reporting queries.
- Phases 25–29 can harden the shared security, testing, deployment, logging, and performance layers without redesigning domain tables.
- Phases 30–31 consume the documented APIs and workflows; they do not require a second backend architecture.

## Request Flow

```text
FastAPI Router
    -> Dependency: database/session/auth/role
    -> Domain Service
    -> SQLAlchemy Model
    -> PostgreSQL
    -> Standard JSON Response
```

AI-enabled flow:

```text
Student or scheduled trigger
    -> AI service creates PENDING ai_execution
    -> Provider adapter (future)
    -> COMPLETED or FAILED ai_execution
    -> Recommendation service stores normalized recommendation
    -> Student reads active recommendations
```

## Design Rules

- PostgreSQL is the only required data service.
- Uploaded document bytes are stored in PostgreSQL `BYTEA`.
- Routers remain thin; business logic belongs in services.
- Deterministic authorization, validation, workflow states, and fixed scores remain rule-based.
- AI is optional and isolated behind execution records and services.
- Every student-owned record is filtered by the authenticated user's ID.
- New phases should add models, schemas, services, and routers without modifying unrelated modules.
