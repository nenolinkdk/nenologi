"""Run consolidated deterministic Nenologi comparison examples."""

import sys

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    analyzer = ControlledEnglishAnalyzer()
    comparator = DeterministicComparator()
    examples = (
        (
            "quantifier + modality + conjunction",
            "All patients must receive treatment A and treatment B.",
            "Some patients may receive treatment A or treatment B.",
        ),
        (
            "numeric threshold inside condition",
            "If the temperature is above 30°C, the system must stop.",
            "If the temperature is at least 30°C, the system must stop.",
        ),
        (
            "temporal relation",
            "Employees must register before Friday.",
            "Employees must register after Friday.",
        ),
    )
    for title, source_text, target_text in examples:
        source = analyzer.analyze(source_text)
        target = analyzer.analyze(target_text)
        result = comparator.compare(source, target)
        print(f"\n{title}")
        print(f"Source formula: {source.logical_representation[0].display}")
        print(f"Target formula: {target.logical_representation[0].display}")
        print(f"Logical relation: {result.logical_relation.value}")
        for finding in result.differences:
            print(
                f"- {finding.difference_type.value}: "
                f"{finding.source_value} -> {finding.target_value} "
                f"[{finding.severity.value}; confidence={finding.confidence.value:.1f}]"
            )
            print(f"  {finding.explanation}")
