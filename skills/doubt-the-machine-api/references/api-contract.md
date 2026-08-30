# GenGatewAI API contract

## Required endpoints

- `GET /healthz` returns service name, version, and status.
- `GET /v1/models` returns the deterministic runner model and any enabled abstract local model ids.
- `POST /v1/chat/completions` accepts OpenAI Chat Completions-shaped requests for `gengatewai/doubt-runner` and, when explicitly enabled, abstract local LM Studio/Ollama model ids.
- `GET /v1/local-models` reports whether local LM Studio/Ollama autodetect is enabled. It must not expose provider base URLs.
- `GET /v1/gates/doubt-the-machine` returns Rule 0, scope, gate fields, surfaces, evidence levels, dev loop, verification effort knobs, endpoint values, and conditions.
- `POST /v1/gates/doubt-the-machine/evaluate` accepts a claim, endpoint fields, risk inputs, and optional gate answers. It returns verification effort, missing gate fields, warnings, and next action.
- `POST /v1/gates/doubt-the-machine/review-records/validate` validates Experiment 001 review records without storing them.
- `GET /v1/experiments/001-seeded-errors` returns the preregistered Experiment 001 design and sample plan.

## MCP tools and resources

The MCP server must expose the same deterministic contract without adding a truth verdict:

- `healthz`
- `get_doubt_the_machine_contract`
- `evaluate_doubt_gate`
- `validate_experiment_001_records`
- `get_experiment_001_contract`

It must also expose JSON resources for:

- `gengatewai://doubt-the-machine/contract`
- `gengatewai://experiments/001-seeded-errors`

For trusted Codex project use, `.codex/config.toml` must point `gengatewai_doubt_the_machine` at `python -m api.gengatewai.mcp_server` with the same five enabled tools.

## Evaluation behavior

- Use `high` effort for experiments, metrics, kill conditions, external claims, high consequence, or hard/irreversible rollback.
- Use `standard` effort for active rules, evidence ledgers, CI checks, medium consequence, medium/high uncertainty, or moderate rollback.
- Use `light` effort only for low-consequence, low-uncertainty, easily reversible presentation or wording checks.
- Always report missing gate fields rather than filling them in.
- Never return an “accepted” or “true” verdict for the claim.

## OpenAI-compatible runner and local capacity

- The built-in model id is `gengatewai/doubt-runner`.
- The runner endpoints are `/v1/models`, `/v1/chat/completions`, and `/v1/local-models`.
- The deterministic runner applies `DOUBT → MEASURE → TEST → REVERT → REPEAT`.
- The runner does not decide whether the claim is true, safe, or acceptable.
- Streaming and tool execution are unsupported until separately preregistered and tested.
- Local LM Studio autodetect uses `http://127.0.0.1:1234/v1/models` by convention.
- Local Ollama autodetect uses `http://127.0.0.1:11434/api/tags` by convention.
- `GENGATEWAI_LOCAL_MODELS` controls discovery mode: `off`, `localhost`, or `lan`.
- `GENGATEWAI_LAN_OLLAMA_BASE_URLS`, `GENGATEWAI_LAN_OLLAMA_CIDRS`, and `GENGATEWAI_LAN_OLLAMA_SCAN_LIMIT` configure bounded LAN Ollama discovery.
- LAN Ollama autodetection is enabled only when explicitly requested by the local operator.
- Local model recruitment is disabled by default, so the default API does_not_call_external_models_by_default.
- Local lab details must stay in ignored local files, not the repository.

## Endpoint matrix

Experiment 001 uses a two-ended endpoint matrix. Both ends are explicit:

- artifact origin: `human | agent`;
- reviewer side: `human | agent`;
- endpoint cells: `human→human`, `human→agent`, `agent→human`, `agent→agent`, where labels mean `origin→reviewer`.

A single reviewer cohort covers the two cells for that reviewer side. Running both human and agent reviewer cohorts covers the full four-cell matrix.

## Review-record validation

The validator must enforce:

- `condition` is one of `ordinary_control`, `active_placebo`, `doubt_gate`;
- `artifact_origin` is `human` or `agent`;
- `reviewer_type` is `human` or `agent`;
- required identity fields are non-empty;
- count fields are non-negative integers;
- boolean decision fields are `0` or `1`;
- `important_defects_caught + important_defects_escaped == important_defect_count`;
- `important_defect_count <= seeded_defect_count`.

## Drift guards

The repo checker must pin:

- gate fields;
- endpoint values;
- condition values;
- Experiment 001 sample constants;
- result CSV header;
- MCP tool names and resource URIs.
- OpenAI-compatible runner endpoint names, model id, local provider names, and local discovery modes.
