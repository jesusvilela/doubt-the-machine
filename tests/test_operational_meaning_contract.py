from __future__ import annotations

import json
from pathlib import Path

from scripts.acaf_meaning_matrix import MeaningOutcome, _load_rules, summarize
from scripts.rule0_surface_contract import _meaning_errors, validate_readme_structure

ROOT = Path(__file__).resolve().parents[1]


def test_all_27_rules_have_directional_meaning_contracts() -> None:
    payload = json.loads((ROOT / "rules.json").read_text(encoding="utf-8"))
    assert payload["version"] == 3
    rules = _load_rules(ROOT)
    assert len(rules) == 27

    for panel, rule_number, rule in rules:
        contract = rule["meaning_contract"]
        paraphrase = contract["paraphrase_example"]
        inversion = contract["inversion_example"]
        assert _meaning_errors(paraphrase, contract) == [], (panel, rule_number, rule["readme"])
        assert _meaning_errors(inversion, contract), (panel, rule_number, rule["readme"])
        assert any(
            phrase.casefold() in inversion.casefold() for phrase in contract["forbidden_phrases"]
        ), (panel, rule_number, rule["readme"])


def test_live_readme_satisfies_all_meaning_contracts() -> None:
    validate_readme_structure(ROOT)


def test_meaning_matrix_keeps_escape_and_false_alarm_separate() -> None:
    outcomes = [
        MeaningOutcome("r1", 1, 1, "inversion", True, False, "PASS", "escaped"),
        MeaningOutcome("r1", 1, 1, "paraphrase", False, True, "FAIL", "false_alarm"),
    ]
    summary = summarize(outcomes)
    assert summary["inversion_escape_rate"] == 1.0
    assert summary["paraphrase_false_alarm_rate"] == 1.0
    assert "score" not in summary
    assert "utility" not in summary
