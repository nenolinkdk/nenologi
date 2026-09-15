"""Phase 3 orchestration with frozen Phase 2 precedence."""

from __future__ import annotations

from ..inference import (
    EXACT_EXPLICIT_RULE, LEXICAL_OPPOSITION_RULE, NOT_ESTABLISHED_RULE,
    UNIVERSAL_INSTANTIATION_RULE, DeterministicInferenceEngine,
)
from ..models import Analysis, Confidence, DomainValidationError, InterpretationStatus
from .interface import InterpretationPolicy
from .models import InterpretationProvenance, InterpretationResult
from .recurrence import DefeasibleRecurrencePredictionPolicy
from .validation import validate_interpretation_evidence

DEFAULT_POLICIES: tuple[InterpretationPolicy, ...] = (
    DefeasibleRecurrencePredictionPolicy(),
)

_DETERMINISTIC_PROVENANCE = {
    EXACT_EXPLICIT_RULE: InterpretationProvenance.EXACT_EXPLICIT,
    LEXICAL_OPPOSITION_RULE: InterpretationProvenance.LEXICAL_OPPOSITION,
    UNIVERSAL_INSTANTIATION_RULE: InterpretationProvenance.UNIVERSAL_INSTANTIATION,
    NOT_ESTABLISHED_RULE: InterpretationProvenance.NOT_ESTABLISHED,
}


class Phase3InterpretationEngine:
    """Apply registered policies only after the conservative Phase 2 fallback."""

    def __init__(
        self,
        policies: tuple[InterpretationPolicy, ...] = DEFAULT_POLICIES,
        deterministic_engine: DeterministicInferenceEngine | None = None,
    ) -> None:
        ids = tuple(policy.policy_id for policy in policies)
        if len(set(ids)) != len(ids):
            raise DomainValidationError("Phase 3 policy IDs must be unique")
        self._policies = policies
        self._deterministic_engine = deterministic_engine or DeterministicInferenceEngine()

    @property
    def policy_ids(self) -> tuple[str, ...]:
        return tuple(policy.policy_id for policy in self._policies)

    def evaluate(self, premise: Analysis, query: Analysis) -> InterpretationResult:
        deterministic = self._deterministic_engine.infer(premise, query)
        provenance = _DETERMINISTIC_PROVENANCE.get(deterministic.rule)
        if provenance is None:
            raise DomainValidationError(
                f"unregistered deterministic inference rule: {deterministic.rule!r}"
            )
        if not (
            deterministic.interpretation_status is InterpretationStatus.UNSUPPORTED
            and deterministic.rule == NOT_ESTABLISHED_RULE
        ):
            return InterpretationResult(
                id="interpretation_001",
                interpretation_status=deterministic.interpretation_status,
                confidence=deterministic.confidence,
                provenance=provenance,
                deterministic_result=deterministic,
            )

        matches = tuple(
            result for policy in self._policies
            if (result := policy.evaluate(premise, query, deterministic)) is not None
        )
        if len(matches) > 1:
            raise DomainValidationError("multiple Phase 3 policies matched one interpretation")
        if matches:
            validate_interpretation_evidence(matches[0], premise, query)
            return matches[0]
        return InterpretationResult(
            id="interpretation_001",
            interpretation_status=deterministic.interpretation_status,
            confidence=Confidence(1.0, "No registered Phase 3 policy applied"),
            provenance=InterpretationProvenance.NOT_ESTABLISHED,
            deterministic_result=deterministic,
        )

    def explain(self, result: InterpretationResult) -> str:
        if result.policy_id == DefeasibleRecurrencePredictionPolicy.policy_id:
            values = dict(result.explanation_inputs)
            count = values["recurrence_count"]
            return (
                f"The same {values['predicate'].lower()} event for {values['entities']} was "
                f"observed on each of the last {count} evenings. This supports recurrence "
                "this evening as probable, but does not logically entail the future event."
            )
        return self._deterministic_engine.explain(result.deterministic_result)
