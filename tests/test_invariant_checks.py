from histosearch.db.check import CHECKS_PATH, parse_checks, run_checks

EXPECTED = {
    "claims_without_evidence",
    "evidence_span_outside_passage",
    "passage_span_outside_document",
    "event_time_more_precise_than_granularity",
    "contradiction_missing_claim",
    "dangling_graph_node",
}


def test_check_file_parses_into_named_queries():
    checks = dict(parse_checks(CHECKS_PATH.read_text(encoding="utf-8")))
    assert set(checks) >= EXPECTED
    for name, query in checks.items():
        assert query.upper().startswith("SELECT"), name


def test_invariants_hold_on_live_db(live_db):
    violations = {k: v for k, v in run_checks().items() if v}
    assert not violations, f"research invariant violations: {violations}"
