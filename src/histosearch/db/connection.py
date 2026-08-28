"""PostgreSQL connection helpers. The local database is the source of truth."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import psycopg

from histosearch.config import get_settings


@contextmanager
def connect(autocommit: bool = False) -> Iterator[psycopg.Connection]:
    settings = get_settings()
    with psycopg.connect(settings.database_url, autocommit=autocommit) as conn:
        yield conn


def database_available(timeout_seconds: int = 3) -> bool:
    """True if the research database accepts connections. Used by tests and health checks.

    Uses a short connect timeout so a stopped database fails fast instead of stalling
    the test suite.
    """
    settings = get_settings()
    try:
        with psycopg.connect(
            settings.database_url, autocommit=True, connect_timeout=timeout_seconds
        ) as conn:
            conn.execute("SELECT 1")
        return True
    except psycopg.Error:
        return False
