"""Forward-only migration runner.

Migrations are plain SQL files in db/migrations, applied in filename order and
recorded in schema_migrations so a run is idempotent and reproducible.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from histosearch.config import get_settings
from histosearch.db.connection import connect

BOOTSTRAP = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     TEXT PRIMARY KEY,
    sha256      TEXT NOT NULL,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def migration_files() -> list[Path]:
    return sorted(get_settings().migrations_dir.glob("*.sql"))


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def applied_versions(conn) -> dict[str, str]:
    rows = conn.execute("SELECT version, sha256 FROM schema_migrations").fetchall()
    return {r[0]: r[1] for r in rows}


def migrate(verbose: bool = True) -> list[str]:
    """Apply pending migrations. Returns the versions applied in this run."""
    applied_now: list[str] = []
    with connect(autocommit=True) as conn:
        conn.execute(BOOTSTRAP)
        known = applied_versions(conn)
        for path in migration_files():
            version = path.stem
            sql = path.read_text(encoding="utf-8")
            digest = _sha256(sql)
            if version in known:
                if known[version] != digest:
                    # Editing an applied migration breaks reproducibility of the DB state.
                    raise RuntimeError(
                        f"Migration {version} changed after it was applied. "
                        "Add a new migration instead of editing an applied one."
                    )
                continue
            conn.execute(sql)
            conn.execute(
                "INSERT INTO schema_migrations (version, sha256) VALUES (%s, %s)",
                (version, digest),
            )
            applied_now.append(version)
            if verbose:
                print(f"applied {version}")
    if verbose and not applied_now:
        print("database already up to date")
    return applied_now


if __name__ == "__main__":
    migrate()
