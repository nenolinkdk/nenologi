import unittest

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine,
    DifferenceType, InterpretationStatus, NOT_ESTABLISHED_RULE, TemporalRelationType,
    UnsupportedConstructionError, analysis_from_json, analysis_to_json, validate_analysis,
)


class ObservationFutureRepresentationV01Tests(unittest.TestCase):
    source_text = "The light flickered on each of the last five evenings."
    query_text = "The light will flicker this evening."

    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.engine = DeterministicInferenceEngine()

    def infer(self, source: str, query: str):
        return self.engine.infer(
            self.analyzer.analyze(source), self.analyzer.analyze(query),
        )

    def test_entailment_003_source_and_query_are_fully_represented(self) -> None:
        source = self.analyzer.analyze(self.source_text)
        query = self.analyzer.analyze(self.query_text)
        for analysis in (source, query):
            validate_analysis(analysis)
            self.assertEqual(analysis.propositions[0].predicate, "FLICKER")
            self.assertEqual(analysis.propositions[0].arguments, ("entity_001",))
            self.assertEqual(analysis.temporal_relations[0].proposition, "prop_001")
            self.assertIs(analysis.temporal_relations[0].relation, TemporalRelationType.ON)

    def test_relative_temporal_references_are_canonical_and_distinct(self) -> None:
        source = self.analyzer.analyze(self.source_text)
        query = self.analyzer.analyze(self.query_text)
        self.assertEqual(source.temporal_relations[0].temporal_reference, "LAST_5_EVENINGS")
        self.assertEqual(query.temporal_relations[0].temporal_reference, "THIS_EVENING")
        self.assertNotEqual(source.temporal_relations, query.temporal_relations)
        self.assertIn("Last5Evenings", source.logical_representation[0].display)
        self.assertIn("ThisEvening", query.logical_representation[0].display)

    def test_source_observation_does_not_establish_future_query(self) -> None:
        result = self.infer(self.source_text, self.query_text)
        self.assertEqual(result.interpretation_status, InterpretationStatus.UNSUPPORTED)
        self.assertEqual(result.rule, NOT_ESTABLISHED_RULE)
        self.assertEqual(result.derived_from, ())
        self.assertNotEqual(result.interpretation_status, InterpretationStatus.CONTRADICTED)

    def test_identical_future_proposition_is_explicit(self) -> None:
        result = self.infer(self.query_text, self.query_text)
        self.assertEqual(result.interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertEqual(result.rule, "EXACT_EXPLICIT")

    def test_parsing_ids_semantics_and_serialization_are_deterministic(self) -> None:
        first = self.analyzer.analyze(self.source_text)
        second = self.analyzer.analyze(self.source_text)
        self.assertEqual(first, second)
        self.assertEqual([item.id for item in first.entities], ["entity_001"])
        self.assertEqual([item.id for item in first.propositions], ["prop_001"])
        self.assertEqual([item.id for item in first.temporal_relations], ["temporal_001"])
        self.assertEqual(analysis_from_json(analysis_to_json(first)), first)

    def test_no_persistence_recurrence_trend_or_weather_inference(self) -> None:
        sources = (
            self.source_text,
            "The temperature is below 10.",
            "The switch is on.",
        )
        for source in sources:
            with self.subTest(source=source):
                result = self.infer(source, self.query_text)
                self.assertEqual(result.interpretation_status, InterpretationStatus.UNSUPPORTED)
                self.assertEqual(result.rule, NOT_ESTABLISHED_RULE)

    def test_existing_inference_behaviors_are_unchanged(self) -> None:
        exact = self.infer("The door is open.", "The door is open.")
        opposition = self.infer("The switch is off.", "The switch is on.")
        universal = self.infer(
            "All marked boxes are inspected. Box A is marked.", "Box A is inspected.",
        )
        residence = self.infer(
            "Peter lived in Paris for five years.", "Peter speaks fluent French.",
        )
        self.assertEqual(exact.interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertEqual(opposition.interpretation_status, InterpretationStatus.CONTRADICTED)
        self.assertEqual(universal.interpretation_status, InterpretationStatus.ENTAILED)
        self.assertEqual(universal.rule, "UNIVERSAL_INSTANTIATION")
        self.assertEqual(residence.interpretation_status, InterpretationStatus.UNSUPPORTED)
        self.assertEqual(residence.rule, NOT_ESTABLISHED_RULE)

    def test_comparator_reuses_temporal_change(self) -> None:
        comparison = DeterministicComparator().compare(
            self.analyzer.analyze(self.source_text),
            self.analyzer.analyze(self.query_text),
        )
        self.assertEqual(
            [item.difference_type for item in comparison.differences],
            [DifferenceType.TEMPORAL_CHANGE],
        )

    def test_supported_case_and_number_normalization_are_deterministic(self) -> None:
        words = self.analyzer.analyze(self.source_text)
        digits = self.analyzer.analyze(
            "THE LIGHT FLICKERED ON EACH OF THE LAST 5 EVENINGS.",
        )
        self.assertEqual(
            words.temporal_relations[0].temporal_reference,
            digits.temporal_relations[0].temporal_reference,
        )
        self.assertEqual(words.propositions[0].predicate, digits.propositions[0].predicate)

    def test_broader_future_and_observation_syntax_is_rejected(self) -> None:
        unsupported = (
            "The light will flicker tomorrow.",
            "The light will flicker next week.",
            "The light will be flickering this evening.",
            "The light might flicker this evening.",
            "The light flickered every evening.",
            "The light flickered on each of the last five mornings.",
        )
        for text in unsupported:
            with self.subTest(text=text):
                with self.assertRaises(UnsupportedConstructionError):
                    self.analyzer.analyze(text)


if __name__ == "__main__":
    unittest.main()
