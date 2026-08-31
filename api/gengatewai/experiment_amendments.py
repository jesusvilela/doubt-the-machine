from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_001_PREREGISTRATION_PATH = ROOT / "experiments" / "001-seeded-errors" / "preregistration.json"
EXPERIMENT_001_AMENDMENT_PATH = ROOT / "experiments" / "001-seeded-errors" / "amendment-2026-08-31-pilot.json"


def _git_blob_sha(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def load_experiment_001_amendment() -> dict[str, Any]:
    amendment = json.loads(EXPERIMENT_001_AMENDMENT_PATH.read_text(encoding="utf-8"))
    expected_blob = str(amendment.get("base_preregistration_blob_sha", ""))
    actual_blob = _git_blob_sha(EXPERIMENT_001_PREREGISTRATION_PATH)
    if not expected_blob or actual_blob != expected_blob:
        raise ValueError(
            "Experiment 001 historical preregistration no longer matches the blob pinned by its pilot amendment"
        )
    return amendment


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
