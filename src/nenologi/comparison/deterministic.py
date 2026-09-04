"""Deterministic comparison of structurally compatible normalized analyses."""

from __future__ import annotations

from collections.abc import Sequence

from ..models import (
    Analysis, Comparison, ComparisonMode, Confidence, Difference,
    DifferenceType, InterpretationStatus, Operator, Proposition,
)
from ..serialization.validation import validate_analysis, validate_comparison
from .interface import UnsupportedComparisonError
from .rules import MODALITY_RULES, NEGATION_RULES, QUANTIFIER_RULES, TransitionRule

_CONFIDENCE = Confidence(1.0, "Exact deterministic comparison of normalized values")


def _single_proposition(analysis: Analysis, side: str) -> Proposition:
    if len(analysis.propositions) != 1:
        raise UnsupportedComparisonError(f"{side} analysis must contain exactly one proposition")
    proposition = analysis.propositions[0]
    if proposition.interpretation_status is not InterpretationStatus.EXPLICIT:
        raise UnsupportedComparisonError(f"{side} proposition must have EXPLICIT interpretation status")
    return proposition


def _entity_signature(analysis: Analysis, proposition: Proposition, side: str) -> tuple[tuple[str, str], ...]:
    entities = {entity.id: entity for entity in analysis.entities}
    signature = []
    for reference in proposition.arguments:
        try:
            entity = entities[reference]
        except KeyError as exc:
            raise UnsupportedComparisonError(f"{side} proposition argument is not an entity: {reference}") from exc
        signature.append((entity.type, entity.label.casefold()))
    return tuple(signature)


def _aligned_propositions(source: Analysis, target: Analysis) -> tuple[Proposition, Proposition]:
    source_prop = _single_proposition(source, "source")
    target_prop = _single_proposition(target, "target")
    if source_prop.predicate != target_prop.predicate:
        raise UnsupportedComparisonError("proposition predicates are not deterministically aligned")
    if _entity_signature(source, source_prop, "source") != _entity_signature(target, target_prop, "target"):
        raise UnsupportedComparisonError("proposition entity roles are not deterministically aligned")
    return source_prop, target_prop


def _reject_unsupported_dimensions(source: Analysis, target: Analysis) -> None:
    for name in ("conditions", "temporal_relations", "sets", "inferences", "ambiguities"):
        if getattr(source, name) or getattr(target, name):
            raise UnsupportedComparisonError(f"{name} comparison is not supported")
    if len(source.relations) != len(target.relations):
        raise UnsupportedComparisonError("relation structures are not deterministically aligned")
    if tuple(item.type for item in source.relations) != tuple(item.type for item in target.relations):
        raise UnsupportedComparisonError("relation types are not deterministically aligned")


def _scoped_value(operators: Sequence[Operator], proposition_id: str, dimension: str) -> tuple[str | None, str | None]:
    if len(operators) > 1:
        raise UnsupportedComparisonError(f"multiple {dimension} operators are unsupported")
    if not operators:
        return None, None
    operator = operators[0]
    if operator.scope != (proposition_id,):
        raise UnsupportedComparisonError(f"{dimension} scope is not the aligned proposition")
    if operator.interpretation_status is not InterpretationStatus.EXPLICIT:
        raise UnsupportedComparisonError(f"{dimension} must have EXPLICIT interpretation status")
    return operator.operator, operator.id


def _explicit_negation(analysis: Analysis, proposition_id: str) -> tuple[bool, str | None]:
    explicit = [operator for operator in analysis.negation if operator.operator == "NOT"]
    other = [operator for operator in analysis.negation if operator.operator not in {"NOT", "NOT_EXISTS"}]
    if other or len(explicit) > 1:
        raise UnsupportedComparisonError("unsupported negation representation")
    if not explicit:
        return False, None
    value, identifier = _scoped_value(explicit, proposition_id, "negation")
    return value == "NOT", identifier


def _transition(
    findings: list[Difference],
    difference_type: DifferenceType,
    source_value: str,
    target_value: str,
    rule: TransitionRule,
    references: tuple[str, ...],
) -> None:
    findings.append(Difference(
        id=f"difference_{len(findings) + 1:03d}",
        difference_type=difference_type,
        source_value=source_value,
        target_value=target_value,
        severity=rule.severity,
        confidence=_CONFIDENCE,
        explanation=rule.explanation,
        references=references,
    ))


class DeterministicComparator:
    """Compare one aligned proposition across supported normalized dimensions."""

    def compare(
        self,
        source: Analysis,
        target: Analysis,
        *,
        mode: ComparisonMode = ComparisonMode.VERSION_COMPARISON,
    ) -> Comparison:
        if not isinstance(source, Analysis) or not isinstance(target, Analysis):
            raise TypeError("source and target must be normalized Analysis objects")
        validate_analysis(source)
        validate_analysis(target)
        _reject_unsupported_dimensions(source, target)
        source_prop, target_prop = _aligned_propositions(source, target)
        findings: list[Difference] = []

        # Stable finding order: quantifier, modality, then explicit negation.
        source_quantifier, source_quantifier_id = _scoped_value(source.quantifiers, source_prop.id, "quantifier")
        target_quantifier, target_quantifier_id = _scoped_value(target.quantifiers, target_prop.id, "quantifier")
        if source_quantifier != target_quantifier:
            rule = QUANTIFIER_RULES.get((source_quantifier, target_quantifier))
            if rule is None:
                raise UnsupportedComparisonError(f"unsupported quantifier transition: {source_quantifier} -> {target_quantifier}")
            _transition(findings, DifferenceType.QUANTIFIER_CHANGE, source_quantifier, target_quantifier, rule,
                        tuple(reference for reference in (f"source.{source_quantifier_id}" if source_quantifier_id else None, f"target.{target_quantifier_id}" if target_quantifier_id else None) if reference))

        source_modality, source_modality_id = _scoped_value(source.modality, source_prop.id, "modality")
        target_modality, target_modality_id = _scoped_value(target.modality, target_prop.id, "modality")
        if source_modality != target_modality:
            rule = MODALITY_RULES.get((source_modality, target_modality))
            if rule is None:
                raise UnsupportedComparisonError(f"unsupported modality transition: {source_modality} -> {target_modality}")
            _transition(findings, DifferenceType.MODALITY_CHANGE, source_modality, target_modality, rule,
                        tuple(reference for reference in (f"source.{source_modality_id}" if source_modality_id else None, f"target.{target_modality_id}" if target_modality_id else None) if reference))

        source_negated, source_negation_id = _explicit_negation(source, source_prop.id)
        target_negated, target_negation_id = _explicit_negation(target, target_prop.id)
        if source_negated != target_negated:
            rule = NEGATION_RULES[(source_negated, target_negated)]
            _transition(
                findings, DifferenceType.NEGATION_CHANGE,
                "NEGATED" if source_negated else "AFFIRMED",
                "NEGATED" if target_negated else "AFFIRMED", rule,
                tuple(reference for reference in (
                    f"source.{source_negation_id}" if source_negation_id else f"source.{source_prop.id}",
                    f"target.{target_negation_id}" if target_negation_id else f"target.{target_prop.id}",
                ) if reference),
            )

        comparison = Comparison(mode, source, target, tuple(findings))
        validate_comparison(comparison)
        return comparison
