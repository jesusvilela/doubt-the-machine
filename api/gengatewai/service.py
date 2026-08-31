from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from api.gengatewai.contracts import FRAMEWORK_SLUG, GATE_FIELDS
from api.gengatewai.experiment_amendments import apply_experiment_001_amendment
from api.gengatewai.models import (
    MAX_VALIDATION_ERRORS,
    MAX_VALIDATION_ERRORS_PER_ROW,
    GateEvaluationRequest,
    GateEvaluationResponse,
    ReviewRecord,
    ReviewRecordValidationError,
    ReviewRecordsValidationRequest,
    ReviewRecordsValidationResponse,
)

ROOT = Path(__file__).resolve().parents[2]
PREREGISTRATION_PATH = ROOT / "experiments" / "001-seeded-errors" / "preregistration.json"

UNASSESSED_GATE_DIMENSIONS = (
    "claim_scope_and_operational_meaning",
    "failure_mode_relevance",
    "evidence_quality_and_independence",
    "test_falsifiability_and_execution",
    "reversal_feasibility",
)
LOW_INFORMATION_EXACT = {".", "..", "...", "?", "none", "n/a", "na", "unknown", "tbd", "todo"}


def load_preregistration() -> dict[str, Any]:
    original = json.loads(PREREGISTRATION_PATH.read_text(encoding="utf-8"))
    return apply_experiment_001_amendment(original)


def normalize_gate(gate: dict[str, str | None]) -> dict[str, str]:
    return {str(key).upper(): str(value).strip() for key, value in gate.items() if value is not None}


def _ceremony_signals(gate: dict[str, str]) -> list[str]:
    """Flag only obvious low-information placeholders; do not score truth or adequacy."""
    signals: list[str] = []
    for field in GATE_FIELDS:
        raw = gate.get(field, "").strip()
        if not raw:
            continue
        normalized = " ".join(raw.lower().split()).strip(" .!?:;")
        if (
            raw in {".", "..", "...", "?"}
            or normalized in LOW_INFORMATION_EXACT
            or normalized.startswith("none,")
            or normalized.startswith("none ")
        ):
            signals.append(f"{field}:low_information_placeholder")
    return signals


def evaluate_effort(request: GateEvaluationRequest) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if request.experiment_or_metric:
        reasons.append("experiments and metrics require high verification effort")
    if request.external_claim:
        reasons.append("external claims require high verification effort")
    if request.consequence.value == "high":
        reasons.append("high consequence requires high verification effort")
    if request.reversibility.value in {"hard", "irreversible"}:
        reasons.append("hard or irreversible rollback requires high verification effort")
    if reasons:
        return "high", reasons

    if request.active_rule_or_evidence_change:
        reasons.append("rule/evidence changes require standard verification effort")
    if request.consequence.value == "medium":
        reasons.append("medium consequence requires standard verification effort")
    if request.uncertainty.value in {"medium", "high"}:
        reasons.append("medium/high uncertainty requires standard verification effort")
    if request.reversibility.value == "moderate":
        reasons.append("moderate rollback requires standard verification effort")
    if reasons:
        return "standard", reasons

    return "light", ["low-consequence, low-uncertainty, easily reversible change"]


def evaluate_gate(request: GateEvaluationRequest) -> GateEvaluationResponse:
    effort, reasons = evaluate_effort(request)
    gate = normalize_gate(request.gate)
    missing = [field for field in GATE_FIELDS if not gate.get(field)]
    form_complete = not missing
    ceremony_signals = _ceremony_signals(gate)

    warnings = [
        "Gate form completeness checks only whether text is present; it does not assess substantive adequacy.",
        "This API does not decide whether the claim is true or acceptable and does not clear it for action.",
    ]
    if missing:
        warnings.append("Gate form is incomplete; missing fields still need reviewer input.")
    if ceremony_signals:
        warnings.append(
            "Obvious low-information placeholder signals were detected; they may be ceremonial and require substance review."
        )
    if request.artifact_origin.value == "agent":
        warnings.append(
            "An agent-origin artifact still needs evidence independent of the generation path; reviewer type alone does not establish independence."
        )
    if request.reviewer_type.value == "agent":
        warnings.append(
            "An agent reviewer is not automatically an independent witness; disclose model/tool lineage when independence matters."
        )

    if missing:
        next_action = "complete_gate_form"
    elif effort == "high":
        next_action = "assess_gate_substance_and_preregister_or_independent_review"
    else:
        next_action = "assess_gate_substance"

    return GateEvaluationResponse(
        framework=FRAMEWORK_SLUG,
        verification_effort=effort,
        reasons=reasons,
        missing_gate_fields=missing,
        gate_form_complete=form_complete,
        unassessed_dimensions=list(UNASSESSED_GATE_DIMENSIONS),
        ceremony_signals=ceremony_signals,
        warnings=warnings,
        next_required_action=next_action,
    )


def validate_record_payloads(request: ReviewRecordsValidationRequest) -> ReviewRecordsValidationResponse:
    errors: list[ReviewRecordValidationError] = []
    accepted_rows = 0
    error_count = 0

    for row_index, record in enumerate(request.records, start=1):
        try:
            ReviewRecord.model_validate(record)
        except ValidationError as exc:
            row_errors = exc.errors()
            error_count += len(row_errors)
            if len(errors) >= MAX_VALIDATION_ERRORS:
                continue
            for error in row_errors[:MAX_VALIDATION_ERRORS_PER_ROW]:
                if len(errors) >= MAX_VALIDATION_ERRORS:
                    break
                location = ".".join(str(part) for part in error["loc"])
                message = f"{location}: {error['msg']}" if location else str(error["msg"])
                errors.append(ReviewRecordValidationError(row_index=row_index, message=message))
        else:
            accepted_rows += 1

    return ReviewRecordsValidationResponse(
        valid=error_count == 0,
        accepted_rows=accepted_rows,
        error_count=error_count,
        errors_truncated=error_count > len(errors),
        errors=errors,
    )
