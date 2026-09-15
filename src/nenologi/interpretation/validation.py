"""Reference validation for Phase 3 evidence."""

from ..models import Analysis, DomainValidationError
from .models import EvidenceObjectKind, EvidenceSide, InterpretationResult


def validate_interpretation_evidence(
    result: InterpretationResult,
    premise: Analysis,
    query: Analysis,
) -> None:
    by_side = {
        EvidenceSide.PREMISE: premise,
        EvidenceSide.QUERY: query,
    }
    for item in result.evidence:
        if item.analysis_side is EvidenceSide.DETERMINISTIC_RESULT:
            if not (
                item.object_kind is EvidenceObjectKind.INFERENCE
                and item.object_id == result.deterministic_result.id
            ):
                raise DomainValidationError("deterministic evidence must reference the underlying inference")
            continue
        analysis = by_side[item.analysis_side]
        collections = {
            EvidenceObjectKind.ENTITY: analysis.entities,
            EvidenceObjectKind.PROPOSITION: analysis.propositions,
            EvidenceObjectKind.OPERATOR: (*analysis.quantifiers, *analysis.modality, *analysis.negation),
            EvidenceObjectKind.TEMPORAL_RELATION: analysis.temporal_relations,
            EvidenceObjectKind.SEMANTIC_ITEM: analysis.relations,
            EvidenceObjectKind.AMBIGUITY: analysis.ambiguities,
            EvidenceObjectKind.ALTERNATIVE: analysis.sets,
        }
        if item.object_kind is EvidenceObjectKind.INFERENCE:
            raise DomainValidationError("analysis evidence cannot use inference kind")
        if not any(candidate.id == item.object_id for candidate in collections[item.object_kind]):
            raise DomainValidationError(
                f"unresolved {item.analysis_side.value} evidence reference: {item.object_id}"
            )

