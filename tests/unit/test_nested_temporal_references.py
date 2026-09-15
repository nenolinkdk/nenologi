import unittest

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine,
    DifferenceType, InterpretationStatus, LogicalRelation, ReferenceValidationError,
    Severity, UnsupportedConstructionError, analysis_from_json, analysis_to_dict,
    analysis_to_json, validate_analysis,
)

SOURCE = "Wait until noon."
TARGET = "Wait until after noon."


class NestedTemporalReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    def test_actual_source_and_target_use_structured_nested_references(self) -> None:
        source = self.analyzer.analyze(SOURCE)
        target = self.analyzer.analyze(TARGET)
        self.assertEqual(source.propositions[0].predicate, "WAIT")
        self.assertEqual(source.temporal_relations[0].temporal_reference, "temporal_reference_001")
        self.assertEqual(source.relations[1].type, "TEMPORAL_POINT")
        self.assertEqual(target.relations[1].type, "TEMPORAL_AFTER")
        self.assertEqual(source.relations[1].arguments, ("entity_002",))
        self.assertEqual(target.relations[1].arguments, ("entity_002",))
        self.assertEqual(source.entities[1].label, "NOON")

    def test_gold_comparison_is_one_medium_temporal_change(self) -> None:
        result = self.comparator.compare(self.analyzer.analyze(SOURCE), self.analyzer.analyze(TARGET))
        self.assertEqual(len(result.differences), 1)
        finding = result.differences[0]
        self.assertIs(finding.difference_type, DifferenceType.TEMPORAL_CHANGE)
        self.assertEqual((finding.source_value, finding.target_value), ("UNTIL_NOON", "UNTIL_AFTER_NOON"))
        self.assertIs(finding.severity, Severity.MEDIUM)
        self.assertEqual(finding.confidence.value, 1.0)
        self.assertIs(result.logical_relation, LogicalRelation.UNDETERMINED)

    def test_proposition_identity_formula_spans_and_determinism(self) -> None:
        first = self.analyzer.analyze(TARGET)
        second = self.analyzer.analyze(TARGET)
        self.assertEqual(first, second)
        self.assertEqual((first.propositions[0].id, first.propositions[0].predicate), ("prop_001", "WAIT"))
        self.assertEqual(first.logical_representation[0].display, "Until(Wait(Addressee), After(Noon))")
        self.assertEqual(TARGET[first.propositions[0].span.start:first.propositions[0].span.end], "Wait")
        self.assertEqual(TARGET[first.temporal_relations[0].span.start:first.temporal_relations[0].span.end], "until")
        reference = first.relations[1]
        self.assertEqual(TARGET[reference.span.start:reference.span.end], "after noon")

    def test_json_round_trip_and_valid_reference_graph(self) -> None:
        analysis = self.analyzer.analyze(TARGET)
        self.assertEqual(analysis_from_json(analysis_to_json(analysis)), analysis)
        self.assertIs(validate_analysis(analysis), analysis)

    def test_dangling_outer_and_inner_references_are_rejected(self) -> None:
        outer = analysis_to_dict(self.analyzer.analyze(TARGET))
        outer["temporal_relations"][0]["temporal_reference"] = "temporal_reference_999"
        with self.assertRaisesRegex(ReferenceValidationError, "temporal_reference_999"):
            validate_analysis(outer)
        inner = analysis_to_dict(self.analyzer.analyze(TARGET))
        inner["relations"][1]["arguments"] = ["entity_999"]
        with self.assertRaisesRegex(ReferenceValidationError, "entity_999"):
            validate_analysis(inner)

    def test_direct_and_indirect_temporal_reference_cycles_are_rejected(self) -> None:
        direct = analysis_to_dict(self.analyzer.analyze(TARGET))
        direct["relations"][1]["arguments"] = ["temporal_reference_001"]
        with self.assertRaisesRegex(ReferenceValidationError, "cyclic temporal reference"):
            validate_analysis(direct)
        indirect = analysis_to_dict(self.analyzer.analyze(TARGET))
        clone = dict(indirect["relations"][1])
        clone["id"] = "temporal_reference_002"
        clone["arguments"] = ["temporal_reference_001"]
        indirect["relations"][1]["arguments"] = ["temporal_reference_002"]
        indirect["relations"].append(clone)
        with self.assertRaisesRegex(ReferenceValidationError, "cyclic temporal reference"):
            validate_analysis(indirect)

    def test_controlled_grammar_rejects_unregistered_nested_forms(self) -> None:
        for text in ("Wait until before noon.", "Wait until after Monday.", "Wait until after after noon."):
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)

    def test_simple_and_event_temporal_families_regress(self) -> None:
        for text, reference in (
            ("Pay the invoice before Monday.", "Monday"),
            ("The system must stop after 18:00.", "18:00"),
            ("Employees must register on Monday.", "Monday"),
            ("Employees must register until Friday.", "Friday"),
            ("The light flickered on each of the last five evenings.", "LAST_5_EVENINGS"),
        ):
            with self.subTest(text=text):
                self.assertEqual(self.analyzer.analyze(text).temporal_relations[0].temporal_reference, reference)
        event = self.comparator.compare(
            self.analyzer.analyze("Inspect the cable before starting the machine."),
            self.analyzer.analyze("Inspect the cable after starting the machine."),
        )
        self.assertEqual([(x.difference_type, x.severity) for x in event.differences],
                         [(DifferenceType.TEMPORAL_CHANGE, Severity.HIGH)])

    def test_conditions_scope_coordination_and_two_sentences_regress(self) -> None:
        self.assertEqual(len(self.analyzer.analyze("If the light is green, you may enter.").conditions), 1)
        self.assertEqual(len(self.analyzer.analyze("Submit the report if the test passes.").conditions), 1)
        self.assertEqual(len(self.analyzer.analyze("You may enter unless the door is locked.").conditions), 1)
        self.assertEqual(len(self.analyzer.analyze("Maria promised not to leave.").negation), 1)
        self.assertEqual(len(self.analyzer.analyze("Register your name and show identification.").propositions), 2)
        independent = self.analyzer.analyze("The window is closed. The door is locked.")
        self.assertEqual(independent.temporal_relations, ())

    def test_inference_and_phase_3_representations_remain_unchanged(self) -> None:
        engine = DeterministicInferenceEngine()
        source = self.analyzer.analyze(SOURCE)
        target = self.analyzer.analyze(TARGET)
        self.assertIs(engine.infer(source, source).interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertIs(engine.infer(source, target).interpretation_status, InterpretationStatus.UNSUPPORTED)
        universal = self.analyzer.analyze("All marked boxes are inspected. Box A is marked.")
        query = self.analyzer.analyze("Box A is inspected.")
        self.assertIs(engine.infer(universal, query).interpretation_status, InterpretationStatus.ENTAILED)
        self.assertEqual(len(self.analyzer.analyze("Alex told Sam that they had won.").ambiguities), 1)
        self.assertEqual(self.analyzer.analyze("Time is a thief.").propositions, ())


if __name__ == "__main__":
    unittest.main()
