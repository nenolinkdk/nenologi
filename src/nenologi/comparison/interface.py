"""Parser-neutral comparison contract."""

from typing import Protocol

from ..models import Analysis, Comparison, ComparisonMode


class UnsupportedComparisonError(ValueError):
    """Normalized analyses cannot be aligned or compared by this strategy."""


class Comparator(Protocol):
    def compare(
        self,
        source: Analysis,
        target: Analysis,
        *,
        mode: ComparisonMode = ComparisonMode.VERSION_COMPARISON,
    ) -> Comparison:
        """Compare normalized analyses without consulting their source strings."""
        ...
