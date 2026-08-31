# GenGatewAI API

GenGatewAI exposes Doubt the Machine as a deterministic cloud API. It recommends verification effort, reports missing gate fields, and validates Experiment 001 records. It does **not** decide whether a claim is true.

## Local run

```bash
python -m pip install -r requirements-dev.txt
python -m uvicorn api.gengatewai.app:app --reload
```

Then open:

- `GET /`
- `GET /healthz`
- `GET /v1/models`
- `POST /v1/chat/completions`
- `GET /v1/local-models`
- `GET /v1/gates/doubt-the-machine`
- `POST /v1/gates/doubt-the-machine/evaluate`
- `POST /v1/gates/doubt-the-machine/review-records/validate`
- `GET /v1/experiments/001-seeded-errors`

## OpenAI-compatible runner

The API exposes a minimal OpenAI Chat Completions-compatible runner so existing clients can point their base URL at GenGatewAI:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gengatewai/doubt-runner",
    "messages": [
      {"role": "user", "content": "CLAIM: This output is safe to deploy.\nFAILURE: hidden production regression"}
    ]
  }'
```

The built-in model id is `gengatewai/doubt-runner`. It returns an OpenAI-shaped `chat.completion` object whose assistant message applies `DOUBT → MEASURE → TEST → REVERT → REPEAT`.

This runner does not decide whether the claim is true, safe, or acceptable. Streaming and tool execution are intentionally unsupported in this slice.

## Local model autodetect

Local model recruitment is abstract and opt-in. It is disabled by default so public Vercel deployments do not probe local or private networks.

Set `GENGATEWAI_LOCAL_MODELS=localhost` for local-only detection:

- LM Studio via `http://127.0.0.1:1234/v1/models`;
- Ollama via `http://127.0.0.1:11434/api/tags`.

Set `GENGATEWAI_LOCAL_MODELS=lan` only on a trusted local network when you want bounded LAN Ollama autodetection. Use `GENGATEWAI_LAN_OLLAMA_BASE_URLS` for explicit LAN endpoints, or `GENGATEWAI_LAN_OLLAMA_CIDRS` plus `GENGATEWAI_LAN_OLLAMA_SCAN_LIMIT` for bounded private-subnet probing.

Local inventory details belong in ignored local files such as `.env.local`, `.gengatewai.local.json`, or `local-lab.json`. Do not commit workstation paths, LAN addresses, model inventories, or credentials.

When local models are enabled, `GET /v1/models` also lists abstract ids such as:

- `local/lmstudio/<model-id>`;
- `local/ollama/<model-id>`.

Calling `POST /v1/chat/completions` with one of those ids forwards the request to the local provider, prepends the Doubt runner system instruction, disables streaming, and appends a deterministic note that the local output is not a truth verdict.

## Experiment 001 effective contract

`GET /v1/experiments/001-seeded-errors` returns the **effective** Experiment 001 contract. The historical `preregistration.json` is preserved byte-for-byte and its Git blob is pinned by `amendment-2026-08-31-pilot.json`; the API overlays that prospective amendment rather than rewriting history.

The effective design role is `pilot`. The endpoint therefore exposes:

- `design_role.name = "pilot"`;
- `confirmatory_effectiveness_decision_allowed = false`;
- `powered_replication_required = true`;
- no invented pre-data baseline escape probability or reviewer ICC;
- the original 10-point effect region as `descriptive_reference_only`;
- an `H` effectiveness status after the pilot; and
- a promotion rule that forbids calling the gate effective, safer, better, or confirmatorily successful from Experiment 001 alone.

Experiment 001 remains the same fixed randomized three-arm, two-origin protocol. Its job is now to estimate the realized important-defect denominator, baseline arm/family/origin rates, reviewer/matched-task dependence, false alarms, review cost, and seed-realism retention needed for a **separately preregistered powered replication**.

The two-ended human/AI matrix still uses `origin→reviewer` labels:

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

Codex project configuration is included at `.codex/config.toml` for trusted local use.

## Cloud targets

- `app.py` re-exports the FastAPI app at a Vercel-supported framework entrypoint; `vercel.json` configures that function without a legacy catch-all rewrite.
- `Dockerfile` runs the same API with Uvicorn for portable container deployment.
- `web/` contains the Vercel Labs `vgpu`-ready visualization contract for the gate loop, effort levels, endpoint matrix, and missing-field state. Its tests use `vgpu/mock` so CI does not require GPU hardware.
