from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_codex_project_mcp_config_points_at_local_server() -> None:
    config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
    server = config["mcp_servers"]["gengatewai_doubt_the_machine"]

    assert server["command"] == "python"
    assert server["args"] == ["-m", "api.gengatewai.mcp_server"]
    assert server["cwd"] == "."
    assert server["enabled"] is True
    assert server["default_tools_approval_mode"] == "auto"
    assert set(server["enabled_tools"]) == {
        "healthz",
        "get_doubt_the_machine_contract",
        "evaluate_doubt_gate",
        "validate_experiment_001_records",
        "get_experiment_001_contract",
    }
