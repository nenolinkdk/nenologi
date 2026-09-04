"""Explicit deterministic comparison rules; prose carries no hidden semantics."""

from dataclasses import dataclass

from ..models import DifferenceType, Severity


@dataclass(frozen=True, slots=True)
class TransitionRule:
    severity: Severity
    explanation: str


# Public taxonomy order. Implemented findings use these positions; the final
# three reserve deterministic locations for future existing taxonomy support.
CANONICAL_DIFFERENCE_ORDER = (
    DifferenceType.QUANTIFIER_CHANGE,
    DifferenceType.MODALITY_CHANGE,
    DifferenceType.NEGATION_CHANGE,
    DifferenceType.CONJUNCTION_CHANGE,
    DifferenceType.NUMERIC_THRESHOLD_CHANGE,
    DifferenceType.CONDITION_CHANGE,
    DifferenceType.TEMPORAL_CHANGE,
    DifferenceType.SCOPE_CHANGE,
    DifferenceType.ENTITY_RELATION_CHANGE,
    DifferenceType.ADDITION,
    DifferenceType.OMISSION,
)


MODALITY_RULES: dict[tuple[str, str], TransitionRule] = {
    ("MUST", "MAY"): TransitionRule(Severity.HIGH, "The target weakens the requirement from obligation to permission or possibility."),
    ("MUST", "SHOULD"): TransitionRule(Severity.HIGH, "The target changes an obligation into a recommendation."),
    ("MAY", "MUST"): TransitionRule(Severity.HIGH, "The target strengthens permission or possibility into an obligation."),
}

QUANTIFIER_RULES: dict[tuple[str, str], TransitionRule] = {
    ("ALL", "SOME"): TransitionRule(Severity.HIGH, "The target changes the quantified scope from all members to at least some members."),
    ("SOME", "ALL"): TransitionRule(Severity.HIGH, "The target changes the quantified scope from at least some members to all members."),
    ("NONE", "SOME"): TransitionRule(Severity.HIGH, "The target changes the quantified claim from no members to at least some members."),
}

NEGATION_RULES: dict[tuple[bool, bool], TransitionRule] = {
    (False, True): TransitionRule(Severity.HIGH, "The target changes the polarity by adding negation."),
    (True, False): TransitionRule(Severity.HIGH, "The target changes the polarity by removing negation."),
}

CONJUNCTION_RULES: dict[tuple[str, str], TransitionRule] = {
    ("AND", "OR"): TransitionRule(Severity.HIGH, "The target changes a requirement involving both alternatives into a choice between alternatives."),
    ("OR", "AND"): TransitionRule(Severity.HIGH, "The target changes a choice between alternatives into a requirement involving both alternatives."),
}
