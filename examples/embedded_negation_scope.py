"""Inspect one controlled embedded-negation scope contrast."""

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator,
    analysis_from_json, analysis_to_json,
)

source_text = "Maria did not promise to leave."
target_text = "Maria promised not to leave."
analyzer = ControlledEnglishAnalyzer()
comparator = DeterministicComparator()
source = analyzer.analyze(source_text)
target = analyzer.analyze(target_text)
result = comparator.compare(source, target)

for label, analysis in (("SOURCE", source), ("TARGET", target)):
    print(label, analysis.propositions[0])
    print("  OPERATORS:", (*analysis.modality, *analysis.negation))
    print("  FORMULA:", analysis.logical_representation[0].display)

print("FINDING:", result.differences)
print("LOGICAL RELATION:", result.logical_relation.value)
print("JSON ROUND TRIP:", analysis_from_json(analysis_to_json(source)) == source)
