"""Public API for Nenologi Core v0.1 domain representation."""

from .analysis import Analyzer, ControlledEnglishAnalyzer, UnsupportedConstructionError
from .comparison import (
    AlignmentResult, AlignmentStatus, CANONICAL_DIFFERENCE_ORDER, Comparator,
    DeterministicComparator, DeterministicPropositionAligner, PropositionAlignment,
    UnsupportedComparisonError, proposition_signature,
)
from .models import (
    Ambiguity, Analysis, Comparison, ComparisonMode, Condition, Confidence, Difference,
    DifferenceType, DiscourseRelation, DiscourseRelationType, Document,
    DomainValidationError, Entity, Inference, InterpretationStatus,
    LocalizedText, LogicalExpression, LogicalRelation, NumericConstraint, NumericOperator, Operator, Proposition, SemanticItem,
    Severity, Span, StructuralNode, Structure, TemporalRelation, TemporalRelationType,
)
from .serialization import (
    ReferenceValidationError, SchemaValidationError, analysis_from_dict,
    analysis_from_json, analysis_to_dict, analysis_to_json,
    comparison_from_dict, comparison_from_json, comparison_to_dict,
    comparison_to_json, validate_analysis, validate_comparison,
)

__all__ = [
    "AlignmentResult", "AlignmentStatus", "Ambiguity", "Analysis", "Analyzer", "CANONICAL_DIFFERENCE_ORDER", "Comparator", "Comparison", "Condition",
    "ComparisonMode", "Confidence", "ControlledEnglishAnalyzer",
    "DeterministicComparator", "DeterministicPropositionAligner",
    "Difference", "DifferenceType", "DiscourseRelation", "DiscourseRelationType",
    "Document", "DomainValidationError", "Entity", "Inference",
    "InterpretationStatus", "LocalizedText", "LogicalExpression", "LogicalRelation", "NumericConstraint", "NumericOperator", "Operator",
    "Proposition", "PropositionAlignment", "ReferenceValidationError", "SchemaValidationError",
    "SemanticItem", "Severity", "Span", "StructuralNode", "Structure", "TemporalRelation", "TemporalRelationType",
    "UnsupportedComparisonError", "UnsupportedConstructionError",
    "analysis_from_dict", "analysis_from_json", "analysis_to_dict",
    "analysis_to_json", "comparison_from_dict", "comparison_from_json",
    "comparison_to_dict", "comparison_to_json", "validate_analysis",
    "validate_comparison", "proposition_signature",
]
