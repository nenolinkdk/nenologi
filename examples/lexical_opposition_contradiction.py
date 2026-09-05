"""Show exact, lexical-opposition, and not-established inference results."""

from nenologi import ControlledEnglishAnalyzer, DeterministicInferenceEngine

analyzer = ControlledEnglishAnalyzer()
engine = DeterministicInferenceEngine()
premise = analyzer.analyze("The switch is off.")

print("PREMISE PROPOSITIONS:")
for proposition in premise.propositions:
    print(proposition)

for query_text in ("The switch is off.", "The switch is on.", "The switch is ready."):
    query = analyzer.analyze(query_text)
    result = engine.infer(premise, query)
    print("\nQUERY:", query_text)
    print("NORMALIZED QUERY:", query.propositions)
    print("STATUS:", result.interpretation_status.value)
    print("RULE:", result.rule)
    print("EVIDENCE:", result.derived_from)
    print("EXPLANATION:", engine.explain(result))
