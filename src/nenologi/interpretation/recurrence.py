"""Controlled, deterministic recurrence-prediction policy."""

from __future__ import annotations

import re

from ..inference import NOT_ESTABLISHED_RULE
from ..models import Analysis, Confidence, Inference, InterpretationStatus, TemporalRelationType
from .models import (
    EvidenceObjectKind, EvidenceReference, EvidenceSide, InterpretationProvenance,
    InterpretationResult,
)

DEFEASIBLE_RECURRENCE_PREDICTION_POLICY = "DEFEASIBLE_RECURRENCE_PREDICTION.v1"
_RECURRENCE_REFERENCE = re.compile(r"^LAST_([1-9][0-9]*)_EVENINGS$")


class DefeasibleRecurrencePredictionPolicy:
    """Recognize one bounded repeated-evening to current-evening pattern."""

    policy_id = DEFEASIBLE_RECURRENCE_PREDICTION_POLICY

    def evaluate(
        self,
        premise: Analysis,
        query: Analysis,
        deterministic_result: Inference,
    ) -> InterpretationResult | None:
        if not (
            deterministic_result.interpretation_status is InterpretationStatus.UNSUPPORTED
            and deterministic_result.rule == NOT_ESTABLISHED_RULE
        ):
            return None
        if not self._has_safe_shape(premise) or not self._has_safe_shape(query):
            return None
        if len(premise.propositions) != 1 or len(query.propositions) != 1:
            return None
        if len(premise.temporal_relations) != 1 or len(query.temporal_relations) != 1:
            return None

        observed = premise.propositions[0]
        future = query.propositions[0]
        observed_time = premise.temporal_relations[0]
        future_time = query.temporal_relations[0]
        match = _RECURRENCE_REFERENCE.fullmatch(observed_time.temporal_reference)
        if match is None or int(match.group(1)) < 2:
            return None
        if not (
            observed_time.relation is TemporalRelationType.ON
            and future_time.relation is TemporalRelationType.ON
            and observed_time.proposition == observed.id
            and future_time.proposition == future.id
            and future_time.temporal_reference == "THIS_EVENING"
            and observed.predicate == future.predicate
            and len(observed.arguments) == len(future.arguments)
            and observed.interpretation_status is InterpretationStatus.EXPLICIT
            and future.interpretation_status is InterpretationStatus.EXPLICIT
            and observed_time.interpretation_status is InterpretationStatus.EXPLICIT
            and future_time.interpretation_status is InterpretationStatus.EXPLICIT
        ):
            return None

        premise_entities = {item.id: item for item in premise.entities}
        query_entities = {item.id: item for item in query.entities}
        entity_pairs = []
        for premise_id, query_id in zip(observed.arguments, future.arguments, strict=True):
            premise_entity = premise_entities.get(premise_id)
            query_entity = query_entities.get(query_id)
            if premise_entity is None or query_entity is None:
                return None
            if (premise_entity.type, premise_entity.label) != (query_entity.type, query_entity.label):
                return None
            entity_pairs.append((premise_entity, query_entity))

        evidence = [
            EvidenceReference("observed_proposition", EvidenceSide.PREMISE,
                              EvidenceObjectKind.PROPOSITION, observed.id),
        ]
        evidence.extend(
            EvidenceReference("observed_entity", EvidenceSide.PREMISE,
                              EvidenceObjectKind.ENTITY, item.id)
            for item, _ in entity_pairs
        )
        evidence.append(EvidenceReference(
            "recurrence_temporal", EvidenceSide.PREMISE,
            EvidenceObjectKind.TEMPORAL_RELATION, observed_time.id,
        ))
        evidence.append(EvidenceReference(
            "future_proposition", EvidenceSide.QUERY,
            EvidenceObjectKind.PROPOSITION, future.id,
        ))
        evidence.extend(
            EvidenceReference("future_entity", EvidenceSide.QUERY,
                              EvidenceObjectKind.ENTITY, item.id)
            for _, item in entity_pairs
        )
        evidence.extend((
            EvidenceReference("future_temporal", EvidenceSide.QUERY,
                              EvidenceObjectKind.TEMPORAL_RELATION, future_time.id),
            EvidenceReference("deterministic_gate", EvidenceSide.DETERMINISTIC_RESULT,
                              EvidenceObjectKind.INFERENCE, deterministic_result.id),
        ))
        labels = ",".join(item.label for item, _ in entity_pairs)
        return InterpretationResult(
            id="interpretation_001",
            interpretation_status=InterpretationStatus.PROBABLE,
            confidence=Confidence(
                1.0,
                "Exact applicability of deterministic recurrence policy; not event probability",
            ),
            provenance=InterpretationProvenance.PHASE3_DETERMINISTIC_POLICY,
            deterministic_result=deterministic_result,
            policy_id=self.policy_id,
            evidence=tuple(evidence),
            explanation_inputs=(
                ("predicate", observed.predicate),
                ("entities", labels),
                ("recurrence_count", match.group(1)),
                ("source_frame", observed_time.temporal_reference),
                ("query_frame", future_time.temporal_reference),
            ),
        )

    @staticmethod
    def _has_safe_shape(analysis: Analysis) -> bool:
        return not (
            analysis.quantifiers or analysis.modality or analysis.negation
            or analysis.numeric_constraints or analysis.conditions
            or analysis.ambiguities or analysis.sets
            or analysis.relations
        )
