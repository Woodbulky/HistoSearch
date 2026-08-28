# SUMMARY.md — what has been built so far

Running record of the system as actually implemented, for anyone (human or model)
picking the project up cold. Updated at the end of every completed phase.

Last updated: 2026-08-29 — end of Phase 0, after the HistoSearch rename.

---

## Phase 0 — Research and environment foundation ✅

### What exists now

**Repository**: git initialised, remote `origin` =
`https://github.com/Woodbulky/HistoSearch.git`. Project, repository, Python package
and CLI all use the name **HistoSearch**. The project was briefly called ChronosGraph
during initial scaffolding; that name was retired before Phase 1 (see the rename note
at the end of this section).

**Python environment**: `uv`-managed, `requires-python >= 3.11`, resolved to Python
3.11.15 in `.venv`. Runtime deps: pydantic v2, pydantic-settings, psycopg 3,
SQLAlchemy 2, pgvector, httpx, tenacity, PyYAML, structlog, typer. Dev deps: pytest,
pytest-cov, ruff, mypy. No LangChain/LlamaIndex, no paid API dependency — as required
by `CLAUDE.md` §7.

**Database**: PostgreSQL 16 with pgvector, run locally via `docker-compose.yml`
(image `pgvector/pgvector:pg16`, container `histosearch-db`, host port **5433** to
avoid clashing with any existing local Postgres). The local database is the source of
truth; Supabase is reserved for the final read-only demo only.

**Schema** — five forward-only migrations in `db/migrations/`, all applied and verified:

| Migration | Contents |
|---|---|
| `0001_extensions` | `vector`, `pg_trgm`; enums `conflict_label`, `time_granularity`, `entity_type`, `node_kind` |
| `0002_documents_passages` | `documents`, `passages` (+ FTS and trigram indexes) |
| `0003_knowledge` | `entities`, `events`, `claims`, `evidence_links` |
| `0004_conflicts_graph` | `contradictions`, `nodes`, `edges` |
| `0005_pipeline_bookkeeping` | HNSW vector index, `llm_cache`, `extraction_failures`, `pipeline_runs`, `stage_counts` |

The schema encodes the research rules rather than leaving them to convention:

- `conflict_label` is a Postgres enum with exactly the four labels, so
  `PERMANENTLY_CONTESTED` and `UNKNOWN` cannot be dropped by a coding mistake, and an
  invented label such as `RECENCY_WINS` is rejected by the database.
- `contradictions.claim_a_id` / `claim_b_id` are `ON DELETE RESTRICT`, so a
  contradiction can never lose one of its claims (invariant 7). A test asserts this.
- `claims.extraction_confidence` and `contradictions.evidence_confidence` are separate
  columns from the label — evidence confidence cannot silently become the conflict
  class (invariant 6 / Contribution B).
- `passages` carries `turn_index` + `sub_index` + exact `char_start`/`char_end`, so the
  one-intervention-per-passage chunking rule (§11) and character-exact provenance are
  representable from the start.
- `events.granularity` exists so a date is never recorded more precisely than its
  source supports (invariant 5).
- `language` is on documents, passages, claims (and event labels), so Hindi can join the
  same representation later without a schema change (§18).
- `llm_cache` is keyed by provider+model+prompt_version+input_hash; `extraction_failures`
  and `stage_counts` exist so failures and row loss are reported, not discarded (§12, invariant 15).

**Migration runner** (`src/histosearch/db/migrate.py`): applies SQL files in filename
order, records each in `schema_migrations` with a sha256, and refuses to proceed if an
already-applied migration file was edited — protecting reproducibility of the DB state.

**Invariant checks** (`db/checks/invariants.sql`, run by `histosearch check`): six named
queries that must each return zero rows — claims without evidence, evidence spans
outside their passage, invalid passage spans, event dates more precise than their
declared granularity, contradictions missing a claim, dangling graph nodes. Currently
all OK on an empty database; they become meaningful from Phase 2 onward.

**Source registry** (`sources/registry.yaml` + typed loader): the human-owned approval
record. Holds the study window (1947-08-01 → 1947-12-31), a `frozen` flag, and five
sources — UK Hansard and Constituent Assembly Debates as `pending_approval`, and
NAI/Abhilekh Patal, Nehru Archive, Gandhi Heritage Portal as `planned`. Approval status
is never changed by code.

**Configuration** (`src/histosearch/config/settings.py`): pydantic-settings with
`HISTOSEARCH_` env prefix and `.env` support; `redacted()` strips the API key and DB
credentials so configuration can be logged or exposed via `/metadata` safely.

**CLI** (`histosearch`): `doctor`, `migrate`, `check`, `sources`, `config`.

**Tests**: 19 passing. Config/redaction, registry validation and research-scope
assertions, migration ordering and data-model coverage, the four conflict labels, the
contradiction delete-rule, embedding dimension consistency, invariant-check parsing,
and live-DB tests (migration idempotence, pgvector + HNSW index present, foreign-key
enforcement on evidence links, enum rejection of unlisted labels). Live-DB tests skip
automatically when no database is running. `ruff check` clean.

### Verified by running

```text
uv run histosearch migrate   → 5 migrations applied
uv run histosearch check     → 6/6 invariants OK
uv run histosearch doctor    → overall: READY
uv run pytest            → 19 passed
uv run ruff check .      → All checks passed
```

### What deliberately does NOT exist yet

No downloaded sources, no `data/manifest.jsonl`, no parsers, no embeddings, no
extraction, no retrieval, no classifier, no API, no frontend. Those belong to Phases
1–11 and were not started, per the phase-gate rule.

### Rename: ChronosGraph → HistoSearch (2026-08-29, before Phase 1)

The project was scaffolded under the working name *ChronosGraph* and renamed to
**HistoSearch** at the researcher's direction before any corpus was acquired.

Renamed: project and product name throughout `CLAUDE.md`, `README.md`,
`PROJECT_STATE.md` and this file; Python package `chronosgraph` → `histosearch`
(directory moved with `git mv`, so history follows the files); CLI command
`chronos` → `histosearch`; distribution name in `pyproject.toml`; environment
variable prefix `CHRONOS_` → `HISTOSEARCH_`; Docker container `chronosgraph-db` →
`histosearch-db`, volume `chronos_pgdata` → `histosearch_pgdata`, and the Postgres
role/database `chronos`/`chronosgraph` → `histosearch`.

Deliberately NOT renamed: every migration filename and every byte of migration SQL
(they contained no project name, so migration history and the recorded sha256 guard
are untouched); all table, column, enum, type and index names; the four conflict
labels; research terminology and source identifiers such as `uk_hansard` and
`cad_india`.

Because the Postgres role and database name changed, the local Docker volume was
recreated and all five migrations re-applied from scratch — a clean re-derivation
that lost nothing, since the database held only schema and no research data.

### Open items carried forward

None.
