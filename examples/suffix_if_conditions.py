"""Demonstrate equivalent prefix- and suffix-IF normalization."""

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator, DeterministicPropositionAligner

prefix_text = "If the light is green, you may enter."
suffix_text = "You may enter if the light is green."
analyzer = ControlledEnglishAnalyzer()
prefix = analyzer.analyze(prefix_text)
suffix = analyzer.analyze(suffix_text)
alignment = DeterministicPropositionAligner().align(prefix, suffix)
comparison = DeterministicComparator().compare(prefix, suffix)

print("Raw prefix:", prefix_text)
print("Raw suffix:", suffix_text)
print("Prefix antecedent:", prefix.conditions[0].antecedent, prefix.propositions[0])
print("Suffix antecedent:", suffix.conditions[0].antecedent, suffix.propositions[0])
print("Prefix consequent:", prefix.conditions[0].consequent, prefix.propositions[1])
print("Suffix consequent:", suffix.conditions[0].consequent, suffix.propositions[1])
print("Normalized prefix condition:", prefix.conditions[0])
print("Normalized suffix condition:", suffix.conditions[0])
print("Alignment:", alignment.alignments)
print("Findings:", comparison.differences)
print("Logical relation:", comparison.logical_relation.value)
