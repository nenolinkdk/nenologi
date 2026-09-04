"""Run the first complete deterministic Nenologi comparison pipeline."""

import sys

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    analyzer = ControlledEnglishAnalyzer()
    comparator = DeterministicComparator()
    source = analyzer.analyze("If the temperature is above 30°C, the system must stop.")
    target = analyzer.analyze("The system must stop.")
    result = comparator.compare(source, target)

    condition = source.conditions[0]
    propositions = {item.id: item for item in source.propositions}
    constraint = source.numeric_constraints[0]
    print(f"Condition: {condition.id}")
    print(f"Antecedent: {propositions[condition.antecedent[0]]}")
    print(f"Antecedent constraint: {constraint.operator.value} {constraint.value} {constraint.unit}")
    print(f"Consequent: {propositions[condition.consequent[0]]}")
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
