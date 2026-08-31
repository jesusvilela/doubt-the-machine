#!/usr/bin/env python3
"""Structural Rule 0 checks for canonical prose surfaces and retirement history."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = "rules.json"
RETIREMENT_PATH = "retired.json"
TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".html",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".py",
    ".svg",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
TEXT_FILENAMES = {"Dockerfile"}
SKIP_DIRS = {".git", ".mypy_cache", ".pytest_cache", ".venv", "__pycache__", "node_modules"}


class SurfaceContractError(ValueError):
    """Raised when a canonical prose-surface invariant is violated."""


def _load_json(root: Path, relative: str) -> dict[str, Any]:
    try:
        value = json.loads((root / relative).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SurfaceContractError(f"invalid or missing {relative}: {exc}") from exc
    if not isinstance(value, dict):
        raise SurfaceContractError(f"{relative} must contain a JSON object")
    return value


def _normalize_space(value: str) -> str:
    return " ".join(value.split())


def _normalize_semantic_text(value: str) -> str:
    """Normalize wording for low-resolution concept checks, not semantic equivalence."""
    return _normalize_space(re.sub(r"[^\w]+", " ", value.casefold(), flags=re.UNICODE))


def _contains_concept(text: str, concept: str) -> bool:
    normalized_text = _normalize_semantic_text(text)
    normalized_concept = _normalize_semantic_text(concept)
    if not normalized_concept:
        return False
    if " " in normalized_concept:
        return f" {normalized_concept} " in f" {normalized_text} "
    tokens = set(normalized_text.split())
    return normalized_concept in tokens or f"{normalized_concept}s" in tokens or f"{normalized_concept}es" in tokens


def _meaning_errors(text: str, contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = contract.get("required_concepts")
    forbidden = contract.get("forbidden_phrases")
    if not isinstance(required, list) or not required:
        return ["meaning_contract.required_concepts must be a non-empty list"]
    if not isinstance(forbidden, list) or not forbidden:
        return ["meaning_contract.forbidden_phrases must be a non-empty list"]

    for group in required:
        if not isinstance(group, list) or not group or not all(isinstance(item, str) and item.strip() for item in group):
            errors.append("meaning_contract concept groups must contain non-empty strings")
            continue
        if not any(_contains_concept(text, variant) for variant in group):
            errors.append("missing concept: " + " / ".join(group))

    for phrase in forbidden:
        if not isinstance(phrase, str) or not phrase.strip():
            errors.append("meaning_contract forbidden phrases must be non-empty strings")
            continue
        if _contains_concept(text, phrase):
            errors.append(f"forbidden inversion phrase present: {phrase}")
    return errors


def _validate_meaning_contract(rule: dict[str, Any], actual_meaning: str, label: str) -> None:
    contract = rule.get("meaning_contract")
    if not isinstance(contract, dict):
        raise SurfaceContractError(f"{label} missing meaning_contract")

    paraphrase = str(contract.get("paraphrase_example", "")).strip()
    inversion = str(contract.get("inversion_example", "")).strip()
    forbidden = contract.get("forbidden_phrases")
    if not paraphrase or not inversion:
        raise SurfaceContractError(f"{label} meaning_contract needs paraphrase_example and inversion_example")
    if not isinstance(forbidden, list) or not any(
        isinstance(phrase, str) and phrase.strip() and _contains_concept(inversion, phrase) for phrase in forbidden
    ):
        raise SurfaceContractError(f"{label} inversion_example must instantiate an explicit forbidden phrase")

    paraphrase_errors = _meaning_errors(paraphrase, contract)
    if paraphrase_errors:
        raise SurfaceContractError(
            f"{label} declared paraphrase does not satisfy its meaning contract: {paraphrase_errors[0]}"
        )

    inversion_errors = _meaning_errors(inversion, contract)
    if not inversion_errors:
        raise SurfaceContractError(f"{label} declared inversion is not rejected by its meaning contract")

    actual_errors = _meaning_errors(actual_meaning, contract)
    if actual_errors:
        raise SurfaceContractError(f"{label} operational meaning drifted: {actual_errors[0]}")


def _panel_section(readme: str, heading: str, next_heading: str | None) -> str:
    start = readme.find(heading)
    if start < 0:
        raise SurfaceContractError(f"README missing canonical panel heading: {heading}")
    if next_heading is None:
        end = readme.find("\n## ", start + len(heading))
    else:
        end = readme.find(next_heading, start + len(heading))
    if end < 0:
        end = len(readme)
    return readme[start:end]


def validate_readme_structure(root: Path = ROOT) -> None:
    mapping = _load_json(root, MAP_PATH)
    readme = (root / "README.md").read_text(encoding="utf-8")
    panels = mapping.get("panels")
    gate_fields = mapping.get("gate_fields")
    if mapping.get("version") != 3:
        raise SurfaceContractError("rules.json version must be 3 for operational-meaning contracts")
    if not isinstance(panels, list) or len(panels) != 3:
        raise SurfaceContractError("rules.json must define exactly three panels")
    if gate_fields != ["CLAIM", "FAILURE", "EVIDENCE", "TEST", "REVERSAL"]:
        raise SurfaceContractError("rules.json must preserve the five 60-second gate fields")

    headings = [str(panel.get("heading", "")) for panel in panels if isinstance(panel, dict)]
    if len(headings) != 3 or len(set(headings)) != 3:
        raise SurfaceContractError("rules.json panel headings must be unique")

    for index, panel in enumerate(panels):
        if not isinstance(panel, dict):
            raise SurfaceContractError("rules.json panels must be objects")
        rules = panel.get("rules")
        if not isinstance(rules, list) or len(rules) != 9:
            raise SurfaceContractError(f"{headings[index]} must map exactly nine rules")
        section = _panel_section(readme, headings[index], headings[index + 1] if index < 2 else None)
        rows = re.findall(
            r"^\|\s*([1-9])\s*\|\s*\*\*(.+?)\*\*\s*\|\s*(.*?)\s*\|$",
            section,
            flags=re.MULTILINE,
        )
        numbers = [int(number) for number, _, _ in rows]
        titles = [title.strip() for _, title, _ in rows]
        meanings = [meaning.strip() for _, _, meaning in rows]
        expected_titles = [str(rule.get("readme", "")).strip() for rule in rules if isinstance(rule, dict)]
        if numbers != list(range(1, 10)):
            raise SurfaceContractError(f"{headings[index]} must contain numbered rule rows 1 through 9 exactly once")
        if titles != expected_titles:
            raise SurfaceContractError(f"{headings[index]} rule titles drifted from rules.json")
        for rule_index, (rule, meaning) in enumerate(zip(rules, meanings, strict=True), start=1):
            if not isinstance(rule, dict):
                raise SurfaceContractError("rules.json rules must be objects")
            _validate_meaning_contract(rule, meaning, f"{headings[index]} rule {rule_index}")
        if "**Reflexive check:**" not in section:
            raise SurfaceContractError(f"{headings[index]} must retain its reflexive Rule 0 check")

    gate_start = readme.find("## Use it in 60 seconds")
    if gate_start < 0:
        raise SurfaceContractError("README missing the 60-second gate")
    gate_end = readme.find("\n## ", gate_start + 1)
    gate_section = readme[gate_start : gate_end if gate_end >= 0 else len(readme)]
    for position, field in enumerate(gate_fields, start=1):
        if re.search(rf"^{position}\.\s+{re.escape(field)}\b", gate_section, flags=re.MULTILINE) is None:
            raise SurfaceContractError(f"README 60-second gate missing field {position}: {field}")


def _svg_visible_text(svg: str) -> str:
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as exc:
        raise SurfaceContractError(f"poster is not valid XML: {exc}") from exc
    chunks: list[str] = []
    for element in root.iter():
        local_name = element.tag.rsplit("}", 1)[-1]
        if local_name in {"title", "desc", "text", "tspan"}:
            value = _normalize_space("".join(element.itertext()))
            if value:
                chunks.append(value)
    return _normalize_space(" ".join(chunks))


def validate_poster_structure(root: Path = ROOT) -> None:
    mapping = _load_json(root, MAP_PATH)
    poster_text = _svg_visible_text((root / "assets/doubt-the-machine.svg").read_text(encoding="utf-8"))
    panels = mapping.get("panels", [])
    expected_labels: list[str] = []
    for panel in panels:
        if not isinstance(panel, dict):
            raise SurfaceContractError("rules.json panels must be objects")
        poster_heading = str(panel.get("poster_heading", "")).strip()
        if not poster_heading or poster_heading not in poster_text:
            raise SurfaceContractError(f"poster missing panel heading: {poster_heading or '<empty>'}")
        for rule in panel.get("rules", []):
            if not isinstance(rule, dict):
                raise SurfaceContractError("rules.json rules must be objects")
            label = str(rule.get("poster", "")).strip()
            if not label:
                raise SurfaceContractError("every mapped rule needs a poster label")
            expected_labels.append(label)
    if len(expected_labels) != 27 or len(set(expected_labels)) != 27:
        raise SurfaceContractError("rules.json must define 27 unique poster rule labels")
    missing = [label for label in expected_labels if label not in poster_text]
    if missing:
        raise SurfaceContractError(f"poster missing active rule labels: {', '.join(missing[:3])}")


def _remove_json_pointer(document: Any, pointer: str) -> None:
    if not pointer.startswith("/"):
        raise SurfaceContractError(f"invalid JSON pointer exemption: {pointer}")
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]
    current = document
    for part in parts[:-1]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise SurfaceContractError(f"JSON pointer exemption does not exist: {pointer}")
    last = parts[-1]
    if isinstance(current, dict) and last in current:
        current[last] = None
    else:
        raise SurfaceContractError(f"JSON pointer exemption does not exist: {pointer}")


def _retirement_exemptions(ledger: dict[str, Any]) -> tuple[set[str], dict[str, list[str]]]:
    allow_in = ledger.get("allow_in")
    if not isinstance(allow_in, list) or not allow_in:
        raise SurfaceContractError("retired.json must define explicit allow_in exemptions")
    whole_files: set[str] = set()
    json_scopes: dict[str, list[str]] = {}
    for exemption in allow_in:
        if not isinstance(exemption, dict):
            raise SurfaceContractError("retired.json allow_in entries must be objects")
        path = str(exemption.get("path", "")).strip()
        scope = str(exemption.get("scope", "")).strip()
        reason = str(exemption.get("reason", "")).strip()
        if not path or not scope or not reason:
            raise SurfaceContractError("retired.json allow_in entries need path, scope, and reason")
        if scope == "whole_file":
            whole_files.add(path)
        elif scope.startswith("json_pointer:"):
            json_scopes.setdefault(path, []).append(scope.removeprefix("json_pointer:"))
        else:
            raise SurfaceContractError(f"unsupported retirement exemption scope: {scope}")
    return whole_files, json_scopes


def _iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_FILENAMES:
            yield path, relative.as_posix()


def validate_retired_repo_wide(root: Path = ROOT) -> None:
    ledger = _load_json(root, RETIREMENT_PATH)
    entries = ledger.get("entries")
    if not isinstance(entries, list) or not entries:
        raise SurfaceContractError("retired.json must contain a non-empty entries list")

    retired_phrases: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("retired"), list):
            raise SurfaceContractError("each retired.json entry must contain retired wording")
        retired_phrases.extend(str(phrase) for phrase in entry["retired"] if str(phrase))
    if not retired_phrases:
        raise SurfaceContractError("retired.json must contain retired phrases")

    # Correction history is part of the contract: every retired wording variant must remain
    # recoverable, not merely one representative phrase per retirement entry.
    graveyard = (root / "GRAVEYARD.md").read_text(encoding="utf-8")
    missing_history = [phrase for phrase in retired_phrases if phrase not in graveyard]
    if missing_history:
        raise SurfaceContractError(
            "graveyard does not preserve every retired wording variant: " + ", ".join(missing_history[:3])
        )

    whole_files, json_scopes = _retirement_exemptions(ledger)
    for path, relative in _iter_text_files(root):
        if relative in whole_files:
            continue
        if relative in json_scopes:
            try:
                document = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise SurfaceContractError(f"cannot apply structured retirement exemption to {relative}: {exc}") from exc
            for pointer in json_scopes[relative]:
                _remove_json_pointer(document, pointer)
            text = json.dumps(document, ensure_ascii=False, sort_keys=True)
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")
        for phrase in retired_phrases:
            if phrase in text:
                raise SurfaceContractError(
                    f"retired wording reintroduced outside an explicit historical exemption: {relative}: {phrase}"
                )


def validate_surface_contract(root: Path = ROOT) -> None:
    validate_readme_structure(root)
    validate_poster_structure(root)
    validate_retired_repo_wide(root)


if __name__ == "__main__":
    try:
        validate_surface_contract()
    except SurfaceContractError as exc:
        raise SystemExit(f"Rule 0 contract failed: {exc}") from exc
    print("Rule 0 prose-surface contract: PASS")
