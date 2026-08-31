# GenGatewAI MCP server

The GenGatewAI MCP server exposes the same deterministic Doubt the Machine contract as the REST API, but in the Model Context Protocol shape used by tool-capable AI hosts.

It does **not** decide whether a claim is true or acceptable. It can inspect the current framework contract, recommend verification effort, identify missing gate fields, distinguish gate-form completion from substantive verification, expose Experiment 001, and validate review records.

## Security boundary

The supported default transport is **stdio**. The current MCP tools are non-mutating: they inspect contracts, evaluate the gate, or validate supplied records without storing them.

Streamable HTTP is intentionally **loopback-only** in the built-in server. Binding directly to `0.0.0.0`, a LAN address, or a public hostname fails closed.

For remote use:

1. keep GenGatewAI bound to `127.0.0.1` / `::1`;
2. put an authenticated TLS reverse proxy or hosting layer in front of it;
3. implement the current MCP authorization requirements at that boundary;
4. apply infrastructure rate/request-size limits and abuse monitoring;
5. never treat network reachability as authorization.

See [SECURITY.md](SECURITY.md) for the repository-wide trust model.

## Run locally

Install the Python dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run the stdio server for a local MCP host:

```bash
python -m api.gengatewai.mcp_server
```

Run Streamable HTTP for local remote-client testing:

```bash
python -m api.gengatewai.mcp_server --transport streamable-http --host 127.0.0.1 --port 8766 --path /mcp
```

A non-loopback host is rejected by design.

## Tools

- `healthz` — returns service name, version, and status.
- `get_doubt_the_machine_contract` — returns Rule 0, scope, gate fields, surfaces, evidence levels, dev loop, verification effort knobs, endpoint values, endpoint matrix, and conditions.
- `evaluate_doubt_gate` — returns verification effort, missing gate fields, `gate_form_complete`, `gate_substance_assessed`, bounded ceremony warnings, and next required action for one claim/change. A complete form is **not** reported as substantive verification, and the tool never returns an acceptance or truth verdict.
- `validate_experiment_001_records` — validates Experiment 001 records without storing them.
- `get_experiment_001_contract` — returns the **effective Experiment 001 pilot contract**: the historical preregistration plus its prospective pilot amendment.

The ceremony heuristics are deliberately weak warning signals only. Obvious placeholders, extremely short fields, claim-as-evidence repetition, or evidence with no obvious observable marker can be flagged; absence of a warning does not mean a gate is good, true, safe, or sufficient.

## Resources

- `gengatewai://doubt-the-machine/contract`
- `gengatewai://experiments/001-seeded-errors`

Both resources return JSON. The Experiment 001 tool and resource expose the same effective contract. The original `preregistration.json` remains byte-for-byte preserved and is pinned by the amendment; the server overlays `amendment-2026-08-31-pilot.json` and fails closed if the historical preregistration blob no longer matches.

The effective Experiment 001 contract says:

- design role: `pilot`;
- confirmatory effectiveness decision: **not allowed**;
- powered replication: **required** before an effectiveness decision;
- pre-data baseline escape probability and reviewer ICC: **unknown, not invented**;
- original effect region: **descriptive planning reference only**;
- effectiveness claim after pilot: remains `H`.

The two-ended endpoint matrix is unchanged:

| Artifact origin | Reviewer side | Cell |
| --- | --- | --- |
| `human` | `human` | `human→human` |
| `human` | `agent` | `human→agent` |
| `agent` | `human` | `agent→human` |
| `agent` | `agent` | `agent→agent` |

A single reviewer cohort covers the two cells for that reviewer side. Running both human and agent reviewer cohorts covers the full four-cell matrix.

## Client configuration sketch

For Codex, this repository ships a project-scoped MCP config at `.codex/config.toml`. Codex loads project-scoped MCP servers from trusted projects, using the same config family as `~/.codex/config.toml`.

The active project entry is:

```toml
[mcp_servers.gengatewai_doubt_the_machine]
command = "python"
args = ["-m", "api.gengatewai.mcp_server"]
cwd = "."
enabled = true
startup_timeout_sec = 20
tool_timeout_sec = 60
default_tools_approval_mode = "auto"
enabled_tools = [
  "healthz",
  "get_doubt_the_machine_contract",
  "evaluate_doubt_gate",
  "validate_experiment_001_records",
  "get_experiment_001_contract",
]
```

`auto` approval is acceptable here only because the enabled tool whitelist is currently non-mutating. If a future MCP tool writes state, executes user content, performs network fetches, or triggers external side effects, this assumption must be revisited before that tool is enabled.

For a host that expects a JSON-style command sketch, use:

```json
{
  "command": "python",
  "args": ["-m", "api.gengatewai.mcp_server"]
}
```

Run it from the repository root so the server can read the Experiment 001 historical preregistration and its prospective pilot amendment.
