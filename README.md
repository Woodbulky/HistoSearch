# HistoSearch

Evidence-grounded historical question answering over the Indian Independence and
Partition period (initial study window: August–December 1947).

HistoSearch is a research system, not a chatbot. Every answer must be traceable:

```text
question → evidence → claims → events → time → conflicting accounts → answer
```

The operating contract for this repository is `CLAUDE.md`. Verified progress lives in
`PROJECT_STATE.md`. A running summary of what has been built is in `SUMMARY.md`.

## Quick start

```bash
uv sync --extra dev          # create .venv and install dependencies
cp .env.example .env         # adjust if your database port differs
docker compose up -d db      # PostgreSQL 16 + pgvector on localhost:5433
uv run histosearch migrate       # apply db/migrations in order
uv run histosearch doctor        # environment + readiness report
uv run pytest                # tests (live-DB tests skip if no database)
```

## CLI

| Command | Purpose |
|---|---|
| `histosearch doctor` | Environment and readiness report. Changes nothing. |
| `histosearch migrate` | Apply pending SQL migrations. |
| `histosearch check` | Run the research invariant checks in `db/checks/invariants.sql`. |
| `histosearch sources` | Show the source registry and its human-owned approval state. |
| `histosearch config` | Print effective configuration with secrets redacted. |

## Layout

```text
CLAUDE.md              operating contract (research rules, phases, invariants)
PROJECT_STATE.md       verified phase/artifact status
SUMMARY.md             what has been built so far
sources/registry.yaml  human-owned source approval record
db/migrations/         forward-only SQL migrations (the data model of CLAUDE.md §8)
db/checks/             research invariant checks — each must return zero rows
src/histosearch/      the research code
  config/  db/  sources/  ingest/  parsing/  extraction/
  retrieval/  temporal/  conflict/  answer/  api/  utils/
data/raw/              immutable downloaded sources (not committed)
data/processed/        derived passages (not committed)
data/manifest.jsonl    acquisition manifest with hashes (committed)
annotation/            annotation guidelines and datasets (Phase 6)
experiments/           experiment configs; outputs are not committed
tests/
```

## Rules that bind the code

- Raw source files are immutable; derived data is regenerated, never edited in place.
- Every claim needs at least one evidence link to a real passage and exact span.
- `asserted_at` (when a claim was made) is never conflated with event time.
- Evidence confidence never decides a conflict label.
- `PERMANENTLY_CONTESTED` and `UNKNOWN` are valid results and are never suppressed.

The full list is `CLAUDE.md` §9.
