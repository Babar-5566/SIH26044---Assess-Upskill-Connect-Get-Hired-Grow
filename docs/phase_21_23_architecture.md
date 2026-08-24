# Phase 21-23 Architecture

The backend uses three small, independent modules so future capabilities can be added without changing authentication or student CRUD.

## Phase 21: Employment Outcome Tracking

Table: `employment_outcomes`

Stores one student's employment state and outcome history: status, company, job title, employment type, joining date, leaving date, salary, and notes. The table is owned by the student and indexed by `student_id`.

Service boundary: `app.services.outcome_service`.

Future endpoints can be added under `/students/me/outcomes` without changing existing profile tables.

## Phase 22: AI Layer

Table: `ai_executions`

Stores an auditable record for each AI operation: feature name, provider, model, input JSON, output JSON, status, error, timestamps, and optional user. AI providers remain outside the request routers.

Service boundary: `app.services.ai_service`.

Recommended flow:

1. Create a `PENDING` execution.
2. Call the selected provider in a future adapter.
3. Save `COMPLETED` output or `FAILED` error.

Deterministic validation, authorization, scoring rules, and workflow state remain rule-based.

## Phase 23: Recommendation Engine

Table: `recommendations`

Stores generated or rule-based recommendations for career, learning, projects, internships, or jobs. Each recommendation has title, reason, priority, source, context JSON, status, and optional expiry.

Service boundary: `app.services.recommendation_service`.

Recommendation generation should read existing student and industry data, then persist a normalized recommendation. The API can later expose active recommendations without coupling to a specific AI provider.

## Database File Storage

PostgreSQL is the only data service. Uploaded documents are stored in `student_documents.file_data` as PostgreSQL `BYTEA` (`LargeBinary`). The application does not write uploaded documents to the filesystem. Metadata remains queryable through normal SQL columns.

## Why This Stays Simple

- One PostgreSQL database
- No message broker required
- No AI provider required for deterministic features
- Service boundaries isolate future adapters
- JSON is used only for provider input/output and recommendation context
- Existing authentication and student ownership rules continue to apply
