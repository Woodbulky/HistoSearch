-- Research invariant checks (CLAUDE.md §9). Each query must return ZERO rows.
-- Run with: python -m chronosgraph.db.check

-- name: claims_without_evidence (invariant 1)
SELECT c.id AS claim_id
FROM claims c
LEFT JOIN evidence_links e ON e.claim_id = c.id
WHERE e.id IS NULL;

-- name: evidence_span_outside_passage (invariant 2)
SELECT e.id AS evidence_id, e.passage_id
FROM evidence_links e
JOIN passages p ON p.id = e.passage_id
WHERE e.char_end > length(p.text) OR e.char_start < 0;

-- name: passage_span_outside_document (invariant 2)
SELECT p.id AS passage_id
FROM passages p
WHERE p.char_start < 0 OR p.char_end <= p.char_start;

-- name: event_time_more_precise_than_granularity (invariant 5)
SELECT id AS event_id, granularity
FROM events
WHERE granularity = 'year'  AND (EXTRACT(MONTH FROM t_start) <> 1 OR EXTRACT(DAY FROM t_start) <> 1)
   OR granularity = 'month' AND EXTRACT(DAY FROM t_start) <> 1;

-- name: contradiction_missing_claim (invariant 7)
SELECT ct.id AS contradiction_id
FROM contradictions ct
LEFT JOIN claims a ON a.id = ct.claim_a_id
LEFT JOIN claims b ON b.id = ct.claim_b_id
WHERE a.id IS NULL OR b.id IS NULL;

-- name: dangling_graph_node (graph integrity)
SELECT n.id AS node_id, n.kind, n.ref_id
FROM nodes n
WHERE (n.kind = 'entity'   AND NOT EXISTS (SELECT 1 FROM entities  x WHERE x.id = n.ref_id))
   OR (n.kind = 'event'    AND NOT EXISTS (SELECT 1 FROM events    x WHERE x.id = n.ref_id))
   OR (n.kind = 'claim'    AND NOT EXISTS (SELECT 1 FROM claims    x WHERE x.id = n.ref_id))
   OR (n.kind = 'document' AND NOT EXISTS (SELECT 1 FROM documents x WHERE x.id = n.ref_id))
   OR (n.kind = 'passage'  AND NOT EXISTS (SELECT 1 FROM passages  x WHERE x.id = n.ref_id));
