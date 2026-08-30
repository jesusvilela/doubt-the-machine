from __future__ import annotations

from fastapi.testclient import TestClient

from api.gengatewai.app import app
from api.gengatewai.contracts import OPENAI_COMPATIBLE_RUNNER_MODEL
from api.gengatewai.local_models import LOCAL_MODELS_MODE_ENV
from api.gengatewai.models import MAX_CLAIM_LENGTH, MAX_OPENAI_MESSAGES, MAX_REVIEW_RECORDS

client = TestClient(app)


def valid_record() -> dict[str, object]:
    return {
        "task_id": "task-1",
        "task_family": "code_review",
        "condition": "doubt_gate",
        "variant_id": "variant-a",
        "artifact_origin": "agent",
        "reviewer_id": "reviewer-1",
        "reviewer_type": "human",
        "cohort_id": "human-cohort-001",
        "seeded_defect_count": 2,
        "important_defect_count": 1,
        "important_defects_caught": 1,
        "important_defects_escaped": 0,
        "false_alarms": 0,
        "accepted": 1,
        "reversed_after_evidence": 0,
        "external_checks": 2,
        "review_minutes": 12.5,
        "notes": "",
    }


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"service": "GenGatewAI", "version": "0.1.0", "status": "ok"}


def test_framework_contract_exposes_gate_and_endpoints() -> None:
    response = client.get("/v1/gates/doubt-the-machine")
    assert response.status_code == 200
    body = response.json()
    assert body["rule_0"].startswith("Apply this framework")
    assert body["gate_fields"] == ["CLAIM", "FAILURE", "EVIDENCE", "TEST", "REVERSAL"]
    assert body["endpoint_values"]["artifact_origin"] == ["human", "agent"]
    assert body["endpoint_matrix"]["reviewer_type_values"] == ["human", "agent"]
    assert [cell["label"] for cell in body["endpoint_matrix"]["cells"]] == [
        "human→human",
        "human→agent",
        "agent→human",
        "agent→agent",
    ]
    assert body["endpoint_matrix"]["per_reviewer_cohort_endpoint_cells"]["human"] == ["human→human", "agent→human"]
    assert body["conditions"] == ["ordinary_control", "active_placebo", "doubt_gate"]
    assert body["openai_compatible_runner"]["model"] == OPENAI_COMPATIBLE_RUNNER_MODEL
    assert body["openai_compatible_runner"]["endpoints"] == ["/v1/models", "/v1/chat/completions", "/v1/local-models"]
    assert body["openai_compatible_runner"]["streaming"] is False
    assert body["openai_compatible_runner"]["local_model_providers"] == ["lmstudio", "ollama"]
    assert body["openai_compatible_runner"]["local_model_discovery_default"] == "off"
    assert body["openai_compatible_runner"]["lan_autodetect"] == "opt-in only"
    assert body["openai_compatible_runner"]["does_not_call_external_models_by_default"] is True
    assert body["does_not_decide_truth"] is True


def test_openai_compatible_models_endpoint_lists_runner() -> None:
    response = client.get("/v1/models")
    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "list"
    assert body["data"][0]["id"] == OPENAI_COMPATIBLE_RUNNER_MODEL
    assert body["data"][0]["object"] == "model"


def test_local_model_capacity_is_off_by_default(monkeypatch) -> None:
    monkeypatch.delenv(LOCAL_MODELS_MODE_ENV, raising=False)

    response = client.get("/v1/local-models")
    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is False
    assert body["mode"] == "off"
    assert body["models"] == []


def test_openai_compatible_chat_completion_runs_doubt_gate() -> None:
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": OPENAI_COMPATIBLE_RUNNER_MODEL,
            "messages": [
                {"role": "system", "content": "Use the Doubt loop."},
                {
                    "role": "user",
                    "content": "CLAIM: This benchmark proves the framework is generally safe.\nFAILURE: Benchmark leakage.",
                },
            ],
            "metadata": {
                "artifact_origin": "agent",
                "reviewer_type": "agent",
                "external_claim": True,
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "chat.completion"
    assert body["model"] == OPENAI_COMPATIBLE_RUNNER_MODEL
    assert body["choices"][0]["finish_reason"] == "stop"
    content = body["choices"][0]["message"]["content"]
    assert "DOUBT → MEASURE → TEST → REVERT → REPEAT" in content
    assert "Verification effort: high" in content
    assert "Missing gate fields: EVIDENCE, TEST, REVERSAL" in content
    assert "does not decide whether the claim is true" in content
    assert body["usage"]["total_tokens"] >= body["usage"]["completion_tokens"] >= 1


def test_openai_compatible_chat_completion_accepts_metadata_gate() -> None:
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": OPENAI_COMPATIBLE_RUNNER_MODEL,
            "messages": [{"role": "user", "content": "Please run the gate."}],
            "metadata": {
                "artifact_origin": "human",
                "reviewer_type": "human",
                "uncertainty": "low",
                "consequence": "low",
                "reversibility": "easy",
                "gate": {
                    "CLAIM": "typo only",
                    "FAILURE": "meaning drift",
                    "EVIDENCE": "diff",
                    "TEST": "read rendered section",
                    "REVERSAL": "git revert",
                },
            },
        },
    )

    assert response.status_code == 200
    content = response.json()["choices"][0]["message"]["content"]
    assert "Claim under review: typo only" in content
    assert "Verification effort: light" in content
    assert "Missing gate fields: none" in content


def test_openai_compatible_chat_completion_rejects_unsupported_features() -> None:
    bad_model = client.post(
        "/v1/chat/completions",
        json={"model": "gpt-5.6", "messages": [{"role": "user", "content": "claim"}]},
    )
    assert bad_model.status_code == 404

    streaming = client.post(
        "/v1/chat/completions",
        json={"model": OPENAI_COMPATIBLE_RUNNER_MODEL, "stream": True, "messages": [{"role": "user", "content": "claim"}]},
    )
    assert streaming.status_code == 400


def test_openai_compatible_chat_completion_rejects_oversized_message_batch() -> None:
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": OPENAI_COMPATIBLE_RUNNER_MODEL,
            "messages": [{"role": "user", "content": "claim"}] * (MAX_OPENAI_MESSAGES + 1),
        },
    )

    assert response.status_code == 422


def test_evaluate_high_effort_external_claim_keeps_missing_fields() -> None:
    response = client.post(
        "/v1/gates/doubt-the-machine/evaluate",
        json={
            "claim": "This benchmark proves the framework is generally safer.",
            "artifact_origin": "agent",
            "reviewer_type": "agent",
            "external_claim": True,
            "gate": {"CLAIM": "general safety claim"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["verification_effort"] == "high"
    assert body["missing_gate_fields"] == ["FAILURE", "EVIDENCE", "TEST", "REVERSAL"]
    assert body["next_required_action"] == "complete_gate"
    assert body["does_not_decide_truth"] is True


def test_evaluate_light_effort_for_low_risk_complete_gate() -> None:
    response = client.post(
        "/v1/gates/doubt-the-machine/evaluate",
        json={
            "claim": "Fix a typo in the README.",
            "artifact_origin": "human",
            "reviewer_type": "human",
            "uncertainty": "low",
            "consequence": "low",
            "reversibility": "easy",
            "gate": {
                "CLAIM": "typo only",
                "FAILURE": "could alter meaning",
                "EVIDENCE": "diff inspection",
                "TEST": "read rendered section",
                "REVERSAL": "git revert",
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["verification_effort"] == "light"
    assert body["missing_gate_fields"] == []
    assert body["next_required_action"] == "run_required_checks"


def test_evaluate_rejects_bad_endpoint_value() -> None:
    response = client.post(
        "/v1/gates/doubt-the-machine/evaluate",
        json={
            "claim": "A claim",
            "artifact_origin": "ai_generated",
            "reviewer_type": "human",
        },
    )
    assert response.status_code == 422


def test_evaluate_rejects_oversized_claim() -> None:
    response = client.post(
        "/v1/gates/doubt-the-machine/evaluate",
        json={
            "claim": "x" * (MAX_CLAIM_LENGTH + 1),
            "artifact_origin": "human",
            "reviewer_type": "human",
        },
    )
    assert response.status_code == 422


def test_validate_review_records_accepts_valid_row() -> None:
    response = client.post(
        "/v1/gates/doubt-the-machine/review-records/validate",
        json={"records": [valid_record()]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body == {"valid": True, "accepted_rows": 1, "errors": []}


def test_validate_review_records_reports_bad_rows() -> None:
    bad_condition = valid_record()
    bad_condition["condition"] = "new_condition"
    bad_arithmetic = valid_record()
    bad_arithmetic["important_defects_escaped"] = 1
    response = client.post(
        "/v1/gates/doubt-the-machine/review-records/validate",
        json={"records": [bad_condition, bad_arithmetic]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert body["accepted_rows"] == 0
    assert any("condition" in error["message"] for error in body["errors"])
    assert any("important_defects_caught + important_defects_escaped" in error["message"] for error in body["errors"])


def test_validate_review_records_rejects_oversized_batch() -> None:
    response = client.post(
        "/v1/gates/doubt-the-machine/review-records/validate",
        json={"records": [valid_record()] * (MAX_REVIEW_RECORDS + 1)},
    )
    assert response.status_code == 422


def test_experiment_endpoint_exposes_tock_003_sample_plan() -> None:
    response = client.get("/v1/experiments/001-seeded-errors")
    assert response.status_code == 200
    body = response.json()
    assert body["sample_plan"]["scorable_reviews_per_cohort"] == 432
    assert body["sample_plan"]["artifact_origin_values"] == ["human", "agent"]
    assert body["sample_plan"]["reviewer_type_values"] == ["human", "agent"]
    assert [cell["label"] for cell in body["sample_plan"]["endpoint_cells"]] == [
        "human→human",
        "human→agent",
        "agent→human",
        "agent→agent",
    ]
    assert body["sample_plan"]["full_crossed_endpoint_reviews_if_both_cohorts_run"] == 864
    assert body["does_not_establish_general_effectiveness"] is True
