# GenGatewAI API

GenGatewAI exposes Doubt the Machine as a deterministic cloud API. It recommends verification effort, reports missing gate fields, and validates Experiment 001 records. It does **not** decide whether a claim is true.

## Local run

```bash
python -m pip install -r requirements-dev.txt
python -m uvicorn api.gengatewai.app:app --reload
```

Then open:

- `GET /healthz`
- `GET /v1/gates/doubt-the-machine`
- `POST /v1/gates/doubt-the-machine/evaluate`
- `POST /v1/gates/doubt-the-machine/review-records/validate`
- `GET /v1/experiments/001-seeded-errors`

Experiment 001 is exposed as a two-ended human/AI matrix, using `origin→reviewer` labels:

| Artifact origin | Reviewer side | Cell |
| --- | --- | --- |
| `human` | `human` | `human→human` |
| `human` | `agent` | `human→agent` |
| `agent` | `human` | `agent→human` |
| `agent` | `agent` | `agent→agent` |

A single reviewer cohort fixes the reviewer side and covers two cells. Running both human and agent reviewer cohorts covers the full four-cell matrix.

## Codex skill

This repo ships a Codex skill at `skills/doubt-the-machine-api`.

Set `DTM_API_BASE_URL` to a running deployment when you want agents to use the live API first. If the API is unavailable, the skill falls back to canonical repo files.

## MCP

The same deterministic contract is available as an MCP server:

```bash
python -m api.gengatewai.mcp_server
```

That starts the local stdio transport used by most desktop MCP hosts. For remote MCP clients during development:

```bash
python -m api.gengatewai.mcp_server --transport streamable-http --host 127.0.0.1 --port 8766 --path /mcp
```

See `MCP.md` for the exposed tools and resources.

## Cloud targets

- `vercel.json` exposes the FastAPI app through Vercel’s Python function shape.
- `Dockerfile` runs the same API with Uvicorn for portable container deployment.
- `web/` contains the Vercel Labs `vgpu`-ready visualization contract for the gate loop, effort levels, endpoint matrix, and missing-field state. Its tests use `vgpu/mock` so CI does not require GPU hardware.
