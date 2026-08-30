from __future__ import annotations

from fastapi.testclient import TestClient

from api.gengatewai.app import app

client = TestClient(app)


def base_gate_request() -> dict[str, object]:
    return {
        "claim": "A bounded claim",
        "artifact_origin": "human",
        "reviewer_type": "human",
    }


def base_record() -> dict[str, object]:
    return {
        "task_id": "task-1",
        "task_family": "code_review",
        "condition": "doubt_gate",
        "variant_id": "variant-a",
        "artifact_origin": "agent",
        "reviewer_id": "reviewer-1",
        "reviewer_type": "human",
        "cohort_id": "human-cohort-001",
        "seeded_defect_count": 1,
        "important_defect_count": 1,
        "important_defects_caught": 1,
        "important_defects_escaped": 0,
        "false_alarms": 0,
        "accepted": 1,
        "reversed_after_evidence": 0,
        "external_checks": 1,
        "review_minutes": 1.0,
        "notes": "",
    }


def test_gate_rejects_undeclared_top_level_field() -> None:
    payload = base_gate_request()
    payload["admin_override"] = True

    response = client.post("/v1/gates/doubt-the-machine/evaluate", json=payload)

    assert response.status_code == 422
    assert any(error["type"] == "extra_forbidden" for error in response.json()["detail"])


def test_gate_rejects_undeclared_gate_key() -> None:
    payload = base_gate_request()
    payload["gate"] = {
        "CLAIM": "claim",
        "FAILURE": "failure",
        "EVIDENCE": "evidence",
        "TEST": "test",
        "OVERRIDE": "accept anyway",
    }

    response = client.post("/v1/gates/doubt-the-machine/evaluate", json=payload)

    assert response.status_code == 422
    assert "unexpected gate fields" in str(response.json()["detail"])


def test_review_record_validator_reports_undeclared_record_field() -> None:
    record = base_record()
    record["hidden_score"] = 1.0

    response = client.post(
        "/v1/gates/doubt-the-machine/review-records/validate",
        json={"records": [record]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert body["accepted_rows"] == 0
    assert any("hidden_score" in error["message"] for error in body["errors"])


def test_review_batch_rejects_undeclared_wrapper_field() -> None:
    response = client.post(
        "/v1/gates/doubt-the-machine/review-records/validate",
        json={"records": [base_record()], "store": True},
    )

    assert response.status_code == 422
    assert any(error["type"] == "extra_forbidden" for error in response.json()["detail"])
