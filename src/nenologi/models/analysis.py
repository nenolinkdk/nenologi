"""Aggregate model for a single Nenologi analysis."""

import re
from dataclasses import dataclass, field

from .common import Confidence, Document, DomainValidationError, LocalizedText
from .logic import Ambiguity, Inference, LogicalExpression
from .semantics import Entity, NumericConstraint, Operator, Proposition, SemanticItem
from .structure import Structure

SCHEMA_VERSION = "0.1"
PROFILE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class Analysis:
    document: Document
    profile: str
    confidence: Confidence
    plain_language_interpretation: LocalizedText
    structure: Structure = field(default_factory=Structure)
    entities: tuple[Entity, ...] = field(default_factory=tuple)
    propositions: tuple[Proposition, ...] = field(default_factory=tuple)
    relations: tuple[SemanticItem, ...] = field(default_factory=tuple)
    quantifiers: tuple[Operator, ...] = field(default_factory=tuple)
    modality: tuple[Operator, ...] = field(default_factory=tuple)
    negation: tuple[Operator, ...] = field(default_factory=tuple)
    numeric_constraints: tuple[NumericConstraint, ...] = field(default_factory=tuple)
    conditions: tuple[SemanticItem, ...] = field(default_factory=tuple)
    temporal_relations: tuple[SemanticItem, ...] = field(default_factory=tuple)
    sets: tuple[SemanticItem, ...] = field(default_factory=tuple)
    logical_representation: tuple[LogicalExpression, ...] = field(default_factory=tuple)
    inferences: tuple[Inference, ...] = field(default_factory=tuple)
    ambiguities: tuple[Ambiguity, ...] = field(default_factory=tuple)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise DomainValidationError(f"unsupported analysis schema version: {self.schema_version!r}")
        if not isinstance(self.profile, str) or not PROFILE_PATTERN.fullmatch(self.profile):
            raise DomainValidationError("profile must be a lower-case machine identifier")
        if not isinstance(self.document, Document):
            raise DomainValidationError("document must be a Document")
        if not isinstance(self.structure, Structure):
            raise DomainValidationError("structure must be a Structure")
        if not isinstance(self.confidence, Confidence):
            raise DomainValidationError("confidence must be a Confidence")
        if not isinstance(self.plain_language_interpretation, LocalizedText):
            raise DomainValidationError("plain_language_interpretation must be LocalizedText")

    def all_identified_objects(self) -> tuple[object, ...]:
        """Return every object participating in v0.1 ID/reference validation."""
        return (
            *self.structure.sentences,
            *self.structure.clauses,
            *self.structure.discourse_relations,
            *self.entities,
            *self.propositions,
            *self.relations,
            *self.quantifiers,
            *self.modality,
            *self.negation,
            *self.numeric_constraints,
            *self.conditions,
            *self.temporal_relations,
            *self.sets,
            *self.logical_representation,
            *self.inferences,
            *self.ambiguities,
        )
