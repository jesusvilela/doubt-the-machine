from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from api.gengatewai.app import app
from api.gengatewai.mcp_server import mcp

client = TestClient(app)


def run_mcp(coro):
    return asyncio.run(coro)


def _assert_pilot_contract(body: dict[str, object]) -> None:
    design_role = body["design_role"]
    assert design_role["name"] == "pilot"
    assert design_role["confirmatory_effectiveness_decision_allowed"] is False
    assert design_role["powered_replication_required"] is True

    power = body["power"]
    assert power["confirmatory_power_claim"] is False
    assert power["assumed_baseline_escape_probability"] is None
    assert power["assumed_reviewer_icc"] is None
    assert power["important_defect_denominator_fixed_before_pilot"] is False
    assert power["effect_region_role"] == "descriptive_reference_only"

    assert body["effect_region"]["role"] == "descriptive_reference_only"
    assert body["amendment"]["base_preregistration_blob_sha"] == "fdba76103db657896342d1d3d24a6383d347bacd"
    assert body["amendment"]["timing"]["outcomes_inspected_before_amendment"] is False
    assert body["amendment"]["timing"]["results_rows_at_amendment"] == 0
    assert body["result"]["effectiveness_status_after"] == "H"
    assert body["result"]["powered_replication_preregistration_required_before_effectiveness_decision"] is True
    assert "may not promote the Doubt gate as effective" in body["promotion_rule"]
    assert body["does_not_establish_general_effectiveness"] is True


def test_rest_experiment_001_exposes_effective_pilot_contract() -> None:
    response = client.get("/v1/experiments/001-seeded-errors")
    assert response.status_code == 200
    _assert_pilot_contract(response.json())


def test_mcp_tool_exposes_same_effective_pilot_contract() -> None:
    result = run_mcp(mcp.call_tool("get_experiment_001_contract", {}))
    assert result.is_error is False
    _assert_pilot_contract(result.structured_content)


def test_mcp_resource_exposes_same_effective_pilot_contract() -> None:
    payloads = run_mcp(mcp.read_resource("gengatewai://experiments/001-seeded-errors"))
    body = json.loads(list(payloads)[0].content)
    _assert_pilot_contract(body)
