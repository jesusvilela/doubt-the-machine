from __future__ import annotations

import re

from api.gengatewai.contracts import GATE_FIELDS

SHORT_FIELD_THRESHOLD = 3
PLACEHOLDER_VALUES = {
    ".",
    "-",
    "none",
    "n/a",
    "na",
    "tbd",
    "unknown",
    "impossible",
    "made up",
    "i made it up",
    "none, i made it up",
}
EVIDENCE_ANCHOR = re.compile(
    r"https?://|\b(?:pytest|curl|git|sha|commit|diff|log|test|command|artifact|source|run|file|line)\b|\d|[/\\]",
    re.IGNORECASE,
)


def ceremony_warnings(gate: dict[str, str], claim: str) -> list[str]:
    """Return cheap warning heuristics only; never a truth or quality verdict."""
    warnings: list[str] = []

    for field in GATE_FIELDS:
        value = gate.get(field, "").strip()
        if not value:
            continue
        normalized = value.casefold()
        if len(value) < SHORT_FIELD_THRESHOLD:
            warnings.append(f"{field} is extremely short; field presence alone is not verification.")
        if normalized in PLACEHOLDER_VALUES:
            warnings.append(f"{field} looks like a placeholder; this is a heuristic warning, not a verdict.")

    evidence = gate.get("EVIDENCE", "").strip()
    if evidence:
        if evidence.casefold() == claim.strip().casefold():
            warnings.append("EVIDENCE repeats the claim; restating a claim is not independent evidence.")
        if EVIDENCE_ANCHOR.search(evidence) is None:
            warnings.append(
                "EVIDENCE contains no obvious source, artifact, command, path, line, run, or numeric marker; heuristic only."
            )

    return warnings
