"""Deterministic comparison of structurally compatible normalized analyses."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from ..models import (
    Analysis, Comparison, ComparisonMode, Condition, Confidence, Difference,
    DifferenceType, InterpretationStatus, LogicalRelation, NumericConstraint, NumericOperator, Operator, Proposition, Severity, TemporalRelation,
)
from ..serialization.validation import validate_analysis, validate_comparison
from .interface import UnsupportedComparisonError
from .rules import CANONICAL_DIFFERENCE_ORDER, CONJUNCTION_RULES, MODALITY_RULES, NEGATION_RULES, QUANTIFIER_RULES, TransitionRule

_CONFIDENCE = Confidence(1.0, "Exact deterministic comparison of normalized values")


def _single_proposition(analysis: Analysis, side: str) -> Proposition:
    if len(analysis.propositions) != 1:
        raise UnsupportedComparisonError(f"{side} analysis must contain exactly one proposition")
    proposition = analysis.propositions[0]
    if proposition.interpretation_status is not InterpretationStatus.EXPLICIT:
        raise UnsupportedComparisonError(f"{side} proposition must have EXPLICIT interpretation status")
    return proposition


def _proposition_entities(analysis: Analysis, proposition: Proposition, side: str):
    entities = {entity.id: entity for entity in analysis.entities}
    aligned = []
    for reference in proposition.arguments:
        try:
            entity = entities[reference]
        except KeyError as exc:
            raise UnsupportedComparisonError(f"{side} proposition argument is not an entity: {reference}") from exc
        aligned.append(entity)
    return tuple(aligned)


def _corresponding_propositions(source: Analysis, target: Analysis, source_prop=None, target_prop=None):
    source_prop = source_prop or _single_proposition(source, "source")
    target_prop = target_prop or _single_proposition(target, "target")
    source_entities = _proposition_entities(source, source_prop, "source")
    target_entities = _proposition_entities(target, target_prop, "target")
    if len(source_entities) != len(target_entities):
        raise UnsupportedComparisonError("proposition argument counts are not structurally aligned")
    if tuple(entity.type for entity in source_entities) != tuple(entity.type for entity in target_entities):
        raise UnsupportedComparisonError("proposition entity roles are not structurally aligned")
    changes = [index for index, (left, right) in enumerate(zip(source_entities, target_entities)) if left.label.casefold() != right.label.casefold()]
    predicate_changed = source_prop.predicate != target_prop.predicate
    if len(changes) > 1 or (changes and predicate_changed):
        raise UnsupportedComparisonError("multiple entity/predicate alignment changes are unsupported")
    return source_prop, target_prop, source_entities, target_entities, changes, predicate_changed


def _reject_unsupported_dimensions(source: Analysis, target: Analysis, source_prop: Proposition, target_prop: Proposition) -> None:
    for name in ("sets", "inferences", "ambiguities"):
        if getattr(source, name) or getattr(target, name):
            raise UnsupportedComparisonError(f"{name} comparison is not supported")
    source_relations = [item for item in source.relations if item.type not in {"AND", "OR"} and source_prop.id in item.derived_from]
    target_relations = [item for item in target.relations if item.type not in {"AND", "OR"} and target_prop.id in item.derived_from]
    if len(source_relations) != len(target_relations):
        raise UnsupportedComparisonError("relation structures are not deterministically aligned")
    if tuple(item.type for item in source_relations) != tuple(item.type for item in target_relations):
        raise UnsupportedComparisonError("relation types are not deterministically aligned")


def _conjunction_value(analysis: Analysis, proposition: Proposition) -> tuple[str | None, str | None]:
    conjunctions = [item for item in analysis.relations if item.type in {"AND", "OR"}]
    if len(conjunctions) > 1:
        raise UnsupportedComparisonError("multiple conjunctions are unsupported")
    if not conjunctions:
        return None, None
    conjunction = conjunctions[0]
    if conjunction.arguments != proposition.arguments[1:] or len(conjunction.arguments) != 2:
        raise UnsupportedComparisonError("conjunction is not a simple pair of proposition objects")
    return conjunction.type, conjunction.id


def _scope_reaches(analysis: Analysis, reference: str, proposition_id: str, seen: frozenset[str] = frozenset()) -> bool:
    if reference == proposition_id:
        return True
    if reference in seen:
        raise UnsupportedComparisonError("cyclic operator scope is unsupported")
    operator_map = {item.id: item for item in (*analysis.quantifiers, *analysis.modality, *analysis.negation)}
    operator = operator_map.get(reference)
    return operator is not None and any(
        _scope_reaches(analysis, target, proposition_id, seen | {reference}) for target in operator.scope
    )


def _scoped_value(analysis: Analysis, operators: Sequence[Operator], proposition_id: str, dimension: str) -> tuple[str | None, str | None]:
    operators = tuple(operator for operator in operators if any(_scope_reaches(analysis, reference, proposition_id) for reference in operator.scope))
    if len(operators) > 1:
        raise UnsupportedComparisonError(f"multiple {dimension} operators are unsupported")
    if not operators:
        return None, None
    operator = operators[0]
    if len(operator.scope) != 1:
        raise UnsupportedComparisonError(f"{dimension} must have one controlled scope target")
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
    value, identifier = _scoped_value(analysis, explicit, proposition_id, "negation")
    return value == "NOT", identifier


def _scope_signature(analysis: Analysis, proposition_id: str) -> tuple[tuple[str, str], ...]:
    operators = (*analysis.quantifiers, *analysis.modality, *analysis.negation)
    relevant = {item.id: item for item in operators if any(_scope_reaches(analysis, ref, proposition_id) for ref in item.scope)}
    categories = {
        **{item.id: "QUANTIFIER" for item in analysis.quantifiers},
        **{item.id: "MODALITY" for item in analysis.modality},
        **{item.id: "NEGATION" for item in analysis.negation},
    }
    edges = []
    for item in relevant.values():
        target = item.scope[0]
        edges.append((categories[item.id], categories.get(target, "PROPOSITION" if target == proposition_id else target)))
    return tuple(sorted(edges))


def _scope_order(analysis: Analysis, proposition_id: str) -> list[str]:
    operators = (*analysis.quantifiers, *analysis.modality, *analysis.negation)
    relevant = {item.id: item for item in operators if any(_scope_reaches(analysis, ref, proposition_id) for ref in item.scope)}
    targeted = {target for item in relevant.values() for target in item.scope if target in relevant}
    roots = sorted((item for item in relevant.values() if item.id not in targeted), key=lambda item: item.operator)
    if len(roots) != 1:
        return [f"{left}>{right}" for left, right in _scope_signature(analysis, proposition_id)]
    order = []
    current = roots[0]
    seen = set()
    while current.id not in seen:
        seen.add(current.id)
        order.append(current.operator)
        target = current.scope[0]
        if target == proposition_id:
            order.append("PROPOSITION")
            break
        if target not in relevant:
            break
        current = relevant[target]
    return order


def _numeric_constraint(analysis: Analysis, proposition_id: str, side: str) -> NumericConstraint | None:
    constraints = tuple(item for item in analysis.numeric_constraints if proposition_id in item.scope)
    if len(constraints) > 1:
        raise UnsupportedComparisonError(f"multiple {side} numeric constraints are unsupported")
    if not constraints:
        return None
    constraint = constraints[0]
    if constraint.scope != (proposition_id,):
        raise UnsupportedComparisonError(f"{side} numeric constraint scope is not the aligned proposition")
    if constraint.interpretation_status is not InterpretationStatus.EXPLICIT:
        raise UnsupportedComparisonError(f"{side} numeric constraint must have EXPLICIT interpretation status")
    return constraint


def _numeric_display(constraint: NumericConstraint, *, include_unit: bool = False) -> str:
    symbols = {
        NumericOperator.GREATER_THAN: ">", NumericOperator.GREATER_THAN_OR_EQUAL: ">=",
        NumericOperator.LESS_THAN: "<", NumericOperator.LESS_THAN_OR_EQUAL: "<=", NumericOperator.EQUAL: "=",
    }
    unit = f" {constraint.unit}" if include_unit and constraint.unit else ""
    return f"{symbols[constraint.operator]} {constraint.value}{unit}"


def _condition_parts(analysis: Analysis, side: str) -> tuple[Condition | None, Proposition | None, Proposition]:
    if len(analysis.conditions) > 1:
        raise UnsupportedComparisonError(f"multiple {side} conditions are unsupported")
    propositions = {item.id: item for item in analysis.propositions}
    if not analysis.conditions:
        return None, None, _single_proposition(analysis, side)
    condition = analysis.conditions[0]
    if condition.interpretation_status is not InterpretationStatus.EXPLICIT:
        raise UnsupportedComparisonError(f"{side} condition must have EXPLICIT interpretation status")
    if len(condition.antecedent) != 1 or len(condition.consequent) != 1:
        raise UnsupportedComparisonError("a condition must reference one antecedent and one consequent proposition")
    try:
        antecedent = propositions[condition.antecedent[0]]
        consequent = propositions[condition.consequent[0]]
    except KeyError as exc:
        raise UnsupportedComparisonError(f"{side} condition references an unknown proposition") from exc
    return condition, antecedent, consequent


def _append_numeric_change(findings: list[Difference], source: Analysis, target: Analysis,
                           source_prop: Proposition, target_prop: Proposition) -> bool:
    source_numeric = _numeric_constraint(source, source_prop.id, "source")
    target_numeric = _numeric_constraint(target, target_prop.id, "target")
    if (source_numeric is None) != (target_numeric is None):
        raise UnsupportedComparisonError("adding or removing a numeric constraint is unsupported")
    if source_numeric is None or target_numeric is None:
        return False
    if (source_numeric.operator, source_numeric.value, source_numeric.unit) == (target_numeric.operator, target_numeric.value, target_numeric.unit):
        return False
    changed = []
    if source_numeric.operator != target_numeric.operator:
        changed.append("operator")
    if source_numeric.value != target_numeric.value:
        changed.append("value")
    if source_numeric.unit != target_numeric.unit:
        changed.append("unit")
    severity = Severity.HIGH if NumericOperator.EQUAL in {source_numeric.operator, target_numeric.operator} else Severity.MEDIUM
    _transition(
        findings, DifferenceType.NUMERIC_THRESHOLD_CHANGE,
        _numeric_display(source_numeric, include_unit=source_numeric.unit != target_numeric.unit),
        _numeric_display(target_numeric, include_unit=source_numeric.unit != target_numeric.unit),
        TransitionRule(
            severity,
            "The numeric threshold changes from "
            f"{_numeric_display(source_numeric, include_unit=True)} to "
            f"{_numeric_display(target_numeric, include_unit=True)} ({', '.join(changed)}); "
            "no domain consequence is inferred.",
        ),
        (f"source.{source_numeric.id}", f"target.{target_numeric.id}"),
    )
    return True


def _condition_value(analysis: Analysis, antecedent: Proposition) -> str:
    numeric = _numeric_constraint(analysis, antecedent.id, "condition")
    return f"IF_{_numeric_display(numeric).replace(' ', '_')}" if numeric else f"IF_{antecedent.predicate}"


def _temporal_relation(analysis: Analysis, proposition_id: str, side: str) -> TemporalRelation | None:
    relations = tuple(item for item in analysis.temporal_relations if item.proposition == proposition_id)
    if len(relations) > 1:
        raise UnsupportedComparisonError(f"multiple {side} temporal relations are unsupported")
    if not relations:
        return None
    relation = relations[0]
    if relation.interpretation_status is not InterpretationStatus.EXPLICIT:
        raise UnsupportedComparisonError(f"{side} temporal relation must have EXPLICIT interpretation status")
    return relation


def _temporal_value(relation: TemporalRelation, *, include_reference: bool) -> str:
    return f"{relation.relation.value} {relation.temporal_reference}" if include_reference else relation.relation.value


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


def _canonical_findings(findings: list[Difference]) -> tuple[Difference, ...]:
    positions = {difference_type: index for index, difference_type in enumerate(CANONICAL_DIFFERENCE_ORDER)}
    ordered = sorted(enumerate(findings), key=lambda item: (positions[item[1].difference_type], item[0]))
    return tuple(replace(finding, id=f"difference_{index:03d}") for index, (_, finding) in enumerate(ordered, 1))


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
        source_condition, source_antecedent, source_prop = _condition_parts(source, "source")
        target_condition, target_antecedent, target_prop = _condition_parts(target, "target")
        _reject_unsupported_dimensions(source, target, source_prop, target_prop)
        (source_prop, target_prop, source_entities, target_entities,
         entity_changes, predicate_changed) = _corresponding_propositions(source, target, source_prop, target_prop)
        findings: list[Difference] = []

        # Stable order continues through negation, conjunction, numeric, and entity/relation.
        source_quantifier, source_quantifier_id = _scoped_value(source, source.quantifiers, source_prop.id, "quantifier")
        target_quantifier, target_quantifier_id = _scoped_value(target, target.quantifiers, target_prop.id, "quantifier")
        if source_quantifier != target_quantifier:
            rule = QUANTIFIER_RULES.get((source_quantifier, target_quantifier))
            if rule is None:
                raise UnsupportedComparisonError(f"unsupported quantifier transition: {source_quantifier} -> {target_quantifier}")
            _transition(findings, DifferenceType.QUANTIFIER_CHANGE, source_quantifier, target_quantifier, rule,
                        tuple(reference for reference in (f"source.{source_quantifier_id}" if source_quantifier_id else None, f"target.{target_quantifier_id}" if target_quantifier_id else None) if reference))

        source_modality, source_modality_id = _scoped_value(source, source.modality, source_prop.id, "modality")
        target_modality, target_modality_id = _scoped_value(target, target.modality, target_prop.id, "modality")
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

        source_conjunction, source_conjunction_id = _conjunction_value(source, source_prop)
        target_conjunction, target_conjunction_id = _conjunction_value(target, target_prop)
        if source_conjunction != target_conjunction:
            rule = CONJUNCTION_RULES.get((source_conjunction, target_conjunction))
            if rule is None:
                raise UnsupportedComparisonError(f"unsupported conjunction transition: {source_conjunction} -> {target_conjunction}")
            _transition(
                findings, DifferenceType.CONJUNCTION_CHANGE,
                source_conjunction, target_conjunction, rule,
                (f"source.{source_conjunction_id}", f"target.{target_conjunction_id}"),
            )

        _append_numeric_change(findings, source, target, source_prop, target_prop)

        condition_changed = False
        if source_condition is None and target_condition is not None:
            condition_changed = True
            condition_source_value, condition_target_value = "NONE", _condition_value(target, target_antecedent)
            condition_refs = (f"source.{source_prop.id}", f"target.{target_condition.id}")
            condition_explanation = "The target makes the aligned consequent conditional by adding an IF antecedent."
        elif source_condition is not None and target_condition is None:
            condition_changed = True
            condition_source_value, condition_target_value = _condition_value(source, source_antecedent), "NONE"
            condition_refs = (f"source.{source_condition.id}", f"target.{target_prop.id}")
            condition_explanation = "The target removes the IF antecedent that governed the aligned consequent."
        elif source_condition is not None and target_condition is not None:
            (_, _, source_antecedent_entities, target_antecedent_entities, _, _) = _corresponding_propositions(
                source, target, source_antecedent, target_antecedent,
            )
            _append_numeric_change(findings, source, target, source_antecedent, target_antecedent)
            source_antecedent_signature = (
                source_antecedent.predicate,
                tuple(entity.label.casefold() for entity in source_antecedent_entities),
            )
            target_antecedent_signature = (
                target_antecedent.predicate,
                tuple(entity.label.casefold() for entity in target_antecedent_entities),
            )
            if source_antecedent_signature != target_antecedent_signature:
                condition_changed = True
                condition_source_value, condition_target_value = _condition_value(source, source_antecedent), _condition_value(target, target_antecedent)
                condition_refs = (f"source.{source_condition.id}", f"target.{target_condition.id}")
                condition_explanation = "The target changes the normalized antecedent governing the aligned consequent."
        if condition_changed:
            _transition(
                findings, DifferenceType.CONDITION_CHANGE,
                condition_source_value, condition_target_value,
                TransitionRule(Severity.HIGH, condition_explanation), condition_refs,
            )

        source_temporal = _temporal_relation(source, source_prop.id, "source")
        target_temporal = _temporal_relation(target, target_prop.id, "target")
        source_temporal_signature = None if source_temporal is None else (source_temporal.relation, source_temporal.temporal_reference)
        target_temporal_signature = None if target_temporal is None else (target_temporal.relation, target_temporal.temporal_reference)
        if source_temporal_signature != target_temporal_signature:
            reference_changed = (
                source_temporal is not None and target_temporal is not None
                and source_temporal.temporal_reference != target_temporal.temporal_reference
            )
            source_value = "NONE" if source_temporal is None else _temporal_value(source_temporal, include_reference=reference_changed or target_temporal is None)
            target_value = "NONE" if target_temporal is None else _temporal_value(target_temporal, include_reference=reference_changed or source_temporal is None)
            reversed_order = (
                source_temporal is not None and target_temporal is not None
                and {source_temporal.relation.value, target_temporal.relation.value} == {"BEFORE", "AFTER"}
            )
            changed = []
            if source_temporal is None or target_temporal is None or source_temporal.relation != target_temporal.relation:
                changed.append("relation")
            if reference_changed:
                changed.append("reference")
            _transition(
                findings, DifferenceType.TEMPORAL_CHANGE, source_value, target_value,
                TransitionRule(
                    Severity.HIGH if reversed_order else Severity.MEDIUM,
                    f"The temporal constraint changes from {source_value} to {target_value} "
                    f"({' and '.join(changed)}); no temporal consequence is inferred.",
                ),
                tuple(reference for reference in (
                    f"source.{source_temporal.id}" if source_temporal else f"source.{source_prop.id}",
                    f"target.{target_temporal.id}" if target_temporal else f"target.{target_prop.id}",
                ) if reference),
            )

        source_scope = _scope_signature(source, source_prop.id)
        target_scope = _scope_signature(target, target_prop.id)
        same_operator_dimensions = (
            len(source.quantifiers), len(source.modality), len(source.negation)
        ) == (
            len(target.quantifiers), len(target.modality), len(target.negation)
        )
        if same_operator_dimensions and source_scope != target_scope:
            source_order = _scope_order(source, source_prop.id)
            target_order = _scope_order(target, target_prop.id)
            source_operator_ids = [item.id for item in (*source.quantifiers, *source.modality, *source.negation)]
            target_operator_ids = [item.id for item in (*target.quantifiers, *target.modality, *target.negation)]
            _transition(
                findings, DifferenceType.SCOPE_CHANGE,
                {"order": source_order, "relations": [list(edge) for edge in source_scope]},
                {"order": target_order, "relations": [list(edge) for edge in target_scope]},
                TransitionRule(
                    Severity.HIGH,
                    "The scope of the aligned semantic operators changes. In the source, "
                    f"{' applies over '.join(source_order)}; in the target, "
                    f"{' applies over '.join(target_order)}. No logical consequence is inferred.",
                ),
                tuple(
                    [*(f"source.{identifier}" for identifier in source_operator_ids),
                     *(f"target.{identifier}" for identifier in target_operator_ids)]
                ),
            )
        if entity_changes:
            index = entity_changes[0]
            source_entity = source_entities[index]
            target_entity = target_entities[index]
            role = "SUBJECT" if index == 0 else "OBJECT"
            explanation = (
                f"The target changes the affected entity from {source_entity.label} to {target_entity.label}."
                if index == 0 else
                f"The target changes the object from {source_entity.label} to {target_entity.label}."
            )
            _transition(
                findings, DifferenceType.ENTITY_RELATION_CHANGE,
                f"{role}:{source_entity.label.upper()}", f"{role}:{target_entity.label.upper()}",
                TransitionRule(Severity.HIGH, explanation),
                (f"source.{source_entity.id}", f"target.{target_entity.id}"),
            )
        elif predicate_changed:
            _transition(
                findings, DifferenceType.ENTITY_RELATION_CHANGE,
                f"PREDICATE:{source_prop.predicate}", f"PREDICATE:{target_prop.predicate}",
                TransitionRule(Severity.HIGH, f"The target changes the action from {source_prop.predicate} to {target_prop.predicate}."),
                (f"source.{source_prop.id}", f"target.{target_prop.id}"),
            )

        canonical_findings = _canonical_findings(findings)
        if not canonical_findings:
            logical_relation = LogicalRelation.EQUIVALENT
        elif len(canonical_findings) == 1 and canonical_findings[0].difference_type is DifferenceType.NEGATION_CHANGE:
            logical_relation = LogicalRelation.CONTRADICTORY
        else:
            logical_relation = LogicalRelation.UNDETERMINED
        comparison = Comparison(
            mode=mode,
            source_analysis=source,
            target_analysis=target,
            differences=canonical_findings,
            logical_relation=logical_relation,
        )
        validate_comparison(comparison)
        return comparison
