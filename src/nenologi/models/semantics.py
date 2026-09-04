"""Semantic-layer domain models."""

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from .common import Confidence, DomainValidationError, InterpretationStatus, NumericOperator, Span, TemporalRelationType, validate_identifier

_DECIMAL_PATTERN = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")


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
        if len(self.scope) != 1:
            raise DomainValidationError("operator scope must contain exactly one reference")
        _validate_references(self.scope, "scope")
        _validate_status_and_confidence(self.interpretation_status, self.confidence)


@dataclass(frozen=True, slots=True)
class NumericConstraint:
    """An exact normalized threshold scoped to one semantic object."""

    id: str
    operator: NumericOperator
    value: Decimal
    scope: tuple[str, ...]
    interpretation_status: InterpretationStatus
    confidence: Confidence
    unit: str | None = None
    span: Span | None = None

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        if not isinstance(self.operator, NumericOperator):
            raise DomainValidationError("numeric operator must be a NumericOperator")
        if isinstance(self.value, bool) or isinstance(self.value, float):
            raise DomainValidationError("numeric value must use exact decimal input")
        text = str(self.value)
        if not _DECIMAL_PATTERN.fullmatch(text):
            raise DomainValidationError("numeric value must be a non-negative integer or simple decimal")
        try:
            normalized = Decimal(text)
        except InvalidOperation as exc:
            raise DomainValidationError("numeric value is invalid") from exc
        rendered = format(normalized, "f")
        canonical = (rendered.rstrip("0").rstrip(".") or "0") if "." in rendered else rendered
        object.__setattr__(self, "value", Decimal(canonical))
        if not self.scope:
            raise DomainValidationError("numeric constraint scope must contain at least one reference")
        _validate_references(self.scope, "scope")
        if self.unit is not None and (not isinstance(self.unit, str) or not self.unit):
            raise DomainValidationError("numeric unit must be non-empty text or None")
        _validate_status_and_confidence(self.interpretation_status, self.confidence)


@dataclass(frozen=True, slots=True)
class Condition:
    """A normalized IF relation between antecedent and consequent propositions."""

    id: str
    antecedent: tuple[str, ...]
    consequent: tuple[str, ...]
    interpretation_status: InterpretationStatus
    confidence: Confidence
    span: Span | None = None

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        if not self.antecedent or not self.consequent:
            raise DomainValidationError("condition requires antecedent and consequent references")
        _validate_references(self.antecedent, "antecedent")
        _validate_references(self.consequent, "consequent")
        _validate_status_and_confidence(self.interpretation_status, self.confidence)


@dataclass(frozen=True, slots=True)
class TemporalRelation:
    """A normalized temporal relation governing one proposition."""

    id: str
    proposition: str
    relation: TemporalRelationType
    temporal_reference: str
    interpretation_status: InterpretationStatus
    confidence: Confidence
    span: Span | None = None

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        validate_identifier(self.proposition, "proposition")
        if not isinstance(self.relation, TemporalRelationType):
            raise DomainValidationError("temporal relation must be a TemporalRelationType")
        if not isinstance(self.temporal_reference, str) or not self.temporal_reference:
            raise DomainValidationError("temporal reference must be non-empty text")
        _validate_status_and_confidence(self.interpretation_status, self.confidence)
