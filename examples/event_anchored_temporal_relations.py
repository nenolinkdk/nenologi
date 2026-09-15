"""Demonstrate controlled proposition-anchored temporal comparison."""

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator, analysis_from_json, analysis_to_json

analyzer = ControlledEnglishAnalyzer()
source = analyzer.analyze("Inspect the cable before starting the machine.")
target = analyzer.analyze("Inspect the cable after starting the machine.")
comparison = DeterministicComparator().compare(source, target)

print("SOURCE PROPOSITIONS:", source.propositions)
print("TARGET PROPOSITIONS:", target.propositions)
print("SOURCE TEMPORAL:", source.temporal_relations[0])
print("TARGET TEMPORAL:", target.temporal_relations[0])
print("SOURCE FORMULA:", source.logical_representation[0].display)
print("TARGET FORMULA:", target.logical_representation[0].display)
print("FINDING:", comparison.differences)
print("LOGICAL RELATION:", comparison.logical_relation.value)
print("JSON ROUND TRIP:", analysis_from_json(analysis_to_json(source)) == source)
