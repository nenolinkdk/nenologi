"""Phase 3 interpretation results built on frozen Phase 2 outputs."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from ..models import Confidence, DomainValidationError, Inference, InterpretationStatus
from ..models.common import validate_identifier

INTERPRETATION_SCHEMA_VERSION = "0.1"


class EvidenceSide(StrEnum):
    PREMISE = "PREMISE"
    QUERY = "QUERY"
    DETERMINISTIC_RESULT = "DETERMINISTIC_RESULT"


class EvidenceObjectKind(StrEnum):
    ENTITY = "ENTITY"
    PROPOSITION = "PROPOSITION"
    OPERATOR = "OPERATOR"
    TEMPORAL_RELATION = "TEMPORAL_RELATION"
    SEMANTIC_ITEM = "SEMANTIC_ITEM"
    AMBIGUITY = "AMBIGUITY"
    ALTERNATIVE = "ALTERNATIVE"
    INFERENCE = "INFERENCE"


class InterpretationProvenance(StrEnum):
    EXACT_EXPLICIT = "EXACT_EXPLICIT"
    LEXICAL_OPPOSITION = "LEXICAL_OPPOSITION"
    UNIVERSAL_INSTANTIATION = "UNIVERSAL_INSTANTIATION"
    PHASE3_DETERMINISTIC_POLICY = "PHASE3_DETERMINISTIC_POLICY"
    BOUNDED_HEURISTIC = "BOUNDED_HEURISTIC"
    AI_ASSISTED_INTERPRETATION = "AI_ASSISTED_INTERPRETATION"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    role: str
    analysis_side: EvidenceSide
    object_kind: EvidenceObjectKind
    object_id: str
    reading_id: str | None = None

    def __post_init__(self) -> None:
        validate_identifier(self.role, "evidence role")
        if not isinstance(self.analysis_side, EvidenceSide):
            raise DomainValidationError("evidence analysis_side must be an EvidenceSide")
        if not isinstance(self.object_kind, EvidenceObjectKind):
            raise DomainValidationError("evidence object_kind must be an EvidenceObjectKind")
        validate_identifier(self.object_id, "evidence object_id")
        if self.reading_id is not None:
            validate_identifier(self.reading_id, "evidence reading_id")


@dataclass(frozen=True, slots=True)
class InterpretationResult:
    id: str
    interpretation_status: InterpretationStatus
    confidence: Confidence
    provenance: InterpretationProvenance
    deterministic_result: Inference
    policy_id: str | None = None
    evidence: tuple[EvidenceReference, ...] = field(default_factory=tuple)
    explanation_inputs: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    schema_version: str = INTERPRETATION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        if self.schema_version != INTERPRETATION_SCHEMA_VERSION:
            raise DomainValidationError(
                f"unsupported interpretation schema version: {self.schema_version!r}"
            )
        if not isinstance(self.interpretation_status, InterpretationStatus):
            raise DomainValidationError("interpretation_status must be an InterpretationStatus")
        if not isinstance(self.confidence, Confidence):
            raise DomainValidationError("confidence must be a Confidence")
        if not isinstance(self.provenance, InterpretationProvenance):
            raise DomainValidationError("provenance must be an InterpretationProvenance")
        if not isinstance(self.deterministic_result, Inference):
            raise DomainValidationError("deterministic_result must be an Inference")
        if self.policy_id is not None:
            validate_identifier(self.policy_id, "policy_id")
        if len(set(self.evidence)) != len(self.evidence):
            raise DomainValidationError("interpretation evidence must not contain duplicates")
        if any(not isinstance(item, EvidenceReference) for item in self.evidence):
            raise DomainValidationError("evidence must contain EvidenceReference values")
        keys: set[str] = set()
        for item in self.explanation_inputs:
            if not isinstance(item, tuple) or len(item) != 2:
                raise DomainValidationError("explanation inputs must be key/value pairs")
            key, value = item
            validate_identifier(key, "explanation input key")
            if key in keys:
                raise DomainValidationError("explanation input keys must be unique")
            if not isinstance(value, str):
                raise DomainValidationError("explanation input values must be text")
            keys.add(key)
        is_policy_result = self.provenance is InterpretationProvenance.PHASE3_DETERMINISTIC_POLICY
        if is_policy_result and (self.policy_id is None or not self.evidence):
            raise DomainValidationError("a Phase 3 deterministic policy result requires policy_id and evidence")
        if self.policy_id is not None and not is_policy_result:
            raise DomainValidationError("policy_id requires Phase 3 deterministic policy provenance")
        try:
            json.dumps(dict(self.explanation_inputs), ensure_ascii=False, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise DomainValidationError("explanation inputs must be JSON-compatible") from exc
