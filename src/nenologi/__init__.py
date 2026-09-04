"""Public API for Nenologi Core v0.1 domain representation."""

from .models import (
    Ambiguity, Analysis, Comparison, ComparisonMode, Confidence, Difference,
    DifferenceType, DiscourseRelation, DiscourseRelationType, Document,
    DomainValidationError, Entity, Inference, InterpretationStatus,
    LocalizedText, LogicalExpression, Operator, Proposition, SemanticItem,
    Severity, Span, StructuralNode, Structure,
)
from .serialization import (
    ReferenceValidationError, SchemaValidationError, analysis_from_dict,
    analysis_from_json, analysis_to_dict, analysis_to_json,
    comparison_from_dict, comparison_from_json, comparison_to_dict,
    comparison_to_json, validate_analysis, validate_comparison,
)

__all__ = [
    "Ambiguity", "Analysis", "Comparison", "ComparisonMode", "Confidence",
    "Difference", "DifferenceType", "DiscourseRelation", "DiscourseRelationType",
    "Document", "DomainValidationError", "Entity", "Inference",
    "InterpretationStatus", "LocalizedText", "LogicalExpression", "Operator",
    "Proposition", "ReferenceValidationError", "SchemaValidationError",
    "SemanticItem", "Severity", "Span", "StructuralNode", "Structure",
    "analysis_from_dict", "analysis_from_json", "analysis_to_dict",
    "analysis_to_json", "comparison_from_dict", "comparison_from_json",
    "comparison_to_dict", "comparison_to_json", "validate_analysis",
    "validate_comparison",
]
