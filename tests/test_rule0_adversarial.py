from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.rule0_surface_contract import (
    SurfaceContractError,
    validate_poster_structure,
    validate_readme_structure,
    validate_retired_repo_wide,
)


MAP = {
    "version": 1,
    "gate_fields": ["CLAIM", "FAILURE", "EVIDENCE", "TEST", "REVERSAL"],
    "panels": [
        {
            "heading": f"## {index} — Panel {index}",
            "poster_heading": f"Panel {index}",
            "rules": [
                {"readme": f"Rule {index}.{rule}", "poster": f"Poster {index}.{rule}"}
                for rule in range(1, 10)
            ],
        }
        for index in range(1, 4)
    ],
}


def _valid_readme() -> str:
    lines = ["# Fixture", "", "## Use it in 60 seconds"]
    for number, field in enumerate(MAP["gate_fields"], start=1):
        lines.append(f"{number}. {field} fixture")
    for panel in MAP["panels"]:
        lines += ["", panel["heading"], "", "| # | Rule | Meaning |", "|---|---|---|"]
        for number, rule in enumerate(panel["rules"], start=1):
            lines.append(f"| {number} | **{rule['readme']}** | fixture |")
        lines += ["", "**Reflexive check:** apply Rule 0."]
    return "\n".join(lines)


def _valid_poster() -> str:
    labels = []
    for panel in MAP["panels"]:
        labels.append(f"<text>{panel['poster_heading']}</text>")
        labels.extend(f"<text>{rule['poster']}</text>" for rule in panel["rules"])
    return '<svg xmlns="http://www.w3.org/2000/svg">' + "".join(labels) + "</svg>"


def _write_surface_fixture(root: Path) -> None:
    (root / "assets").mkdir(parents=True)
    (root / "README.md").write_text(_valid_readme(), encoding="utf-8")
    (root / "assets/doubt-the-machine.svg").write_text(_valid_poster(), encoding="utf-8")
    (root / "rule0_surface_map.json").write_text(json.dumps(MAP), encoding="utf-8")


def test_readme_rule_deletion_is_rejected(tmp_path: Path) -> None:
    _write_surface_fixture(tmp_path)
    text = (tmp_path / "README.md").read_text(encoding="utf-8")
    text = text.split("## 1 — Panel 1", 1)[0] + "\n(all rules deleted)\n"
    (tmp_path / "README.md").write_text(text, encoding="utf-8")
    with pytest.raises(SurfaceContractError):
        validate_readme_structure(tmp_path)


def test_magic_string_poster_replacement_is_rejected(tmp_path: Path) -> None:
    _write_surface_fixture(tmp_path)
    (tmp_path / "assets/doubt-the-machine.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><desc>fixture marker</desc><text>TRUST THE MACHINE</text></svg>',
        encoding="utf-8",
    )
    with pytest.raises(SurfaceContractError):
        validate_poster_structure(tmp_path)


def test_retired_wording_is_forbidden_repo_wide_except_declared_history(tmp_path: Path) -> None:
    retired_phrase = "No test" + ", no merge"
    ledger = {
        "version": 2,
        "allow_in": [
            {"path": "GRAVEYARD.md", "scope": "whole_file", "reason": "correction history"},
            {"path": "retired.json", "scope": "whole_file", "reason": "machine-readable ledger"},
            {
                "path": "preregistration.json",
                "scope": "json_pointer:/result/retired_claims",
                "reason": "structured experiment correction history",
            },
        ],
        "entries": [{"id": "fixture", "retired": [retired_phrase], "replacement": "replacement", "forbid_in": ["README.md"]}],
    }
    (tmp_path / "retired.json").write_text(json.dumps(ledger), encoding="utf-8")
    (tmp_path / "GRAVEYARD.md").write_text(retired_phrase, encoding="utf-8")
    (tmp_path / "preregistration.json").write_text(
        json.dumps({"result": {"retired_claims": [retired_phrase]}, "active": "clean"}), encoding="utf-8"
    )
    (tmp_path / "MCP.md").write_text(retired_phrase, encoding="utf-8")
    with pytest.raises(SurfaceContractError):
        validate_retired_repo_wide(tmp_path)

    (tmp_path / "MCP.md").write_text("active wording", encoding="utf-8")
    validate_retired_repo_wide(tmp_path)

    (tmp_path / "preregistration.json").write_text(
        json.dumps({"result": {"retired_claims": [retired_phrase]}, "active": retired_phrase}), encoding="utf-8"
    )
    with pytest.raises(SurfaceContractError):
        validate_retired_repo_wide(tmp_path)
