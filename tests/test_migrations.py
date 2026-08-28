"""Migrations are the contract for the data model in CLAUDE.md §8."""

import re

from chronosgraph.config import get_settings
from chronosgraph.db.migrate import migration_files

REQUIRED_TABLES = {
    "documents",
    "passages",
    "entities",
    "events",
    "claims",
    "evidence_links",
    "contradictions",
    "nodes",
    "edges",
}


def all_migration_sql() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in migration_files())


def test_migrations_are_ordered_and_uniquely_versioned():
    stems = [p.stem for p in migration_files()]
    versions = [s.split("_")[0] for s in stems]
    assert versions == sorted(versions)
    assert len(set(versions)) == len(versions)


def test_all_core_tables_are_defined():
    sql = all_migration_sql()
    defined = set(re.findall(r"CREATE TABLE IF NOT EXISTS (\w+)", sql))
    assert defined >= REQUIRED_TABLES, REQUIRED_TABLES - defined


def test_all_four_conflict_labels_exist():
    sql = all_migration_sql()
    for label in (
        "NOT_CONTRADICTION",
        "RESOLVABLE_BY_RECENCY",
        "PERMANENTLY_CONTESTED",
        "UNKNOWN",
    ):
        assert f"'{label}'" in sql, f"conflict label {label} missing from schema"


def test_embedding_dimension_matches_settings():
    sql = all_migration_sql()
    assert f"vector({get_settings().embedding_dim})" in sql


def test_contradictions_never_cascade_delete_claims():
    """Invariant 7: a contradiction must retain both claims."""
    sql = all_migration_sql()
    block = sql[sql.index("CREATE TABLE IF NOT EXISTS contradictions") :]
    block = block[: block.index(");")]
    assert block.count("ON DELETE RESTRICT") == 2
    assert "ON DELETE CASCADE" not in block
