"""Inspect the controlled UNLESS gold case and its normalized comparison."""

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator,
    analysis_from_json, analysis_to_json,
)

source_text = "You may enter unless the door is locked."
target_text = "You may enter if the door is locked."
analyzer = ControlledEnglishAnalyzer()
source = analyzer.analyze(source_text)
target = analyzer.analyze(target_text)
result = DeterministicComparator().compare(source, target)

print("ANTECEDENT:", source.propositions[0])
print("ANTECEDENT NEGATION:", source.negation[0])
print("CONSEQUENT:", source.propositions[1])
print("CONDITION:", source.conditions[0])
print("FORMULA:", source.logical_representation[0].display)
print("FINDING:", result.differences)
print("LOGICAL RELATION:", result.logical_relation.value)
print("JSON ROUND TRIP:", analysis_from_json(analysis_to_json(source)) == source)
