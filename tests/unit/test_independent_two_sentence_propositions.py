import unittest
from dataclasses import replace

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine,
    DeterministicPropositionAligner, DifferenceType, InterpretationStatus,
    LogicalRelation, ReferenceValidationError, UnsupportedConstructionError,
    analysis_from_json, analysis_to_json, proposition_signature, validate_analysis,
)


SOURCE = "The window is closed."
TARGET = "The window is closed. The door is locked."


class IndependentTwoSentencePropositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    def test_addition_002_is_exact(self) -> None:
        result = self.comparator.compare(
            self.analyzer.analyze(SOURCE), self.analyzer.analyze(TARGET),
        )
        self.assertEqual(len(result.differences), 1)
        finding = result.differences[0]
        self.assertIs(finding.difference_type, DifferenceType.ADDITION)
        self.assertIsNone(finding.source_value)
        self.assertEqual(finding.target_value, "DOOR_LOCKED")
        self.assertEqual(finding.severity.value, "MEDIUM")
        self.assertEqual(finding.confidence.value, 1.0)
        self.assertIs(result.logical_relation, LogicalRelation.UNDETERMINED)

    def test_two_sentences_are_independent_authoritative_propositions(self) -> None:
        analysis = self.analyzer.analyze(TARGET)
        self.assertEqual(
            [(item.id, item.predicate, item.arguments) for item in analysis.propositions],
            [
                ("prop_001", "CLOSED", ("entity_001",)),
                ("prop_002", "LOCKED", ("entity_002",)),
            ],
        )
        self.assertEqual([item.id for item in analysis.structure.sentences], ["sentence_001", "sentence_002"])
        self.assertEqual(analysis.structure.discourse_relations, ())
        self.assertEqual(analysis.relations, ())
        self.assertEqual(analysis.temporal_relations, ())

    def test_semantic_identity_matches_standalone_parsing(self) -> None:
        document = self.analyzer.analyze(TARGET)
        for proposition, text in zip(
            document.propositions, (SOURCE, "The door is locked."), strict=True,
        ):
            standalone = self.analyzer.analyze(text)
            self.assertEqual(
                proposition_signature(document, proposition),
                proposition_signature(standalone, standalone.propositions[0]),
            )

    def test_ids_spans_and_repeated_parsing_are_deterministic(self) -> None:
        first = self.analyzer.analyze(TARGET)
        self.assertEqual(first, self.analyzer.analyze(TARGET))
        self.assertEqual(
            [(item.id, item.span.start, item.span.end) for item in first.structure.sentences],
            [("sentence_001", 0, 21), ("sentence_002", 22, 41)],
        )
        self.assertEqual(first.entities[1].span, replace(first.entities[1].span, start=26, end=30))
        self.assertEqual((first.propositions[1].span.start, first.propositions[1].span.end), (34, 40))

    def test_repeated_explicit_label_remains_separate_traceable_mentions(self) -> None:
        analysis = self.analyzer.analyze("The window is closed. The window is open.")
        self.assertEqual([item.id for item in analysis.entities], ["entity_001", "entity_002"])
        self.assertEqual([item.label for item in analysis.entities], ["window", "window"])
        self.assertNotEqual(analysis.entities[0].span, analysis.entities[1].span)

    def test_alignment_addition_and_reverse_omission_are_symmetric(self) -> None:
        one = self.analyzer.analyze(SOURCE)
        two = self.analyzer.analyze(TARGET)
        alignment = DeterministicPropositionAligner().align(one, two)
        self.assertEqual(
            [(item.source_proposition_id, item.target_proposition_id) for item in alignment.alignments],
            [("prop_001", "prop_001")],
        )
        self.assertEqual(alignment.safely_unmatched_target_ids, ("prop_002",))
        reverse = self.comparator.compare(two, one)
        self.assertEqual([item.difference_type for item in reverse.differences], [DifferenceType.OMISSION])
        self.assertEqual(reverse.differences[0].source_value, "DOOR_LOCKED")
        self.assertIs(reverse.logical_relation, LogicalRelation.UNDETERMINED)

    def test_formulae_are_independent_and_round_trip(self) -> None:
        analysis = self.analyzer.analyze(TARGET)
        self.assertEqual(
            [item.display for item in analysis.logical_representation],
            ["Closed(Window)", "Locked(Door)"],
        )
        self.assertFalse(any("∧" in (item.display or "") for item in analysis.logical_representation))
        self.assertEqual(analysis_from_json(analysis_to_json(analysis)), analysis)

    def test_exact_explicit_lookup_finds_second_proposition(self) -> None:
        result = DeterministicInferenceEngine().infer(
            self.analyzer.analyze(TARGET), self.analyzer.analyze("The door is locked."),
        )
        self.assertIs(result.interpretation_status, InterpretationStatus.EXPLICIT)

    def test_unsupported_sentence_is_never_silently_dropped(self) -> None:
        cases = (
            "The window is closed. Dragons evaporate moonlight.",
            "Dragons evaporate moonlight. The door is locked.",
            "The window is closed. The door is locked. The alarm is active.",
        )
        for text in cases:
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)

    def test_pronouns_are_not_coreferred_across_sentences(self) -> None:
        analysis = self.analyzer.analyze("Alice opened the door. She opened the window.")
        self.assertEqual([item.label for item in analysis.entities], ["alice", "door", "she", "window"])
        self.assertNotEqual(analysis.propositions[0].arguments[0], analysis.propositions[1].arguments[0])

    def test_sentence_order_has_no_invented_semantics_in_bounded_subset(self) -> None:
        reversed_document = self.analyzer.analyze("The door is locked. The window is closed.")
        result = self.comparator.compare(self.analyzer.analyze(TARGET), reversed_document)
        self.assertEqual(result.differences, ())
        self.assertIs(result.logical_relation, LogicalRelation.EQUIVALENT)

    def test_reference_validation_remains_strict(self) -> None:
        analysis = self.analyzer.analyze(TARGET)
        invalid = replace(
            analysis,
            propositions=(analysis.propositions[0], replace(
                analysis.propositions[1], arguments=("entity_999",),
            )),
        )
        with self.assertRaisesRegex(ReferenceValidationError, "entity_999"):
            validate_analysis(invalid)

    def test_special_multisentence_and_safety_parsers_are_unchanged(self) -> None:
        rule_text = "All marked boxes are inspected. Box A is marked."
        rule = self.analyzer.analyze(rule_text)
        result = DeterministicInferenceEngine().infer(
            rule, self.analyzer.analyze("Box A is inspected."),
        )
        self.assertEqual(result.rule, "UNIVERSAL_INSTANTIATION")
        coordinated = self.analyzer.analyze("Sign and date the form.")
        self.assertEqual([item.predicate for item in coordinated.propositions], ["SIGN", "DATE"])
        coreference = self.analyzer.analyze("Alex told Sam that they had won.")
        self.assertEqual(len(coreference.ambiguities), 1)
        with self.assertRaises(UnsupportedConstructionError):
            self.analyzer.analyze("Time is a thief. The door is locked.")


if __name__ == "__main__":
    unittest.main()
