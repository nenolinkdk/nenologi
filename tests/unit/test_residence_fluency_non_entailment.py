import unittest
from dataclasses import replace

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine,
    InterpretationStatus, NOT_ESTABLISHED_RULE, UnsupportedConstructionError,
    analysis_from_json, analysis_to_json, validate_analysis,
)


class ResidenceFluencyNonEntailmentV01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.engine = DeterministicInferenceEngine()

    def infer(self, source: str, query: str):
        return self.engine.infer(
            self.analyzer.analyze(source), self.analyzer.analyze(query),
        )

    def assert_not_established(self, source: str, query: str) -> None:
        result = self.infer(source, query)
        self.assertEqual(result.interpretation_status, InterpretationStatus.UNSUPPORTED)
        self.assertEqual(result.rule, NOT_ESTABLISHED_RULE)
        self.assertEqual(result.derived_from, ())

    def test_entailment_004_is_exactly_unsupported(self) -> None:
        self.assert_not_established(
            "Peter lived in Paris for five years.",
            "Peter speaks fluent French.",
        )

    def test_residence_has_ordered_binary_arguments_and_structured_duration(self) -> None:
        analysis = self.analyzer.analyze("Peter lived in Paris for five years.")
        self.assertEqual(
            [(entity.id, entity.type, entity.label) for entity in analysis.entities],
            [
                ("entity_001", "INDIVIDUAL", "peter"),
                ("entity_002", "LOCATION", "paris"),
                ("entity_003", "DURATION", "5_year"),
            ],
        )
        self.assertEqual(analysis.propositions[0].predicate, "LIVES_IN")
        self.assertEqual(analysis.propositions[0].arguments, ("entity_001", "entity_002"))
        self.assertEqual(analysis.relations[1].type, "DURATION")
        self.assertEqual(analysis.relations[1].arguments, ("prop_001", "entity_003"))

    def test_language_propositions_are_distinct_and_deterministic(self) -> None:
        plain = self.analyzer.analyze("Peter speaks French.")
        fluent = self.analyzer.analyze("Peter speaks fluent French.")
        self.assertEqual(plain.propositions[0].predicate, "SPEAKS")
        self.assertEqual(fluent.propositions[0].predicate, "SPEAKS_FLUENTLY")
        self.assertEqual(fluent.propositions[0].arguments, ("entity_001", "entity_002"))
        self.assertEqual(fluent.entities[1].type, "LANGUAGE")
        self.assertEqual(fluent, self.analyzer.analyze("Peter speaks fluent French."))

    def test_no_place_language_or_nationality_world_knowledge_is_added(self) -> None:
        for source, query in (
            ("Alice lives in France.", "Alice speaks French."),
            ("Alice lived in Paris for five years.", "Alice speaks fluent French."),
            ("Alice lives in France.", "Bob speaks French."),
        ):
            with self.subTest(source=source, query=query):
                self.assert_not_established(source, query)

    def test_no_converse_or_argument_reversal_is_inferred(self) -> None:
        self.assert_not_established("Alice speaks French.", "Alice lives in France.")
        source = self.analyzer.analyze("Alice lives in France.")
        query = self.analyzer.analyze("Alice lives in France.")
        reversed_query = replace(
            query,
            propositions=(replace(query.propositions[0], arguments=("entity_002", "entity_001")),),
            logical_representation=(),
        )
        self.assertEqual(
            self.engine.infer(source, reversed_query).interpretation_status,
            InterpretationStatus.UNSUPPORTED,
        )

    def test_exact_language_and_residence_propositions_remain_explicit(self) -> None:
        for text in ("Alice speaks French.", "Alice speaks fluent French.", "Alice lives in France."):
            with self.subTest(text=text):
                self.assertEqual(
                    self.infer(text, text).interpretation_status,
                    InterpretationStatus.EXPLICIT,
                )

    def test_serialization_round_trip_preserves_ids_and_references(self) -> None:
        analysis = self.analyzer.analyze("Peter lived in Paris for 5 years.")
        validate_analysis(analysis)
        self.assertEqual(analysis_from_json(analysis_to_json(analysis)), analysis)

    def test_existing_inference_rules_are_unchanged(self) -> None:
        universal = self.infer(
            "All marked boxes are inspected. Box A is marked.",
            "Box A is inspected.",
        )
        opposition = self.infer("The switch is off.", "The switch is on.")
        self.assertEqual(universal.interpretation_status, InterpretationStatus.ENTAILED)
        self.assertEqual(universal.rule, "UNIVERSAL_INSTANTIATION")
        self.assertEqual(opposition.interpretation_status, InterpretationStatus.CONTRADICTED)
        self.assertEqual(opposition.rule, "LEXICAL_OPPOSITION")

    def test_comparator_regression_and_place_change(self) -> None:
        left = self.analyzer.analyze("Alice lives in France.")
        self.assertEqual(DeterministicComparator().compare(left, left).differences, ())
        changed = DeterministicComparator().compare(
            left, self.analyzer.analyze("Alice lives in Denmark."),
        )
        self.assertTrue(changed.differences)

    def test_broader_residence_and_language_syntax_is_rejected(self) -> None:
        unsupported = (
            "Peter resided in Paris.",
            "Peter lived near Paris.",
            "Peter lived in the city of Paris.",
            "Peter speaks very fluent French.",
            "Peter can speak French.",
            "Peter speaks French and Danish.",
        )
        for text in unsupported:
            with self.subTest(text=text):
                with self.assertRaises(UnsupportedConstructionError):
                    self.analyzer.analyze(text)


if __name__ == "__main__":
    unittest.main()
