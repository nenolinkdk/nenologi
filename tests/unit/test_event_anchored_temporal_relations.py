import unittest

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine,
    DifferenceType, InterpretationStatus, LogicalRelation, ReferenceValidationError,
    Severity, UnsupportedConstructionError,
    analysis_from_json, analysis_to_dict, analysis_to_json, validate_analysis,
)

SOURCE = "Inspect the cable before starting the machine."
TARGET = "Inspect the cable after starting the machine."


class EventAnchoredTemporalRelationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    def test_actual_gold_case_is_exact_without_duplicate_findings(self) -> None:
        result = self.comparator.compare(self.analyzer.analyze(SOURCE), self.analyzer.analyze(TARGET))
        self.assertEqual(len(result.differences), 1)
        finding = result.differences[0]
        self.assertIs(finding.difference_type, DifferenceType.TEMPORAL_CHANGE)
        self.assertEqual((finding.source_value, finding.target_value), ("BEFORE", "AFTER"))
        self.assertIs(finding.severity, Severity.HIGH)
        self.assertEqual(finding.confidence.value, 1.0)
        self.assertIs(result.logical_relation, LogicalRelation.UNDETERMINED)

    def test_events_are_ordinary_aligned_propositions_and_anchor_is_structured(self) -> None:
        source = self.analyzer.analyze(SOURCE)
        target = self.analyzer.analyze(TARGET)
        self.assertEqual(
            [(item.id, item.predicate, item.arguments) for item in source.propositions],
            [("prop_001", "INSPECT", ("entity_001", "entity_002")),
             ("prop_002", "START", ("entity_001", "entity_003"))],
        )
        self.assertEqual(
            [(item.id, item.predicate, item.arguments) for item in source.propositions],
            [(item.id, item.predicate, item.arguments) for item in target.propositions],
        )
        temporal = source.temporal_relations[0]
        self.assertEqual((temporal.proposition, temporal.temporal_reference), ("prop_001", "prop_002"))

    def test_direction_formula_and_source_spans(self) -> None:
        source = self.analyzer.analyze(SOURCE)
        temporal = source.temporal_relations[0]
        self.assertEqual(SOURCE[temporal.span.start:temporal.span.end], "before")
        self.assertEqual(SOURCE[source.propositions[0].span.start:source.propositions[0].span.end], "Inspect")
        self.assertEqual(SOURCE[source.propositions[1].span.start:source.propositions[1].span.end], "starting")
        self.assertEqual(source.logical_representation[0].display,
                         "Before(Inspect(Addressee, Cable), Start(Addressee, Machine))")

    def test_serialization_round_trip_reference_validation_and_determinism(self) -> None:
        first = self.analyzer.analyze(SOURCE)
        second = self.analyzer.analyze(SOURCE)
        self.assertEqual(first, second)
        self.assertEqual(analysis_from_json(analysis_to_json(first)), first)
        self.assertIs(validate_analysis(first), first)

    def test_dangling_and_self_anchor_rejected(self) -> None:
        data = analysis_to_dict(self.analyzer.analyze(SOURCE))
        data["temporal_relations"][0]["temporal_reference"] = "prop_999"
        with self.assertRaisesRegex(ReferenceValidationError, "prop_999"):
            validate_analysis(data)
        data = analysis_to_dict(self.analyzer.analyze(SOURCE))
        data["temporal_relations"][0]["temporal_reference"] = "prop_001"
        with self.assertRaisesRegex(ReferenceValidationError, "cannot reference"):
            validate_analysis(data)

    def test_controlled_grammar_rejects_unregistered_event_temporal_forms(self) -> None:
        for text in (
            "Inspect the cable while starting the machine.",
            "Start the machine after inspecting the cable.",
            "Inspect the cable before restarting the machine.",
        ):
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)

    def test_calendar_clock_on_and_until_regress(self) -> None:
        for text, reference in (
            ("Employees must register before Friday.", "Friday"),
            ("The system must stop after 18:00.", "18:00"),
            ("Employees must register on Monday.", "Monday"),
            ("Employees must register until Friday.", "Friday"),
        ):
            with self.subTest(text=text):
                self.assertEqual(self.analyzer.analyze(text).temporal_relations[0].temporal_reference, reference)

    def test_condition_unless_scope_and_coordination_regress(self) -> None:
        self.assertEqual(len(self.analyzer.analyze("If the light is green, employees may enter.").conditions), 1)
        self.assertEqual(len(self.analyzer.analyze("You may enter unless the door is locked.").conditions), 1)
        self.assertEqual(len(self.analyzer.analyze("Maria did not promise to leave.").negation), 1)
        self.assertEqual(len(self.analyzer.analyze("Register your name and show identification.").propositions), 2)

    def test_two_sentences_do_not_gain_chronology(self) -> None:
        analysis = self.analyzer.analyze("The window is closed. The door is locked.")
        self.assertEqual(len(analysis.propositions), 2)
        self.assertEqual(analysis.temporal_relations, ())

    def test_observation_coreference_and_nonliteral_regress(self) -> None:
        observation = self.analyzer.analyze("The light flickered on each of the last five evenings.")
        self.assertEqual(observation.temporal_relations[0].temporal_reference, "LAST_5_EVENINGS")
        self.assertEqual(self.analyzer.analyze("Alex told Sam that they had won.").ambiguities[0].reading_ids,
                         ("alternative_001", "alternative_002"))
        self.assertEqual(self.analyzer.analyze("Time is a thief.").propositions, ())

    def test_exact_explicit_and_universal_inference_safety(self) -> None:
        engine = DeterministicInferenceEngine()
        source = self.analyzer.analyze(SOURCE)
        target = self.analyzer.analyze(TARGET)
        self.assertIs(engine.infer(source, source).interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertIs(engine.infer(source, target).interpretation_status, InterpretationStatus.UNSUPPORTED)
        universal = self.analyzer.analyze("All marked boxes are inspected. Box A is marked.")
        query = self.analyzer.analyze("Box A is inspected.")
        self.assertIs(engine.infer(universal, query).interpretation_status, InterpretationStatus.ENTAILED)

    def test_temporal_003_remains_unsupported(self) -> None:
        for text in ("Wait until noon.", "Wait until after noon."):
            with self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)


if __name__ == "__main__":
    unittest.main()
