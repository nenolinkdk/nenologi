"""Semantic-layer domain models."""

from dataclasses import dataclass, field

from .common import Confidence, DomainValidationError, InterpretationStatus, Span, validate_identifier


def _validate_references(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        validate_identifier(value, field_name)


def _validate_status_and_confidence(status: InterpretationStatus, confidence: Confidence) -> None:
    if not isinstance(status, InterpretationStatus):
        raise DomainValidationError("interpretation_status must be an InterpretationStatus")
    if not isinstance(confidence, Confidence):
        raise DomainValidationError("confidence must be a Confidence")


@dataclass(frozen=True, slots=True)
class Entity:
    id: str
    type: str
    label: str
    interpretation_status: InterpretationStatus
    confidence: Confidence
    span: Span | None = None

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        if not self.type or not isinstance(self.type, str):
            raise DomainValidationError("entity type must be non-empty text")
        if not isinstance(self.label, str):
            raise DomainValidationError("entity label must be text")
        _validate_status_and_confidence(self.interpretation_status, self.confidence)


@dataclass(frozen=True, slots=True)
class Proposition:
    id: str
    predicate: str
    arguments: tuple[str, ...]
    interpretation_status: InterpretationStatus
    confidence: Confidence
    span: Span | None = None
    derived_from: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        if not self.predicate or not isinstance(self.predicate, str):
            raise DomainValidationError("predicate must be non-empty text")
        _validate_references(self.arguments, "argument")
        _validate_references(self.derived_from, "derived_from")
        _validate_status_and_confidence(self.interpretation_status, self.confidence)


@dataclass(frozen=True, slots=True)
class SemanticItem:
    id: str
    type: str
    arguments: tuple[str, ...]
    interpretation_status: InterpretationStatus
    confidence: Confidence
    span: Span | None = None
    derived_from: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        if not self.type or not isinstance(self.type, str):
            raise DomainValidationError("semantic item type must be non-empty text")
        _validate_references(self.arguments, "argument")
        _validate_references(self.derived_from, "derived_from")
        _validate_status_and_confidence(self.interpretation_status, self.confidence)


@dataclass(frozen=True, slots=True)
class Operator:
    id: str
    operator: str
    scope: tuple[str, ...]
    interpretation_status: InterpretationStatus
    confidence: Confidence
    span: Span | None = None

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        if not self.operator or not isinstance(self.operator, str):
            raise DomainValidationError("operator must be non-empty text")
        if not self.scope:
            raise DomainValidationError("operator scope must contain at least one reference")
        _validate_references(self.scope, "scope")
        _validate_status_and_confidence(self.interpretation_status, self.confidence)
