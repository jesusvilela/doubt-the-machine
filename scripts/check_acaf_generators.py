#!/usr/bin/env python3
"""Fail-closed integrity check for the ACAF mutation generator span.

ACAF's fuzzer historically skipped mutation-application exceptions. That makes the reported
escape/false-alarm denominator vulnerable to silent shrinkage if a generator drifts out of sync
with the repository. This preflight exercises the exact deterministic Ambigator sweep on throwaway
copies and requires every declared mutation to apply successfully and materially change the tree.

This checks the mutation machinery, not whether the Rule 0 checker catches the mutations.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import tempfile
from pathlib import Path

try:  # package import under pytest / module execution
    from scripts.acaf_ambigator import Ambigator, ROOT
except ModuleNotFoundError:  # direct `python scripts/check_acaf_generators.py`
    from acaf_ambigator import Ambigator, ROOT

SKIP_NAMES = {".git", "__pycache__", "node_modules", ".pytest_cache"}


class GeneratorIntegrityError(RuntimeError):
    """Raised when the declared mutation span cannot be exercised as specified."""


def _tree_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root)
        if any(part in SKIP_NAMES for part in relative.parts):
            continue
        if not path.is_file():
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
        digest.update(b"\0")
    return digest.hexdigest()


def validate_generators(seeds: int, base_seed: int = 0, root: Path = ROOT) -> dict[str, int]:
    if seeds <= 0:
        raise GeneratorIntegrityError("seeds must be positive")

    ambigator = Ambigator()
    generator_count = len(ambigator.generators())
    expected = seeds * generator_count
    exercised = 0

    with tempfile.TemporaryDirectory(prefix="acaf-generator-integrity-") as tmp:
        pristine = Path(tmp) / "pristine"
        shutil.copytree(
            root,
            pristine,
            ignore=shutil.ignore_patterns(*SKIP_NAMES),
        )
        pristine_fingerprint = _tree_fingerprint(pristine)

        for mutation in ambigator.sweep(seeds, base_seed):
            work = Path(tmp) / "work"
            if work.exists():
                shutil.rmtree(work)
            shutil.copytree(pristine, work)
            try:
                mutation.apply(work)
            except Exception as exc:
                raise GeneratorIntegrityError(
                    f"mutation application failed: {mutation.family}/{mutation.seed}: {exc}"
                ) from exc

            changed_fingerprint = _tree_fingerprint(work)
            if changed_fingerprint == pristine_fingerprint:
                raise GeneratorIntegrityError(
                    f"mutation was a no-op: {mutation.family}/{mutation.seed}: {mutation.description}"
                )
            exercised += 1

    if exercised != expected:
        raise GeneratorIntegrityError(
            f"mutation span shrank: exercised {exercised}, expected {expected} "
            f"({generator_count} families x {seeds} seeds)"
        )

    return {
        "generator_families": generator_count,
        "seeds": seeds,
        "expected_mutations": expected,
        "exercised_mutations": exercised,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate that every declared ACAF mutation applies and changes the tree.")
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--base-seed", type=int, default=0)
    args = parser.parse_args()

    try:
        result = validate_generators(args.seeds, args.base_seed)
    except GeneratorIntegrityError as exc:
        raise SystemExit(f"ACAF generator integrity: FAIL\n- {exc}") from exc

    print("ACAF generator integrity: PASS")
    print(
        f"- families={result['generator_families']} seeds={result['seeds']} "
        f"mutations={result['exercised_mutations']}/{result['expected_mutations']}"
    )


if __name__ == "__main__":
    main()
