"""Create integrated feature tables using migration-owned DDL."""
from alembic import op

revision = "0007_feature_tables"
down_revision = "0006_mentor_assignments"
branch_labels = None
depends_on = None

TABLES = ("learning_resources", "student_learning_plans", "learning_plan_items", "learning_certifications", "learning_outcomes", "internship_postings", "academician_opportunities", "internship_applications", "internship_progress", "internship_mentor_feedback", "audit_logs", "student_documents")

def upgrade():
    ddl = {
        "learning_resources": "id UUID PRIMARY KEY, organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL, title VARCHAR NOT NULL, type VARCHAR NOT NULL, provider VARCHAR, description TEXT, skills_covered VARCHAR[], target_level VARCHAR, duration_hours INTEGER, url VARCHAR, thumbnail_url VARCHAR, industry_relevant BOOLEAN DEFAULT TRUE, is_free BOOLEAN DEFAULT FALSE, completion_rate FLOAT DEFAULT 0, avg_assessment_score FLOAT DEFAULT 0, placement_outcome_rate FLOAT DEFAULT 0, created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ",
        "student_learning_plans": "id UUID PRIMARY KEY, organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL, student_id UUID NOT NULL, target_role VARCHAR NOT NULL, status VARCHAR DEFAULT 'active', created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ",
        "learning_plan_items": "id UUID PRIMARY KEY, plan_id UUID NOT NULL, resource_id UUID NOT NULL, skill_gap_addressed VARCHAR, priority INTEGER DEFAULT 1, status VARCHAR DEFAULT 'not_started', progress_percent INTEGER DEFAULT 0, started_at TIMESTAMPTZ, completed_at TIMESTAMPTZ",
        "learning_certifications": "id UUID PRIMARY KEY, student_id UUID NOT NULL, resource_id UUID, certification_name VARCHAR NOT NULL, issuer VARCHAR, issued_date TIMESTAMPTZ, expiry_date TIMESTAMPTZ, credential_url VARCHAR, certificate_file_url VARCHAR, verified BOOLEAN DEFAULT FALSE, created_at TIMESTAMPTZ DEFAULT now()",
        "learning_outcomes": "id UUID PRIMARY KEY, resource_id UUID NOT NULL, target_role VARCHAR NOT NULL, completion_count INTEGER DEFAULT 0, placement_count INTEGER DEFAULT 0, avg_time_to_placement_days INTEGER, updated_at TIMESTAMPTZ",
        "internship_postings": "id UUID PRIMARY KEY, company_id UUID NOT NULL, organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL, company_name VARCHAR NOT NULL, title VARCHAR NOT NULL, type VARCHAR NOT NULL, description TEXT, location VARCHAR, is_remote BOOLEAN DEFAULT FALSE, duration_weeks INTEGER, stipend_monthly INTEGER, required_skills VARCHAR[], required_education VARCHAR, required_cgpa FLOAT DEFAULT 0, required_year INTEGER[], required_certifications VARCHAR[], seats_available INTEGER DEFAULT 1, application_deadline DATE, start_date DATE, status VARCHAR DEFAULT 'open', posted_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ",
        "academician_opportunities": "id UUID PRIMARY KEY, company_id UUID, organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL, company_name VARCHAR, type VARCHAR NOT NULL, title VARCHAR NOT NULL, description TEXT, duration VARCHAR, stipend_or_honorarium INTEGER, domain VARCHAR[], eligibility TEXT, application_deadline DATE, status VARCHAR DEFAULT 'open', posted_at TIMESTAMPTZ DEFAULT now()",
        "internship_applications": "id UUID PRIMARY KEY, organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL, student_id UUID NOT NULL, internship_id UUID NOT NULL, status VARCHAR DEFAULT 'applied', skill_match_percent INTEGER DEFAULT 0, cover_letter TEXT, applied_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ, company_notes TEXT",
        "internship_progress": "id UUID PRIMARY KEY, application_id UUID NOT NULL UNIQUE, mentor_name VARCHAR, mentor_email VARCHAR, start_date DATE, end_date DATE, tasks_assigned JSON, milestones_completed INTEGER DEFAULT 0, total_milestones INTEGER DEFAULT 0, mentor_feedback TEXT, final_rating FLOAT, completion_certificate_url VARCHAR, status VARCHAR DEFAULT 'ongoing', updated_at TIMESTAMPTZ",
        "internship_mentor_feedback": "id UUID PRIMARY KEY, progress_id UUID NOT NULL, week_number INTEGER NOT NULL, technical_rating INTEGER, communication_rating INTEGER, initiative_rating INTEGER, overall_rating INTEGER, comments TEXT, submitted_at TIMESTAMPTZ DEFAULT now()",
        "audit_logs": "id UUID PRIMARY KEY, user_id UUID REFERENCES users(id) ON DELETE SET NULL, action VARCHAR(100) NOT NULL, entity VARCHAR(100), entity_id VARCHAR(100), details JSON, ip VARCHAR(50), created_at TIMESTAMPTZ DEFAULT now()",
        "student_documents": "id UUID PRIMARY KEY, student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE, document_type VARCHAR(20) DEFAULT 'RESUME', file_name VARCHAR(255) NOT NULL, file_data BYTEA, file_size INTEGER NOT NULL, mime_type VARCHAR(100), is_active BOOLEAN DEFAULT TRUE, uploaded_at TIMESTAMPTZ DEFAULT now()",
    }
    for table, columns in ddl.items():
        op.execute(f"CREATE TABLE IF NOT EXISTS {table} ({columns})")
    for name, table, column in (
        ("ix_learning_resources_organization_id", "learning_resources", "organization_id"),
        ("ix_student_learning_plans_student_id", "student_learning_plans", "student_id"),
        ("ix_learning_plan_items_plan_id", "learning_plan_items", "plan_id"),
        ("ix_learning_certifications_student_id", "learning_certifications", "student_id"),
        ("ix_learning_outcomes_resource_id", "learning_outcomes", "resource_id"),
        ("ix_internship_postings_company_id", "internship_postings", "company_id"),
        ("ix_academician_opportunities_company_id", "academician_opportunities", "company_id"),
        ("ix_internship_applications_student_id", "internship_applications", "student_id"),
        ("ix_internship_applications_internship_id", "internship_applications", "internship_id"),
        ("ix_internship_progress_application_id", "internship_progress", "application_id"),
        ("ix_internship_mentor_feedback_progress_id", "internship_mentor_feedback", "progress_id"),
    ):
        op.execute(f"CREATE INDEX IF NOT EXISTS {name} ON {table} ({column})")

def downgrade():
    for table in reversed(TABLES):
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
