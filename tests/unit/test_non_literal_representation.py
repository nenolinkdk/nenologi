import unittest

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine,
    InterpretationStatus, NOT_ESTABLISHED_RULE, UnsupportedConstructionError,
    analysis_from_json, analysis_to_json, validate_analysis,
)


class NonLiteralRepresentationV01Tests(unittest.TestCase):
    source_text = "Time is a thief."
    query_text = "Time commits theft."

    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.engine = DeterministicInferenceEngine()

    def infer(self, source: str, query: str):
        return self.engine.infer(
            self.analyzer.analyze(source), self.analyzer.analyze(query),
        )

    def test_entailment_007_source_and_query_parse(self) -> None:
        source = self.analyzer.analyze(self.source_text)
        query = self.analyzer.analyze(self.query_text)
        validate_analysis(source)
        validate_analysis(query)
        self.assertEqual(source.propositions, ())
        self.assertEqual(query.propositions[0].predicate, "COMMIT_THEFT")

    def test_non_literal_status_is_authoritative_and_literal_fact_is_absent(self) -> None:
        source = self.analyzer.analyze(self.source_text)
        marker = source.relations[0]
        self.assertEqual(marker.id, "non_literal_001")
        self.assertEqual(marker.type, "NON_LITERAL_EXPRESSION")
        self.assertEqual(
            marker.interpretation_status,
            InterpretationStatus.CANNOT_BE_SAFELY_FORMALIZED,
        )
        self.assertEqual(source.propositions, ())
        self.assertFalse(any(
            item.predicate in {"THIEF", "COMMIT_THEFT"}
            for item in source.propositions
        ))

    def test_safe_entity_structure_and_source_spans_are_retained(self) -> None:
        source = self.analyzer.analyze(self.source_text)
        self.assertEqual((source.entities[0].id, source.entities[0].label), (
            "entity_001", "time",
        ))
        self.assertEqual(
            self.source_text[source.entities[0].span.start:source.entities[0].span.end],
            "Time",
        )
        marker = source.relations[0]
        self.assertEqual(
            self.source_text[marker.span.start:marker.span.end], "is a thief",
        )

    def test_ids_status_and_structure_round_trip_deterministically(self) -> None:
        first = self.analyzer.analyze(self.source_text)
        second = self.analyzer.analyze(self.source_text)
        self.assertEqual(first, second)
        restored = analysis_from_json(analysis_to_json(first))
        self.assertEqual(restored, first)
        self.assertEqual(
            restored.logical_representation[0].interpretation_status,
            InterpretationStatus.CANNOT_BE_SAFELY_FORMALIZED,
        )

    def test_literal_query_is_neither_established_nor_contradicted(self) -> None:
        result = self.infer(self.source_text, self.query_text)
        self.assertEqual(result.interpretation_status, InterpretationStatus.UNSUPPORTED)
        self.assertEqual(result.rule, NOT_ESTABLISHED_RULE)
        self.assertEqual(result.derived_from, ())
        self.assertNotEqual(result.interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertNotEqual(result.interpretation_status, InterpretationStatus.ENTAILED)
        self.assertNotEqual(result.interpretation_status, InterpretationStatus.CONTRADICTED)

    def test_unsafe_content_cannot_feed_exact_opposition_or_universal_rules(self) -> None:
        for query in (
            self.query_text,
            "The switch is on.",
            "Box A is inspected.",
        ):
            with self.subTest(query=query):
                result = self.infer(self.source_text, query)
                self.assertEqual(result.interpretation_status, InterpretationStatus.UNSUPPORTED)
                self.assertEqual(result.rule, NOT_ESTABLISHED_RULE)

    def test_ordinary_literal_proposition_remains_explicit(self) -> None:
        result = self.infer(self.query_text, self.query_text)
        self.assertEqual(result.interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertEqual(result.rule, "EXACT_EXPLICIT")

    def test_existing_inference_milestones_are_unchanged(self) -> None:
        universal = self.infer(
            "All marked boxes are inspected. Box A is marked.", "Box A is inspected.",
        )
        residence = self.infer(
            "Peter lived in Paris for five years.", "Peter speaks fluent French.",
        )
        prediction = self.infer(
            "The light flickered on each of the last five evenings.",
            "The light will flicker this evening.",
        )
        coreference = self.infer(
            "Alex told Sam that they had won.", "Alex had won.",
        )
        opposition = self.infer("The switch is off.", "The switch is on.")
        self.assertEqual(universal.interpretation_status, InterpretationStatus.ENTAILED)
        self.assertEqual(residence.interpretation_status, InterpretationStatus.UNSUPPORTED)
        self.assertEqual(prediction.interpretation_status, InterpretationStatus.UNSUPPORTED)
        self.assertEqual(coreference.interpretation_status, InterpretationStatus.UNSUPPORTED)
        self.assertEqual(opposition.interpretation_status, InterpretationStatus.CONTRADICTED)

    def test_comparator_regression_is_unchanged(self) -> None:
        literal = self.analyzer.analyze(self.query_text)
        self.assertEqual(DeterministicComparator().compare(literal, literal).differences, ())

    def test_broader_metaphorical_syntax_is_rejected_not_guessed(self) -> None:
        unsupported = (
            "The city sleeps.",
            "The market panicked.",
            "The idea took flight.",
            "Time devours moments.",
            "Time steals moments.",
            "Time committed theft.",
        )
        for text in unsupported:
            with self.subTest(text=text):
                with self.assertRaises(UnsupportedConstructionError):
                    self.analyzer.analyze(text)


if __name__ == "__main__":
    unittest.main()
