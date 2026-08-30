from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from api.gengatewai.contracts import (
    API_VERSION,
    SERVICE_NAME,
    experiment_summary,
    framework_contract,
)
from api.gengatewai.models import (
    GateEvaluationRequest,
    GateEvaluationResponse,
    ReviewRecordsValidationRequest,
    ReviewRecordsValidationResponse,
)
from api.gengatewai.service import evaluate_gate, load_preregistration, validate_record_payloads

app = FastAPI(
    title="GenGatewAI",
    version=API_VERSION,
    summary="Deterministic API exposing the Doubt the Machine verification gate.",
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"service": SERVICE_NAME, "version": API_VERSION, "status": "ok"}


@app.get("/v1/gates/doubt-the-machine")
def get_doubt_the_machine() -> dict[str, Any]:
    return framework_contract()


@app.post("/v1/gates/doubt-the-machine/evaluate", response_model=GateEvaluationResponse)
def evaluate_doubt_gate(request: GateEvaluationRequest) -> GateEvaluationResponse:
    return evaluate_gate(request)


@app.post("/v1/gates/doubt-the-machine/review-records/validate", response_model=ReviewRecordsValidationResponse)
def validate_review_records(request: ReviewRecordsValidationRequest) -> ReviewRecordsValidationResponse:
    return validate_record_payloads(request)


@app.get("/v1/experiments/001-seeded-errors")
def get_experiment_001() -> dict[str, Any]:
    return experiment_summary(load_preregistration())
