from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from api.gengatewai.experiment_amendments import apply_experiment_001_amendment
from scripts.exp001_pilot_contract import PilotContractError, ROOT, validate_exp001_pilot_contract


PREREG = ROOT / "experiments" / "001-seeded-errors" / "preregistration.json"
AMENDMENT = ROOT / "experiments" / "001-seeded-errors" / "amendment-2026-08-31-pilot.json"


def _fixture_root(tmp_path: Path) -> Path:
    target = tmp_path / "repo" / "experiments" / "001-seeded-errors"
    target.mkdir(parents=True)
    (target / "preregistration.json").write_bytes(PREREG.read_bytes())
    (target / "amendment-2026-08-31-pilot.json").write_bytes(AMENDMENT.read_bytes())
    return tmp_path / "repo"


def test_current_exp001_pilot_contract_passes() -> None:
    validate_exp001_pilot_contract()


def test_pilot_amendment_rejects_effectiveness_promotion(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    path = root / "experiments" / "001-seeded-errors" / "amendment-2026-08-31-pilot.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["design_role"]["confirmatory_effectiveness_decision_allowed"] = True
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(PilotContractError, match="cannot make a confirmatory effectiveness decision"):
        validate_exp001_pilot_contract(root)


def test_pilot_amendment_rejects_rewriting_original_preregistration(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    path = root / "experiments" / "001-seeded-errors" / "preregistration.json"
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(PilotContractError, match="original preregistration bytes changed"):
        validate_exp001_pilot_contract(root)


def test_effective_overlay_preserves_historical_preregistration() -> None:
    original = json.loads(PREREG.read_text(encoding="utf-8"))
    amendment = json.loads(AMENDMENT.read_text(encoding="utf-8"))
    before = copy.deepcopy(original)

    effective = apply_experiment_001_amendment(original, amendment)

    assert original == before
    assert effective["design_role"]["name"] == "pilot"
    assert effective["design_role"]["confirmatory_effectiveness_decision_allowed"] is False
    assert effective["power"]["confirmatory_power_claim"] is False
    assert effective["effect_region"]["role"] == "descriptive_reference_only"
    assert effective["result"]["effectiveness_status_after"] == "H"
    assert "may not promote the Doubt gate as effective" in effective["preregistration"]["promotion_rule"]
