from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import ValidationError

from api.gengatewai.contracts import (
    API_VERSION,
    FRAMEWORK_SLUG,
    GATE_FIELDS,
    SERVICE_NAME,
    experiment_summary,
    framework_contract,
)
from api.gengatewai.models import (
    GateEvaluationRequest,
    GateEvaluationResponse,
    ReviewRecord,
    ReviewRecordValidationError,
    ReviewRecordsValidationRequest,
    ReviewRecordsValidationResponse,
)

ROOT = Path(__file__).resolve().parents[2]
PREREGISTRATION_PATH = ROOT / "experiments" / "001-seeded-errors" / "preregistration.json"

app = FastAPI(
    title="GenGatewAI",
    version=API_VERSION,
    summary="Deterministic API exposing the Doubt the Machine verification gate.",
)


def load_preregistration() -> dict[str, Any]:
    return json.loads(PREREGISTRATION_PATH.read_text(encoding="utf-8"))


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"service": SERVICE_NAME, "version": API_VERSION, "status": "ok"}


@app.get("/v1/gates/doubt-the-machine")
def get_doubt_the_machine() -> dict[str, Any]:
    return framework_contract()


def normalize_gate(gate: dict[str, str | None]) -> dict[str, str]:
    return {str(key).upper(): str(value).strip() for key, value in gate.items() if value is not None}


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


@app.post("/v1/gates/doubt-the-machine/evaluate", response_model=GateEvaluationResponse)
def evaluate_doubt_gate(request: GateEvaluationRequest) -> GateEvaluationResponse:
    effort, reasons = evaluate_effort(request)
    gate = normalize_gate(request.gate)
    missing = [field for field in GATE_FIELDS if not gate.get(field)]

    warnings = ["This API does not decide whether the claim is true or acceptable."]
    if missing:
        warnings.append("Gate record is incomplete; missing fields must be filled by the reviewer.")
    if request.artifact_origin.value == "agent" and request.reviewer_type.value == "agent":
        warnings.append("agent→agent review still needs evidence independent of the model path.")

    if missing:
        next_action = "complete_gate"
    elif effort == "high":
        next_action = "preregister_or_independent_review"
    else:
        next_action = "run_required_checks"

    return GateEvaluationResponse(
        framework=FRAMEWORK_SLUG,
        verification_effort=effort,
        reasons=reasons,
        missing_gate_fields=missing,
        warnings=warnings,
        next_required_action=next_action,
    )


@app.post("/v1/gates/doubt-the-machine/review-records/validate", response_model=ReviewRecordsValidationResponse)
def validate_review_records(request: ReviewRecordsValidationRequest) -> ReviewRecordsValidationResponse:
    errors: list[ReviewRecordValidationError] = []
    accepted_rows = 0

    for row_index, record in enumerate(request.records, start=1):
        try:
            ReviewRecord.model_validate(record)
        except ValidationError as exc:
            for error in exc.errors():
                location = ".".join(str(part) for part in error["loc"])
                message = f"{location}: {error['msg']}" if location else str(error["msg"])
                errors.append(ReviewRecordValidationError(row_index=row_index, message=message))
        else:
            accepted_rows += 1

    return ReviewRecordsValidationResponse(valid=not errors, accepted_rows=accepted_rows, errors=errors)


@app.get("/v1/experiments/001-seeded-errors")
def get_experiment_001() -> dict[str, Any]:
    return experiment_summary(load_preregistration())
