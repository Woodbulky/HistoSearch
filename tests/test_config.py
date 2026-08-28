from pathlib import Path

from chronosgraph.config import Settings, get_settings


def test_repo_root_contains_claude_md():
    assert (get_settings().repo_root / "CLAUDE.md").exists()


def test_derived_paths_are_absolute():
    s = get_settings()
    for p in (s.raw_dir, s.processed_dir, s.migrations_dir, s.registry_path):
        assert Path(p).is_absolute()


def test_redacted_hides_api_key_and_credentials():
    s = Settings(
        llm_api_key="secret-value",
        database_url="postgresql://user:pw@localhost:5433/chronosgraph",
    )
    red = s.redacted()
    assert red["llm_api_key"] == "***set***"
    assert "secret-value" not in str(red)
    assert "pw" not in str(red["database_url"])
