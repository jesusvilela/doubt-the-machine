---
name: doubt-the-machine-api
description: Use the GenGatewAI API to apply the Doubt the Machine gate, validate Experiment 001 records, or inspect the framework contract; fall back to canonical repo files when the API is unavailable.
---

# Doubt the Machine API

Use this skill when a task asks to apply, expose, test, or integrate the Doubt the Machine framework through the GenGatewAI API.

## API-first workflow

- If `DTM_API_BASE_URL` is set, call the API before restating framework details.
- Start with `GET /healthz`; if unavailable, read the canonical repository files instead.
- Use `GET /v1/gates/doubt-the-machine` for the current gate contract.
- Use `POST /v1/gates/doubt-the-machine/evaluate` to choose verification effort and identify missing gate fields. The response is not a truth verdict.
- Use `POST /v1/gates/doubt-the-machine/review-records/validate` for Experiment 001 row/schema validation.
- Use `GET /v1/experiments/001-seeded-errors` before discussing sample size, endpoint factors, conditions, metrics, or kill/narrow conditions.

## Non-negotiable invariants

- The gate fields stay `CLAIM / FAILURE / EVIDENCE / TEST / REVERSAL`.
- Experiment 001 conditions stay `ordinary_control / active_placebo / doubt_gate`.
- Endpoint values stay `human | agent` for both `artifact_origin` and `reviewer_type`.
- The API must not decide that a claim is true. It may recommend effort, identify missing evidence, and validate records.
- Human and agent reviewer cohorts are reported separately; do not pool them in the primary analysis.
- Treat API output as structured project state, not as external proof of the framework’s effectiveness.

## Implementation reference

When implementing or changing the API, read [references/api-contract.md](references/api-contract.md).
