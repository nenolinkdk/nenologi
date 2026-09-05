"""Demonstrate controlled binary spatial relations and comparison."""

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator, DeterministicPropositionAligner

analyzer = ControlledEnglishAnalyzer()
source = analyzer.analyze("The key is inside the box.")
target = analyzer.analyze("The key is beside the box.")
alignment = DeterministicPropositionAligner().align(source, target, allow_structural_counterparts=True)
comparison = DeterministicComparator().compare(source, target)

print("Source entities:", [(item.type, item.label) for item in source.entities])
print("Target entities:", [(item.type, item.label) for item in target.entities])
print("Source predicate:", source.propositions[0].predicate)
print("Target predicate:", target.propositions[0].predicate)
print("Source proposition:", source.propositions[0])
print("Target proposition:", target.propositions[0])
print("Alignment:", alignment.alignments)
print("Findings:", comparison.differences)
print("Logical relation:", comparison.logical_relation.value)
