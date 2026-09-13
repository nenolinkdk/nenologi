"""Show why controlled residence does not establish language fluency."""

from nenologi import ControlledEnglishAnalyzer, DeterministicInferenceEngine

source_text = "Peter lived in Paris for five years."
query_text = "Peter speaks fluent French."

analyzer = ControlledEnglishAnalyzer()
engine = DeterministicInferenceEngine()
source = analyzer.analyze(source_text)
query = analyzer.analyze(query_text)
result = engine.infer(source, query)

print("SOURCE:", source_text)
print("SOURCE ENTITIES:", source.entities)
print("SOURCE PROPOSITION:", source.propositions[0])
print("SOURCE DURATION:", source.relations[1])
print("QUERY:", query_text)
print("QUERY PROPOSITION:", query.propositions[0])
print("STATUS:", result.interpretation_status.value)
print("RULE:", result.rule)
print("EXPLANATION:", engine.explain(result))
print("NO WORLD KNOWLEDGE: residence and language fluency remain distinct predicates")

explicit = engine.infer(
    analyzer.analyze("Alice speaks French."),
    analyzer.analyze("Alice speaks French."),
)
print("EXACT CONTROL STATUS:", explicit.interpretation_status.value)
