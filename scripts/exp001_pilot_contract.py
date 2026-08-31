#!/usr/bin/env python3
"""Validate the prospective Experiment 001 pilot amendment without rewriting its base preregistration."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PREREGISTRATION_PATH = ROOT / "experiments" / "001-seeded-errors" / "preregistration.json"
AMENDMENT_PATH = ROOT / "experiments" / "001-seeded-errors" / "amendment-2026-08-31-pilot.json"


class PilotContractError(ValueError):
    """Raised when the effective Experiment 001 pilot contract drifts."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PilotContractError(f"invalid or missing {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise PilotContractError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def _git_blob_sha(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def validate_exp001_pilot_contract(root: Path = ROOT) -> None:
    preregistration_path = root / "experiments" / "001-seeded-errors" / "preregistration.json"
    amendment_path = root / "experiments" / "001-seeded-errors" / "amendment-2026-08-31-pilot.json"
    prereg = _load_json(preregistration_path) if root == ROOT else json.loads(preregistration_path.read_text(encoding="utf-8"))
    amendment = _load_json(amendment_path) if root == ROOT else json.loads(amendment_path.read_text(encoding="utf-8"))

    if amendment.get("applies_to") != prereg.get("task_id"):
        raise PilotContractError("pilot amendment must target the exact Experiment 001 task id")
    expected_blob = str(amendment.get("base_preregistration_blob_sha", ""))
    actual_blob = _git_blob_sha(preregistration_path)
    if not expected_blob or actual_blob != expected_blob:
        raise PilotContractError(
            f"original preregistration bytes changed under the amendment: expected {expected_blob or '<missing>'}, got {actual_blob}"
        )

    timing = amendment.get("timing", {})
    if timing.get("prospective") is not True:
        raise PilotContractError("Experiment 001 amendment must remain prospective")
    if timing.get("outcomes_inspected_before_amendment") is not False:
        raise PilotContractError("pilot amendment must record that no outcomes were inspected before amendment")
    if timing.get("results_rows_at_amendment") != 0:
        raise PilotContractError("pilot amendment must preserve the measured zero-row result state at amendment time")

    role = amendment.get("design_role", {})
    if role.get("name") != "pilot":
        raise PilotContractError("Experiment 001 effective design role must remain pilot")
    if role.get("confirmatory_effectiveness_decision_allowed") is not False:
        raise PilotContractError("Experiment 001 pilot cannot make a confirmatory effectiveness decision")
    if role.get("powered_replication_required") is not True:
        raise PilotContractError("Experiment 001 must require a separately preregistered powered replication")
    if not str(role.get("reason", "")).strip() or not str(role.get("purpose", "")).strip():
        raise PilotContractError("pilot role must preserve its purpose and decidability rationale")

    power = amendment.get("power", {})
    if power.get("confirmatory_power_claim") is not False:
        raise PilotContractError("pilot must not claim confirmatory power")
    if power.get("assumed_baseline_escape_probability") is not None:
        raise PilotContractError("pilot must not invent a pre-data baseline escape probability")
    if power.get("assumed_reviewer_icc") is not None:
        raise PilotContractError("pilot must not invent a pre-data reviewer ICC")
    if power.get("important_defect_denominator_fixed_before_pilot") is not False:
        raise PilotContractError("pilot amendment must preserve that the per-defect denominator was not fixed")
    if power.get("small_cluster_confirmatory_inference_allowed") is not False:
        raise PilotContractError("pilot must not treat the minimum reviewer cluster count as confirmatory inference")
    if power.get("effect_region_role") != "descriptive_reference_only":
        raise PilotContractError("original effect region must be a descriptive planning reference in the pilot")
    planning_inputs = power.get("planning_inputs_to_estimate")
    if not isinstance(planning_inputs, list) or len(planning_inputs) < 5:
        raise PilotContractError("pilot must estimate the missing denominator/baseline/dependence/cost planning inputs")
    if not str(power.get("replication_sample_size_rule", "")).strip():
        raise PilotContractError("pilot must preserve the rule for preregistering a powered replication")

    effective = amendment.get("effective_preregistration", {})
    for field in (
        "prediction",
        "primary_metric",
        "uncertainty_method",
        "kill_condition",
        "stop_condition",
        "promotion_rule",
    ):
        if not str(effective.get(field, "")).strip():
            raise PilotContractError(f"effective_preregistration.{field} must be non-empty")
    promotion = str(effective.get("promotion_rule", ""))
    if "may not promote the Doubt gate as effective" not in promotion:
        raise PilotContractError("pilot promotion rule must explicitly forbid an effectiveness promotion")
    if "separate powered preregistration" not in promotion:
        raise PilotContractError("pilot promotion rule must require a separate powered preregistration")

    effect_region = amendment.get("effect_region", {})
    if effect_region.get("role") != "descriptive_reference_only":
        raise PilotContractError("amendment effect region must remain descriptive-reference-only")

    result_contract = amendment.get("result_contract", {})
    if result_contract.get("effectiveness_status_after_pilot") != "H":
        raise PilotContractError("pilot must leave the effectiveness claim at H rather than promote it")
    if result_contract.get("powered_replication_preregistration_required_before_effectiveness_decision") is not True:
        raise PilotContractError("effectiveness decision must require a future powered preregistration")
    required_outputs = result_contract.get("required_outputs")
    if not isinstance(required_outputs, list) or len(required_outputs) < 5:
        raise PilotContractError("pilot must preserve its required planning outputs")

    if prereg.get("result", {}).get("status_after") != "H":
        raise PilotContractError("historical preregistration must still show the pre-data H status")


if __name__ == "__main__":
    try:
        validate_exp001_pilot_contract()
    except (PilotContractError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Rule 0 contract failed: {exc}") from exc
    print("Experiment 001 pilot amendment contract: PASS")
