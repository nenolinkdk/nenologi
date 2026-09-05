"""Recognize a candidate that is already explicit in normalized analysis."""

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicInferenceEngine, analysis_to_json,
)

analyzer = ControlledEnglishAnalyzer()
engine = DeterministicInferenceEngine()

input_text = "The door is open."
premise = analyzer.analyze(input_text)

print("INPUT:", input_text)
print("NORMALIZED ANALYSIS:")
print(analysis_to_json(premise))

for query_text in ("The door is open.", "The door is closed."):
    conclusion = analyzer.analyze(query_text)
    result = engine.infer(premise, conclusion)
    print("\nQUERY:", query_text)
    print("RESULT:", result.interpretation_status.value)
    print("RULE:", result.rule)
    print("EVIDENCE:", result.derived_from)
    print("EXPLANATION:", engine.explain(result))
