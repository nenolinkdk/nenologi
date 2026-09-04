"""Public API for Nenologi Core v0.1 domain representation."""

from .analysis import Analyzer, ControlledEnglishAnalyzer, UnsupportedConstructionError
from .comparison import Comparator, DeterministicComparator, UnsupportedComparisonError
from .models import (
    Ambiguity, Analysis, Comparison, ComparisonMode, Condition, Confidence, Difference,
    DifferenceType, DiscourseRelation, DiscourseRelationType, Document,
    DomainValidationError, Entity, Inference, InterpretationStatus,
    LocalizedText, LogicalExpression, LogicalRelation, NumericConstraint, NumericOperator, Operator, Proposition, SemanticItem,
    Severity, Span, StructuralNode, Structure,
)
from .serialization import (
    ReferenceValidationError, SchemaValidationError, analysis_from_dict,
    analysis_from_json, analysis_to_dict, analysis_to_json,
    comparison_from_dict, comparison_from_json, comparison_to_dict,
    comparison_to_json, validate_analysis, validate_comparison,
)

__all__ = [
    "Ambiguity", "Analysis", "Analyzer", "Comparator", "Comparison", "Condition",
    "ComparisonMode", "Confidence", "ControlledEnglishAnalyzer",
    "DeterministicComparator",
    "Difference", "DifferenceType", "DiscourseRelation", "DiscourseRelationType",
    "Document", "DomainValidationError", "Entity", "Inference",
    "InterpretationStatus", "LocalizedText", "LogicalExpression", "LogicalRelation", "NumericConstraint", "NumericOperator", "Operator",
    "Proposition", "ReferenceValidationError", "SchemaValidationError",
    "SemanticItem", "Severity", "Span", "StructuralNode", "Structure",
    "UnsupportedComparisonError", "UnsupportedConstructionError",
    "analysis_from_dict", "analysis_from_json", "analysis_to_dict",
    "analysis_to_json", "comparison_from_dict", "comparison_from_json",
    "comparison_to_dict", "comparison_to_json", "validate_analysis",
    "validate_comparison",
]
