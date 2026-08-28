"""Live-database checks. Skipped automatically when no database is running."""

import psycopg
import pytest

from histosearch.db.connection import connect
from histosearch.db.migrate import migrate

pytestmark = pytest.mark.db


@pytest.fixture(scope="module")
def migrated(live_db):
    migrate(verbose=False)
    return True


def test_migrations_are_idempotent(migrated):
    assert migrate(verbose=False) == []


def test_pgvector_and_hnsw_index_exist(migrated):
    with connect(autocommit=True) as conn:
        ext = conn.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'").fetchone()
        assert ext is not None
        idx = conn.execute(
            "SELECT indexdef FROM pg_indexes WHERE indexname = 'passages_embedding_hnsw_idx'"
        ).fetchone()
        assert idx is not None and "hnsw" in idx[0]


def test_evidence_link_requires_a_real_passage(migrated):
    """Invariant 2: evidence must point at a real passage."""
    with connect() as conn:
        with pytest.raises(psycopg.Error):
            conn.execute(
                "INSERT INTO claims (text, claim_type, language) VALUES ('x', 'test', 'en')"
            )
            conn.execute(
                "INSERT INTO evidence_links (claim_id, passage_id, relation, char_start, char_end)"
                " VALUES (currval('claims_id_seq'), 999999999, 'supports', 0, 1)"
            )
        conn.rollback()


def test_conflict_label_enum_rejects_unlisted_labels(migrated):
    with connect() as conn:
        with pytest.raises(psycopg.Error):
            conn.execute("SELECT 'RECENCY_WINS'::conflict_label")
        conn.rollback()
