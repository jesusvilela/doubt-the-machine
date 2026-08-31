#!/usr/bin/env python3
"""ACAF operational-meaning matrix: unchanged titles, paraphrases versus inversions.

This attacks the known gap left by title-only rule identity. For each of the 27 active rules,
`rules.json` declares one meaning-preserving paraphrase (MUST_PASS) and one explicit semantic
inversion (MUST_CATCH). The matrix applies each case to a throwaway README and runs the same
`scripts/check_rule0.py` Actor used by CI.

The oracle and checker remain correlated because they are authored in the same repository loop.
A zero escape rate here establishes only behavior over these declared 54 cases; it is not general
natural-language entailment and not evidence that the framework is effective.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKIP_NAMES = {".git", "__pycache__", "node_modules", ".pytest_cache"}


@dataclass(frozen=True)
class MeaningOutcome:
    title: str
    panel: int
    rule: int
    case: str
    must_catch: bool
    checker_failed: bool
    checker_message: str
    verdict: str


def _load_rules(root: Path = ROOT) -> list[tuple[int, int, dict[str, Any]]]:
    payload = json.loads((root / "rules.json").read_text(encoding="utf-8"))
    rules: list[tuple[int, int, dict[str, Any]]] = []
    for panel_index, panel in enumerate(payload.get("panels", []), start=1):
        if not isinstance(panel, dict):
            raise ValueError(f"panel {panel_index} is not an object")
        for rule_index, rule in enumerate(panel.get("rules", []), start=1):
            if not isinstance(rule, dict):
                raise ValueError(f"panel {panel_index} rule {rule_index} is not an object")
            contract = rule.get("meaning_contract")
            if not isinstance(contract, dict):
                raise ValueError(f"panel {panel_index} rule {rule_index} lacks meaning_contract")
            rules.append((panel_index, rule_index, rule))
    if len(rules) != 27:
        raise ValueError(f"expected 27 active rules, found {len(rules)}")
    return rules


def _replace_operational_meaning(root: Path, title: str, replacement: str) -> None:
    path = root / "README.md"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"^(\|\s*[1-9]\s*\|\s*\*\*{re.escape(title)}\*\*\s*\|\s*)(.*?)(\s*\|)$",
        flags=re.MULTILINE,
    )
    updated, count = pattern.subn(lambda match: match.group(1) + replacement + match.group(3), text, count=1)
    if count != 1:
        raise ValueError(f"could not uniquely replace README meaning for {title!r}: matches={count}")
    path.write_text(updated, encoding="utf-8")


def _run_checker(root: Path) -> tuple[bool, str]:
    process = subprocess.run(
        [sys.executable, "scripts/check_rule0.py"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    lines = (process.stdout + process.stderr).strip().splitlines()
    return process.returncode != 0, (lines[-1] if lines else "")


def run_matrix(root: Path = ROOT) -> list[MeaningOutcome]:
    rules = _load_rules(root)
    outcomes: list[MeaningOutcome] = []

    with tempfile.TemporaryDirectory(prefix="acaf-meaning-") as tmp:
        pristine = Path(tmp) / "pristine"
        shutil.copytree(root, pristine, ignore=shutil.ignore_patterns(*SKIP_NAMES))

        for panel_index, rule_index, rule in rules:
            title = str(rule.get("readme", "")).strip()
            contract = rule["meaning_contract"]
            cases = [
                ("inversion", True, str(contract.get("inversion_example", "")).strip()),
                ("paraphrase", False, str(contract.get("paraphrase_example", "")).strip()),
            ]
            for case, must_catch, replacement in cases:
                if not title or not replacement:
                    raise ValueError(f"incomplete meaning case at panel {panel_index} rule {rule_index}")
                work = Path(tmp) / "work"
                if work.exists():
                    shutil.rmtree(work)
                shutil.copytree(pristine, work)
                _replace_operational_meaning(work, title, replacement)
                checker_failed, checker_message = _run_checker(work)
                if must_catch:
                    verdict = "caught" if checker_failed else "escaped"
                else:
                    verdict = "false_alarm" if checker_failed else "correctly_passed"
                outcomes.append(
                    MeaningOutcome(
                        title=title,
                        panel=panel_index,
                        rule=rule_index,
                        case=case,
                        must_catch=must_catch,
                        checker_failed=checker_failed,
                        checker_message=checker_message,
                        verdict=verdict,
                    )
                )

    return outcomes


def summarize(outcomes: list[MeaningOutcome]) -> dict[str, Any]:
    inversions = [outcome for outcome in outcomes if outcome.must_catch]
    paraphrases = [outcome for outcome in outcomes if not outcome.must_catch]
    escaped = [outcome for outcome in inversions if outcome.verdict == "escaped"]
    false_alarms = [outcome for outcome in paraphrases if outcome.verdict == "false_alarm"]
    return {
        "total_cases": len(outcomes),
        "inversions": len(inversions),
        "paraphrases": len(paraphrases),
        "escaped_inversions": len(escaped),
        "paraphrase_false_alarms": len(false_alarms),
        "inversion_escape_rate": (len(escaped) / len(inversions)) if inversions else 0.0,
        "paraphrase_false_alarm_rate": (len(false_alarms) / len(paraphrases)) if paraphrases else 0.0,
        "escaped_examples": [asdict(outcome) for outcome in escaped[:10]],
        "false_alarm_examples": [asdict(outcome) for outcome in false_alarms[:10]],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the 27-rule ACAF operational-meaning matrix.")
    parser.add_argument("--json", type=str, default="", help="Write matrix outcomes to this file.")
    parser.add_argument("--max-inversion-escape-rate", type=float, default=None)
    parser.add_argument("--max-paraphrase-false-alarm-rate", type=float, default=None)
    args = parser.parse_args()

    print("--- ACAF operational-meaning matrix: 27 inversions + 27 paraphrases ---")
    outcomes = run_matrix()
    summary = summarize(outcomes)
    print(
        f"inversion escape rate : {summary['inversion_escape_rate']:.3f} "
        f"({summary['escaped_inversions']}/{summary['inversions']})"
    )
    print(
        f"paraphrase false alarm: {summary['paraphrase_false_alarm_rate']:.3f} "
        f"({summary['paraphrase_false_alarms']}/{summary['paraphrases']})"
    )

    if args.json:
        Path(args.json).write_text(
            json.dumps(
                {"summary": summary, "outcomes": [asdict(outcome) for outcome in outcomes]},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    failed = False
    if (
        args.max_inversion_escape_rate is not None
        and summary["inversion_escape_rate"] > args.max_inversion_escape_rate
    ):
        print(
            f"ACAF meaning FAIL: inversion escape rate {summary['inversion_escape_rate']:.3f} "
            f"> {args.max_inversion_escape_rate}"
        )
        failed = True
    if (
        args.max_paraphrase_false_alarm_rate is not None
        and summary["paraphrase_false_alarm_rate"] > args.max_paraphrase_false_alarm_rate
    ):
        print(
            f"ACAF meaning FAIL: paraphrase false-alarm rate {summary['paraphrase_false_alarm_rate']:.3f} "
            f"> {args.max_paraphrase_false_alarm_rate}"
        )
        failed = True
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
