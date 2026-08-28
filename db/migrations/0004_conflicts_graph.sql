-- 0004: contradictions and the in-Postgres knowledge graph
-- Invariant 7: every contradiction retains BOTH claims. No row is ever deleted to
-- simplify an answer; PERMANENTLY_CONTESTED is a first-class result.
CREATE TABLE IF NOT EXISTS contradictions (
    id                  BIGSERIAL PRIMARY KEY,
    claim_a_id          BIGINT NOT NULL REFERENCES claims(id) ON DELETE RESTRICT,
    claim_b_id          BIGINT NOT NULL REFERENCES claims(id) ON DELETE RESTRICT,
    label               conflict_label NOT NULL,
    rationale           TEXT,
    scope               TEXT,
    classifier_version  TEXT NOT NULL,
    -- Evidence confidence is recorded separately and must NOT determine the label
    -- (invariant 6 / Contribution B).
    evidence_confidence REAL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT contradictions_distinct_claims CHECK (claim_a_id <> claim_b_id),
    CONSTRAINT contradictions_pair_uniq UNIQUE (claim_a_id, claim_b_id, classifier_version),
    CONSTRAINT contradictions_conf_range CHECK (
        evidence_confidence IS NULL
        OR (evidence_confidence >= 0 AND evidence_confidence <= 1)
    )
);
CREATE INDEX IF NOT EXISTS contradictions_label_idx ON contradictions (label);

-- Graph lives in PostgreSQL. Traversal uses recursive SQL. No Neo4j (CLAUDE.md §7).
CREATE TABLE IF NOT EXISTS nodes (
    id         BIGSERIAL PRIMARY KEY,
    kind       node_kind NOT NULL,
    ref_id     BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT nodes_ref_uniq UNIQUE (kind, ref_id)
);

CREATE TABLE IF NOT EXISTS edges (
    id          BIGSERIAL PRIMARY KEY,
    src_node_id BIGINT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    dst_node_id BIGINT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    rel         TEXT NOT NULL,
    t_start     DATE,
    t_end       DATE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT edges_uniq UNIQUE (src_node_id, dst_node_id, rel),
    CONSTRAINT edges_interval_valid CHECK (t_end IS NULL OR t_start IS NULL OR t_end >= t_start)
);
CREATE INDEX IF NOT EXISTS edges_src_idx ON edges (src_node_id, rel);
CREATE INDEX IF NOT EXISTS edges_dst_idx ON edges (dst_node_id, rel);
