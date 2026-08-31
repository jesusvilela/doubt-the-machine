from __future__ import annotations

from scripts.acaf_ambigator import Ambigator, Outcome, summarize


def test_acaf_span_has_declared_catch_and_pass_families() -> None:
    mutations = list(Ambigator().sweep(1))
    assert len(mutations) == 24
    assert sum(mutation.must_catch for mutation in mutations) == 17
    assert sum(not mutation.must_catch for mutation in mutations) == 7
    assert len({mutation.family for mutation in mutations}) == 24


def test_acaf_summary_keeps_escape_and_false_alarm_as_separate_coordinates() -> None:
    outcomes = [
        Outcome("must-catch", 0, True, "bad mutation", False, "PASS", "escaped"),
        Outcome("must-pass", 0, False, "benign mutation", True, "FAIL", "false_alarm"),
    ]
    summary = summarize(outcomes)

    assert summary["escape_rate"] == 1.0
    assert summary["false_alarm_rate"] == 1.0
    assert "score" not in summary
    assert "utility" not in summary


def test_operational_meaning_edit_is_explicitly_a_benign_control() -> None:
    mutations = {mutation.family: mutation for mutation in Ambigator().sweep(1)}
    assert mutations["benign_meaning_edit"].must_catch is False
    assert mutations["rule_retitle"].must_catch is True
    assert mutations["graveyard_erasure"].must_catch is True
    assert mutations["codex_approval_widening"].must_catch is True
