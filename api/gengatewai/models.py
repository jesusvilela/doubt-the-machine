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
MAX_VALIDATION_ERRORS = 100
MAX_VALIDATION_ERRORS_PER_ROW = 3
MAX_OPENAI_MESSAGES = 64
MAX_OPENAI_MESSAGE_CONTENT_LENGTH = 65_536
MAX_OPENAI_TOTAL_MESSAGE_CHARS = 131_072
MAX_OPENAI_METADATA_KEYS = 32
MAX_OPENAI_METADATA_VALUE_LENGTH = 8_192

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_IDENTIFIER_LENGTH)]
ClaimString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_CLAIM_LENGTH)]
ArtifactString = Annotated[str, StringConstraints(max_length=MAX_ARTIFACT_LENGTH)]
GateValue = Annotated[str, StringConstraints(max_length=MAX_GATE_VALUE_LENGTH)]
NotesString = Annotated[str, StringConstraints(max_length=MAX_NOTES_LENGTH)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OpenAICompatibleModel(BaseModel):
    model_config = ConfigDict(extra="allow")


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
        normalized = [str(key).upper() for key in gate]
        unexpected = sorted(str(key) for key in gate if str(key).upper() not in allowed)
        if unexpected:
            raise ValueError(f"unexpected gate fields: {', '.join(unexpected)}")
        if len(set(normalized)) != len(normalized):
            collisions = sorted({name for name in normalized if normalized.count(name) > 1})
            raise ValueError(f"gate fields collide after case normalization: {', '.join(collisions)}")
        return gate


class GateEvaluationResponse(StrictModel):
    framework: str
    verification_effort: Literal["light", "standard", "high"]
    reasons: list[str]
    missing_gate_fields: list[str]
    gate_form_complete: bool
    gate_substance_assessed: Literal[False] = False
    unassessed_dimensions: list[str]
    ceremony_signals: list[str]
    warnings: list[str]
    next_required_action: Literal[
        "complete_gate_form",
        "assess_gate_substance",
        "assess_gate_substance_and_preregister_or_independent_review",
    ]
    does_not_decide_truth: Literal[True] = True
    does_not_clear_for_action: Literal[True] = True


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
    error_count: NonNegativeInt
    errors_truncated: bool
    errors: list[ReviewRecordValidationError]


def _bounded_content_length(content: Any) -> int:
    if content is None:
        return 0
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        total = 0
        for item in content:
            if not isinstance(item, dict):
                raise ValueError("message content parts must be objects")
            for value in item.values():
                if isinstance(value, str):
                    total += len(value)
        return total
    raise ValueError("message content must be a string, list of content parts, or null")


class OpenAIChatMessage(OpenAICompatibleModel):
    role: Literal["system", "developer", "user", "assistant", "tool"]
    content: Any = None
    name: str | None = Field(default=None, max_length=MAX_IDENTIFIER_LENGTH)
    tool_call_id: str | None = Field(default=None, max_length=MAX_IDENTIFIER_LENGTH)

    @field_validator("content")
    @classmethod
    def validate_content_size(cls, content: Any) -> Any:
        if _bounded_content_length(content) > MAX_OPENAI_MESSAGE_CONTENT_LENGTH:
            raise ValueError("message content exceeds maximum length")
        return content


class OpenAIChatCompletionRequest(OpenAICompatibleModel):
    model: NonEmptyString
    messages: list[OpenAIChatMessage] = Field(min_length=1, max_length=MAX_OPENAI_MESSAGES)
    stream: bool = False
    n: int = Field(default=1, ge=1, le=1)
    metadata: dict[str, Any] | None = Field(default=None, max_length=MAX_OPENAI_METADATA_KEYS)
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: NonNegativeInt | None = None
    max_completion_tokens: NonNegativeInt | None = None
    user: str | None = Field(default=None, max_length=MAX_IDENTIFIER_LENGTH)

    @field_validator("metadata")
    @classmethod
    def validate_metadata_values(cls, metadata: dict[str, Any] | None) -> dict[str, Any] | None:
        if metadata is None:
            return None
        for key, value in metadata.items():
            if len(str(key)) > MAX_IDENTIFIER_LENGTH:
                raise ValueError("metadata key exceeds maximum length")
            if isinstance(value, str) and len(value) > MAX_OPENAI_METADATA_VALUE_LENGTH:
                raise ValueError("metadata value exceeds maximum length")
        return metadata

    @model_validator(mode="after")
    def validate_total_message_size(self) -> "OpenAIChatCompletionRequest":
        total = sum(_bounded_content_length(message.content) for message in self.messages)
        if total > MAX_OPENAI_TOTAL_MESSAGE_CHARS:
            raise ValueError("total message content exceeds maximum length")
        return self


class OpenAIChatCompletionResponseMessage(StrictModel):
    role: Literal["assistant"]
    content: str


class OpenAIChatCompletionChoice(StrictModel):
    index: int
    message: OpenAIChatCompletionResponseMessage
    finish_reason: Literal["stop"]
    logprobs: None = None


class OpenAIUsage(StrictModel):
    prompt_tokens: NonNegativeInt
    completion_tokens: NonNegativeInt
    total_tokens: NonNegativeInt


class OpenAIChatCompletionResponse(StrictModel):
    id: str
    object: Literal["chat.completion"]
    created: NonNegativeInt
    model: str
    choices: list[OpenAIChatCompletionChoice]
    usage: OpenAIUsage
    system_fingerprint: str
