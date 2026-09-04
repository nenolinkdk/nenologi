"""Run the first complete deterministic Nenologi comparison pipeline."""

import sys

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    analyzer = ControlledEnglishAnalyzer()
    comparator = DeterministicComparator()
    source = analyzer.analyze("Employees must register before Friday.")
    target = analyzer.analyze("Employees must register after Friday.")
    result = comparator.compare(source, target)

    for label, analysis in (("Source", source), ("Target", target)):
        temporal = analysis.temporal_relations[0]
        print(
            f"{label} temporal: relation={temporal.relation.value}, "
            f"reference={temporal.temporal_reference}, proposition={temporal.proposition}"
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
