from __future__ import annotations

from scripts.check_repository_rules import evaluate_rulesets


REQUIRED_CHECKS = [
    "self-audit-contract",
    "container-contract",
    "analyze (python)",
    "analyze (javascript-typescript)",
]

CONTRACT = {
    "branches": {
        "dev": {
            "ruleset": "dev-integration-gate",
            "target_ref": "refs/heads/dev",
            "required_rule_types": ["deletion", "non_fast_forward", "pull_request", "required_status_checks"],
            "required_status_checks": REQUIRED_CHECKS,
            "require_up_to_date": True,
            "require_review_thread_resolution": True,
            "allow_always_bypass": False,
        },
        "main": {
            "ruleset": "main-release-gate",
            "target_ref": "refs/heads/main",
            "required_rule_types": ["deletion", "non_fast_forward", "pull_request", "required_status_checks"],
            "required_status_checks": REQUIRED_CHECKS,
            "require_up_to_date": True,
            "require_review_thread_resolution": True,
            "allow_always_bypass": False,
        },
    },
    "release_tags": {
        "ruleset": "release-tags-immutable",
        "target": "tag",
        "target_ref": "refs/tags/v*",
        "required_rule_types": ["deletion", "non_fast_forward"],
        "allow_always_bypass": False,
    },
}


def branch_ruleset(name: str, ref: str) -> dict:
    return {
        "name": name,
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": [ref], "exclude": []}},
        "bypass_actors": [],
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {"type": "pull_request", "parameters": {"required_review_thread_resolution": True}},
            {
                "type": "required_status_checks",
                "parameters": {
                    "strict_required_status_checks_policy": True,
                    "required_status_checks": [{"context": context} for context in REQUIRED_CHECKS],
                },
            },
        ],
    }


def good_rulesets() -> list[dict]:
    return [
        branch_ruleset("dev-integration-gate", "refs/heads/dev"),
        branch_ruleset("main-release-gate", "refs/heads/main"),
        {
            "name": "release-tags-immutable",
            "target": "tag",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
            "bypass_actors": [],
            "rules": [{"type": "deletion"}, {"type": "non_fast_forward"}],
        },
    ]


def test_repository_rules_contract_accepts_complete_configuration() -> None:
    assert evaluate_rulesets(good_rulesets(), CONTRACT) == []


def test_repository_rules_contract_rejects_always_bypass() -> None:
    rulesets = good_rulesets()
    rulesets[0]["bypass_actors"] = [{"actor_type": "RepositoryRole", "actor_id": 5, "bypass_mode": "always"}]
    errors = evaluate_rulesets(rulesets, CONTRACT)
    assert any("always-bypass actors are forbidden" in error for error in errors)


def test_repository_rules_contract_rejects_missing_check_and_wrong_tag_target() -> None:
    rulesets = good_rulesets()
    status_rule = next(rule for rule in rulesets[1]["rules"] if rule["type"] == "required_status_checks")
    status_rule["parameters"]["required_status_checks"].pop()
    rulesets[2]["target"] = "branch"
    errors = evaluate_rulesets(rulesets, CONTRACT)
    assert any("analyze (javascript-typescript)" in error for error in errors)
    assert any("target must be 'tag'" in error for error in errors)
