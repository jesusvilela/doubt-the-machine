from __future__ import annotations

from typing import Any

SERVICE_NAME = "GenGatewAI"
API_VERSION = "0.1.0"
FRAMEWORK_SLUG = "doubt-the-machine"

RULE_0 = "Apply this framework to itself. Doubt it, measure it, test it, and revert it when it fails."
SCOPE = "Use this when AI output crosses the boundary from proposal into belief, decision, execution, or persistence."

DEV_LOOP = ("DOUBT", "MEASURE", "TEST", "REVERT", "REPEAT")
GATE_FIELDS = ("CLAIM", "FAILURE", "EVIDENCE", "TEST", "REVERSAL")
CONDITIONS = ("ordinary_control", "active_placebo", "doubt_gate")
ENDPOINT_VALUES = ("human", "agent")

SURFACES = (
    {
        "name": "Doubt the machine",
        "focus": "Interaction and authority",
        "default_question": "Who or what am I letting judge the claim?",
    },
    {
        "name": "Doubt the bits",
        "focus": "Information and uncertainty",
        "default_question": "What is sourced, inferred, missing, or merely fluent?",
    },
    {
        "name": "Doubt the build",
        "focus": "Execution and operations",
        "default_question": "What observed behavior proves this survives reality?",
    },
)

EVIDENCE_LEVELS = (
    {"level": "P", "name": "proved", "meaning": "definitionally closed or inspectable structural claim"},
    {"level": "M", "name": "measured", "meaning": "bounded empirical result with data, controls, and uncertainty"},
    {"level": "H", "name": "hypothesis", "meaning": "testable claim not yet adequately measured here"},
    {"level": "S", "name": "semantic/design", "meaning": "framing, architecture, slogan, or operational proposal"},
    {"level": "R", "name": "retired", "meaning": "claim or formulation killed or narrowed by evidence or contradiction"},
)

VERIFICATION_EFFORTS = {
    "light": {
        "use_when": "Wording, links, or presentation only.",
        "required_checks": ("Run the Rule 0 checker.", "Inspect every touched surface."),
    },
    "standard": {
        "use_when": "Active rules, retired-rule coverage, falsifiers, evidence ledgers, or CI checks.",
        "required_checks": (
            "Run the Rule 0 checker.",
            "Verify affected claims against their sources.",
            "Keep the rollback path explicit.",
        ),
    },
    "high": {
        "use_when": "Experiments, metrics, kill conditions, external claims, or anything that could rescue a failed result.",
        "required_checks": (
            "Preregister the claim and failure mode.",
            "Preserve controls.",
            "Require independent review.",
            "Treat insufficient precision as inconclusive.",
        ),
    },
}

SAMPLE_PLAN = {
    "scorable_reviews_per_cohort": 432,
    "conditions": CONDITIONS,
    "reviews_per_condition": 144,
    "task_families": ("factual_current", "numerical_analytical", "code_review", "summary_design"),
    "reviews_per_family_per_condition": 36,
    "artifact_origin_values": ENDPOINT_VALUES,
    "reviews_per_family_per_condition_per_origin": 18,
    "minimum_distinct_reviewer_ids": 12,
    "optional_stopping": False,
}


def framework_contract() -> dict[str, Any]:
    return {
        "service": SERVICE_NAME,
        "api_version": API_VERSION,
        "framework": FRAMEWORK_SLUG,
        "rule_0": RULE_0,
        "scope": SCOPE,
        "dev_loop": list(DEV_LOOP),
        "gate_fields": list(GATE_FIELDS),
        "surfaces": list(SURFACES),
        "verification_efforts": VERIFICATION_EFFORTS,
        "evidence_levels": list(EVIDENCE_LEVELS),
        "endpoint_values": {
            "artifact_origin": list(ENDPOINT_VALUES),
            "reviewer_type": list(ENDPOINT_VALUES),
        },
        "conditions": list(CONDITIONS),
        "does_not_decide_truth": True,
    }


def experiment_summary(preregistration: dict[str, Any]) -> dict[str, Any]:
    gate = preregistration["preregistration"]
    return {
        "task_id": preregistration["task_id"],
        "status": preregistration["claim"]["status_before"],
        "claim": preregistration["claim"],
        "conditions": list(CONDITIONS),
        "endpoint_values": {
            "artifact_origin": list(ENDPOINT_VALUES),
            "reviewer_type": list(ENDPOINT_VALUES),
        },
        "sample_plan": preregistration["sample_plan"],
        "primary_metric": gate["primary_metric"],
        "prediction": gate["prediction"],
        "kill_condition": gate["kill_condition"],
        "stop_condition": gate["stop_condition"],
        "promotion_rule": gate["promotion_rule"],
        "does_not_establish_general_effectiveness": True,
    }
