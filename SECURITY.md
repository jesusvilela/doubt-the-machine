# Security

Doubt the Machine exposes executable surfaces through the GenGatewAI REST API and MCP server. This document defines the security boundary for those surfaces.

## Supported security boundary

### REST API

The REST API is designed to be **stateless and non-authoritative**. It evaluates the verification gate and validates records; it does not persist submitted artifacts, execute submitted code, fetch arbitrary user-provided URLs, hold user credentials, or decide truth.

Public deployments should still enforce infrastructure-level rate limits, request-body limits, TLS, abuse monitoring, and deployment protection where appropriate.

The application schema rejects undeclared top-level fields, undeclared review-record fields, gate keys outside `CLAIM / FAILURE / EVIDENCE / TEST / REVERSAL`, and case-variant gate-key collisions. Declared text fields and validation batches are bounded. Validation responses are bounded separately from requests: total error count is preserved, while the detailed error list is capped and explicitly reports truncation.

### Local model recruitment

The OpenAI-compatible runner can optionally recruit local LM Studio and Ollama capacity. This is disabled by default.

Local detection is limited to fixed provider conventions and operator-configured environment variables. Request payloads cannot supply arbitrary provider URLs. LAN Ollama discovery is opt-in and should only be enabled on trusted local networks.

Actual lab details — workstation paths, LAN addresses, model inventories, and local credentials — must stay in ignored local files such as `.env.local`, `.gengatewai.local.json`, or `local-lab.json`.

The public Vercel deployment should keep local model recruitment disabled unless a separate trusted private-network boundary is deliberately configured.

### MCP

The supported default MCP transport is **stdio**.

Streamable HTTP is supported for local development on loopback (`127.0.0.1` / `::1`). The built-in server must not be bound directly to a non-loopback interface. Remote MCP exposure requires an authenticated reverse proxy or hosting layer implementing the current MCP authorization requirements before forwarding to the loopback server.

Do not treat network reachability as authorization.

The committed Codex project configuration uses automatic approval only for the exact audited non-mutating GenGatewAI tool whitelist. `check_rule0.py` rejects widening that whitelist; the configuration test also pins the approval mode. Adding a mutating tool requires revisiting this trust boundary rather than inheriting automatic approval silently.

### Self-iteration

No model, agent, workflow, or API response may directly promote its own changes to `main`. Self-iteration means proposal → evidence → checks → review → reversible promotion, not autonomous self-modification without an independent gate.

`ACAF.md` and `scripts/acaf_ambigator.py` adversarially mutate the repository contract in throwaway copies. The required PR gate runs a shallow sweep and the nightly workflow runs a deeper sweep. An ACAF pass establishes only that the checker rejects the declared mutation span with the measured escape/false-alarm rates. It is not evidence that the framework works, and because the harness and hardening were developed in the same loop it is not an independent replication witness.

## Branch trust model

- `main`: stable/release branch. Promote only from `dev` through a reviewed PR after required checks pass.
- `dev`: integration branch for accepted feature/security work.
- `feature/*`, `security/*`, `experiment/*`, `tock/*`: short-lived branches targeting `dev`.

Repository rulesets require pull requests, resolved review conversations, an up-to-date base, and the required status checks for both `dev` and `main`, while blocking deletion and non-fast-forward updates. `v*` release tags are immutable under a tag ruleset. These controls live in GitHub repository settings; repository files audit them but do not create them.

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
- The required `self-audit-contract` includes a 3-seed/family ACAF sweep. A separate nightly workflow runs 25 seeds/family.

## Release boundary

A human-pushed `v*` tag triggers `.github/workflows/release.yml`. The workflow re-checks Rule 0, runs a deep ACAF sweep, runs Python/API/MCP and vGPU tests, builds the production image, re-tests the container boundary and `/healthz`, and only then enters the `release` environment to create the GitHub Release.

The workflow reference to `environment: release` is not itself proof that the GitHub environment has reviewer protection configured. Protect that environment in repository settings before relying on it as a human approval boundary. Release tags remain immutable independently through the repository tag ruleset.

## Container boundary

The production container runs as an unprivileged user. Build context excludes local secrets, VCS metadata, development caches, and local MCP/Codex configuration.

The `Container security contract` workflow builds the actual production image and verifies:

- effective runtime UID is non-root;
- image config does not declare `root`/UID 0;
- `/app` contains runtime API/experiment content but not VCS, Codex, tests, web sources, or `.env` material;
- `/healthz` responds successfully from the built image.

The Dockerfile text alone is not treated as evidence that these runtime properties hold.

## Vercel function boundary

Vercel deployments expose the deterministic FastAPI surface through the supported root `app.py` entrypoint.

The Vercel function bundle and deployment upload exclude non-runtime surfaces: tests, local agent/Codex state, Git metadata, GitHub workflow files, documentation, visual assets, skills, web experiments, Python caches, and `.env` material. The runtime contract must keep the API package, Python dependencies, and Experiment 001 preregistration available.

Do not treat deployment packaging as the only control. Public Vercel deployments should still use provider-side abuse controls such as deployment protection, firewall/rate-limit policy, request-size policy, and secret-managed environment variables where appropriate.

## Security invariants

1. No submitted artifact is executed.
2. No user-controlled URL is fetched by the service.
3. Request fields, batch sizes, and detailed validation-error output are bounded; undeclared schema fields and normalized gate-key collisions are rejected.
4. Remote MCP cannot be accidentally exposed by changing only `--host`.
5. API/MCP outputs are advisory and never a truth/security verdict.
6. Production container runtime is non-root and its minimal filesystem is tested from the built image.
7. Vercel function deployments exclude non-runtime surfaces while preserving required runtime inputs.
8. Local model recruitment is disabled by default, fixed-provider only, and never accepts arbitrary provider URLs from request payloads.
9. Automatic MCP tool approval is coupled to the audited non-mutating whitelist.
10. A security-control change must remain reversible and testable.
11. Self-iteration cannot directly promote its own output; passing ACAF/CI is evidence about checks, not authority to merge.

## Reporting a vulnerability

Please do **not** publish exploit details in a public issue before a fix is available. Use GitHub's private vulnerability reporting/security-advisory mechanism for this repository when available. If that channel is unavailable, contact the maintainer privately and include:

- affected commit/version;
- attack surface and prerequisites;
- minimal reproduction;
- expected impact;
- suggested mitigation, if known.

Security reports are evidence. They can and should cause rules, code, or assumptions to be retired under Rule 0.
