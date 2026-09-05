"""Show rule/membership representation before universal instantiation exists."""

from nenologi import ControlledEnglishAnalyzer, DeterministicInferenceEngine

text = "All doctors are professionals. Alice is a doctor."
query_text = "Alice is a professional."

analyzer = ControlledEnglishAnalyzer()
analysis = analyzer.analyze(text)
query = analyzer.analyze(query_text)
result = DeterministicInferenceEngine().infer(analysis, query)

print("INPUT:", text)
print("CLASSES:", sorted({item.predicate for item in analysis.propositions}))
print("MEMBERSHIP FACTS:", [
    item for item in analysis.propositions if item.id.startswith("membership_")
])
print("UNIVERSAL RULE:", analysis.conditions[0])
print("DERIVED FORMULA:", analysis.logical_representation[0].display)
print("QUERY:", query_text)
print("CURRENT STATUS:", result.interpretation_status.value)
print("CURRENT RULE:", result.rule)
print("UNIVERSAL INSTANTIATION IMPLEMENTED: no")
