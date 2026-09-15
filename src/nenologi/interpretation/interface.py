"""Parser-independent Phase 3 policy interface."""

from typing import Protocol

from ..models import Analysis, Inference
from .models import InterpretationResult


class InterpretationPolicy(Protocol):
    policy_id: str

    def evaluate(
        self,
        premise: Analysis,
        query: Analysis,
        deterministic_result: Inference,
    ) -> InterpretationResult | None:
        """Return an interpretation result when the policy applies, else no match."""
        ...

