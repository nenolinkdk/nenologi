"""Schema-shape and cross-reference validation for Nenologi v0.1."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import Analysis, Comparison


class SchemaValidationError(ValueError):
    """Serialized input does not conform to the v0.1 schema contract."""


class ReferenceValidationError(ValueError):
    """An otherwise valid model contains duplicate or unresolved IDs."""


def _id_map(analysis: Analysis) -> dict[str, object]:
    result: dict[str, object] = {}
    for item in analysis.all_identified_objects():
        identifier = getattr(item, "id")
        if identifier in result:
            raise ReferenceValidationError(f"duplicate analysis ID: {identifier}")
        result[identifier] = item
    return result


def _require(reference: str, valid_ids: set[str], context: str) -> None:
    if reference not in valid_ids:
        raise ReferenceValidationError(f"{context} references unknown ID: {reference}")


def validate_analysis_references(analysis: Analysis) -> None:
    """Validate the deliberately limited cross-reference rules for v0.1."""
    id_map = _id_map(analysis)
    all_ids = set(id_map)
    structural_ids = {node.id for node in (*analysis.structure.sentences, *analysis.structure.clauses)}
    entity_ids = {entity.id for entity in analysis.entities}

    for node in (*analysis.structure.sentences, *analysis.structure.clauses):
        if node.parent_id is not None:
            _require(node.parent_id, structural_ids, f"structural node {node.id}")
    for relation in analysis.structure.discourse_relations:
        _require(relation.source_id, structural_ids, f"discourse relation {relation.id}")
        _require(relation.target_id, structural_ids, f"discourse relation {relation.id}")
    for proposition in analysis.propositions:
        for reference in proposition.arguments:
            _require(reference, entity_ids, f"proposition {proposition.id}")
        for reference in proposition.derived_from:
            _require(reference, all_ids, f"proposition {proposition.id}")
    for collection in (
        analysis.relations, analysis.conditions, analysis.temporal_relations, analysis.sets
    ):
        for item in collection:
            for reference in (*item.arguments, *item.derived_from):
                _require(reference, all_ids, f"semantic item {item.id}")
    for collection in (analysis.quantifiers, analysis.modality, analysis.negation, analysis.numeric_constraints):
        for operator in collection:
            for reference in operator.scope:
                _require(reference, all_ids, f"operator {operator.id}")
    for expression in analysis.logical_representation:
        for reference in expression.derived_from:
            _require(reference, all_ids, f"logical expression {expression.id}")
    for inference in analysis.inferences:
        for reference in inference.derived_from:
            _require(reference, all_ids, f"inference {inference.id}")
    for ambiguity in analysis.ambiguities:
        for reference in ambiguity.reading_ids:
            _require(reference, all_ids, f"ambiguity {ambiguity.id}")


def validate_analysis(value: Analysis | Mapping[str, Any]) -> Analysis:
    """Return a validated analysis or raise a typed validation exception."""
    if isinstance(value, Analysis):
        analysis = value
    elif isinstance(value, Mapping):
        from .json_io import analysis_from_dict
        analysis = analysis_from_dict(value)
    else:
        raise SchemaValidationError("analysis must be an Analysis or mapping")
    validate_analysis_references(analysis)
    return analysis


def validate_comparison(value: Comparison | Mapping[str, Any]) -> Comparison:
    """Return a validated comparison, including nested analyses and references."""
    if isinstance(value, Comparison):
        comparison = value
    elif isinstance(value, Mapping):
        from .json_io import comparison_from_dict
        comparison = comparison_from_dict(value)
    else:
        raise SchemaValidationError("comparison must be a Comparison or mapping")
    validate_analysis_references(comparison.source_analysis)
    validate_analysis_references(comparison.target_analysis)
    source_ids = set(_id_map(comparison.source_analysis))
    target_ids = set(_id_map(comparison.target_analysis))
    available = (
        {f"source.{identifier}" for identifier in source_ids}
        | {f"target.{identifier}" for identifier in target_ids}
    )
    difference_ids: set[str] = set()
    for difference in comparison.differences:
        if difference.id in difference_ids:
            raise ReferenceValidationError(f"duplicate difference ID: {difference.id}")
        difference_ids.add(difference.id)
        for reference in difference.references:
            _require(reference, available, f"difference {difference.id}")
    return comparison
