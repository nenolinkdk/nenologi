"""Demonstrate controlled nested temporal-reference comparison."""

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator, analysis_from_json, analysis_to_json

analyzer = ControlledEnglishAnalyzer()
source = analyzer.analyze("Wait until noon.")
target = analyzer.analyze("Wait until after noon.")
comparison = DeterministicComparator().compare(source, target)

print("SOURCE PROPOSITIONS:", source.propositions)
print("TARGET PROPOSITIONS:", target.propositions)
print("SOURCE REFERENCES:", source.relations)
print("TARGET REFERENCES:", target.relations)
print("SOURCE TEMPORAL:", source.temporal_relations)
print("TARGET TEMPORAL:", target.temporal_relations)
print("SOURCE FORMULA:", source.logical_representation[0].display)
print("TARGET FORMULA:", target.logical_representation[0].display)
print("FINDING:", comparison.differences)
print("LOGICAL RELATION:", comparison.logical_relation.value)
print("JSON ROUND TRIP:", analysis_from_json(analysis_to_json(target)) == target)
