from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_001_AMENDMENT_PATH = ROOT / "experiments" / "001-seeded-errors" / "amendment-2026-08-31-pilot.json"


def load_experiment_001_amendment() -> dict[str, Any]:
    return json.loads(EXPERIMENT_001_AMENDMENT_PATH.read_text(encoding="utf-8"))


def apply_experiment_001_amendment(
    preregistration: dict[str, Any], amendment: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Return the effective Experiment 001 contract without rewriting the original preregistration."""
    amendment = amendment or load_experiment_001_amendment()
    effective = copy.deepcopy(preregistration)

    if amendment.get("applies_to") != effective.get("task_id"):
        raise ValueError("Experiment 001 amendment does not target this preregistration")

    effective["amendment"] = copy.deepcopy(amendment)
    effective["design_role"] = copy.deepcopy(amendment["design_role"])
    effective["power"] = copy.deepcopy(amendment["power"])

    effective_gate = effective.setdefault("preregistration", {})
    effective_gate.update(copy.deepcopy(amendment["effective_preregistration"]))

    effective_effect_region = effective.setdefault("effect_region", {})
    effective_effect_region.update(copy.deepcopy(amendment["effect_region"]))

    effective_result = effective.setdefault("result", {})
    effective_result["effectiveness_status_after"] = amendment["result_contract"][
        "effectiveness_status_after_pilot"
    ]
    effective_result["powered_replication_preregistration_required_before_effectiveness_decision"] = amendment[
        "result_contract"
    ]["powered_replication_preregistration_required_before_effectiveness_decision"]

    return effective
