"""Parser-neutral analyzer contract."""

from typing import Protocol

from ..models import Analysis


class UnsupportedConstructionError(ValueError):
    """Input falls outside an analyzer's declared grammar."""


class Analyzer(Protocol):
    """Common interface implemented by replaceable analysis strategies."""

    def analyze(self, text: str, *, language: str = "en", profile: str = "general") -> Analysis:
        """Analyze text or explicitly reject an unsupported construction."""
        ...
