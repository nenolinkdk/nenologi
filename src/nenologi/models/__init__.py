from .analysis import Analysis, SCHEMA_VERSION
from .common import (
    ComparisonMode,
    Confidence,
    DifferenceType,
    Document,
    DomainValidationError,
    InterpretationStatus,
    LogicalRelation,
    NumericOperator,
    TemporalRelationType,
    LocalizedText,
    Severity,
    Span,
)
from .comparison import Comparison, Difference
from .logic import Ambiguity, Inference, LogicalExpression
from .semantics import Condition, Entity, NumericConstraint, Operator, Proposition, SemanticItem, TemporalRelation
from .structure import DiscourseRelation, DiscourseRelationType, StructuralNode, Structure

__all__ = [
    "Ambiguity", "Analysis", "Comparison", "ComparisonMode", "Condition", "Confidence",
    "Difference", "DifferenceType", "DiscourseRelation", "DiscourseRelationType",
    "Document", "DomainValidationError", "Entity", "Inference",
    "InterpretationStatus", "LocalizedText", "LogicalExpression", "LogicalRelation", "NumericConstraint", "NumericOperator", "Operator",
    "Proposition", "SCHEMA_VERSION", "SemanticItem", "Severity", "Span", "TemporalRelation", "TemporalRelationType",
    "StructuralNode", "Structure",
]
