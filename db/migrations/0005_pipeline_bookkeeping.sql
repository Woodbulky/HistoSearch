-- 0005: vector index + reproducibility/pipeline bookkeeping

-- HNSW index for dense retrieval (CLAUDE.md §7).
CREATE INDEX IF NOT EXISTS passages_embedding_hnsw_idx
    ON passages USING hnsw (embedding vector_cosine_ops);

-- Every LLM request is cached. Key includes model + prompt version + input hash (§12).
CREATE TABLE IF NOT EXISTS llm_cache (
    cache_key      TEXT PRIMARY KEY,           -- sha256(provider|model|prompt_version|input)
    provider       TEXT NOT NULL,
    model          TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    input_hash     TEXT NOT NULL,
    request        JSONB NOT NULL,
    response       JSONB NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Persistent failures go to a log; invalid output is never silently coerced (§12).
CREATE TABLE IF NOT EXISTS extraction_failures (
    id           BIGSERIAL PRIMARY KEY,
    passage_id   BIGINT REFERENCES passages(id) ON DELETE CASCADE,
    stage        TEXT NOT NULL,
    provider     TEXT,
    model        TEXT,
    prompt_version TEXT,
    error_kind   TEXT NOT NULL,
    error_detail TEXT,
    raw_output   TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS extraction_failures_stage_idx ON extraction_failures (stage);

-- Invariant 13/14: every run records commit, config and model version.
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id           BIGSERIAL PRIMARY KEY,
    stage        TEXT NOT NULL,
    git_commit   TEXT,
    config       JSONB NOT NULL DEFAULT '{}'::jsonb,
    model_version TEXT,
    started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at  TIMESTAMPTZ,
    status       TEXT NOT NULL DEFAULT 'running'
);

-- Invariant 15: unexpected row loss between stages must be reported, not discarded.
CREATE TABLE IF NOT EXISTS stage_counts (
    id            BIGSERIAL PRIMARY KEY,
    run_id        BIGINT NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    stage         TEXT NOT NULL,
    input_count   BIGINT NOT NULL,
    output_count  BIGINT NOT NULL,
    failed_count  BIGINT NOT NULL DEFAULT 0,
    note          TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
