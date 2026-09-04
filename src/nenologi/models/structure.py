"""Structural-layer domain models."""

from dataclasses import dataclass, field
from enum import StrEnum

from .common import DomainValidationError, Span, validate_identifier


class DiscourseRelationType(StrEnum):
    COORDINATION = "COORDINATION"
    SUBORDINATION = "SUBORDINATION"
    SEQUENCE = "SEQUENCE"
    CONTRAST = "CONTRAST"
    EXCEPTION = "EXCEPTION"
    CAUSE = "CAUSE"
    CONSEQUENCE = "CONSEQUENCE"


@dataclass(frozen=True, slots=True)
class StructuralNode:
    id: str
    span: Span
    parent_id: str | None = None
    kind: str | None = None

    def __post_init__(self) -> None:
        validate_identifier(self.id)
        if self.parent_id is not None:
            validate_identifier(self.parent_id, "parent_id")
        if self.kind is not None and not isinstance(self.kind, str):
            raise DomainValidationError("structural-node kind must be text or None")


@dataclass(frozen=True, slots=True)
class DiscourseRelation:
    id: str
    type: DiscourseRelationType
    source_id: str
    target_id: str

    def __post_init__(self) -> None:
        for name in ("id", "source_id", "target_id"):
            validate_identifier(getattr(self, name), name)
        if not isinstance(self.type, DiscourseRelationType):
            raise DomainValidationError("type must be a DiscourseRelationType")


@dataclass(frozen=True, slots=True)
class Structure:
    sentences: tuple[StructuralNode, ...] = field(default_factory=tuple)
    clauses: tuple[StructuralNode, ...] = field(default_factory=tuple)
    discourse_relations: tuple[DiscourseRelation, ...] = field(default_factory=tuple)
