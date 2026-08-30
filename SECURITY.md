# Security

Doubt the Machine now exposes executable surfaces through the GenGatewAI REST API and MCP server. This document defines the security boundary for those surfaces.

## Supported security boundary

### REST API

The REST API is designed to be **stateless and non-authoritative**. It evaluates the verification gate and validates records; it does not persist submitted artifacts, execute submitted code, fetch arbitrary URLs, hold user credentials, or decide truth.

Public deployments should still enforce infrastructure-level rate limits, request-body limits, TLS, abuse monitoring, and deployment protection where appropriate.

The application schema rejects undeclared top-level fields, undeclared review-record fields, and gate keys outside `CLAIM / FAILURE / EVIDENCE / TEST / REVERSAL`. Declared text fields and validation batches are bounded.

### MCP

The supported default MCP transport is **stdio**.

Streamable HTTP is supported for local development on loopback (`127.0.0.1` / `::1`). The built-in server must not be bound directly to a non-loopback interface. Remote MCP exposure requires an authenticated reverse proxy or hosting layer implementing the current MCP authorization requirements before forwarding to the loopback server.

Do not treat network reachability as authorization.

### Self-iteration

No model, agent, workflow, or API response may directly promote its own changes to `main`. Self-iteration means proposal → evidence → checks → review → reversible promotion, not autonomous self-modification without an independent gate.

## Branch trust model

- `main`: stable/release branch. Promote only from `dev` through a reviewed PR after required checks pass.
- `dev`: integration branch for accepted feature/security work.
- `feature/*`, `security/*`, `experiment/*`: short-lived branches targeting `dev`.

Repository branch protection/rulesets should require PRs and required status checks for both `dev` and `main`. This setting is enforced at GitHub repository level, not by files in this repository. The remaining repository-setting work is tracked separately because documentation is not enforcement.

## Secrets

- Never commit credentials, API tokens, OAuth client secrets, deployment bypass tokens, or `.env` files.
- Use deployment-provider secret/environment-variable facilities.
- Treat logs and experiment notes as potentially sensitive; do not put secrets or personal data into review records.

## Dependency and CI supply chain

- GitHub Actions are pinned to immutable commit SHAs.
- Dependabot tracks Python, npm, Docker, and GitHub Actions dependencies.
- CodeQL scans Python and JavaScript/TypeScript changes.
- CI receives read-only repository contents unless a job explicitly requires more.
- The production Python base image is pinned by digest; Docker Dependabot is responsible for proposing digest/version refreshes rather than silently following a mutable tag.

## Container boundary

The production container runs as an unprivileged user. Build context excludes local secrets, VCS metadata, development caches, and local MCP/Codex configuration.

The `Container security contract` workflow builds the actual production image and verifies:

- effective runtime UID is non-root;
- image config does not declare `root`/UID 0;
- `/app` contains runtime API/experiment content but not VCS, Codex, tests, web sources, or `.env` material;
- `/healthz` responds successfully from the built image.

The Dockerfile text alone is not treated as evidence that these runtime properties hold.

## Vercel function boundary

Vercel deployments expose only the deterministic FastAPI surface through `api/index.py`.

The Vercel function bundle and deployment upload exclude non-runtime surfaces: tests, local agent/Codex state, Git metadata, GitHub workflow files, documentation, visual assets, skills, web experiments, Python caches, and `.env` material. The runtime contract must keep the API package, Python dependencies, and Experiment 001 preregistration available.

Do not treat deployment packaging as the only control. Public Vercel deployments should still use provider-side abuse controls such as deployment protection, firewall/rate-limit policy, request-size policy, and secret-managed environment variables where appropriate.

## Security invariants

1. No submitted artifact is executed.
2. No user-controlled URL is fetched by the service.
3. Request fields and batch sizes are bounded; undeclared schema fields are rejected.
4. Remote MCP cannot be accidentally exposed by changing only `--host`.
5. API/MCP outputs are advisory and never a truth/security verdict.
6. Production container runtime is non-root and its minimal filesystem is tested from the built image.
7. Vercel function deployments exclude non-runtime surfaces while preserving required runtime inputs.
8. A security-control change must remain reversible and testable.

## Reporting a vulnerability

Please do **not** publish exploit details in a public issue before a fix is available. Use GitHub's private vulnerability reporting/security-advisory mechanism for this repository when available. If that channel is unavailable, contact the maintainer privately and include:

- affected commit/version;
- attack surface and prerequisites;
- minimal reproduction;
- expected impact;
- suggested mitigation, if known.

Security reports are evidence. They can and should cause rules, code, or assumptions to be retired under Rule 0.
