from __future__ import annotations

import argparse
import ipaddress
import json
from typing import Any, Literal

from mcp.server import MCPServer
from pydantic import ValidationError

from api.gengatewai.contracts import API_VERSION, SERVICE_NAME, experiment_summary, framework_contract
from api.gengatewai.models import GateEvaluationRequest, ReviewRecordsValidationRequest
from api.gengatewai.service import evaluate_gate, load_preregistration, validate_record_payloads

MCP_SERVER_NAME = "gengatewai-doubt-the-machine"
MCP_SERVER_TITLE = "GenGatewAI Doubt the Machine"

mcp = MCPServer(
    MCP_SERVER_NAME,
    title=MCP_SERVER_TITLE,
    version=API_VERSION,
    description=(
        "MCP server exposing the deterministic Doubt the Machine gate, "
        "Experiment 001 contract, and review-record validator."
    ),
    instructions=(
        "Use these tools to inspect the framework contract, choose verification effort, "
        "or validate Experiment 001 records. The server does not decide whether the claim is true."
    ),
)


def _json_resource(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _validation_error_response(exc: ValidationError) -> dict[str, Any]:
    return {
        "valid": False,
        "errors": [
            {
                "location": ".".join(str(part) for part in error["loc"]),
                "message": str(error["msg"]),
            }
            for error in exc.errors()
        ],
        "does_not_decide_truth": True,
    }


def _is_loopback_host(host: str) -> bool:
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


@mcp.tool()
def healthz() -> dict[str, str]:
    """Return the GenGatewAI service identity and health status."""
    return {"service": SERVICE_NAME, "version": API_VERSION, "status": "ok"}


@mcp.tool()
def get_doubt_the_machine_contract() -> dict[str, Any]:
    """Return the current Doubt the Machine framework contract."""
    return framework_contract()


@mcp.tool()
def evaluate_doubt_gate(
    claim: str,
    artifact_origin: Literal["human", "agent"],
    reviewer_type: Literal["human", "agent"],
    artifact: str | None = None,
    uncertainty: Literal["low", "medium", "high"] = "medium",
    consequence: Literal["low", "medium", "high"] = "medium",
    reversibility: Literal["easy", "moderate", "hard", "irreversible"] = "moderate",
    external_claim: bool = False,
    experiment_or_metric: bool = False,
    active_rule_or_evidence_change: bool = False,
    gate: dict[str, str | None] | None = None,
) -> dict[str, Any]:
    """Evaluate a claim/change against the Doubt gate without returning a truth verdict."""
    try:
        request = GateEvaluationRequest(
            claim=claim,
            artifact=artifact,
            artifact_origin=artifact_origin,
            reviewer_type=reviewer_type,
            uncertainty=uncertainty,
            consequence=consequence,
            reversibility=reversibility,
            external_claim=external_claim,
            experiment_or_metric=experiment_or_metric,
            active_rule_or_evidence_change=active_rule_or_evidence_change,
            gate=gate or {},
        )
    except ValidationError as exc:
        return _validation_error_response(exc)

    return evaluate_gate(request).model_dump(mode="json")


@mcp.tool()
def validate_experiment_001_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate Experiment 001 review records without storing them."""
    try:
        request = ReviewRecordsValidationRequest(records=records)
    except ValidationError as exc:
        return _validation_error_response(exc)
    return validate_record_payloads(request).model_dump(mode="json")


@mcp.tool()
def get_experiment_001_contract() -> dict[str, Any]:
    """Return the preregistered Experiment 001 design and sample plan."""
    return experiment_summary(load_preregistration())


@mcp.resource(
    "gengatewai://doubt-the-machine/contract",
    mime_type="application/json",
)
def doubt_the_machine_contract_resource() -> str:
    """JSON resource for the current Doubt the Machine framework contract."""
    return _json_resource(framework_contract())


@mcp.resource(
    "gengatewai://experiments/001-seeded-errors",
    mime_type="application/json",
)
def experiment_001_resource() -> str:
    """JSON resource for the preregistered Experiment 001 contract."""
    return _json_resource(experiment_summary(load_preregistration()))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the GenGatewAI Doubt the Machine MCP server.")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default="stdio",
        help="MCP transport to use. Defaults to stdio for local MCP hosts.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host for streamable-http transport.")
    parser.add_argument("--port", type=int, default=8766, help="Port for streamable-http transport.")
    parser.add_argument("--path", default="/mcp", help="Path for streamable-http transport.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.transport == "stdio":
        mcp.run("stdio")
        return

    if not _is_loopback_host(args.host):
        raise SystemExit(
            "Refusing non-loopback MCP binding without an authenticated front proxy. "
            "Bind this server to 127.0.0.1/::1 and terminate remote authentication upstream."
        )

    mcp.run(
        "streamable-http",
        host=args.host,
        port=args.port,
        streamable_http_path=args.path,
    )


if __name__ == "__main__":
    main()
