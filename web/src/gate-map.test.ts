import { describe, expect, it } from "vitest";

import { buildGateMap, effortWeight, endpointCell, endpointCells, perReviewerCohortEndpointCells } from "./gate-map.js";

describe("gate map", () => {
  it("maps endpoint cells consistently", () => {
    expect(endpointCell("human", "agent")).toBe("human→agent");
    expect(endpointCell("agent", "human")).toBe("agent→human");
    expect(endpointCells.map((cell) => cell.label)).toEqual([
      "human→human",
      "human→agent",
      "agent→human",
      "agent→agent",
    ]);
    expect(perReviewerCohortEndpointCells.human).toEqual(["human→human", "agent→human"]);
    expect(perReviewerCohortEndpointCells.agent).toEqual(["human→agent", "agent→agent"]);
  });

  it("marks missing gate fields inactive and selected effort active", () => {
    const map = buildGateMap({
      verification_effort: "high",
      missing_gate_fields: ["EVIDENCE", "REVERSAL"],
      artifact_origin: "agent",
      reviewer_type: "human",
    });

    expect(map.nodes.find((node) => node.id === "field:EVIDENCE")?.active).toBe(false);
    expect(map.nodes.find((node) => node.id === "field:CLAIM")?.active).toBe(true);
    expect(map.nodes.find((node) => node.id === "effort:high")?.active).toBe(true);
    expect(map.nodes.find((node) => node.id === "endpoint:agent→human")?.active).toBe(true);
    expect(map.edges).toContainEqual({ from: "loop:DOUBT", to: "loop:MEASURE" });
  });

  it("keeps effort ordering explicit for visual weight", () => {
    expect(effortWeight("light")).toBeLessThan(effortWeight("standard"));
    expect(effortWeight("standard")).toBeLessThan(effortWeight("high"));
  });

  it("can load the Vercel Labs vgpu mock export for GPU-free CI", async () => {
    const mock = await import("vgpu/mock");
    expect(Object.keys(mock).length).toBeGreaterThan(0);
  });
});
