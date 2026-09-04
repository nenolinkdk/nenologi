"""Explicit JSON serialization and deserialization for schema version 0.1."""

from __future__ import annotations

import json
from collections.abc import Mapping
from copy import deepcopy
from typing import Any, Callable, TypeVar

from ..models import (
    Ambiguity, Analysis, Comparison, ComparisonMode, Condition, Confidence, Difference,
    DifferenceType, DiscourseRelation, DiscourseRelationType, Document, Entity,
    Inference, InterpretationStatus, LocalizedText, LogicalExpression, LogicalRelation, NumericConstraint, NumericOperator, Operator,
    Proposition, SCHEMA_VERSION, SemanticItem, Severity, Span, StructuralNode,
    Structure, TemporalRelation, TemporalRelationType,
)
from ..models.common import DomainValidationError
from .validation import SchemaValidationError

T = TypeVar("T")


def _object(value: Any, required: set[str], optional: set[str], location: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise SchemaValidationError(f"{location} must be an object")
    data = dict(value)
    missing = required - data.keys()
    unknown = data.keys() - required - optional
    if missing:
        raise SchemaValidationError(f"{location} missing required fields: {sorted(missing)}")
    if unknown:
        raise SchemaValidationError(f"{location} has unknown fields: {sorted(unknown)}")
    return data


def _array(value: Any, location: str) -> list[Any]:
    if not isinstance(value, list):
        raise SchemaValidationError(f"{location} must be an array")
    return value


def _enum(enum_type: type[T], value: Any, location: str) -> T:
    try:
        return enum_type(value)
    except (TypeError, ValueError) as exc:
        raise SchemaValidationError(f"{location} has invalid enum value: {value!r}") from exc


def _construct(factory: Callable[..., T], location: str, **values: Any) -> T:
    try:
        return factory(**values)
    except DomainValidationError as exc:
        raise SchemaValidationError(f"{location}: {exc}") from exc


def _confidence_to_dict(value: Confidence) -> dict[str, Any]:
    result: dict[str, Any] = {"value": value.value}
    if value.rationale is not None:
        result["rationale"] = value.rationale
    return result


def _confidence_from_dict(value: Any, location: str) -> Confidence:
    data = _object(value, {"value"}, {"rationale"}, location)
    return _construct(Confidence, location, value=data["value"], rationale=data.get("rationale"))


def _span_to_dict(value: Span) -> dict[str, int]:
    return {"start": value.start, "end": value.end}


def _span_from_dict(value: Any, location: str) -> Span:
    data = _object(value, {"start", "end"}, set(), location)
    return _construct(Span, location, start=data["start"], end=data["end"])


def _status(value: Any, location: str) -> InterpretationStatus:
    return _enum(InterpretationStatus, value, location)


def _with_grounding(result: dict[str, Any], span: Span | None, derived_from: tuple[str, ...] | None = None) -> None:
    if span is not None:
        result["span"] = _span_to_dict(span)
    if derived_from:
        result["derived_from"] = list(derived_from)


def _entity_to_dict(value: Entity) -> dict[str, Any]:
    result = {"id": value.id, "type": value.type, "label": value.label,
              "interpretation_status": value.interpretation_status.value,
              "confidence": _confidence_to_dict(value.confidence)}
    _with_grounding(result, value.span)
    return result


def _entity_from_dict(value: Any, location: str) -> Entity:
    data = _object(value, {"id", "type", "label", "interpretation_status", "confidence"}, {"span"}, location)
    return _construct(Entity, location, id=data["id"], type=data["type"], label=data["label"],
                      interpretation_status=_status(data["interpretation_status"], f"{location}.interpretation_status"),
                      confidence=_confidence_from_dict(data["confidence"], f"{location}.confidence"),
                      span=_span_from_dict(data["span"], f"{location}.span") if "span" in data else None)


def _proposition_to_dict(value: Proposition) -> dict[str, Any]:
    result = {"id": value.id, "predicate": value.predicate, "arguments": list(value.arguments),
              "interpretation_status": value.interpretation_status.value,
              "confidence": _confidence_to_dict(value.confidence)}
    _with_grounding(result, value.span, value.derived_from)
    return result


def _proposition_from_dict(value: Any, location: str) -> Proposition:
    data = _object(value, {"id", "predicate", "arguments", "interpretation_status", "confidence"}, {"span", "derived_from"}, location)
    return _construct(Proposition, location, id=data["id"], predicate=data["predicate"],
                      arguments=tuple(_array(data["arguments"], f"{location}.arguments")),
                      interpretation_status=_status(data["interpretation_status"], f"{location}.interpretation_status"),
                      confidence=_confidence_from_dict(data["confidence"], f"{location}.confidence"),
                      span=_span_from_dict(data["span"], f"{location}.span") if "span" in data else None,
                      derived_from=tuple(_array(data.get("derived_from", []), f"{location}.derived_from")))


def _semantic_to_dict(value: SemanticItem) -> dict[str, Any]:
    result = {"id": value.id, "type": value.type, "arguments": list(value.arguments),
              "interpretation_status": value.interpretation_status.value,
              "confidence": _confidence_to_dict(value.confidence)}
    _with_grounding(result, value.span, value.derived_from)
    return result


def _semantic_from_dict(value: Any, location: str) -> SemanticItem:
    data = _object(value, {"id", "type", "arguments", "interpretation_status", "confidence"}, {"span", "derived_from"}, location)
    return _construct(SemanticItem, location, id=data["id"], type=data["type"],
                      arguments=tuple(_array(data["arguments"], f"{location}.arguments")),
                      interpretation_status=_status(data["interpretation_status"], f"{location}.interpretation_status"),
                      confidence=_confidence_from_dict(data["confidence"], f"{location}.confidence"),
                      span=_span_from_dict(data["span"], f"{location}.span") if "span" in data else None,
                      derived_from=tuple(_array(data.get("derived_from", []), f"{location}.derived_from")))


def _operator_to_dict(value: Operator) -> dict[str, Any]:
    result = {"id": value.id, "operator": value.operator, "scope": list(value.scope),
              "interpretation_status": value.interpretation_status.value,
              "confidence": _confidence_to_dict(value.confidence)}
    _with_grounding(result, value.span)
    return result


def _operator_from_dict(value: Any, location: str) -> Operator:
    data = _object(value, {"id", "operator", "scope", "interpretation_status", "confidence"}, {"span"}, location)
    return _construct(Operator, location, id=data["id"], operator=data["operator"],
                      scope=tuple(_array(data["scope"], f"{location}.scope")),
                      interpretation_status=_status(data["interpretation_status"], f"{location}.interpretation_status"),
                      confidence=_confidence_from_dict(data["confidence"], f"{location}.confidence"),
                      span=_span_from_dict(data["span"], f"{location}.span") if "span" in data else None)


def _numeric_to_dict(value: NumericConstraint) -> dict[str, Any]:
    result = {
        "id": value.id, "operator": value.operator.value, "value": str(value.value),
        "scope": list(value.scope), "interpretation_status": value.interpretation_status.value,
        "confidence": _confidence_to_dict(value.confidence),
    }
    if value.unit is not None:
        result["unit"] = value.unit
    if value.span is not None:
        result["span"] = _span_to_dict(value.span)
    return result


def _numeric_from_dict(value: Any, location: str) -> NumericConstraint:
    required = {"id", "operator", "value", "scope", "interpretation_status", "confidence"}
    data = _object(value, required, {"unit", "span"}, location)
    return _construct(
        NumericConstraint, location, id=data["id"],
        operator=_enum(NumericOperator, data["operator"], f"{location}.operator"), value=data["value"],
        unit=data.get("unit"), scope=tuple(_array(data["scope"], f"{location}.scope")),
        interpretation_status=_status(data["interpretation_status"], f"{location}.interpretation_status"),
        confidence=_confidence_from_dict(data["confidence"], f"{location}.confidence"),
        span=_span_from_dict(data["span"], f"{location}.span") if "span" in data else None,
    )


def _condition_to_dict(value: Condition) -> dict[str, Any]:
    result = {
        "id": value.id, "antecedent": list(value.antecedent), "consequent": list(value.consequent),
        "interpretation_status": value.interpretation_status.value,
        "confidence": _confidence_to_dict(value.confidence),
    }
    if value.span is not None:
        result["span"] = _span_to_dict(value.span)
    return result


def _condition_from_dict(value: Any, location: str) -> Condition:
    required = {"id", "antecedent", "consequent", "interpretation_status", "confidence"}
    data = _object(value, required, {"span"}, location)
    return _construct(
        Condition, location, id=data["id"],
        antecedent=tuple(_array(data["antecedent"], f"{location}.antecedent")),
        consequent=tuple(_array(data["consequent"], f"{location}.consequent")),
        interpretation_status=_status(data["interpretation_status"], f"{location}.interpretation_status"),
        confidence=_confidence_from_dict(data["confidence"], f"{location}.confidence"),
        span=_span_from_dict(data["span"], f"{location}.span") if "span" in data else None,
    )


def _temporal_to_dict(value: TemporalRelation) -> dict[str, Any]:
    result = {
        "id": value.id, "proposition": value.proposition, "relation": value.relation.value,
        "temporal_reference": value.temporal_reference,
        "interpretation_status": value.interpretation_status.value,
        "confidence": _confidence_to_dict(value.confidence),
    }
    if value.span is not None:
        result["span"] = _span_to_dict(value.span)
    return result


def _temporal_from_dict(value: Any, location: str) -> TemporalRelation:
    required = {"id", "proposition", "relation", "temporal_reference", "interpretation_status", "confidence"}
    data = _object(value, required, {"span"}, location)
    return _construct(
        TemporalRelation, location, id=data["id"], proposition=data["proposition"],
        relation=_enum(TemporalRelationType, data["relation"], f"{location}.relation"),
        temporal_reference=data["temporal_reference"],
        interpretation_status=_status(data["interpretation_status"], f"{location}.interpretation_status"),
        confidence=_confidence_from_dict(data["confidence"], f"{location}.confidence"),
        span=_span_from_dict(data["span"], f"{location}.span") if "span" in data else None,
    )


def _node_to_dict(value: StructuralNode) -> dict[str, Any]:
    result: dict[str, Any] = {"id": value.id, "span": _span_to_dict(value.span)}
    if value.parent_id is not None: result["parent_id"] = value.parent_id
    if value.kind is not None: result["kind"] = value.kind
    return result


def _node_from_dict(value: Any, location: str) -> StructuralNode:
    data = _object(value, {"id", "span"}, {"parent_id", "kind"}, location)
    return _construct(StructuralNode, location, id=data["id"], span=_span_from_dict(data["span"], f"{location}.span"), parent_id=data.get("parent_id"), kind=data.get("kind"))


def _discourse_to_dict(value: DiscourseRelation) -> dict[str, str]:
    return {"id": value.id, "type": value.type.value, "source_id": value.source_id, "target_id": value.target_id}


def _discourse_from_dict(value: Any, location: str) -> DiscourseRelation:
    data = _object(value, {"id", "type", "source_id", "target_id"}, set(), location)
    return _construct(DiscourseRelation, location, id=data["id"], type=_enum(DiscourseRelationType, data["type"], f"{location}.type"), source_id=data["source_id"], target_id=data["target_id"])


def _logical_to_dict(value: LogicalExpression) -> dict[str, Any]:
    result = {"id": value.id, "expression": deepcopy(value.expression),
              "interpretation_status": value.interpretation_status.value,
              "confidence": _confidence_to_dict(value.confidence)}
    if value.display is not None: result["display"] = value.display
    if value.derived_from: result["derived_from"] = list(value.derived_from)
    return result


def _logical_from_dict(value: Any, location: str) -> LogicalExpression:
    data = _object(value, {"id", "expression", "interpretation_status", "confidence"}, {"display", "derived_from"}, location)
    if not isinstance(data["expression"], dict):
        raise SchemaValidationError(f"{location}.expression must be an object")
    return _construct(LogicalExpression, location, id=data["id"], expression=deepcopy(data["expression"]),
                      interpretation_status=_status(data["interpretation_status"], f"{location}.interpretation_status"),
                      confidence=_confidence_from_dict(data["confidence"], f"{location}.confidence"),
                      display=data.get("display"), derived_from=tuple(_array(data.get("derived_from", []), f"{location}.derived_from")))


def _inference_to_dict(value: Inference) -> dict[str, Any]:
    result = {"id": value.id, "claim": value.claim,
              "interpretation_status": value.interpretation_status.value,
              "confidence": _confidence_to_dict(value.confidence)}
    if value.derived_from: result["derived_from"] = list(value.derived_from)
    if value.rule is not None: result["rule"] = value.rule
    return result


def _inference_from_dict(value: Any, location: str) -> Inference:
    data = _object(value, {"id", "claim", "interpretation_status", "confidence"}, {"derived_from", "rule"}, location)
    return _construct(Inference, location, id=data["id"], claim=data["claim"],
                      interpretation_status=_status(data["interpretation_status"], f"{location}.interpretation_status"),
                      confidence=_confidence_from_dict(data["confidence"], f"{location}.confidence"),
                      derived_from=tuple(_array(data.get("derived_from", []), f"{location}.derived_from")), rule=data.get("rule"))


def _ambiguity_to_dict(value: Ambiguity) -> dict[str, Any]:
    return {"id": value.id, "description": value.description, "reading_ids": list(value.reading_ids), "confidence": _confidence_to_dict(value.confidence)}


def _ambiguity_from_dict(value: Any, location: str) -> Ambiguity:
    data = _object(value, {"id", "description", "reading_ids", "confidence"}, set(), location)
    return _construct(Ambiguity, location, id=data["id"], description=data["description"],
                      reading_ids=tuple(_array(data["reading_ids"], f"{location}.reading_ids")),
                      confidence=_confidence_from_dict(data["confidence"], f"{location}.confidence"))


def analysis_to_dict(value: Analysis) -> dict[str, Any]:
    """Convert a typed analysis to the one canonical v0.1 JSON shape."""
    document = {"id": value.document.id, "language": value.document.language, "text": value.document.text}
    structure = {
        "sentences": [_node_to_dict(item) for item in value.structure.sentences],
        "clauses": [_node_to_dict(item) for item in value.structure.clauses],
        "discourse_relations": [_discourse_to_dict(item) for item in value.structure.discourse_relations],
    }
    return {
        "schema_version": value.schema_version,
        "document": document,
        "profile": value.profile,
        "structure": structure,
        "entities": [_entity_to_dict(item) for item in value.entities],
        "propositions": [_proposition_to_dict(item) for item in value.propositions],
        "relations": [_semantic_to_dict(item) for item in value.relations],
        "quantifiers": [_operator_to_dict(item) for item in value.quantifiers],
        "modality": [_operator_to_dict(item) for item in value.modality],
        "negation": [_operator_to_dict(item) for item in value.negation],
        "numeric_constraints": [_numeric_to_dict(item) for item in value.numeric_constraints],
        "conditions": [_condition_to_dict(item) for item in value.conditions],
        "temporal_relations": [_temporal_to_dict(item) for item in value.temporal_relations],
        "sets": [_semantic_to_dict(item) for item in value.sets],
        "logical_representation": [_logical_to_dict(item) for item in value.logical_representation],
        "inferences": [_inference_to_dict(item) for item in value.inferences],
        "ambiguities": [_ambiguity_to_dict(item) for item in value.ambiguities],
        "confidence": _confidence_to_dict(value.confidence),
        "plain_language_interpretation": {"language": value.plain_language_interpretation.language, "text": value.plain_language_interpretation.text},
    }


def analysis_from_dict(value: Mapping[str, Any]) -> Analysis:
    """Build a typed analysis, rejecting schema-shape and domain-value errors."""
    required = {"schema_version", "document", "profile", "structure", "entities", "propositions", "relations", "quantifiers", "modality", "negation", "numeric_constraints", "conditions", "temporal_relations", "sets", "logical_representation", "inferences", "ambiguities", "confidence", "plain_language_interpretation"}
    data = _object(value, required, set(), "analysis")
    document_data = _object(data["document"], {"id", "language", "text"}, set(), "analysis.document")
    document = _construct(Document, "analysis.document", **document_data)
    structure_data = _object(data["structure"], {"sentences", "clauses", "discourse_relations"}, set(), "analysis.structure")
    structure = Structure(
        sentences=tuple(_node_from_dict(item, f"analysis.structure.sentences[{i}]") for i, item in enumerate(_array(structure_data["sentences"], "analysis.structure.sentences"))),
        clauses=tuple(_node_from_dict(item, f"analysis.structure.clauses[{i}]") for i, item in enumerate(_array(structure_data["clauses"], "analysis.structure.clauses"))),
        discourse_relations=tuple(_discourse_from_dict(item, f"analysis.structure.discourse_relations[{i}]") for i, item in enumerate(_array(structure_data["discourse_relations"], "analysis.structure.discourse_relations"))),
    )
    localized = _object(data["plain_language_interpretation"], {"language", "text"}, set(), "analysis.plain_language_interpretation")
    def items(name: str, factory: Callable[[Any, str], T]) -> tuple[T, ...]:
        return tuple(factory(item, f"analysis.{name}[{i}]") for i, item in enumerate(_array(data[name], f"analysis.{name}")))
    return _construct(
        Analysis, "analysis", schema_version=data["schema_version"], document=document,
        profile=data["profile"], structure=structure, entities=items("entities", _entity_from_dict),
        propositions=items("propositions", _proposition_from_dict), relations=items("relations", _semantic_from_dict),
        quantifiers=items("quantifiers", _operator_from_dict), modality=items("modality", _operator_from_dict),
        negation=items("negation", _operator_from_dict), numeric_constraints=items("numeric_constraints", _numeric_from_dict), conditions=items("conditions", _condition_from_dict),
        temporal_relations=items("temporal_relations", _temporal_from_dict), sets=items("sets", _semantic_from_dict),
        logical_representation=items("logical_representation", _logical_from_dict),
        inferences=items("inferences", _inference_from_dict), ambiguities=items("ambiguities", _ambiguity_from_dict),
        confidence=_confidence_from_dict(data["confidence"], "analysis.confidence"),
        plain_language_interpretation=_construct(LocalizedText, "analysis.plain_language_interpretation", **localized),
    )


def _difference_to_dict(value: Difference) -> dict[str, Any]:
    return {
        "id": value.id,
        "difference_type": value.difference_type.value,
        "source_value": deepcopy(value.source_value),
        "target_value": deepcopy(value.target_value),
        "severity": value.severity.value,
        "confidence": _confidence_to_dict(value.confidence),
        "explanation": value.explanation,
        "references": list(value.references),
    }


def _difference_from_dict(value: Any, location: str) -> Difference:
    fields = {"id", "difference_type", "source_value", "target_value", "severity", "confidence", "explanation", "references"}
    data = _object(value, fields, set(), location)
    return _construct(
        Difference, location, id=data["id"],
        difference_type=_enum(DifferenceType, data["difference_type"], f"{location}.difference_type"),
        source_value=deepcopy(data["source_value"]), target_value=deepcopy(data["target_value"]),
        severity=_enum(Severity, data["severity"], f"{location}.severity"),
        confidence=_confidence_from_dict(data["confidence"], f"{location}.confidence"),
        explanation=data["explanation"], references=tuple(_array(data["references"], f"{location}.references")),
    )


def comparison_to_dict(value: Comparison) -> dict[str, Any]:
    return {
        "schema_version": value.schema_version,
        "mode": value.mode.value,
        "logical_relation": value.logical_relation.value,
        "source_analysis": analysis_to_dict(value.source_analysis),
        "target_analysis": analysis_to_dict(value.target_analysis),
        "differences": [_difference_to_dict(item) for item in value.differences],
    }


def comparison_from_dict(value: Mapping[str, Any]) -> Comparison:
    required = {"schema_version", "mode", "source_analysis", "target_analysis", "differences"}
    data = _object(value, required, {"logical_relation"}, "comparison")
    return _construct(
        Comparison, "comparison", schema_version=data["schema_version"],
        mode=_enum(ComparisonMode, data["mode"], "comparison.mode"),
        logical_relation=_enum(LogicalRelation, data.get("logical_relation", "UNDETERMINED"), "comparison.logical_relation"),
        source_analysis=analysis_from_dict(data["source_analysis"]),
        target_analysis=analysis_from_dict(data["target_analysis"]),
        differences=tuple(_difference_from_dict(item, f"comparison.differences[{i}]") for i, item in enumerate(_array(data["differences"], "comparison.differences"))),
    )


def analysis_to_json(value: Analysis, *, indent: int | None = 2) -> str:
    return json.dumps(analysis_to_dict(value), ensure_ascii=False, allow_nan=False, indent=indent) + ("\n" if indent is not None else "")


def analysis_from_json(value: str) -> Analysis:
    try:
        data = json.loads(value)
    except (TypeError, json.JSONDecodeError) as exc:
        raise SchemaValidationError(f"invalid analysis JSON: {exc}") from exc
    return analysis_from_dict(data)


def comparison_to_json(value: Comparison, *, indent: int | None = 2) -> str:
    return json.dumps(comparison_to_dict(value), ensure_ascii=False, allow_nan=False, indent=indent) + ("\n" if indent is not None else "")


def comparison_from_json(value: str) -> Comparison:
    try:
        data = json.loads(value)
    except (TypeError, json.JSONDecodeError) as exc:
        raise SchemaValidationError(f"invalid comparison JSON: {exc}") from exc
    return comparison_from_dict(data)
