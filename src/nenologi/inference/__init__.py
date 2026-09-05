from .deterministic import (
    EXACT_EXPLICIT_RULE, LEXICAL_OPPOSITION_PAIRS, LEXICAL_OPPOSITION_RULE,
    NOT_ESTABLISHED_RULE, DeterministicInferenceEngine, are_lexical_opposites,
)
from .interface import InferenceEngine

__all__ = [
    "DeterministicInferenceEngine", "EXACT_EXPLICIT_RULE", "InferenceEngine",
    "LEXICAL_OPPOSITION_PAIRS", "LEXICAL_OPPOSITION_RULE", "NOT_ESTABLISHED_RULE",
    "are_lexical_opposites",
]
