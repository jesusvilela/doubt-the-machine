export const devLoop = ["DOUBT", "MEASURE", "TEST", "REVERT", "REPEAT"] as const;
export const gateFields = ["CLAIM", "FAILURE", "EVIDENCE", "TEST", "REVERSAL"] as const;
export const efforts = ["light", "standard", "high"] as const;
export const endpointValues = ["human", "agent"] as const;

export type Effort = (typeof efforts)[number];
export type EndpointValue = (typeof endpointValues)[number];

export interface GateEvaluationSummary {
  verification_effort?: Effort;
  missing_gate_fields?: string[];
  artifact_origin?: EndpointValue;
  reviewer_type?: EndpointValue;
}

export interface GateMapNode {
  id: string;
  label: string;
  kind: "loop" | "field" | "effort" | "endpoint";
  active: boolean;
}

export interface GateMapEdge {
  from: string;
  to: string;
}

export function endpointCell(origin: EndpointValue, reviewer: EndpointValue): string {
  return `${origin}→${reviewer}`;
}

export const endpointCells = endpointValues.flatMap((artifact_origin) =>
  endpointValues.map((reviewer_type) => ({
    artifact_origin,
    reviewer_type,
    label: endpointCell(artifact_origin, reviewer_type),
  })),
);

export const perReviewerCohortEndpointCells = {
  human: endpointValues.map((artifact_origin) => endpointCell(artifact_origin, "human")),
  agent: endpointValues.map((artifact_origin) => endpointCell(artifact_origin, "agent")),
} as const;

export function effortWeight(effort: Effort): number {
  return effort === "high" ? 3 : effort === "standard" ? 2 : 1;
}

export function buildGateMap(summary: GateEvaluationSummary = {}): { nodes: GateMapNode[]; edges: GateMapEdge[] } {
  const missing = new Set(summary.missing_gate_fields ?? []);
  const selectedEffort = summary.verification_effort ?? "standard";
  const selectedEndpoint =
    summary.artifact_origin && summary.reviewer_type ? endpointCell(summary.artifact_origin, summary.reviewer_type) : "";

  const loopNodes = devLoop.map((label) => ({
    id: `loop:${label}`,
    label,
    kind: "loop" as const,
    active: true,
  }));

  const fieldNodes = gateFields.map((label) => ({
    id: `field:${label}`,
    label,
    kind: "field" as const,
    active: !missing.has(label),
  }));

  const effortNodes = efforts.map((label) => ({
    id: `effort:${label}`,
    label,
    kind: "effort" as const,
    active: label === selectedEffort,
  }));

  const endpointNodes = endpointCells.map((cell) => ({
    id: `endpoint:${cell.label}`,
    label: cell.label,
    kind: "endpoint" as const,
    active: cell.label === selectedEndpoint,
  }));

  const edges = devLoop.slice(0, -1).map((step, index) => ({
    from: `loop:${step}`,
    to: `loop:${devLoop[index + 1]}`,
  }));

  return { nodes: [...loopNodes, ...fieldNodes, ...effortNodes, ...endpointNodes], edges };
}
