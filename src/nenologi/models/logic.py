"""Logical and inference-layer domain models."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .common import Confidence, DomainValidationError, InterpretationStatus, validate_identifier
from .semantics import _validate_references, _validate_status_and_confidence


@dataclass(frozen=True, slots=True)
class LogicalExpression:
    id: str
    expression: dict[str, Any]
    interpretation_status: InterpretationStatus
    confidence: Confidence
    display: str | None = None
    derived_from: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        if not isinstance(self.expression, dict) or not isinstance(self.expression.get("operator"), str):
            raise DomainValidationError("logical expression must contain a text operator")
        try:
            json.dumps(self.expression, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise DomainValidationError("logical expression must be JSON-compatible") from exc
        if self.display is not None and not isinstance(self.display, str):
            raise DomainValidationError("logical display must be text or None")
        _validate_references(self.derived_from, "derived_from")
        _validate_status_and_confidence(self.interpretation_status, self.confidence)


@dataclass(frozen=True, slots=True)
class Inference:
    id: str
    claim: str
    interpretation_status: InterpretationStatus
    confidence: Confidence
    derived_from: tuple[str, ...] = field(default_factory=tuple)
    rule: str | None = None

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        if not self.claim or not isinstance(self.claim, str):
            raise DomainValidationError("inference claim must be non-empty text")
        if self.rule is not None and not isinstance(self.rule, str):
            raise DomainValidationError("inference rule must be text or None")
        _validate_references(self.derived_from, "derived_from")
        _validate_status_and_confidence(self.interpretation_status, self.confidence)


@dataclass(frozen=True, slots=True)
class Ambiguity:
    id: str
    description: str
    reading_ids: tuple[str, ...]
    confidence: Confidence

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        if not self.description or not isinstance(self.description, str):
            raise DomainValidationError("ambiguity description must be non-empty text")
        if len(self.reading_ids) < 2:
            raise DomainValidationError("ambiguity must reference at least two readings")
        _validate_references(self.reading_ids, "reading_id")
        if not isinstance(self.confidence, Confidence):
            raise DomainValidationError("confidence must be a Confidence")
