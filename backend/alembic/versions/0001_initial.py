from alembic import op
revision='0001_initial'; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    from app.db.base import Base
    from app import models  # noqa: F401 - register the model metadata

    # Keep the initial revision limited to the original identity/profile
    # tables. Later revisions own organizations, assessments, interviews and
    # the remaining feature tables. Creating the full current metadata here
    # makes every later CREATE TABLE fail on a clean database.
    initial_tables = {
        "users", "student_profiles", "skills", "student_skills",
        "student_projects", "student_certifications", "student_achievements",
        "student_internships", "student_preferred_roles", "career_roles",
        "student_documents",
    }
    Base.metadata.create_all(
        op.get_bind(),
        tables=[table for table in Base.metadata.sorted_tables if table.name in initial_tables],
    )
def downgrade():
    from app.db.base import Base
    from app import models  # noqa: F401
    initial_tables = {
        "users", "student_profiles", "skills", "student_skills",
        "student_projects", "student_certifications", "student_achievements",
        "student_internships", "student_preferred_roles", "career_roles",
        "student_documents",
    }
    Base.metadata.drop_all(
        op.get_bind(),
        tables=[table for table in reversed(Base.metadata.sorted_tables) if table.name in initial_tables],
    )
