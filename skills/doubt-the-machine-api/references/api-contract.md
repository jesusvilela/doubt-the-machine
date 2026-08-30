# GenGatewAI API contract

## Required endpoints

- `GET /healthz` returns service name, version, and status.
- `GET /v1/gates/doubt-the-machine` returns Rule 0, scope, gate fields, surfaces, evidence levels, dev loop, verification effort knobs, endpoint values, and conditions.
- `POST /v1/gates/doubt-the-machine/evaluate` accepts a claim, endpoint fields, risk inputs, and optional gate answers. It returns verification effort, missing gate fields, warnings, and next action.
- `POST /v1/gates/doubt-the-machine/review-records/validate` validates Experiment 001 review records without storing them.
- `GET /v1/experiments/001-seeded-errors` returns the preregistered Experiment 001 design and sample plan.

## Evaluation behavior

- Use `high` effort for experiments, metrics, kill conditions, external claims, high consequence, or hard/irreversible rollback.
- Use `standard` effort for active rules, evidence ledgers, CI checks, medium consequence, medium/high uncertainty, or moderate rollback.
- Use `light` effort only for low-consequence, low-uncertainty, easily reversible presentation or wording checks.
- Always report missing gate fields rather than filling them in.
- Never return an “accepted” or “true” verdict for the claim.

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
- result CSV header.
