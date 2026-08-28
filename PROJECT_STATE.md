# PROJECT_STATE.md — HistoSearch

This file records verified project progress for Claude Code.

## Current phase

```text
0 COMPLETE — awaiting human gate before Phase 1
```

## Phase status

```text
Phase 0  Research + environment foundation       [x] COMPLETE (2026-08-28,
                                                     re-verified 2026-08-29)
Phase 1  Corpus acquisition                       [ ] BLOCKED — source approval pending
Phase 2  Parsing + cleaning + passages            [ ] NOT STARTED
Phase 3  Claim/entity/event extraction             [ ] NOT STARTED
Phase 4  Baseline retrieval + QA                  [ ] NOT STARTED
Phase 5  Temporal + evidence reasoning             [ ] NOT STARTED
Phase 6  Contradiction dataset + pipeline          [ ] NOT STARTED
Phase 7  Fine-tuning                               [ ] NOT STARTED
Phase 8  Hindi + multilingual extension            [ ] NOT STARTED
Phase 9  Full evaluation + ablation               [ ] NOT STARTED
Phase 10 Backend/API                              [ ] NOT STARTED
Phase 11 Frontend                                 [ ] NOT STARTED
Phase 12 Release + paper                          [ ] NOT STARTED
```

## Human-owned inputs

```text
Research scope                  [x] provided in CLAUDE.md (Indian Independence
                                    and Partition; RQ1-RQ5)
Historical window               [~] stated as 1947-08-01..1947-12-31 in CLAUDE.md;
                                    NOT yet explicitly confirmed by the researcher
Approved source list            [ ] pending — Hansard and CAD are registered as
                                    pending_approval, 0 approved
Source access/credentials       [ ] pending — neither registered source is marked
                                    as requiring credentials; needs confirmation
Gold research questions         [ ] pending
Gold answers/evidence           [ ] pending
Annotation guidelines approval  [ ] pending
Human annotation                [ ] pending
Inter-annotator agreement       [ ] pending
Colab training run              [ ] pending
Final classifier selection      [ ] pending
Hindi source approval           [ ] pending
Multilingual evaluation set     [ ] pending
Final result interpretation     [ ] pending
Paper claims/discussion         [ ] pending
```

## Project artifacts

```text
Raw corpus                      [ ] pending (Phase 1)
Manifest + hashes               [ ] pending (Phase 1)
Processed passages              [ ] pending
Embeddings                      [ ] pending
Extracted claims                [ ] pending
Extracted entities              [ ] pending
Extracted events                [ ] pending
Temporal graph                  [ ] pending
Baseline results                [ ] pending
Annotation dataset              [ ] pending
Trained classifier              [ ] pending
Multilingual dataset            [ ] pending
Final evaluation results        [ ] pending
API                             [ ] pending
Frontend                        [ ] pending
Database schema                 [x] applied and verified (5 migrations;
                                    re-applied from scratch 2026-08-29)
Database snapshot               [ ] pending
Demo deployment                 [ ] pending
```

## Last verified facts

- Current phase: 0 complete; Phase 1 not started
- Last completed milestone: Phase 0 environment foundation (2026-08-28)
- Last verified commit: see git log (rename commit on main, 2026-08-29);
  Phase 0 scaffold was 0d6f0b9
- Last verified dataset snapshot: none (no corpus acquired yet)
- Last model version: none (no model used yet)
- Last evaluation run: none

Re-verified by execution on 2026-08-29, after the ChronosGraph -> HistoSearch
rename and a from-scratch database recreation:

```text
uv run histosearch migrate    5 migrations applied (0001..0005) on a fresh volume
uv run histosearch check      6/6 research invariant checks OK
uv run histosearch doctor     overall: READY
uv run pytest                 19 passed, 0 failed
uv run ruff check .           clean
uv run ruff format --check .  31 files already formatted
```

Environment: Python 3.11.15 via uv, PostgreSQL 16 + pgvector in Docker
(container histosearch-db, database/role histosearch, localhost:5433), git remote
https://github.com/Woodbulky/HistoSearch.git

## Rename record — ChronosGraph -> HistoSearch (2026-08-29)

The project was scaffolded under the working name ChronosGraph and renamed before
Phase 1, at the researcher's direction. No corpus had been acquired.

Renamed: project/product name in all documentation; Python package
chronosgraph -> histosearch (git mv, history preserved); CLI chronos -> histosearch;
distribution name; env prefix CHRONOS_ -> HISTOSEARCH_; Docker container, volume,
Postgres role and database name.

Not renamed, deliberately: migration filenames and migration SQL (byte-identical,
verified by `git diff` showing zero changes under db/migrations/, so the recorded
sha256 migration guard still matches); all table, column, enum, type and index
names; the four conflict labels; source identifiers uk_hansard and cad_india;
research terminology.

The Docker volume was recreated because the Postgres role and database name
changed. The database held only schema, no research data, and was re-derived
deterministically by re-running the same unchanged migrations.

## Current blockers

1. Phase 1 cannot start: 0 sources are approved. `sources/registry.yaml` lists
   uk_hansard and cad_india as `pending_approval`. Approval is human-owned.
2. The historical window is stated in CLAUDE.md but not explicitly confirmed by
   the researcher.
3. Licence terms for the specific Hansard 1947 volumes and the CAD digital edition
   are recorded as "confirm before freezing" and remain unconfirmed.

## Next actions

For the researcher (unblocks Phase 1):
- Approve or reject uk_hansard and cad_india in `sources/registry.yaml`.
- Confirm the 1947-08-01..1947-12-31 window.
- Confirm licence/reuse terms for both sources.
- Confirm whether either source needs credentials.

For Claude Code (once unblocked): Phase 1 corpus acquisition — discovery scripts,
resumable downloads, sha256 hashing, immutable raw storage, `data/manifest.jsonl`,
acquisition report.

## Phase handoff — Phase 0

```text
PHASE COMPLETE:
Phase 0 — Research and environment foundation

EVIDENCE:
- git repository initialised; remote origin set to the researcher's GitHub repo
- uv project resolving on Python 3.11; ruff + pytest configured and clean
- PostgreSQL 16 + pgvector running locally via docker compose on port 5433
- 5 migrations applied and idempotent; full data model of CLAUDE.md section 8 present
- conflict_label enum contains exactly the four required labels; the database
  rejects any other label
- contradictions retain both claims by ON DELETE RESTRICT (invariant 7), asserted
  by test
- extraction confidence and evidence confidence are stored separately from the
  conflict label (invariant 6)
- 6 research invariant checks implemented and passing
- source registry present with the human-owned approval field; 0 sources approved
- 19 tests passing, including live-database schema tests

BEFORE STARTING PHASE 1:
1. Approve the initial source list (uk_hansard, cad_india) in sources/registry.yaml.
2. Confirm the historical date window (1947-08-01 to 1947-12-31).
3. Confirm access/credentials for any source that requires them.
4. Confirm the local data directory is available (data/ exists and is writable).
5. Confirm whether any source has explicit usage/licence restrictions.

NOT NEEDED YET:
- gold research questions and gold answers
- annotation guidelines, labels, inter-annotator agreement
- conflict classifier choice, Colab/Kaggle training configuration
- Hugging Face account or model publication
- Hindi corpus decisions
- backend API and frontend design
- Supabase or any deployment decision
```

## Phase handoff

At phase completion, Claude Code must write:

```text
PHASE COMPLETE:
<phase>

EVIDENCE:
<what was verified>

BEFORE STARTING NEXT PHASE:
<only actual prerequisites for the next phase>

NOT NEEDED YET:
<future work that should not block the next phase>
```

## Rules

- Never mark a human-owned item complete from file existence alone.
- Never mark a phase complete without verification.
- Never erase historical status. Update it.
- Record blockers explicitly.
- Keep this file small and factual.
