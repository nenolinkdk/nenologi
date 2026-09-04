"""Shared value objects and stable machine-readable identifiers."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import StrEnum

IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*$")
LANGUAGE_PATTERN = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")


class DomainValidationError(ValueError):
    """A Python domain value violates a model invariant."""


class InterpretationStatus(StrEnum):
    EXPLICIT = "EXPLICIT"
    ENTAILED = "ENTAILED"
    PROBABLE = "PROBABLE"
    AMBIGUOUS = "AMBIGUOUS"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    CANNOT_BE_SAFELY_FORMALIZED = "CANNOT_BE_SAFELY_FORMALIZED"


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DifferenceType(StrEnum):
    NEGATION_CHANGE = "NEGATION_CHANGE"
    CONJUNCTION_CHANGE = "CONJUNCTION_CHANGE"
    QUANTIFIER_CHANGE = "QUANTIFIER_CHANGE"
    MODALITY_CHANGE = "MODALITY_CHANGE"
    CONDITION_CHANGE = "CONDITION_CHANGE"
    TEMPORAL_CHANGE = "TEMPORAL_CHANGE"
    SCOPE_CHANGE = "SCOPE_CHANGE"
    ENTITY_RELATION_CHANGE = "ENTITY_RELATION_CHANGE"
    ADDITION = "ADDITION"
    OMISSION = "OMISSION"
    CONTRADICTION = "CONTRADICTION"
    NUMERIC_THRESHOLD_CHANGE = "NUMERIC_THRESHOLD_CHANGE"


class ComparisonMode(StrEnum):
    SOURCE_TRANSLATION = "SOURCE_TRANSLATION"
    VERSION_COMPARISON = "VERSION_COMPARISON"
    PROMPT_OUTPUT = "PROMPT_OUTPUT"
    SEO_LOCALIZATION = "SEO_LOCALIZATION"


def validate_identifier(value: str, field_name: str = "id") -> None:
    if not isinstance(value, str) or not IDENTIFIER_PATTERN.fullmatch(value):
        raise DomainValidationError(f"{field_name} is not a valid Nenologi identifier: {value!r}")


def validate_language(value: str) -> None:
    if not isinstance(value, str) or not LANGUAGE_PATTERN.fullmatch(value):
        raise DomainValidationError(f"invalid document language tag: {value!r}")


@dataclass(frozen=True, slots=True)
class Confidence:
    value: float
    rationale: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise DomainValidationError("confidence value must be numeric")
        numeric = float(self.value)
        if not math.isfinite(numeric) or not 0.0 <= numeric <= 1.0:
            raise DomainValidationError("confidence value must be between 0.0 and 1.0")
        object.__setattr__(self, "value", numeric)
        if self.rationale is not None and not isinstance(self.rationale, str):
            raise DomainValidationError("confidence rationale must be text or None")


@dataclass(frozen=True, slots=True)
class Span:
    start: int
    end: int

    def __post_init__(self) -> None:
        if isinstance(self.start, bool) or isinstance(self.end, bool):
            raise DomainValidationError("span offsets must be integers")
        if not isinstance(self.start, int) or not isinstance(self.end, int):
            raise DomainValidationError("span offsets must be integers")
        if self.start < 0 or self.end < self.start:
            raise DomainValidationError("span must be zero-based and end-exclusive")


@dataclass(frozen=True, slots=True)
class Document:
    id: str
    language: str
    text: str

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        validate_language(self.language)
        if not isinstance(self.text, str) or not self.text:
            raise DomainValidationError("document text must be non-empty")


@dataclass(frozen=True, slots=True)
class LocalizedText:
    language: str
    text: str

    def __post_init__(self) -> None:
        validate_language(self.language)
        if not isinstance(self.text, str):
            raise DomainValidationError("localized text must be text")
