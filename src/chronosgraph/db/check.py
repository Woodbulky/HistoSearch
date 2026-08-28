"""Run the research invariant checks in db/checks/invariants.sql.

Each named query must return zero rows. Any row is a research-correctness failure
(CLAUDE.md §9) and is reported rather than silently ignored.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from chronosgraph.config import get_settings
from chronosgraph.db.connection import connect

CHECKS_PATH = Path(get_settings().repo_root) / "db" / "checks" / "invariants.sql"
_NAME_RE = re.compile(r"^--\s*name:\s*(\S+).*$", re.MULTILINE)


def parse_checks(sql_text: str) -> list[tuple[str, str]]:
    """Split the checks file into (name, query) pairs on `-- name:` markers."""
    matches = list(_NAME_RE.finditer(sql_text))
    checks: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(sql_text)
        body = sql_text[m.end() : end].strip().rstrip(";")
        if body:
            checks.append((m.group(1), body))
    return checks


def run_checks() -> dict[str, int]:
    checks = parse_checks(CHECKS_PATH.read_text(encoding="utf-8"))
    violations: dict[str, int] = {}
    with connect(autocommit=True) as conn:
        for name, query in checks:
            rows = conn.execute(query).fetchall()
            violations[name] = len(rows)
    return violations


def main() -> int:
    results = run_checks()
    failed = False
    for name, count in results.items():
        status = "OK" if count == 0 else f"VIOLATED ({count} rows)"
        if count:
            failed = True
        print(f"{name}: {status}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
