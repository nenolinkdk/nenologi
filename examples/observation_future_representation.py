"""Represent a repeated observation and a distinct future claim."""

from nenologi import ControlledEnglishAnalyzer, DeterministicInferenceEngine

source_text = "The light flickered on each of the last five evenings."
query_text = "The light will flicker this evening."

analyzer = ControlledEnglishAnalyzer()
engine = DeterministicInferenceEngine()
source = analyzer.analyze(source_text)
query = analyzer.analyze(query_text)
result = engine.infer(source, query)

print("SOURCE:", source_text)
print("SOURCE PROPOSITION:", source.propositions[0])
print("SOURCE TEMPORAL STRUCTURE:", source.temporal_relations[0])
print("QUERY:", query_text)
print("QUERY PROPOSITION:", query.propositions[0])
print("QUERY TEMPORAL STRUCTURE:", query.temporal_relations[0])
print("TEMPORAL REFERENCES DIFFER:", source.temporal_relations != query.temporal_relations)
print("STATUS:", result.interpretation_status.value)
print("RULE:", result.rule)
print("EXPLANATION:", engine.explain(result))
print("PREDICTION: not implemented; repeated observations do not establish future events")

explicit = engine.infer(query, analyzer.analyze(query_text))
print("IDENTICAL FUTURE CONTROL:", explicit.interpretation_status.value)
