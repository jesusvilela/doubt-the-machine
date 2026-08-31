from __future__ import annotations

import asyncio
import json

from api.gengatewai.mcp_server import _is_loopback_host, mcp
from api.gengatewai.models import MAX_REVIEW_RECORDS


def run_mcp(coro):
    return asyncio.run(coro)


def test_mcp_lists_expected_tools_and_resources() -> None:
    tools = run_mcp(mcp.list_tools())
    resources = run_mcp(mcp.list_resources())

    assert {tool.name for tool in tools} >= {
        "healthz",
        "get_doubt_the_machine_contract",
        "evaluate_doubt_gate",
        "validate_experiment_001_records",
        "get_experiment_001_contract",
    }
    assert {str(resource.uri) for resource in resources} >= {
        "gengatewai://doubt-the-machine/contract",
        "gengatewai://experiments/001-seeded-errors",
    }


def test_mcp_evaluates_gate_without_truth_verdict() -> None:
    result = run_mcp(
        mcp.call_tool(
            "evaluate_doubt_gate",
            {
                "claim": "Experiment 001 proves the framework is generally safer.",
                "artifact_origin": "agent",
                "reviewer_type": "agent",
                "external_claim": True,
                "gate": {"CLAIM": "general safety claim"},
            },
        )
    )

    assert result.is_error is False
    body = result.structured_content
    assert body["verification_effort"] == "high"
    assert body["missing_gate_fields"] == ["FAILURE", "EVIDENCE", "TEST", "REVERSAL"]
    assert body["does_not_decide_truth"] is True
    assert "verdict" not in body
    assert any("does not decide" in warning for warning in body["warnings"])


def test_mcp_resource_preserves_endpoint_matrix() -> None:
    payloads = run_mcp(mcp.read_resource("gengatewai://experiments/001-seeded-errors"))
    body = json.loads(list(payloads)[0].content)

    assert [cell["label"] for cell in body["endpoint_matrix"]["cells"]] == [
        "human→human",
        "human→agent",
        "agent→human",
        "agent→agent",
    ]
    assert body["endpoint_matrix"]["per_reviewer_cohort_endpoint_cells"]["agent"] == [
        "human→agent",
        "agent→agent",
    ]
    assert body["sample_plan"]["full_crossed_endpoint_reviews_if_both_cohorts_run"] == 864


def valid_record() -> dict[str, object]:
    return {
        "task_id": "task-1",
        "task_family": "code_review",
        "condition": "doubt_gate",
        "variant_id": "variant-a",
        "artifact_origin": "human",
        "reviewer_id": "reviewer-1",
        "reviewer_type": "agent",
        "cohort_id": "agent-cohort-001",
        "seeded_defect_count": 2,
        "important_defect_count": 1,
        "important_defects_caught": 1,
        "important_defects_escaped": 0,
        "false_alarms": 0,
        "accepted": 1,
        "reversed_after_evidence": 0,
        "external_checks": 3,
        "review_minutes": 9.5,
        "notes": "",
    }


def test_mcp_validates_experiment_records() -> None:
    result = run_mcp(mcp.call_tool("validate_experiment_001_records", {"records": [valid_record()]}))

    assert result.is_error is False
    assert result.structured_content == {
        "valid": True,
        "accepted_rows": 1,
        "error_count": 0,
        "errors_truncated": False,
        "errors": [],
    }


def test_mcp_rejects_oversized_record_batch_without_crashing() -> None:
    result = run_mcp(
        mcp.call_tool(
            "validate_experiment_001_records",
            {"records": [valid_record()] * (MAX_REVIEW_RECORDS + 1)},
        )
    )

    assert result.is_error is False
    body = result.structured_content
    assert body["valid"] is False
    assert body["does_not_decide_truth"] is True
    assert any("records" in error["location"] for error in body["errors"])


def test_streamable_http_host_policy_is_loopback_only() -> None:
    assert _is_loopback_host("127.0.0.1") is True
    assert _is_loopback_host("::1") is True
    assert _is_loopback_host("localhost") is True
    assert _is_loopback_host("0.0.0.0") is False
    assert _is_loopback_host("192.168.1.10") is False
    assert _is_loopback_host("example.com") is False
