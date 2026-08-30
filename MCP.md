# GenGatewAI MCP server

The GenGatewAI MCP server exposes the same deterministic Doubt the Machine contract as the REST API, but in the Model Context Protocol shape used by tool-capable AI hosts.

It does **not** decide whether a claim is true or acceptable. It can inspect the current framework contract, recommend verification effort, identify missing gate fields, expose Experiment 001, and validate review records.

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

## Tools

- `healthz` — returns service name, version, and status.
- `get_doubt_the_machine_contract` — returns Rule 0, scope, gate fields, surfaces, evidence levels, dev loop, verification effort knobs, endpoint values, endpoint matrix, and conditions.
- `evaluate_doubt_gate` — returns verification effort, missing gate fields, warnings, and next required action for one claim/change. It never returns an acceptance or truth verdict.
- `validate_experiment_001_records` — validates Experiment 001 records without storing them.
- `get_experiment_001_contract` — returns the preregistered Experiment 001 design and sample plan.

## Resources

- `gengatewai://doubt-the-machine/contract`
- `gengatewai://experiments/001-seeded-errors`

Both resources return JSON. The Experiment 001 resource preserves the two-ended endpoint matrix:

| Artifact origin | Reviewer side | Cell |
| --- | --- | --- |
| `human` | `human` | `human→human` |
| `human` | `agent` | `human→agent` |
| `agent` | `human` | `agent→human` |
| `agent` | `agent` | `agent→agent` |

## Client configuration sketch

Use this command as the MCP server entrypoint from a desktop host:

```json
{
  "command": "python",
  "args": ["-m", "api.gengatewai.mcp_server"]
}
```

Run it from the repository root so the server can read `experiments/001-seeded-errors/preregistration.json`.
