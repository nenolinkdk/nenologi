"""Runnable controlled simple-past transitive comparison."""

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator

analyzer = ControlledEnglishAnalyzer()
source = analyzer.analyze("The company acquired the firm.")
target = analyzer.analyze("The company acquired the subsidiary.")
comparison = DeterministicComparator().compare(source, target)

print("Source proposition:", source.propositions[0])
print("Target proposition:", target.propositions[0])
print("Canonical predicate:", source.propositions[0].predicate)
print("Source entities:", [(item.type, item.label) for item in source.entities])
print("Target entities:", [(item.type, item.label) for item in target.entities])
print("Differences:", [item.difference_type.value for item in comparison.differences])
