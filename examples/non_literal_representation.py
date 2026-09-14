"""Represent one controlled metaphor without asserting a literal meaning."""

from nenologi import ControlledEnglishAnalyzer, DeterministicInferenceEngine

source_text = "Time is a thief."
query_text = "Time commits theft."

analyzer = ControlledEnglishAnalyzer()
engine = DeterministicInferenceEngine()
source = analyzer.analyze(source_text)
query = analyzer.analyze(query_text)
result = engine.infer(source, query)

print("SOURCE:", source_text)
print("QUERY:", query_text)
print("SAFE ENTITY:", source.entities[0])
print("NON-LITERAL MARKER:", source.relations[0])
print("AUTHORITATIVE LITERAL PROPOSITIONS:", source.propositions)
print("SAFE DISPLAY:", source.logical_representation[0].display)
print("QUERY PROPOSITION:", query.propositions[0])
print("STATUS:", result.interpretation_status.value)
print("RULE:", result.rule)
print("EXPLANATION: deterministic core does not guess figurative meaning")

explicit = engine.infer(query, analyzer.analyze(query_text))
print("ORDINARY LITERAL CONTRAST:", explicit.interpretation_status.value)
