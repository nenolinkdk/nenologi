"""Public API for Nenologi Core v0.1 domain representation."""

from .analysis import Analyzer, ControlledEnglishAnalyzer, UnsupportedConstructionError
from .comparison import (
    AlignmentResult, AlignmentStatus, CANONICAL_DIFFERENCE_ORDER, Comparator,
    DeterministicComparator, DeterministicPropositionAligner, PropositionAlignment,
    UnsupportedComparisonError, proposition_signature,
)
from .inference import (
    EXACT_EXPLICIT_RULE, LEXICAL_OPPOSITION_PAIRS, LEXICAL_OPPOSITION_RULE,
    NOT_ESTABLISHED_RULE, UNIVERSAL_INSTANTIATION_RULE,
    DeterministicInferenceEngine, InferenceEngine,
    are_lexical_opposites,
)
from .interpretation import (
    DEFAULT_POLICIES, DEFEASIBLE_RECURRENCE_PREDICTION_POLICY,
    INTERPRETATION_SCHEMA_VERSION, DefeasibleRecurrencePredictionPolicy,
    EvidenceObjectKind, EvidenceReference, EvidenceSide, InterpretationPolicy,
    InterpretationProvenance, InterpretationResult, Phase3InterpretationEngine,
    interpretation_result_from_dict, interpretation_result_from_json,
    interpretation_result_to_dict, interpretation_result_to_json,
    validate_interpretation_evidence,
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
    "DEFAULT_POLICIES", "DEFEASIBLE_RECURRENCE_PREDICTION_POLICY",
    "DefeasibleRecurrencePredictionPolicy", "EvidenceObjectKind", "EvidenceReference", "EvidenceSide",
    "DeterministicComparator", "DeterministicInferenceEngine", "DeterministicPropositionAligner",
    "Difference", "DifferenceType", "DiscourseRelation", "DiscourseRelationType",
    "Document", "DomainValidationError", "Entity", "EXACT_EXPLICIT_RULE", "Inference", "InferenceEngine",
    "LEXICAL_OPPOSITION_PAIRS", "LEXICAL_OPPOSITION_RULE",
    "INTERPRETATION_SCHEMA_VERSION", "InterpretationPolicy", "InterpretationProvenance",
    "InterpretationResult", "InterpretationStatus", "LocalizedText", "LogicalExpression", "LogicalRelation", "NumericConstraint", "NumericOperator", "Operator",
    "Proposition", "PropositionAlignment", "ReferenceValidationError", "SchemaValidationError",
    "NOT_ESTABLISHED_RULE", "SemanticItem", "Severity", "Span", "StructuralNode", "Structure", "TemporalRelation", "TemporalRelationType",
    "UNIVERSAL_INSTANTIATION_RULE",
    "UnsupportedComparisonError", "UnsupportedConstructionError",
    "analysis_from_dict", "analysis_from_json", "analysis_to_dict",
    "analysis_to_json", "comparison_from_dict", "comparison_from_json",
    "comparison_to_dict", "comparison_to_json", "interpretation_result_from_dict",
    "interpretation_result_from_json", "interpretation_result_to_dict",
    "interpretation_result_to_json", "validate_analysis", "validate_comparison",
    "validate_interpretation_evidence", "Phase3InterpretationEngine",
    "proposition_signature", "are_lexical_opposites",
]
