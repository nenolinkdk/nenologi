"""Demonstrate semantically transparent controlled contraction expansion."""

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator, DeterministicPropositionAligner

analyzer = ControlledEnglishAnalyzer()
expanded = analyzer.analyze("The valve is not open.")
contracted = analyzer.analyze("The valve isn't open.")
alignment = DeterministicPropositionAligner().align(expanded, contracted)
comparison = DeterministicComparator().compare(expanded, contracted)

print("Expanded proposition:", expanded.propositions[0])
print("Contracted proposition:", contracted.propositions[0])
print("Expanded negation:", expanded.negation[0])
print("Contracted negation:", contracted.negation[0])
print("Alignment:", alignment.alignments)
print("Differences:", comparison.differences)
print("Logical relation:", comparison.logical_relation.value)
