#!/usr/bin/env python3
"""Fail when the repository's Rule 0 self-audit contract silently regresses."""

from __future__ import annotations

import csv
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.gengatewai import contracts as api_contracts  # noqa: E402

REQUIRED = [
    "FALSIFIERS.md",
    "GRAVEYARD.md",
    "EVIDENCE.md",
    "API.md",
    "MCP.md",
    ".codex/config.toml",
    "retired.json",
    "assets/doubt-the-machine.svg",
    "experiments/001-seeded-errors/README.md",
    "experiments/001-seeded-errors/preregistration.json",
    "experiments/001-seeded-errors/results.csv",
    "api/gengatewai/contracts.py",
    "api/gengatewai/app.py",
    "api/gengatewai/service.py",
    "api/gengatewai/openai_compat.py",
    "api/gengatewai/local_models.py",
    "api/gengatewai/mcp_server.py",
    "skills/doubt-the-machine-api/SKILL.md",
    "skills/doubt-the-machine-api/references/api-contract.md",
]

EXPECTED_RESULTS_COLUMNS = [
    "task_id",
    "task_family",
    "condition",
    "variant_id",
    "artifact_origin",
    "reviewer_id",
    "reviewer_type",
    "cohort_id",
    "seeded_defect_count",
    "important_defect_count",
    "important_defects_caught",
    "important_defects_escaped",
    "false_alarms",
    "accepted",
    "reversed_after_evidence",
    "external_checks",
    "review_minutes",
    "notes",
]

REQUIRED_PREREG = {
    "task_id",
    "claim",
    "specification",
    "implementation",
    "metric",
    "tests",
    "controls",
    "preregistration",
    "sample_plan",
    "effect_region",
    "seed_realism_audit",
    "evidence",
    "round_trip",
    "result",
}

ALLOWED_CONDITIONS = {"ordinary_control", "active_placebo", "doubt_gate"}
ALLOWED_REVIEWER_TYPES = {"human", "agent"}
ALLOWED_ARTIFACT_ORIGINS = {"human", "agent"}
EXPECTED_ENDPOINT_CELL_LABELS = {"human→human", "human→agent", "agent→human", "agent→agent"}
EXPECTED_PER_COHORT_ENDPOINT_CELLS = {
    "human": {"human→human", "agent→human"},
    "agent": {"human→agent", "agent→agent"},
}
BOOLEAN_FIELDS = {"accepted", "reversed_after_evidence"}
NONNEGATIVE_INTEGER_FIELDS = {
    "seeded_defect_count",
    "important_defect_count",
    "important_defects_caught",
    "important_defects_escaped",
    "false_alarms",
    "external_checks",
}


def fail(message: str) -> None:
    raise SystemExit(f"Rule 0 contract failed: {message}")


def load_json(relative: str) -> dict:
    try:
        value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {relative}: {exc}")
    if not isinstance(value, dict):
        fail(f"{relative} must contain a JSON object")
    return value


def endpoint_cell_labels(cells: object) -> set[str]:
    if not isinstance(cells, list):
        return set()
    labels: set[str] = set()
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        if cell.get("artifact_origin") not in ALLOWED_ARTIFACT_ORIGINS:
            continue
        if cell.get("reviewer_type") not in ALLOWED_REVIEWER_TYPES:
            continue
        labels.add(str(cell.get("label", "")))
    return labels


def validate_retired_surfaces() -> None:
    ledger = load_json("retired.json")
    entries = ledger.get("entries")
    if not isinstance(entries, list) or not entries:
        fail("retired.json must contain a non-empty entries list")

    graveyard = (ROOT / "GRAVEYARD.md").read_text(encoding="utf-8")
    for entry in entries:
        if not isinstance(entry, dict):
            fail("each retired.json entry must be an object")
        retired = entry.get("retired")
        replacement = str(entry.get("replacement", "")).strip()
        forbid_in = entry.get("forbid_in")
        if not isinstance(retired, list) or not retired or not replacement:
            fail("each retired entry needs retired wording and a replacement")
        if not isinstance(forbid_in, list) or not forbid_in:
            fail("each retired entry needs at least one forbidden surface")

        # The correction history must preserve at least one full retired wording.
        if not any(str(phrase) in graveyard for phrase in retired):
            fail(f"graveyard does not preserve retirement evidence for {entry.get('id', 'unknown')}")

        for relative in forbid_in:
            path = ROOT / str(relative)
            if not path.is_file():
                fail(f"retirement ledger references missing surface: {relative}")
            text = path.read_text(encoding="utf-8")
            for phrase in retired:
                if str(phrase) in text:
                    fail(f"retired wording reintroduced in {relative}: {phrase}")


def validate_readme_and_poster() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "**Rule 0:** apply this framework to itself." not in readme[:1200]:
        fail("README must state the governing Rule 0 near the top")
    if "this README was assembled with AI assistance. Doubt it too." not in readme[-1200:]:
        fail("README must retain the AI-assistance disclosure footer")
    if "| 0 |" in readme:
        fail("local panel Rule 0 rows were retired; use reflexive checks instead")

    poster = (ROOT / "assets/doubt-the-machine.svg").read_text(encoding="utf-8")
    if "Twenty-seven practical rules plus one governing Rule 0" not in poster:
        fail("poster description must reflect 27 panel rules plus one global Rule 0")
    if "v1.2" not in poster:
        fail("poster must carry the post-self-audit v1.2 marker")
    if "Re-sample; don’t call it independent" not in poster:
        fail("poster must preserve the non-independence caveat for re-sampling")


def validate_preregistration() -> None:
    prereg = load_json("experiments/001-seeded-errors/preregistration.json")
    missing = sorted(REQUIRED_PREREG - prereg.keys())
    if missing:
        fail(f"preregistration missing top-level fields: {', '.join(missing)}")

    gate = prereg.get("preregistration", {})
    for field in ("prediction", "primary_metric", "uncertainty_method", "kill_condition", "stop_condition", "promotion_rule"):
        if not str(gate.get(field, "")).strip():
            fail(f"preregistration.{field} must be non-empty")

    sample = prereg.get("sample_plan", {})
    if sample.get("scorable_reviews_per_cohort") != 432:
        fail("Experiment 001 fixed sample must remain 432 scorable reviews per cohort (two artifact-origin blocks)")
    if sample.get("reviews_per_condition") != 144:
        fail("Experiment 001 must retain 144 reviews per condition")
    if sample.get("reviews_per_family_per_condition") != 36:
        fail("Experiment 001 must retain 36 reviews per family per condition")
    if sample.get("reviews_per_family_per_condition_per_origin") != 18:
        fail("Experiment 001 must retain 18 reviews per family, condition, and artifact-origin cell")
    if set(sample.get("artifact_origin_values", [])) != ALLOWED_ARTIFACT_ORIGINS:
        fail("Experiment 001 must cross both artifact-origin sides: human and agent")
    if set(sample.get("reviewer_type_values", [])) != ALLOWED_REVIEWER_TYPES:
        fail("Experiment 001 must preserve both reviewer endpoint sides: human and agent")
    if endpoint_cell_labels(sample.get("endpoint_cells")) != EXPECTED_ENDPOINT_CELL_LABELS:
        fail("Experiment 001 must preserve the four human/agent endpoint cells")
    cohort_cells = sample.get("per_reviewer_cohort_endpoint_cells", {})
    if not isinstance(cohort_cells, dict) or {
        cohort: set(cohort_cells.get(cohort, [])) for cohort in EXPECTED_PER_COHORT_ENDPOINT_CELLS
    } != EXPECTED_PER_COHORT_ENDPOINT_CELLS:
        fail("Experiment 001 must preserve the per-cohort endpoint-cell mapping")
    if sample.get("full_crossed_endpoint_reviews_if_both_cohorts_run") != 864:
        fail("Experiment 001 full human/agent crossed endpoint plan must remain 864 reviews")
    if sample.get("minimum_distinct_reviewer_ids", 0) < 12:
        fail("Experiment 001 requires at least 12 distinct reviewer IDs per cohort")
    if sample.get("optional_stopping") is not False:
        fail("Experiment 001 forbids optional stopping")
    if set(sample.get("conditions", [])) != ALLOWED_CONDITIONS:
        fail("Experiment 001 must retain ordinary, active-placebo, and Doubt-gate conditions")

    effect = prereg.get("effect_region", {})
    if effect.get("minimum_absolute_escape_reduction_vs_each_comparator") != 0.10:
        fail("minimum practical escape reduction must remain 10 percentage points")
    if effect.get("maximum_false_alarm_increase_vs_each_comparator") != 0.10:
        fail("maximum allowed false-alarm increase must remain 10 percentage points")
    if effect.get("primary_intervals_must_exclude_zero_benefit") is not True:
        fail("primary intervals must exclude zero benefit for promotion")

    seed_audit = prereg.get("seed_realism_audit", {})
    if seed_audit.get("minimum_non_author_judges_per_seed", 0) < 2:
        fail("seed realism requires at least two non-author judges per seed")
    if seed_audit.get("post_outcome_seed_rewriting") is not False:
        fail("seed rewriting after outcomes begin is forbidden")

    if prereg.get("result", {}).get("status_after") not in {"H", "M", "R"}:
        fail("Experiment 001 status must remain H, M, or R; it cannot become proof by checklist")


def validate_api_contract() -> None:
    if tuple(api_contracts.GATE_FIELDS) != ("CLAIM", "FAILURE", "EVIDENCE", "TEST", "REVERSAL"):
        fail("GenGatewAI API contract must preserve the five Doubt gate fields")
    if set(api_contracts.CONDITIONS) != ALLOWED_CONDITIONS:
        fail("GenGatewAI API contract must preserve Experiment 001 condition values")
    if set(api_contracts.ENDPOINT_VALUES) != ALLOWED_ARTIFACT_ORIGINS:
        fail("GenGatewAI API contract must preserve human/agent endpoint values")
    if endpoint_cell_labels(list(api_contracts.ENDPOINT_CELLS)) != EXPECTED_ENDPOINT_CELL_LABELS:
        fail("GenGatewAI API contract must preserve the four human/agent endpoint cells")

    sample = api_contracts.SAMPLE_PLAN
    if sample.get("scorable_reviews_per_cohort") != 432:
        fail("GenGatewAI API contract must preserve the 432-review per-cohort sample")
    if sample.get("reviews_per_condition") != 144:
        fail("GenGatewAI API contract must preserve 144 reviews per condition")
    if sample.get("reviews_per_family_per_condition") != 36:
        fail("GenGatewAI API contract must preserve 36 reviews per family per condition")
    if sample.get("reviews_per_family_per_condition_per_origin") != 18:
        fail("GenGatewAI API contract must preserve 18 reviews per family, condition, and origin")
    if set(sample.get("artifact_origin_values", [])) != ALLOWED_ARTIFACT_ORIGINS:
        fail("GenGatewAI API contract must preserve both artifact-origin endpoint values")
    if set(sample.get("reviewer_type_values", [])) != ALLOWED_REVIEWER_TYPES:
        fail("GenGatewAI API contract must preserve both reviewer endpoint values")
    if endpoint_cell_labels(list(sample.get("endpoint_cells", []))) != EXPECTED_ENDPOINT_CELL_LABELS:
        fail("GenGatewAI API contract must preserve the endpoint matrix")
    if sample.get("full_crossed_endpoint_reviews_if_both_cohorts_run") != 864:
        fail("GenGatewAI API contract must preserve the full crossed endpoint sample")

    if api_contracts.OPENAI_COMPATIBLE_RUNNER_MODEL != "gengatewai/doubt-runner":
        fail("OpenAI-compatible runner model id must remain stable")
    if tuple(api_contracts.OPENAI_COMPATIBLE_ENDPOINTS) != ("/v1/models", "/v1/chat/completions", "/v1/local-models"):
        fail("OpenAI-compatible runner endpoints must remain stable")
    if tuple(api_contracts.LOCAL_MODEL_PROVIDERS) != ("lmstudio", "ollama"):
        fail("OpenAI-compatible runner must preserve LM Studio and Ollama providers")
    if tuple(api_contracts.LOCAL_MODEL_DISCOVERY_MODES) != ("off", "localhost", "lan"):
        fail("OpenAI-compatible runner must preserve off/localhost/lan discovery modes")

    app_text = (ROOT / "api/gengatewai/app.py").read_text(encoding="utf-8")
    runner_text = (ROOT / "api/gengatewai/openai_compat.py").read_text(encoding="utf-8")
    local_models_text = (ROOT / "api/gengatewai/local_models.py").read_text(encoding="utf-8")
    api_doc = (ROOT / "API.md").read_text(encoding="utf-8")
    skill = (ROOT / "skills/doubt-the-machine-api/SKILL.md").read_text(encoding="utf-8")
    reference = (ROOT / "skills/doubt-the-machine-api/references/api-contract.md").read_text(encoding="utf-8")
    for required in (
        "/v1/models",
        "/v1/chat/completions",
        "/v1/local-models",
        "gengatewai/doubt-runner",
        "does not decide whether the claim is true",
    ):
        if required not in app_text + runner_text + api_doc + skill + reference:
            fail(f"OpenAI-compatible runner contract missing: {required}")
    for required in (
        "GENGATEWAI_LOCAL_MODELS",
        "GENGATEWAI_LAN_OLLAMA_BASE_URLS",
        "127.0.0.1:1234",
        "127.0.0.1:11434",
        "LAN Ollama autodetection is enabled",
    ):
        if required not in local_models_text + api_doc + reference:
            fail(f"local model autodetect contract missing: {required}")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for required in (".env", ".env.*", ".gengatewai.local*", "local-lab*"):
        if required not in gitignore:
            fail(f"local lab detail pattern missing from .gitignore: {required}")
    if "does_not_call_external_models_by_default" not in runner_text + api_doc + reference + str(api_contracts.framework_contract()):
        fail("OpenAI-compatible runner must document that local/external calls are disabled by default")


def validate_mcp_contract() -> None:
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    if "mcp>=2.1,<3" not in requirements:
        fail("requirements.txt must include the MCP SDK dependency")

    mcp_server = (ROOT / "api/gengatewai/mcp_server.py").read_text(encoding="utf-8")
    mcp_doc = (ROOT / "MCP.md").read_text(encoding="utf-8")
    skill = (ROOT / "skills/doubt-the-machine-api/SKILL.md").read_text(encoding="utf-8")
    reference = (ROOT / "skills/doubt-the-machine-api/references/api-contract.md").read_text(encoding="utf-8")
    codex_config = tomllib.loads((ROOT / ".codex/config.toml").read_text(encoding="utf-8"))
    mcp_servers = codex_config.get("mcp_servers", {})
    gengatewai_server = mcp_servers.get("gengatewai_doubt_the_machine", {})

    if "from mcp.server import MCPServer" not in mcp_server:
        fail("MCP server must use the official MCP SDK server")
    if "streamable-http" not in mcp_server or "stdio" not in mcp_server:
        fail("MCP server must preserve stdio and streamable-http transport options")
    if gengatewai_server.get("command") != "python":
        fail("Codex MCP config must launch the server with python")
    if gengatewai_server.get("args") != ["-m", "api.gengatewai.mcp_server"]:
        fail("Codex MCP config must launch api.gengatewai.mcp_server")
    if gengatewai_server.get("cwd") != ".":
        fail("Codex MCP config must run from the repository root")
    if gengatewai_server.get("enabled") is not True:
        fail("Codex MCP config must keep the GenGatewAI MCP server enabled")

    expected_tools = {
        "healthz",
        "get_doubt_the_machine_contract",
        "evaluate_doubt_gate",
        "validate_experiment_001_records",
        "get_experiment_001_contract",
    }
    if set(gengatewai_server.get("enabled_tools", [])) != expected_tools:
        fail("Codex MCP config must enable exactly the expected GenGatewAI MCP tools")
    for tool_name in (
        "healthz",
        "get_doubt_the_machine_contract",
        "evaluate_doubt_gate",
        "validate_experiment_001_records",
        "get_experiment_001_contract",
    ):
        if f"def {tool_name}" not in mcp_server:
            fail(f"MCP server missing tool: {tool_name}")
        if tool_name not in mcp_doc:
            fail(f"MCP.md missing tool documentation: {tool_name}")
        if tool_name not in reference:
            fail(f"skill API reference missing MCP tool: {tool_name}")

    for uri in (
        "gengatewai://doubt-the-machine/contract",
        "gengatewai://experiments/001-seeded-errors",
    ):
        if uri not in mcp_server:
            fail(f"MCP server missing resource: {uri}")
        if uri not in mcp_doc:
            fail(f"MCP.md missing resource documentation: {uri}")
        if uri not in reference:
            fail(f"skill API reference missing MCP resource: {uri}")

    if "does not decide whether the claim is true" not in mcp_server:
        fail("MCP server must preserve the no-truth-verdict instruction")
    if "MCP workflow" not in skill:
        fail("skill must document the MCP workflow")


def validate_active_falsifiers() -> None:
    falsifiers = (ROOT / "FALSIFIERS.md").read_text(encoding="utf-8")
    if "preregistered utility criterion" in falsifiers:
        fail("FALSIFIERS.md reintroduced the retired undefined utility criterion")
    if "separate Pareto coordinate" not in falsifiers:
        fail("FALSIFIERS.md must preserve review cost as a separate Pareto coordinate")


def validate_results() -> None:
    results_path = ROOT / "experiments/001-seeded-errors/results.csv"
    with results_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_RESULTS_COLUMNS:
            fail("results.csv schema changed without updating the contract checker")

        for line_number, row in enumerate(reader, start=2):
            if row["condition"] not in ALLOWED_CONDITIONS:
                fail(f"results.csv:{line_number} invalid condition")
            if row["reviewer_type"] not in ALLOWED_REVIEWER_TYPES:
                fail(f"results.csv:{line_number} reviewer_type must be human or agent")
            if row["artifact_origin"] not in ALLOWED_ARTIFACT_ORIGINS:
                fail(f"results.csv:{line_number} artifact_origin must be human or agent")
            for field in ("task_id", "task_family", "variant_id", "reviewer_id", "cohort_id"):
                if not row[field].strip():
                    fail(f"results.csv:{line_number} missing {field}")

            parsed: dict[str, int] = {}
            for field in NONNEGATIVE_INTEGER_FIELDS:
                try:
                    value = int(row[field])
                except ValueError:
                    fail(f"results.csv:{line_number} {field} must be an integer")
                if value < 0:
                    fail(f"results.csv:{line_number} {field} must be non-negative")
                parsed[field] = value

            for field in BOOLEAN_FIELDS:
                if row[field] not in {"0", "1"}:
                    fail(f"results.csv:{line_number} {field} must be 0 or 1")

            try:
                minutes = float(row["review_minutes"])
            except ValueError:
                fail(f"results.csv:{line_number} review_minutes must be numeric")
            if minutes < 0:
                fail(f"results.csv:{line_number} review_minutes must be non-negative")

            if parsed["important_defect_count"] > parsed["seeded_defect_count"]:
                fail(f"results.csv:{line_number} important_defect_count exceeds seeded_defect_count")
            if parsed["important_defects_caught"] + parsed["important_defects_escaped"] != parsed["important_defect_count"]:
                fail(f"results.csv:{line_number} caught + escaped must equal important_defect_count")


def main() -> None:
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            fail(f"missing required artifact: {relative}")

    validate_retired_surfaces()
    validate_readme_and_poster()
    validate_preregistration()
    validate_active_falsifiers()
    validate_api_contract()
    validate_mcp_contract()
    validate_results()

    print("Rule 0 contract: PASS")


if __name__ == "__main__":
    main()
