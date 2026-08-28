"""Source registry.

The registry is the human-owned record of which historical collections are approved
for the frozen corpus. Claude Code never marks a source approved; the researcher does
(CLAUDE.md §19, Phase 1).
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

ApprovalStatus = Literal["approved", "pending_approval", "rejected", "planned"]


class Source(BaseModel):
    id: str
    name: str
    kind: Literal["primary", "secondary"]
    language: str
    approval_status: ApprovalStatus
    base_url: str | None = None
    archive_id: str | None = None
    license_note: str | None = None
    access_requires_credentials: bool = False
    notes: str | None = None


class StudyWindow(BaseModel):
    start: str
    end: str
    note: str | None = None


class SourceRegistry(BaseModel):
    project: str
    study_window: StudyWindow
    frozen: bool = False
    sources: list[Source] = Field(default_factory=list)

    def approved(self) -> list[Source]:
        return [s for s in self.sources if s.approval_status == "approved"]

    def by_id(self, source_id: str) -> Source | None:
        return next((s for s in self.sources if s.id == source_id), None)


def load_registry(path: Path | None = None) -> SourceRegistry:
    from histosearch.config import get_settings

    path = path or get_settings().registry_path
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return SourceRegistry.model_validate(data)
