"""Demonstrate controlled active/passive semantic normalization."""

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator, DeterministicPropositionAligner

analyzer = ControlledEnglishAnalyzer()
active = analyzer.analyze("The company acquired the firm.")
passive = analyzer.analyze("The firm was acquired by the company.")
alignment = DeterministicPropositionAligner().align(active, passive)
comparison = DeterministicComparator().compare(active, passive)

print("Normalized active proposition:", active.propositions[0])
print("Normalized passive proposition:", passive.propositions[0])
print("Canonical predicate:", passive.propositions[0].predicate)
print("Active semantic arguments:", [(item.type, item.label) for item in active.entities])
print("Passive semantic arguments:", [(item.type, item.label) for item in passive.entities])
print("Alignment:", alignment.alignments)
print("Differences:", comparison.differences)
print("Logical relation:", comparison.logical_relation.value)
