#!/usr/bin/env python3
"""Fail when the repository's Rule 0 self-audit contract silently regresses."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "FALSIFIERS.md",
    "GRAVEYARD.md",
    "EVIDENCE.md",
    "experiments/001-seeded-errors/README.md",
    "experiments/001-seeded-errors/preregistration.json",
    "experiments/001-seeded-errors/results.csv",
]

EXPECTED_RESULTS_COLUMNS = [
    "task_id",
    "task_family",
    "condition",
    "variant_id",
    "seeded_defect_count",
    "important_defect_count",
    "important_defects_caught",
    "important_defects_escaped",
    "false_alarms",
    "accepted",
    "reversed_after_evidence",
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
    "evidence",
    "round_trip",
    "result",
}


def fail(message: str) -> None:
    raise SystemExit(f"Rule 0 contract failed: {message}")


def main() -> None:
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            fail(f"missing required artifact: {relative}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if readme.count("**Rule 0:**") != 2:
        fail("README must contain one governing Rule 0 near the top and one disclosure footer")
    if "| 0 |" in readme:
        fail("local panel Rule 0 rows were retired; use reflexive checks instead")
    if "No test, no merge" in readme:
        fail("retired absolute rule reintroduced: No test, no merge")
    if "Count how often it disagrees with you" in readme:
        fail("retired disagreement-count rule reintroduced")
    if "Own every changed line" in readme:
        fail("retired universal line-ownership wording reintroduced")

    prereg_path = ROOT / "experiments/001-seeded-errors/preregistration.json"
    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED_PREREG - prereg.keys())
    if missing:
        fail(f"preregistration missing top-level fields: {', '.join(missing)}")

    gate = prereg.get("preregistration", {})
    for field in ("prediction", "primary_metric", "kill_condition", "stop_condition", "promotion_rule"):
        if not str(gate.get(field, "")).strip():
            fail(f"preregistration.{field} must be non-empty")

    if prereg.get("result", {}).get("status_after") not in {"H", "M", "R"}:
        fail("Experiment 001 status must remain H, M, or R; it cannot become proof by checklist")

    results_path = ROOT / "experiments/001-seeded-errors/results.csv"
    with results_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
    if header != EXPECTED_RESULTS_COLUMNS:
        fail("results.csv schema changed without updating the contract checker")

    graveyard = (ROOT / "GRAVEYARD.md").read_text(encoding="utf-8")
    for retired in (
        "Count how often it disagrees with you",
        "No test, no merge",
        "Own every changed line",
        "uncertainty × consequence × irreversibility",
    ):
        if retired not in graveyard:
            fail(f"correction history missing retired formulation: {retired}")

    print("Rule 0 contract: PASS")


if __name__ == "__main__":
    main()
