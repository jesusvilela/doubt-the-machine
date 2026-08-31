from __future__ import annotations

from fastapi.testclient import TestClient

from api.gengatewai.app import app

client = TestClient(app)


def _payload(gate: dict[str, str]) -> dict[str, object]:
    return {
        "claim": "The change is ready to merge.",
        "artifact_origin": "agent",
        "reviewer_type": "human",
        "uncertainty": "low",
        "consequence": "low",
        "reversibility": "easy",
        "gate": gate,
    }


def test_complete_form_is_explicitly_not_substance_assessed() -> None:
    response = client.post(
        "/v1/gates/doubt-the-machine/evaluate",
        json=_payload(
            {
                "CLAIM": ".",
                "FAILURE": ".",
                "EVIDENCE": ".",
                "TEST": ".",
                "REVERSAL": ".",
            }
        ),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["missing_gate_fields"] == []
    assert body["gate_form_complete"] is True
    assert body["gate_substance_assessed"] is False
    assert body["ceremony_warnings"]
    assert any("Field completion is not verification" in warning for warning in body["warnings"])
    assert body["does_not_decide_truth"] is True


def test_ceremonial_evidence_is_warned_not_rejected_or_scored() -> None:
    response = client.post(
        "/v1/gates/doubt-the-machine/evaluate",
        json=_payload(
            {
                "CLAIM": "ready",
                "FAILURE": "none",
                "EVIDENCE": "none, I made it up",
                "TEST": "none",
                "REVERSAL": "impossible",
            }
        ),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["gate_form_complete"] is True
    assert body["gate_substance_assessed"] is False
    assert any("EVIDENCE looks like a placeholder" in warning for warning in body["ceremony_warnings"])
    assert any("REVERSAL looks like a placeholder" in warning for warning in body["ceremony_warnings"])
    assert body["next_required_action"] == "run_required_checks"


def test_observable_short_evidence_does_not_trigger_anchor_warning() -> None:
    response = client.post(
        "/v1/gates/doubt-the-machine/evaluate",
        json=_payload(
            {
                "CLAIM": "typo only",
                "FAILURE": "meaning drift",
                "EVIDENCE": "pytest -q: 21 passed",
                "TEST": "pytest -q",
                "REVERSAL": "git revert",
            }
        ),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["gate_form_complete"] is True
    assert body["gate_substance_assessed"] is False
    assert body["ceremony_warnings"] == []


def test_repeating_claim_as_evidence_is_warned() -> None:
    claim = "The change is ready to merge."
    response = client.post(
        "/v1/gates/doubt-the-machine/evaluate",
        json={
            **_payload(
                {
                    "CLAIM": claim,
                    "FAILURE": "regression",
                    "EVIDENCE": claim,
                    "TEST": "pytest -q",
                    "REVERSAL": "git revert",
                }
            ),
            "claim": claim,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert any("EVIDENCE repeats the claim" in warning for warning in body["ceremony_warnings"])


def test_incomplete_form_remains_distinct_from_substance_boundary() -> None:
    response = client.post(
        "/v1/gates/doubt-the-machine/evaluate",
        json=_payload({"CLAIM": "bounded claim"}),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["gate_form_complete"] is False
    assert body["gate_substance_assessed"] is False
    assert body["next_required_action"] == "complete_gate"
