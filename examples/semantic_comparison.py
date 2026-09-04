"""Run the first complete deterministic Nenologi comparison pipeline."""

import sys

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    analyzer = ControlledEnglishAnalyzer()
    comparator = DeterministicComparator()
    source = analyzer.analyze("All scores must be at least 18.")
    target = analyzer.analyze("Some scores must be more than 21.")
    result = comparator.compare(source, target)

    for label, analysis in (("Source", source), ("Target", target)):
        constraint = analysis.numeric_constraints[0]
        print(
            f"{label} constraint: operator={constraint.operator.value}, "
            f"value={constraint.value}, unit={constraint.unit or 'NONE'}"
        )
    print(f"Source formula: {source.logical_representation[0].display}")
    print(f"Target formula: {target.logical_representation[0].display}")
    print("Differences:")
    for finding in result.differences:
        print(
            f"- {finding.difference_type.value}: "
            f"{finding.source_value} -> {finding.target_value} "
            f"[{finding.severity.value}; confidence={finding.confidence.value:.1f}]"
        )
        print(f"  {finding.explanation}")
