from __future__ import annotations

import itertools

from api.gengatewai.models import GateEvaluationRequest
from api.gengatewai.service import evaluate_gate

INDEPENDENCE_WARNING = (
    "Human/agent labels do not establish independent review; independence depends on evidence provenance "
    "and separation from the producing model or evidence path."
)


def _evaluate(artifact_origin: str, reviewer_type: str):
    return evaluate_gate(
        GateEvaluationRequest(
            claim="Check this claim.",
            artifact_origin=artifact_origin,
            reviewer_type=reviewer_type,
            gate={"CLAIM": "Check this claim."},
        )
    )


def test_all_human_agent_endpoint_pairs_share_the_same_independence_boundary() -> None:
    for artifact_origin, reviewer_type in itertools.product(("human", "agent"), repeat=2):
        result = _evaluate(artifact_origin, reviewer_type)
        assert INDEPENDENCE_WARNING in result.warnings
        assert not any("agent→agent review" in warning for warning in result.warnings)


def test_human_review_of_agent_artifact_is_not_mislabeled_independent() -> None:
    result = _evaluate("agent", "human")
    assert INDEPENDENCE_WARNING in result.warnings


def test_agent_review_is_not_automatically_mislabeled_correlated() -> None:
    result = _evaluate("human", "agent")
    assert INDEPENDENCE_WARNING in result.warnings
    assert not any("agent→agent review" in warning for warning in result.warnings)
