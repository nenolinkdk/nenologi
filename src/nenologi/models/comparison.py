"""Typed representation of comparison findings; no detection logic lives here."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .analysis import Analysis, SCHEMA_VERSION
from .common import (
    ComparisonMode,
    Confidence,
    DifferenceType,
    DomainValidationError,
    Severity,
    LogicalRelation,
    validate_identifier,
)


@dataclass(frozen=True, slots=True)
class Difference:
    id: str
    difference_type: DifferenceType
    source_value: Any
    target_value: Any
    severity: Severity
    confidence: Confidence
    explanation: str
    references: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        if not isinstance(self.difference_type, DifferenceType):
            raise DomainValidationError("difference_type must be a DifferenceType")
        if not isinstance(self.severity, Severity):
            raise DomainValidationError("severity must be a Severity")
        if not isinstance(self.confidence, Confidence):
            raise DomainValidationError("confidence must be a Confidence")
        if not self.explanation or not isinstance(self.explanation, str):
            raise DomainValidationError("difference explanation must be non-empty text")
        for reference in self.references:
            validate_identifier(reference, "difference reference")
        try:
            json.dumps([self.source_value, self.target_value], allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise DomainValidationError("difference values must be JSON-compatible") from exc


@dataclass(frozen=True, slots=True)
class Comparison:
    mode: ComparisonMode
    source_analysis: Analysis
    target_analysis: Analysis
    differences: tuple[Difference, ...] = field(default_factory=tuple)
    schema_version: str = SCHEMA_VERSION
    logical_relation: LogicalRelation = LogicalRelation.UNDETERMINED

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise DomainValidationError(f"unsupported comparison schema version: {self.schema_version!r}")
        if not isinstance(self.mode, ComparisonMode):
            raise DomainValidationError("mode must be a ComparisonMode")
        if not isinstance(self.logical_relation, LogicalRelation):
            raise DomainValidationError("logical_relation must be a LogicalRelation")
        if not isinstance(self.source_analysis, Analysis) or not isinstance(self.target_analysis, Analysis):
            raise DomainValidationError("source_analysis and target_analysis must be Analysis values")
