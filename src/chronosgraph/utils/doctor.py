"""Environment readiness report.

Reports facts only. It never marks a phase complete and never approves a source —
those are human-owned decisions (CLAUDE.md §0).
"""

from __future__ import annotations

import shutil
import subprocess
import sys

from chronosgraph.config import get_settings


def _tool(name: str) -> tuple[bool, str]:
    path = shutil.which(name)
    if not path:
        return False, "not found"
    try:
        out = subprocess.run(
            [name, "--version"], capture_output=True, text=True, timeout=20
        ).stdout.strip()
    except Exception as exc:  # pragma: no cover - defensive
        return True, f"found, version unknown ({exc})"
    return True, out.splitlines()[0] if out else "found"


def report() -> bool:
    settings = get_settings()
    ok = True

    print("== toolchain")
    print(f"  python           {sys.version.split()[0]}")
    for tool in ("git", "uv", "docker"):
        found, detail = _tool(tool)
        print(f"  {tool:<16} {detail}")
        ok = ok and found

    print("== filesystem")
    for label, path in (
        ("raw", settings.raw_dir),
        ("interim", settings.interim_dir),
        ("processed", settings.processed_dir),
        (
            "cache",
            settings.cache_dir
            if settings.cache_dir.is_absolute()
            else settings.repo_root / settings.cache_dir,
        ),
    ):
        exists = path.exists()
        print(f"  {label:<16} {'ok' if exists else 'MISSING'}  {path}")
        ok = ok and exists

    print("== database")
    from chronosgraph.db.connection import database_available

    if database_available():
        from chronosgraph.db.connection import connect
        from chronosgraph.db.migrate import applied_versions, migration_files

        with connect(autocommit=True) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations "
                "(version TEXT PRIMARY KEY, sha256 TEXT NOT NULL, "
                "applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"
            )
            applied = set(applied_versions(conn))
        pending = [p.stem for p in migration_files() if p.stem not in applied]
        print(f"  reachable        yes ({settings.database_url.split('@')[-1]})")
        print(f"  migrations       {len(applied)} applied, {len(pending)} pending")
        if pending:
            print(f"  pending          {', '.join(pending)}")
    else:
        print("  reachable        NO — start it with: docker compose up -d db")
        ok = False

    print("== corpus")
    try:
        from chronosgraph.sources import load_registry

        reg = load_registry()
        print(f"  registry         ok ({len(reg.sources)} sources)")
        print(f"  approved         {len(reg.approved())}  (human-owned decision)")
        print(f"  frozen           {reg.frozen}")
    except Exception as exc:
        print(f"  registry         ERROR {exc}")
        ok = False
    manifest = settings.manifest_path
    print(f"  manifest         {'present' if manifest.exists() else 'absent (Phase 1 output)'}")

    print(f"\noverall: {'READY' if ok else 'NOT READY'}")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if report() else 1)
