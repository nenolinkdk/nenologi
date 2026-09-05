"""Conservative exact-explicit inference over normalized analyses."""

from __future__ import annotations

from decimal import Decimal

from ..models import Analysis, Confidence, Inference, InterpretationStatus

EXACT_EXPLICIT_RULE = "EXACT_EXPLICIT"
NOT_ESTABLISHED_RULE = "NOT_ESTABLISHED"


def _text(value: str) -> str:
    """Normalize non-semantic presentation variation in model text values."""
    return " ".join(value.casefold().split())


def _decimal(value: Decimal) -> str:
    rendered = format(value, "f")
    return (rendered.rstrip("0").rstrip(".") or "0") if "." in rendered else rendered


def _reference_map(analysis: Analysis) -> dict[str, str]:
    """Replace analysis-local IDs with stable, collection-relative references."""
    collections = (
        ("entity", analysis.entities),
        ("proposition", analysis.propositions),
        ("relation", analysis.relations),
        ("quantifier", analysis.quantifiers),
        ("modality", analysis.modality),
        ("negation", analysis.negation),
        ("numeric", analysis.numeric_constraints),
        ("condition", analysis.conditions),
        ("temporal", analysis.temporal_relations),
        ("set", analysis.sets),
    )
    return {
        item.id: f"{kind}:{index}"
        for kind, items in collections
        for index, item in enumerate(items)
    }


def _semantic_signature(analysis: Analysis) -> tuple[object, ...]:
    """Return the complete v0.1 semantic graph, excluding raw text and source metadata."""
    references = _reference_map(analysis)

    def ref(identifier: str) -> str:
        # Unknown references are structural provenance and do not establish semantics.
        return references.get(identifier, "structural")

    entities = tuple(
        (_text(item.type), _text(item.label), item.interpretation_status.value)
        for item in analysis.entities
    )
    propositions = tuple(
        (_text(item.predicate), tuple(ref(value) for value in item.arguments), item.interpretation_status.value)
        for item in analysis.propositions
    )
    relations = tuple(
        (_text(item.type), tuple(ref(value) for value in item.arguments), item.interpretation_status.value)
        for item in analysis.relations
    )

    def operators(items) -> tuple[object, ...]:
        return tuple(
            (_text(item.operator), tuple(ref(value) for value in item.scope), item.interpretation_status.value)
            for item in items
        )

    numeric = tuple(
        (
            item.operator.value, _decimal(item.value), _text(item.unit) if item.unit else None,
            tuple(ref(value) for value in item.scope), item.interpretation_status.value,
        )
        for item in analysis.numeric_constraints
    )
    conditions = tuple(
        (
            tuple(ref(value) for value in item.antecedent),
            tuple(ref(value) for value in item.consequent),
            item.interpretation_status.value,
        )
        for item in analysis.conditions
    )
    temporal = tuple(
        (
            ref(item.proposition), item.relation.value, _text(item.temporal_reference),
            item.interpretation_status.value,
        )
        for item in analysis.temporal_relations
    )
    sets = tuple(
        (_text(item.type), tuple(ref(value) for value in item.arguments), item.interpretation_status.value)
        for item in analysis.sets
    )
    return (
        entities, propositions, relations, operators(analysis.quantifiers),
        operators(analysis.modality), operators(analysis.negation), numeric,
        conditions, temporal, sets,
    )


def _evidence_ids(analysis: Analysis) -> tuple[str, ...]:
    """Return semantic evidence in stable model order."""
    return tuple(
        item.id
        for items in (
            analysis.entities, analysis.propositions, analysis.relations,
            analysis.quantifiers, analysis.modality, analysis.negation,
            analysis.numeric_constraints, analysis.conditions,
            analysis.temporal_relations, analysis.sets,
        )
        for item in items
    )


class DeterministicInferenceEngine:
    """Recognize only conclusions already explicit in the normalized premise."""

    def infer(self, premise: Analysis, conclusion: Analysis) -> Inference:
        if _semantic_signature(premise) == _semantic_signature(conclusion):
            return Inference(
                id="inference_001",
                claim=conclusion.document.text,
                interpretation_status=InterpretationStatus.EXPLICIT,
                confidence=Confidence(1.0, "Exact normalized semantic identity"),
                derived_from=_evidence_ids(premise),
                rule=EXACT_EXPLICIT_RULE,
            )
        return Inference(
            id="inference_001",
            claim=conclusion.document.text,
            interpretation_status=InterpretationStatus.UNSUPPORTED,
            confidence=Confidence(1.0, "Not established by exact explicit inference"),
            rule=NOT_ESTABLISHED_RULE,
        )

    def explain(self, inference: Inference) -> str:
        if inference.rule == EXACT_EXPLICIT_RULE:
            return "The conclusion is explicitly represented in the normalized premise."
        return "The conclusion is not established by the supported exact inference rules."
