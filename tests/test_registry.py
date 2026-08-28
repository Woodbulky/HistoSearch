"""The registry is a research artifact: its shape and approval semantics are tested."""

import pytest
from pydantic import ValidationError

from chronosgraph.sources import load_registry
from chronosgraph.sources.registry import SourceRegistry


def test_registry_loads_and_validates():
    reg = load_registry()
    assert isinstance(reg, SourceRegistry)
    assert reg.sources


def test_core_corpus_pairing_is_registered():
    reg = load_registry()
    # Hansard x CAD pairing is central to the research design (CLAUDE.md §4).
    assert reg.by_id("uk_hansard") is not None
    assert reg.by_id("cad_india") is not None


def test_study_window_matches_declared_scope():
    reg = load_registry()
    assert reg.study_window.start == "1947-08-01"
    assert reg.study_window.end == "1947-12-31"


def test_every_source_records_language_for_multilingual_design():
    for s in load_registry().sources:
        assert s.language, f"{s.id} has no language"


def test_unknown_approval_status_is_rejected():
    with pytest.raises(ValidationError):
        SourceRegistry.model_validate(
            {
                "project": "x",
                "study_window": {"start": "1947-08-01", "end": "1947-12-31"},
                "sources": [
                    {
                        "id": "s",
                        "name": "s",
                        "kind": "primary",
                        "language": "en",
                        "approval_status": "definitely_fine",
                    }
                ],
            }
        )
