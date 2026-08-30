from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_VERCEL_EXCLUDES = {
    ".agent/**",
    ".codex/**",
    ".github/**",
    ".git/**",
    ".env",
    ".env.*",
    ".gengatewai.local*",
    "local-lab*",
    "tests/**",
    "web/**",
    "assets/**",
    "skills/**",
    "*.md",
}

REQUIRED_VERCELIGNORE_ENTRIES = {
    ".agent",
    ".codex",
    ".git",
    ".github",
    ".env",
    ".env.*",
    ".gengatewai.local*",
    "local-lab*",
    "tests",
    "web",
    "assets",
    "skills",
    "*.md",
}

RUNTIME_REQUIRED_PATHS = {
    "api/index.py",
    "api/gengatewai/app.py",
    "api/gengatewai/contracts.py",
    "api/gengatewai/local_models.py",
    "api/gengatewai/openai_compat.py",
    "experiments/001-seeded-errors/preregistration.json",
    "requirements.txt",
}


def vercel_config() -> dict[str, object]:
    return json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))


def test_vercel_python_function_excludes_non_runtime_surfaces() -> None:
    function_config = vercel_config()["functions"]["api/index.py"]
    exclude_files = function_config["excludeFiles"]

    for required_pattern in REQUIRED_VERCEL_EXCLUDES:
        assert required_pattern in exclude_files


def test_vercelignore_excludes_non_runtime_surfaces() -> None:
    entries = {
        line.strip()
        for line in (ROOT / ".vercelignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert REQUIRED_VERCELIGNORE_ENTRIES <= entries


def test_vercel_runtime_inputs_are_not_excluded() -> None:
    ignored_text = (ROOT / ".vercelignore").read_text(encoding="utf-8")
    function_excludes = vercel_config()["functions"]["api/index.py"]["excludeFiles"]

    for required_path in RUNTIME_REQUIRED_PATHS:
        assert required_path not in ignored_text
        assert required_path not in function_excludes
