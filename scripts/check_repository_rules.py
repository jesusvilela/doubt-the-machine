#!/usr/bin/env python3
"""Validate live GitHub repository rules against the checked-in governance contract."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "repository-rules-contract.json"
API_ROOT = "https://api.github.com"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_json(url: str, token: str | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "doubt-the-machine-repository-rules-auditor",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {exc.code} for {url}: {body[:500]}") from exc


def fetch_live_rulesets(repository: str, token: str | None = None) -> list[dict[str, Any]]:
    summary_url = f"{API_ROOT}/repos/{repository}/rulesets?per_page=100"
    summaries = fetch_json(summary_url, token)
    if not isinstance(summaries, list):
        raise RuntimeError("GitHub rulesets response must be a list")

    details: list[dict[str, Any]] = []
    for summary in summaries:
        ruleset_id = summary.get("id")
        if not ruleset_id:
            continue
        detail = fetch_json(f"{API_ROOT}/repos/{repository}/rulesets/{ruleset_id}", token)
        if isinstance(detail, dict):
            details.append(detail)
    return details


def rule_map(ruleset: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for rule in ruleset.get("rules", []):
        if isinstance(rule, dict) and isinstance(rule.get("type"), str):
            result[rule["type"]] = rule
    return result


def includes_ref(ruleset: dict[str, Any], target_ref: str) -> bool:
    conditions = ruleset.get("conditions", {})
    ref_name = conditions.get("ref_name", {}) if isinstance(conditions, dict) else {}
    includes = ref_name.get("include", []) if isinstance(ref_name, dict) else []
    return target_ref in includes


def has_always_bypass(ruleset: dict[str, Any]) -> bool:
    return any(
        isinstance(actor, dict) and actor.get("bypass_mode") == "always"
        for actor in ruleset.get("bypass_actors", [])
    )


def status_contexts(rule: dict[str, Any]) -> set[str]:
    parameters = rule.get("parameters", {})
    checks = parameters.get("required_status_checks", []) if isinstance(parameters, dict) else []
    contexts: set[str] = set()
    for check in checks:
        if isinstance(check, dict) and isinstance(check.get("context"), str):
            contexts.add(check["context"])
    return contexts


def evaluate_named_ruleset(
    rulesets: list[dict[str, Any]],
    spec: dict[str, Any],
    *,
    expected_target: str = "branch",
) -> list[str]:
    errors: list[str] = []
    expected_name = spec["ruleset"]
    candidates = [r for r in rulesets if r.get("name") == expected_name]
    if len(candidates) != 1:
        return [f"expected exactly one active ruleset named {expected_name!r}; found {len(candidates)}"]

    ruleset = candidates[0]
    if ruleset.get("enforcement") != "active":
        errors.append(f"{expected_name}: enforcement must be active")
    if ruleset.get("target") != expected_target:
        errors.append(f"{expected_name}: target must be {expected_target!r}")
    if not includes_ref(ruleset, spec["target_ref"]):
        errors.append(f"{expected_name}: must include {spec['target_ref']!r}")

    rules = rule_map(ruleset)
    required_types = set(spec.get("required_rule_types", []))
    missing_types = sorted(required_types - set(rules))
    if missing_types:
        errors.append(f"{expected_name}: missing rule types: {', '.join(missing_types)}")

    if not spec.get("allow_always_bypass", False) and has_always_bypass(ruleset):
        errors.append(f"{expected_name}: always-bypass actors are forbidden")

    pull_request = rules.get("pull_request")
    if pull_request and spec.get("require_review_thread_resolution"):
        params = pull_request.get("parameters", {})
        if params.get("required_review_thread_resolution") is not True:
            errors.append(f"{expected_name}: review-thread resolution must be required")

    status_rule = rules.get("required_status_checks")
    if status_rule:
        params = status_rule.get("parameters", {})
        required_checks = set(spec.get("required_status_checks", []))
        missing_checks = sorted(required_checks - status_contexts(status_rule))
        if missing_checks:
            errors.append(f"{expected_name}: missing required checks: {', '.join(missing_checks)}")
        if spec.get("require_up_to_date") and params.get("strict_required_status_checks_policy") is not True:
            errors.append(f"{expected_name}: strict/up-to-date status-check policy must be enabled")

    return errors


def evaluate_rulesets(rulesets: list[dict[str, Any]], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for branch_name, spec in contract.get("branches", {}).items():
        branch_errors = evaluate_named_ruleset(rulesets, spec, expected_target="branch")
        errors.extend(f"{branch_name}: {message}" for message in branch_errors)

    tag_spec = contract.get("release_tags")
    if isinstance(tag_spec, dict):
        tag_errors = evaluate_named_ruleset(rulesets, tag_spec, expected_target=tag_spec.get("target", "tag"))
        errors.extend(f"release_tags: {message}" for message in tag_errors)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--repository", help="owner/name; defaults to contract.repository or GITHUB_REPOSITORY")
    parser.add_argument("--snapshot", type=Path, help="read detailed rulesets from JSON instead of calling GitHub")
    args = parser.parse_args()

    contract = load_json(args.contract)
    repository = args.repository or os.getenv("GITHUB_REPOSITORY") or contract.get("repository")
    if not repository:
        print("Repository rules contract failed: repository is not configured", file=sys.stderr)
        return 2

    if args.snapshot:
        rulesets = load_json(args.snapshot)
    else:
        try:
            rulesets = fetch_live_rulesets(repository, os.getenv("GITHUB_TOKEN"))
        except Exception as exc:  # fail closed: an unreadable control plane is not verified
            print(f"Repository rules contract failed: {exc}", file=sys.stderr)
            return 2

    if not isinstance(rulesets, list):
        print("Repository rules contract failed: ruleset snapshot must be a list", file=sys.stderr)
        return 2

    errors = evaluate_rulesets(rulesets, contract)
    if errors:
        print("Repository rules contract: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository rules contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
