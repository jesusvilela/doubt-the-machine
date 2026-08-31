from __future__ import annotations

import asyncio
import itertools

from fastapi.testclient import TestClient

from api.gengatewai.app import app
from api.gengatewai.mcp_server import mcp

INDEPENDENCE_WARNING = (
    "Human/agent labels do not establish independent review; independence depends on evidence provenance "
    "and separation from the producing model or evidence path."
)

client = TestClient(app)


def _payload(artifact_origin: str, reviewer_type: str) -> dict[str, object]:
    return {
        "claim": "Check this claim.",
        "artifact_origin": artifact_origin,
        "reviewer_type": reviewer_type,
        "gate": {"CLAIM": "Check this claim."},
    }


def test_rest_all_human_agent_endpoint_pairs_share_the_same_independence_boundary() -> None:
    for artifact_origin, reviewer_type in itertools.product(("human", "agent"), repeat=2):
        response = client.post(
            "/v1/gates/doubt-the-machine/evaluate",
            json=_payload(artifact_origin, reviewer_type),
        )
        assert response.status_code == 200
        warnings = response.json()["warnings"]
        assert INDEPENDENCE_WARNING in warnings
        assert not any("agent→agent review" in warning for warning in warnings)


def test_mcp_human_review_of_agent_artifact_keeps_provenance_boundary() -> None:
    result = asyncio.run(
        mcp.call_tool(
            "evaluate_doubt_gate",
            _payload("agent", "human"),
        )
    )
    assert result.is_error is False
    warnings = result.structured_content["warnings"]
    assert INDEPENDENCE_WARNING in warnings
    assert not any("agent→agent review" in warning for warning in warnings)


def test_mcp_agent_reviewer_is_not_automatically_mislabeled_correlated() -> None:
    result = asyncio.run(
        mcp.call_tool(
            "evaluate_doubt_gate",
            _payload("human", "agent"),
        )
    )
    assert result.is_error is False
    warnings = result.structured_content["warnings"]
    assert INDEPENDENCE_WARNING in warnings
    assert not any("agent→agent review" in warning for warning in warnings)
