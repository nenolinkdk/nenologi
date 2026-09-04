"""Conservative, deterministic proposition alignment over normalized analyses."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..models import Analysis, Confidence, Proposition
from ..models.common import DomainValidationError, validate_identifier
from ..serialization.validation import validate_analysis


class AlignmentStatus(StrEnum):
    EXACT = "EXACT"
    STRUCTURAL = "STRUCTURAL"


@dataclass(frozen=True, slots=True)
class PropositionAlignment:
    source_proposition_id: str
    target_proposition_id: str
    status: AlignmentStatus
    confidence: Confidence
    rule_id: str

    def __post_init__(self) -> None:
        validate_identifier(self.source_proposition_id, "source proposition")
        validate_identifier(self.target_proposition_id, "target proposition")
        if not isinstance(self.status, AlignmentStatus):
            raise DomainValidationError("alignment status must be an AlignmentStatus")
        if not isinstance(self.confidence, Confidence) or self.confidence.value != 1.0:
            raise DomainValidationError("deterministic alignment confidence must be 1.0")
        if not self.rule_id:
            raise DomainValidationError("alignment rule_id must be non-empty")


@dataclass(frozen=True, slots=True)
class AlignmentResult:
    alignments: tuple[PropositionAlignment, ...]
    unaligned_source_ids: tuple[str, ...]
    unaligned_target_ids: tuple[str, ...]


def _role(analysis: Analysis, proposition_id: str) -> str:
    for condition in analysis.conditions:
        if proposition_id in condition.antecedent:
            return "ANTECEDENT"
        if proposition_id in condition.consequent:
            return "ASSERTED"
    return "ASSERTED"


def _core(analysis: Analysis, proposition: Proposition) -> tuple[str, tuple[tuple[str, str], ...]]:
    entities = {item.id: item for item in analysis.entities}
    try:
        arguments = tuple((entities[ref].type, entities[ref].label.casefold()) for ref in proposition.arguments)
    except KeyError as exc:
        raise DomainValidationError(f"proposition {proposition.id} has a non-entity core argument") from exc
    return proposition.predicate, arguments


def proposition_signature(analysis: Analysis, proposition: Proposition) -> tuple[object, ...]:
    """Return role, predicate, and typed normalized core arguments only."""
    predicate, arguments = _core(analysis, proposition)
    return _role(analysis, proposition.id), predicate, arguments


def _structural_counterpart(source: Analysis, target: Analysis, left: Proposition, right: Proposition) -> bool:
    if _role(source, left.id) != _role(target, right.id):
        return False
    left_predicate, left_arguments = _core(source, left)
    right_predicate, right_arguments = _core(target, right)
    if len(left_arguments) != len(right_arguments):
        return False
    if tuple(item[0] for item in left_arguments) != tuple(item[0] for item in right_arguments):
        return False
    changes = int(left_predicate != right_predicate) + sum(
        left_item[1] != right_item[1] for left_item, right_item in zip(left_arguments, right_arguments)
    )
    return changes == 1


class DeterministicPropositionAligner:
    """Produce unique one-to-one alignments without fuzzy evidence."""

    def align(self, source: Analysis, target: Analysis, *, allow_structural_counterparts: bool = False) -> AlignmentResult:
        validate_analysis(source)
        validate_analysis(target)
        unmatched_source = {item.id: item for item in source.propositions}
        unmatched_target = {item.id: item for item in target.propositions}
        alignments: list[PropositionAlignment] = []

        def apply(rule_id: str, status: AlignmentStatus, predicate) -> None:
            candidates = {
                source_id: tuple(sorted(target_id for target_id, right in unmatched_target.items() if predicate(left, right)))
                for source_id, left in unmatched_source.items()
            }
            reverse_counts = {
                target_id: sum(target_id in values for values in candidates.values())
                for target_id in unmatched_target
            }
            pairs = sorted(
                (source_id, values[0]) for source_id, values in candidates.items()
                if len(values) == 1 and reverse_counts[values[0]] == 1
            )
            for source_id, target_id in pairs:
                alignments.append(PropositionAlignment(
                    source_id, target_id, status,
                    Confidence(1.0, "Unique deterministic normalized-structure match"), rule_id,
                ))
            for source_id, target_id in pairs:
                unmatched_source.pop(source_id)
                unmatched_target.pop(target_id)

        apply(
            "EXACT_NORMALIZED_SIGNATURE", AlignmentStatus.EXACT,
            lambda left, right: proposition_signature(source, left) == proposition_signature(target, right),
        )
        if allow_structural_counterparts:
            apply(
                "SINGLE_CORE_POSITION_CHANGE", AlignmentStatus.STRUCTURAL,
                lambda left, right: _structural_counterpart(source, target, left, right),
            )
        return AlignmentResult(
            tuple(alignments), tuple(sorted(unmatched_source)), tuple(sorted(unmatched_target)),
        )
