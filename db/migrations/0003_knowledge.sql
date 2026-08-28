-- 0003: entities, events, claims, evidence links
-- Entity identity is independent of language (CLAUDE.md §18).
CREATE TABLE IF NOT EXISTS entities (
    id             BIGSERIAL PRIMARY KEY,
    type           entity_type NOT NULL,
    canonical_name TEXT NOT NULL,
    aliases        TEXT[] NOT NULL DEFAULT '{}',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT entities_canonical_uniq UNIQUE (type, canonical_name)
);

-- Event identity is independent of language. Event time = when it happened.
CREATE TABLE IF NOT EXISTS events (
    id             BIGSERIAL PRIMARY KEY,
    label          TEXT NOT NULL,
    t_start        DATE,
    t_end          DATE,
    granularity    time_granularity NOT NULL DEFAULT 'unknown',
    is_interval    BOOLEAN NOT NULL DEFAULT FALSE,
    language       TEXT,                       -- language of the label, not of the event
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT events_interval_valid CHECK (t_end IS NULL OR t_start IS NULL OR t_end >= t_start)
);
CREATE INDEX IF NOT EXISTS events_time_idx ON events (t_start, t_end);

-- asserted_at = when the claim was made (NOT when the described event happened).
CREATE TABLE IF NOT EXISTS claims (
    id                    BIGSERIAL PRIMARY KEY,
    text                  TEXT NOT NULL,
    claim_type            TEXT NOT NULL,
    subject_entity_id     BIGINT REFERENCES entities(id) ON DELETE SET NULL,
    event_id              BIGINT REFERENCES events(id) ON DELETE SET NULL,
    asserted_at           DATE,
    language              TEXT NOT NULL,
    extraction_confidence REAL,                -- extraction confidence, NOT historical truth
    extractor_model       TEXT,
    prompt_version        TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT claims_conf_range CHECK (
        extraction_confidence IS NULL
        OR (extraction_confidence >= 0 AND extraction_confidence <= 1)
    )
);
CREATE INDEX IF NOT EXISTS claims_event_idx ON claims (event_id);
CREATE INDEX IF NOT EXISTS claims_entity_idx ON claims (subject_entity_id);
CREATE INDEX IF NOT EXISTS claims_asserted_at_idx ON claims (asserted_at);

-- Invariant 1/2: every claim needs >=1 evidence link to a real passage + exact span.
CREATE TABLE IF NOT EXISTS evidence_links (
    id          BIGSERIAL PRIMARY KEY,
    claim_id    BIGINT NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    passage_id  BIGINT NOT NULL REFERENCES passages(id) ON DELETE RESTRICT,
    relation    TEXT NOT NULL,                 -- e.g. 'supports', 'mentions', 'contradicts'
    char_start  INTEGER NOT NULL,              -- offsets relative to passages.text
    char_end    INTEGER NOT NULL,
    support     REAL,                          -- strength of support of this passage
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT evidence_span_valid CHECK (char_end > char_start),
    CONSTRAINT evidence_support_range CHECK (
        support IS NULL OR (support >= 0 AND support <= 1)
    )
);
CREATE INDEX IF NOT EXISTS evidence_claim_idx ON evidence_links (claim_id);
CREATE INDEX IF NOT EXISTS evidence_passage_idx ON evidence_links (passage_id);
