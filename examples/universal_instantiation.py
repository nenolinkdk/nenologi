"""Derive one unary conclusion from a normalized universal rule and facts."""

from nenologi import ControlledEnglishAnalyzer, DeterministicInferenceEngine

source_text = "All marked boxes are inspected. Box A is marked."
query_text = "Box A is inspected."

analyzer = ControlledEnglishAnalyzer()
engine = DeterministicInferenceEngine()
source = analyzer.analyze(source_text)
query = analyzer.analyze(query_text)
result = engine.infer(source, query)

print("SOURCE:", source_text)
print("RULE:", source.conditions[0])
print("QUANTIFIER:", source.quantifiers[0])
print("FACTS:", [item for item in source.propositions if item.id.startswith("membership_")])
print("QUERY:", query_text)
print("STATUS:", result.interpretation_status.value)
print("INFERENCE RULE:", result.rule)
print("EVIDENCE:", result.derived_from)
print("SUBSTITUTION:", result.confidence.rationale)
print("EXPLANATION:", engine.explain(result))
