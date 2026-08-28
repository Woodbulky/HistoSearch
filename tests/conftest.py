import pytest

from histosearch.db.connection import database_available


@pytest.fixture(scope="session")
def live_db():
    if not database_available():
        pytest.skip("no live PostgreSQL; start it with `docker compose up -d db`")
    return True
