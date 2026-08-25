import ast
from pathlib import Path

from app.db.base import Base
import app.models  # noqa: F401


def _literal_assignment(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{name} missing from {path.name}")


def test_alembic_revision_chain_is_linear_and_reaches_0010():
    versions = Path(__file__).parents[1] / "alembic" / "versions"
    revisions = {}
    for path in versions.glob("[0-9][0-9][0-9][0-9]_*.py"):
        revision = _literal_assignment(path, "revision")
        revisions[revision] = _literal_assignment(path, "down_revision")

    assert revisions["0010_org_scope_backfill"] == "0009_notifications"
    assert revisions["0011_notification_delivery"] == "0010_org_scope_backfill"
    heads = set(revisions) - {parent for parent in revisions.values() if parent}
    assert heads == {"0011_notification_delivery"}
    assert max(map(len, revisions)) <= 32


def test_remaining_domain_tables_have_organization_scope():
    for table_name in (
        "learning_resources",
        "student_learning_plans",
        "assessments",
        "interview_sessions",
        "internship_applications",
        "employment_outcomes",
    ):
        assert "organization_id" in Base.metadata.tables[table_name].columns


def test_notifications_have_delivery_state():
    columns = Base.metadata.tables["notifications"].columns
    assert {"delivery_status", "delivery_attempts", "delivered_at", "last_delivery_error"}.issubset(set(columns.keys()))


def test_initial_revision_does_not_create_later_feature_tables():
    initial = Path(__file__).parents[1] / "alembic" / "versions" / "0001_initial.py"
    source = initial.read_text(encoding="utf-8")
    assert '"organizations"' not in source.split("initial_tables =", 1)[1].split("}", 1)[0]
    assert '"assessments"' not in source.split("initial_tables =", 1)[1].split("}", 1)[0]


def test_organization_backfill_uses_valid_correlated_update():
    migration = Path(__file__).parents[1] / "alembic" / "versions" / "0010_organization_scope_and_backfill.py"
    source = migration.read_text(encoding="utf-8")
    assert "FROM LATERAL" not in source
    assert "membership.user_id = opportunity.company_id" in source
