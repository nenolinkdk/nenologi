"""Conservative exact-explicit inference over normalized analyses."""

from __future__ import annotations

from decimal import Decimal

from ..models import Analysis, Confidence, Inference, InterpretationStatus

EXACT_EXPLICIT_RULE = "EXACT_EXPLICIT"
LEXICAL_OPPOSITION_RULE = "LEXICAL_OPPOSITION"
NOT_ESTABLISHED_RULE = "NOT_ESTABLISHED"
UNIVERSAL_INSTANTIATION_RULE = "UNIVERSAL_INSTANTIATION"

# Deliberately closed and auditable. Additions require controlled-domain review.
LEXICAL_OPPOSITION_PAIRS: tuple[tuple[str, str], ...] = (("OFF", "ON"),)


def are_lexical_opposites(left: str, right: str) -> bool:
    """Return whether normalized predicates form a declared symmetric pair."""
    normalized = {_text(left).upper(), _text(right).upper()}
    return any(normalized == set(pair) for pair in LEXICAL_OPPOSITION_PAIRS)


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


def _semantic_signature(analysis: Analysis, *, abstract_predicates: bool = False) -> tuple[object, ...]:
    """Return the complete v0.1 semantic graph, excluding raw text and source metadata."""
    references = _reference_map(analysis)

    def ref(identifier: str) -> str:
        # Unknown references are structural provenance and do not establish semantics.
        return references.get(identifier, "structural")

    entities = tuple(
        (
            _text(item.type),
            "bound_variable" if _text(item.type) == "bound_variable" else _text(item.label),
            item.interpretation_status.value,
        )
        for item in analysis.entities
    )
    propositions = tuple(
        (
            "predicate" if abstract_predicates else _text(item.predicate),
            tuple(ref(value) for value in item.arguments), item.interpretation_status.value,
        )
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


def _entity_key(entity) -> tuple[str, str, str]:
    return (_text(entity.type), _text(entity.label), entity.interpretation_status.value)


def _bare_membership(analysis: Analysis):
    """Return one individual and its unary facts, or None for any wrapped query."""
    if (
        len(analysis.entities) != 1
        or _text(analysis.entities[0].type) != "individual"
        or analysis.entities[0].interpretation_status != InterpretationStatus.EXPLICIT
    ):
        return None
    if any((
        analysis.relations, analysis.quantifiers, analysis.modality, analysis.negation,
        analysis.numeric_constraints, analysis.conditions, analysis.temporal_relations,
        analysis.sets,
    )):
        return None
    entity = analysis.entities[0]
    if not analysis.propositions or any(
        proposition.arguments != (entity.id,)
        or proposition.interpretation_status != InterpretationStatus.EXPLICIT
        for proposition in analysis.propositions
    ):
        return None
    return entity, analysis.propositions


def _rule_proposition_ids(analysis: Analysis) -> set[str]:
    return {
        reference
        for condition in analysis.conditions
        for reference in (*condition.antecedent, *condition.consequent)
    }


def _explicit_membership_evidence(premise: Analysis, conclusion: Analysis) -> tuple[str, ...] | None:
    """Recognize a complete bare membership query among explicit premise facts."""
    query_membership = _bare_membership(conclusion)
    if query_membership is None:
        return None
    query_entity, query_facts = query_membership
    template_ids = _rule_proposition_ids(premise)
    entities = {entity.id: entity for entity in premise.entities}
    for entity in premise.entities:
        if _text(entity.type) != "individual" or _entity_key(entity) != _entity_key(query_entity):
            continue
        source_facts = {
            _text(proposition.predicate): proposition
            for proposition in premise.propositions
            if proposition.id not in template_ids
            and proposition.arguments == (entity.id,)
            and proposition.interpretation_status == InterpretationStatus.EXPLICIT
        }
        matched = [source_facts.get(_text(proposition.predicate)) for proposition in query_facts]
        if all(matched):
            return (entity.id, *(proposition.id for proposition in matched))
    return None


def _universal_instantiation_evidence(
    premise: Analysis, conclusion: Analysis,
) -> tuple[tuple[str, ...], str] | None:
    """Match the one controlled unary universal-rule shape without chaining."""
    query_membership = _bare_membership(conclusion)
    if query_membership is None or any((
        premise.relations, premise.modality, premise.negation,
        premise.numeric_constraints, premise.temporal_relations, premise.sets,
    )):
        return None
    query_entity, query_facts = query_membership
    query_predicates = {_text(proposition.predicate) for proposition in query_facts}
    propositions = {proposition.id: proposition for proposition in premise.propositions}
    entities = {entity.id: entity for entity in premise.entities}
    template_ids = _rule_proposition_ids(premise)

    for quantifier in premise.quantifiers:
        if (
            quantifier.operator != "ALL"
            or quantifier.interpretation_status != InterpretationStatus.EXPLICIT
        ):
            continue
        condition = next(
            (item for item in premise.conditions if quantifier.scope == (item.id,)), None,
        )
        if (
            condition is None
            or condition.interpretation_status != InterpretationStatus.EXPLICIT
            or len(condition.consequent) != 1
        ):
            continue
        templates = [propositions.get(identifier) for identifier in (*condition.antecedent, *condition.consequent)]
        if any(item is None for item in templates):
            continue
        bound_ids = {
            item.arguments[0]
            for item in templates
            if len(item.arguments) == 1
        }
        if (
            len(bound_ids) != 1
            or any(len(item.arguments) != 1 for item in templates)
            or any(item.interpretation_status != InterpretationStatus.EXPLICIT for item in templates)
        ):
            continue
        bound_id = next(iter(bound_ids))
        bound = entities.get(bound_id)
        if (
            bound is None
            or _text(bound.type) != "bound_variable"
            or bound.interpretation_status != InterpretationStatus.EXPLICIT
        ):
            continue
        consequent = templates[-1]
        if _text(consequent.predicate) not in query_predicates:
            continue

        for concrete in premise.entities:
            if _text(concrete.type) != "individual" or _entity_key(concrete) != _entity_key(query_entity):
                continue
            concrete_facts = {
                _text(proposition.predicate): proposition
                for proposition in premise.propositions
                if proposition.id not in template_ids
                and proposition.arguments == (concrete.id,)
                and proposition.interpretation_status == InterpretationStatus.EXPLICIT
            }
            supporting = [concrete_facts.get(_text(item.predicate)) for item in templates[:-1]]
            if not all(supporting):
                continue
            established = set(concrete_facts) | {_text(consequent.predicate)}
            if not query_predicates <= established:
                continue
            evidence = (
                quantifier.id, condition.id, *condition.antecedent,
                *(item.id for item in supporting), concrete.id, consequent.id,
            )
            substitution = f"{bound.id} := {concrete.label}"
            return tuple(dict.fromkeys(evidence)), substitution
    return None


def _unqualified_explicit_evidence(premise: Analysis, conclusion: Analysis) -> tuple[str, ...] | None:
    """Find one exact bare proposition inside a larger normalized premise."""
    if len(conclusion.propositions) != 1 or any((
        conclusion.relations, conclusion.quantifiers, conclusion.modality,
        conclusion.negation, conclusion.numeric_constraints, conclusion.conditions,
        conclusion.temporal_relations, conclusion.sets,
    )):
        return None
    query = conclusion.propositions[0]
    query_entities = {
        entity.id: (_text(entity.type), _text(entity.label), entity.interpretation_status.value)
        for entity in conclusion.entities
    }
    governed_ids = {
        reference
        for item in (
            *premise.relations, *premise.quantifiers, *premise.modality,
            *premise.negation, *premise.numeric_constraints, *premise.sets,
        )
        for reference in (*getattr(item, "arguments", ()), *getattr(item, "scope", ()))
    }
    governed_ids.update(item.proposition for item in premise.temporal_relations)
    governed_ids.update(
        reference
        for item in premise.conditions
        for reference in (*item.antecedent, *item.consequent)
    )
    for proposition in premise.propositions:
        if (
            proposition.id in governed_ids
            or _text(proposition.predicate) != _text(query.predicate)
            or proposition.interpretation_status != query.interpretation_status
            or len(proposition.arguments) != len(query.arguments)
        ):
            continue
        premise_entities = {entity.id: entity for entity in premise.entities}
        pairs = zip(proposition.arguments, query.arguments, strict=True)
        if all(
            source_id in premise_entities and query_id in query_entities
            and (
                _text(premise_entities[source_id].type),
                _text(premise_entities[source_id].label),
                premise_entities[source_id].interpretation_status.value,
            ) == query_entities[query_id]
            for source_id, query_id in pairs
        ):
            return tuple((*proposition.arguments, proposition.id))
    return None


class DeterministicInferenceEngine:
    """Apply exact identity, then closed lexical opposition, then no-proof fallback."""

    def infer(self, premise: Analysis, conclusion: Analysis) -> Inference:
        explicit_evidence = None
        if _semantic_signature(premise) == _semantic_signature(conclusion):
            explicit_evidence = _evidence_ids(premise)
        else:
            explicit_evidence = _unqualified_explicit_evidence(premise, conclusion)
        if explicit_evidence is None:
            explicit_evidence = _explicit_membership_evidence(premise, conclusion)
        if explicit_evidence is not None:
            return Inference(
                id="inference_001",
                claim=conclusion.document.text,
                interpretation_status=InterpretationStatus.EXPLICIT,
                confidence=Confidence(1.0, "Exact normalized semantic identity"),
                derived_from=explicit_evidence,
                rule=EXACT_EXPLICIT_RULE,
            )
        if (
            len(premise.propositions) == 1
            and len(conclusion.propositions) == 1
            and are_lexical_opposites(
                premise.propositions[0].predicate, conclusion.propositions[0].predicate,
            )
            and _semantic_signature(premise, abstract_predicates=True)
            == _semantic_signature(conclusion, abstract_predicates=True)
        ):
            proposition = premise.propositions[0]
            return Inference(
                id="inference_001",
                claim=conclusion.document.text,
                interpretation_status=InterpretationStatus.CONTRADICTED,
                confidence=Confidence(1.0, "Declared controlled lexical opposition"),
                derived_from=tuple((*proposition.arguments, proposition.id)),
                rule=LEXICAL_OPPOSITION_RULE,
            )
        universal = _universal_instantiation_evidence(premise, conclusion)
        if universal is not None:
            evidence, substitution = universal
            return Inference(
                id="inference_001",
                claim=conclusion.document.text,
                interpretation_status=InterpretationStatus.ENTAILED,
                confidence=Confidence(1.0, f"Universal instantiation ({substitution})"),
                derived_from=evidence,
                rule=UNIVERSAL_INSTANTIATION_RULE,
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
        if inference.rule == LEXICAL_OPPOSITION_RULE:
            return (
                "The conclusion conflicts with an explicitly represented predicate whose "
                "opposition is declared in the controlled lexical rule set."
            )
        if inference.rule == UNIVERSAL_INSTANTIATION_RULE:
            substitution = inference.confidence.rationale or "Universal instantiation"
            return (
                "The conclusion follows by applying an explicitly represented universal rule "
                f"to matching membership facts. {substitution}."
            )
        return "The conclusion is not established by the supported exact inference rules."
