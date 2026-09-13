"""Show unresolved coreference alternatives without guessing an antecedent."""

from nenologi import ControlledEnglishAnalyzer, DeterministicInferenceEngine

source_text = "Alex told Sam that they had won."
query_text = "Alex had won."

analyzer = ControlledEnglishAnalyzer()
engine = DeterministicInferenceEngine()
source = analyzer.analyze(source_text)
query = analyzer.analyze(query_text)
result = engine.infer(source, query)

print("SOURCE:", source_text)
print("QUERY:", query_text)
print("ENTITIES:", source.entities)
print("REFERRING EXPRESSION:", source.entities[2])
print("CANDIDATE ALTERNATIVES:", source.sets)
print("AMBIGUITY:", source.ambiguities[0])
print("EMBEDDED PROPOSITION:", source.propositions[1])
print("STATUS:", result.interpretation_status.value)
print("RULE:", result.rule)
print("EXPLANATION: no candidate antecedent was guessed")

explicit_source = analyzer.analyze("Alex had won.")
explicit = engine.infer(explicit_source, query)
print("DIRECT EXPLICIT-NAME CONTRAST:", explicit.interpretation_status.value)
