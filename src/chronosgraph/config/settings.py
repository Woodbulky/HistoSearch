"""Project configuration. Every value is overridable via CHRONOS_* env vars or .env."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CHRONOS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql://chronos:chronos@localhost:5433/chronosgraph"

    data_dir: Path = Path("data")
    cache_dir: Path = Path("data/cache")

    # Extraction provider is not required before Phase 3.
    llm_provider: str = ""
    llm_model: str = ""
    llm_api_key: str = ""

    embedding_model: str = "intfloat/multilingual-e5-base"
    embedding_dim: int = Field(default=768, gt=0)

    @property
    def repo_root(self) -> Path:
        return REPO_ROOT

    @property
    def raw_dir(self) -> Path:
        return self._abs(self.data_dir) / "raw"

    @property
    def interim_dir(self) -> Path:
        return self._abs(self.data_dir) / "interim"

    @property
    def processed_dir(self) -> Path:
        return self._abs(self.data_dir) / "processed"

    @property
    def manifest_path(self) -> Path:
        return self._abs(self.data_dir) / "manifest.jsonl"

    @property
    def migrations_dir(self) -> Path:
        return REPO_ROOT / "db" / "migrations"

    @property
    def registry_path(self) -> Path:
        return REPO_ROOT / "sources" / "registry.yaml"

    def _abs(self, p: Path) -> Path:
        return p if p.is_absolute() else REPO_ROOT / p

    def redacted(self) -> dict[str, object]:
        """Settings safe to log or return from /metadata. Never exposes secrets."""
        data = self.model_dump()
        data["llm_api_key"] = "***set***" if self.llm_api_key else ""
        data["database_url"] = self.database_url.split("@")[-1]
        return data


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
