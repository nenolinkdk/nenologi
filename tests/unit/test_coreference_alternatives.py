import unittest
from dataclasses import replace

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine,
    InterpretationStatus, NOT_ESTABLISHED_RULE, ReferenceValidationError,
    UnsupportedConstructionError,
    analysis_from_json, analysis_to_json, validate_analysis,
)


class CoreferenceAlternativesV01Tests(unittest.TestCase):
    source_text = "Alex told Sam that they had won."

    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.engine = DeterministicInferenceEngine()

    def infer(self, source: str, query: str):
        return self.engine.infer(
            self.analyzer.analyze(source), self.analyzer.analyze(query),
        )

    def test_entailment_006_source_and_query_parse(self) -> None:
        source = self.analyzer.analyze(self.source_text)
        query = self.analyzer.analyze("Alex had won.")
        validate_analysis(source)
        validate_analysis(query)
        self.assertEqual([item.predicate for item in source.propositions], ["TELL", "WON"])
        self.assertEqual(query.propositions[0].predicate, "WON")

    def test_reference_and_candidate_alternatives_are_explicitly_represented(self) -> None:
        analysis = self.analyzer.analyze(self.source_text)
        reference = analysis.entities[2]
        self.assertEqual((reference.id, reference.type, reference.label), (
            "reference_001", "UNRESOLVED_REFERENCE", "they",
        ))
        self.assertEqual(reference.interpretation_status, InterpretationStatus.AMBIGUOUS)
        self.assertEqual(
            [(item.id, item.arguments) for item in analysis.sets],
            [
                ("alternative_001", ("reference_001", "entity_001")),
                ("alternative_002", ("reference_001", "entity_002")),
            ],
        )
        self.assertEqual(
            analysis.ambiguities[0].reading_ids,
            ("alternative_001", "alternative_002"),
        )

    def test_embedded_proposition_uses_reference_not_both_candidates(self) -> None:
        analysis = self.analyzer.analyze(self.source_text)
        embedded = analysis.propositions[1]
        self.assertEqual(embedded.id, "embedded_prop_001")
        self.assertEqual(embedded.arguments, ("reference_001",))
        self.assertEqual(embedded.interpretation_status, InterpretationStatus.AMBIGUOUS)
        self.assertFalse(any(
            proposition.predicate == "WON" and proposition.arguments in {
                ("entity_001",), ("entity_002",),
            }
            for proposition in analysis.propositions
        ))
        self.assertEqual(
            analysis.relations[0].arguments, ("prop_001", "embedded_prop_001"),
        )

    def test_no_candidate_is_preferred_or_established(self) -> None:
        for name in ("Alex", "Sam"):
            with self.subTest(name=name):
                result = self.infer(self.source_text, f"{name} had won.")
                self.assertEqual(result.interpretation_status, InterpretationStatus.UNSUPPORTED)
                self.assertEqual(result.rule, NOT_ESTABLISHED_RULE)
                self.assertEqual(result.derived_from, ())

    def test_document_order_and_ids_are_deterministic_without_ranking(self) -> None:
        first = self.analyzer.analyze(self.source_text)
        second = self.analyzer.analyze(self.source_text)
        reversed_mentions = self.analyzer.analyze("Sam told Alex that they had won.")
        self.assertEqual(first, second)
        self.assertEqual(
            [item.arguments[1] for item in first.sets], ["entity_001", "entity_002"],
        )
        self.assertEqual(
            [entity.label for entity in reversed_mentions.entities[:2]], ["sam", "alex"],
        )
        self.assertEqual(
            [item.arguments[1] for item in reversed_mentions.sets],
            ["entity_001", "entity_002"],
        )

    def test_round_trip_and_invalid_candidate_reference_validation(self) -> None:
        analysis = self.analyzer.analyze(self.source_text)
        self.assertEqual(analysis_from_json(analysis_to_json(analysis)), analysis)
        invalid = replace(
            analysis,
            sets=(replace(analysis.sets[0], arguments=("reference_001", "entity_999")),
                  analysis.sets[1]),
        )
        with self.assertRaisesRegex(ReferenceValidationError, "entity_999"):
            validate_analysis(invalid)

    def test_repeated_name_is_resolved_but_reported_content_is_not_a_fact(self) -> None:
        repeated_source = self.analyzer.analyze(
            "Alex told Sam that Alex had won.",
        )
        repeated = self.engine.infer(
            repeated_source, self.analyzer.analyze("Alex had won."),
        )
        direct = self.infer("Alex had won.", "Alex had won.")
        self.assertEqual(repeated_source.propositions[1].interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertEqual(repeated_source.propositions[1].arguments, ("entity_001",))
        self.assertEqual(repeated.interpretation_status, InterpretationStatus.UNSUPPORTED)
        self.assertEqual(direct.interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertEqual(self.analyzer.analyze(
            "Alex told Sam that Sam had won.",
        ).ambiguities, ())

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
        opposition = self.infer("The switch is off.", "The switch is on.")
        self.assertEqual((universal.interpretation_status, universal.rule), (
            InterpretationStatus.ENTAILED, "UNIVERSAL_INSTANTIATION",
        ))
        self.assertEqual(residence.interpretation_status, InterpretationStatus.UNSUPPORTED)
        self.assertEqual(prediction.interpretation_status, InterpretationStatus.UNSUPPORTED)
        self.assertEqual(opposition.interpretation_status, InterpretationStatus.CONTRADICTED)

    def test_comparator_regression_is_unchanged(self) -> None:
        direct = self.analyzer.analyze("Alex had won.")
        self.assertEqual(DeterministicComparator().compare(direct, direct).differences, ())

    def test_broader_pronoun_and_complement_syntax_is_rejected(self) -> None:
        unsupported = (
            "Alex told Sam that he had won.",
            "Alex told Sam that she had won.",
            "Alex told Sam that they had lost.",
            "Alex believed that they had won.",
            "Alex told Sam they had won.",
            "Alex told Sam that their team had won.",
        )
        for text in unsupported:
            with self.subTest(text=text):
                with self.assertRaises(UnsupportedConstructionError):
                    self.analyzer.analyze(text)


if __name__ == "__main__":
    unittest.main()
