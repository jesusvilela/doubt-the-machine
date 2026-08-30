from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    StringConstraints,
    field_validator,
    model_validator,
)

from api.gengatewai.contracts import GATE_FIELDS

MAX_IDENTIFIER_LENGTH = 256
MAX_CLAIM_LENGTH = 8_192
MAX_ARTIFACT_LENGTH = 65_536
MAX_GATE_VALUE_LENGTH = 8_192
MAX_NOTES_LENGTH = 8_192
MAX_REVIEW_RECORDS = 1_000

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_IDENTIFIER_LENGTH)]
ClaimString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_CLAIM_LENGTH)]
ArtifactString = Annotated[str, StringConstraints(max_length=MAX_ARTIFACT_LENGTH)]
GateValue = Annotated[str, StringConstraints(max_length=MAX_GATE_VALUE_LENGTH)]
NotesString = Annotated[str, StringConstraints(max_length=MAX_NOTES_LENGTH)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EndpointValue(str, Enum):
    human = "human"
    agent = "agent"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Reversibility(str, Enum):
    easy = "easy"
    moderate = "moderate"
    hard = "hard"
    irreversible = "irreversible"


class GateEvaluationRequest(StrictModel):
    claim: ClaimString
    artifact: ArtifactString | None = None
    artifact_origin: EndpointValue
    reviewer_type: EndpointValue
    uncertainty: RiskLevel = RiskLevel.medium
    consequence: RiskLevel = RiskLevel.medium
    reversibility: Reversibility = Reversibility.moderate
    external_claim: bool = False
    experiment_or_metric: bool = False
    active_rule_or_evidence_change: bool = False
    gate: dict[str, GateValue | None] = Field(default_factory=dict, max_length=len(GATE_FIELDS))

    @field_validator("gate")
    @classmethod
    def validate_gate_keys(cls, gate: dict[str, GateValue | None]) -> dict[str, GateValue | None]:
        allowed = set(GATE_FIELDS)
        unexpected = sorted(str(key) for key in gate if str(key).upper() not in allowed)
        if unexpected:
            raise ValueError(f"unexpected gate fields: {', '.join(unexpected)}")
        return gate


class GateEvaluationResponse(StrictModel):
    framework: str
    verification_effort: Literal["light", "standard", "high"]
    reasons: list[str]
    missing_gate_fields: list[str]
    warnings: list[str]
    next_required_action: Literal["complete_gate", "run_required_checks", "preregister_or_independent_review"]
    does_not_decide_truth: Literal[True] = True


class ReviewRecord(StrictModel):
    task_id: NonEmptyString
    task_family: NonEmptyString
    condition: Literal["ordinary_control", "active_placebo", "doubt_gate"]
    variant_id: NonEmptyString
    artifact_origin: Literal["human", "agent"]
    reviewer_id: NonEmptyString
    reviewer_type: Literal["human", "agent"]
    cohort_id: NonEmptyString
    seeded_defect_count: NonNegativeInt
    important_defect_count: NonNegativeInt
    important_defects_caught: NonNegativeInt
    important_defects_escaped: NonNegativeInt
    false_alarms: NonNegativeInt
    accepted: Literal[0, 1]
    reversed_after_evidence: Literal[0, 1]
    external_checks: NonNegativeInt
    review_minutes: NonNegativeFloat
    notes: NotesString = ""

    @model_validator(mode="after")
    def validate_counts(self) -> "ReviewRecord":
        if self.important_defect_count > self.seeded_defect_count:
            raise ValueError("important_defect_count exceeds seeded_defect_count")
        if self.important_defects_caught + self.important_defects_escaped != self.important_defect_count:
            raise ValueError("important_defects_caught + important_defects_escaped must equal important_defect_count")
        return self


class ReviewRecordsValidationRequest(StrictModel):
    records: list[dict[str, Any]] = Field(max_length=MAX_REVIEW_RECORDS)


class ReviewRecordValidationError(StrictModel):
    row_index: int
    message: str


class ReviewRecordsValidationResponse(StrictModel):
    valid: bool
    accepted_rows: int
    errors: list[ReviewRecordValidationError]
