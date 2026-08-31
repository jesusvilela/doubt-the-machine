from __future__ import annotations

from pathlib import Path

import pytest

from scripts.acaf_ambigator import Ambigator, Mutation
from scripts.check_acaf_generators import GeneratorIntegrityError, validate_generators


def test_live_generator_span_is_material_for_one_seed() -> None:
    result = validate_generators(1)
    assert result == {
        "generator_families": 24,
        "seeds": 1,
        "expected_mutations": 24,
        "exercised_mutations": 24,
    }


def test_generator_integrity_rejects_application_failure(monkeypatch, tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("baseline\n", encoding="utf-8")

    def broken_generator(self, rng, seed):
        def apply(root: Path) -> None:
            raise RuntimeError("synthetic failure")

        return Mutation("broken", seed, True, "synthetic failure", apply)

    monkeypatch.setattr(Ambigator, "generators", lambda self: [self.broken] if hasattr(self, "broken") else [])
    monkeypatch.setattr(Ambigator, "broken", broken_generator, raising=False)

    with pytest.raises(GeneratorIntegrityError, match="mutation application failed"):
        validate_generators(1, root=tmp_path)


def test_generator_integrity_rejects_noop(monkeypatch, tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("baseline\n", encoding="utf-8")

    def noop_generator(self, rng, seed):
        return Mutation("noop", seed, False, "does nothing", lambda root: None)

    monkeypatch.setattr(Ambigator, "generators", lambda self: [self.noop] if hasattr(self, "noop") else [])
    monkeypatch.setattr(Ambigator, "noop", noop_generator, raising=False)

    with pytest.raises(GeneratorIntegrityError, match="mutation was a no-op"):
        validate_generators(1, root=tmp_path)


def test_generator_integrity_rejects_nonpositive_seed_count() -> None:
    with pytest.raises(GeneratorIntegrityError, match="seeds must be positive"):
        validate_generators(0)
