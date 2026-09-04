"""Runnable Scope v0.1 controlled contrast."""

import sys

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator

sys.stdout.reconfigure(encoding="utf-8")
analyzer = ControlledEnglishAnalyzer()
source = analyzer.analyze("Not all employees must register.")
target = analyzer.analyze("All employees must not register.")
comparison = DeterministicComparator().compare(source, target)

print("Source scope:", [(item.operator, item.scope) for item in (*source.negation, *source.quantifiers, *source.modality)])
print("Target scope:", [(item.operator, item.scope) for item in (*target.quantifiers, *target.modality, *target.negation)])
print("Source formula:", source.logical_representation[0].display)
print("Target formula:", target.logical_representation[0].display)
print("Difference:", comparison.differences[0].difference_type.value)
print("Explanation:", comparison.differences[0].explanation)
print("Logical relation:", comparison.logical_relation.value)
