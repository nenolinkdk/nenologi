"""Parser-independent inference contract."""

from typing import Protocol

from ..models import Analysis, Inference


class InferenceEngine(Protocol):
    """Classify a candidate conclusion from normalized analyses."""

    def infer(self, premise: Analysis, conclusion: Analysis) -> Inference:
        """Return a bounded, inspectable inference result."""
        ...

    def explain(self, inference: Inference) -> str:
        """Render a deterministic explanation for an inference result."""
        ...
