-- 0002: documents and passages (provenance backbone)
CREATE TABLE IF NOT EXISTS documents (
    id             BIGSERIAL PRIMARY KEY,
    source         TEXT NOT NULL,              -- registry source id, e.g. 'uk_hansard'
    title          TEXT NOT NULL,
    date           DATE,                       -- publication / sitting date
    language       TEXT NOT NULL,              -- BCP-47, e.g. 'en', 'hi'
    url            TEXT,
    archive_id     TEXT,
    sha256         TEXT NOT NULL,              -- hash of the immutable raw file
    retrieved_at   TIMESTAMPTZ NOT NULL,
    license_note   TEXT,
    raw_path       TEXT NOT NULL,              -- path under data/raw (immutable)
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT documents_sha256_uniq UNIQUE (sha256)
);
CREATE INDEX IF NOT EXISTS documents_source_date_idx ON documents (source, date);
CREATE INDEX IF NOT EXISTS documents_language_idx ON documents (language);

-- One speaker intervention = one passage (CLAUDE.md §11).
-- Long interventions split at paragraph boundaries keep turn_index and gain sub_index.
CREATE TABLE IF NOT EXISTS passages (
    id             BIGSERIAL PRIMARY KEY,
    document_id    BIGINT NOT NULL REFERENCES documents(id) ON DELETE RESTRICT,
    speaker        TEXT,
    speaker_role   TEXT,
    turn_index     INTEGER NOT NULL,
    sub_index      INTEGER NOT NULL DEFAULT 0,
    language       TEXT NOT NULL,
    text           TEXT NOT NULL,
    char_start     INTEGER NOT NULL,           -- offset into the parsed document text
    char_end       INTEGER NOT NULL,
    is_procedural  BOOLEAN NOT NULL DEFAULT FALSE,
    embedding      vector(768),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT passages_span_valid CHECK (char_end > char_start),
    CONSTRAINT passages_turn_uniq UNIQUE (document_id, turn_index, sub_index)
);
CREATE INDEX IF NOT EXISTS passages_document_idx ON passages (document_id);
CREATE INDEX IF NOT EXISTS passages_language_idx ON passages (language);
-- Lexical search for exact historical terms.
CREATE INDEX IF NOT EXISTS passages_text_fts_idx
    ON passages USING GIN (to_tsvector('english', text));
CREATE INDEX IF NOT EXISTS passages_text_trgm_idx
    ON passages USING GIN (text gin_trgm_ops);
