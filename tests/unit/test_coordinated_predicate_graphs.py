import unittest
from dataclasses import replace

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine,
    DeterministicPropositionAligner, DifferenceType, InterpretationStatus,
    LogicalRelation, ReferenceValidationError, SemanticItem, Severity,
    analysis_from_json, analysis_to_json, validate_analysis,
)


class CoordinatedPredicateGraphTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    def test_register_and_show_are_separate_authoritative_propositions(self) -> None:
        analysis = self.analyzer.analyze("Register your name and show identification.")
        self.assertEqual(
            [(item.id, item.predicate, item.arguments) for item in analysis.propositions],
            [
                ("prop_001", "REGISTER", ("entity_001", "entity_002")),
                ("prop_002", "SHOW", ("entity_001", "entity_003")),
            ],
        )
        coordination = next(item for item in analysis.relations if item.type == "PREDICATE_AND")
        self.assertEqual(coordination.arguments, ("prop_001", "prop_002"))

    def test_sign_and_date_share_subject_and_object(self) -> None:
        analysis = self.analyzer.analyze("Sign and date the form.")
        self.assertEqual(
            [(item.predicate, item.arguments) for item in analysis.propositions],
            [
                ("SIGN", ("entity_001", "entity_002")),
                ("DATE", ("entity_001", "entity_002")),
            ],
        )
        coordination = next(item for item in analysis.relations if item.type == "PREDICATE_AND")
        self.assertEqual(coordination.arguments, ("prop_002", "prop_001"))
        self.assertEqual(analysis.logical_representation[0].display, "Date(Addressee, Form) ∧ Sign(Addressee, Form)")

    def test_added_coordinated_member_is_a_single_high_severity_addition(self) -> None:
        result = self.comparator.compare(
            self.analyzer.analyze("Register your name."),
            self.analyzer.analyze("Register your name and show identification."),
        )
        self.assertEqual(len(result.differences), 1)
        finding = result.differences[0]
        self.assertIs(finding.difference_type, DifferenceType.ADDITION)
        self.assertEqual(finding.target_value, "SHOW_IDENTIFICATION")
        self.assertIs(finding.severity, Severity.HIGH)
        self.assertIs(result.logical_relation, LogicalRelation.UNDETERMINED)

    def test_omitted_coordinated_member_is_a_single_high_severity_omission(self) -> None:
        result = self.comparator.compare(
            self.analyzer.analyze("Sign and date the form."),
            self.analyzer.analyze("Sign the form."),
        )
        self.assertEqual(len(result.differences), 1)
        finding = result.differences[0]
        self.assertIs(finding.difference_type, DifferenceType.OMISSION)
        self.assertEqual(finding.source_value, "DATE_FORM")
        self.assertIs(finding.severity, Severity.HIGH)

    def test_flat_object_and_is_order_invariant(self) -> None:
        source = self.analyzer.analyze("Submit form A and form B.")
        target = self.analyzer.analyze("Submit form B and form A.")
        def labels(analysis):
            entities = {item.id: item.label for item in analysis.entities}
            return tuple(entities[item] for item in analysis.propositions[0].arguments)

        self.assertEqual(labels(source), labels(target))
        self.assertEqual(
            source.logical_representation[0].display,
            target.logical_representation[0].display,
        )
        result = self.comparator.compare(source, target)
        self.assertEqual(result.differences, ())
        self.assertIs(result.logical_relation, LogicalRelation.EQUIVALENT)

    def test_and_to_or_remains_a_conjunction_change(self) -> None:
        result = self.comparator.compare(
            self.analyzer.analyze("All patients must receive treatment A and treatment B."),
            self.analyzer.analyze("All patients must receive treatment A or treatment B."),
        )
        self.assertEqual(
            [item.difference_type for item in result.differences],
            [DifferenceType.CONJUNCTION_CHANGE],
        )

    def test_alignment_is_exact_for_shared_member_and_safe_for_extra_member(self) -> None:
        alignment = DeterministicPropositionAligner().align(
            self.analyzer.analyze("Register your name."),
            self.analyzer.analyze("Register your name and show identification."),
        )
        self.assertEqual(
            [(item.source_proposition_id, item.target_proposition_id) for item in alignment.alignments],
            [("prop_001", "prop_001")],
        )
        self.assertEqual(alignment.safely_unmatched_target_ids, ("prop_002",))

    def test_coordinated_member_is_available_as_exact_explicit_evidence(self) -> None:
        result = DeterministicInferenceEngine().infer(
            self.analyzer.analyze("Sign and date the form."),
            self.analyzer.analyze("Sign the form."),
        )
        self.assertIs(result.interpretation_status, InterpretationStatus.EXPLICIT)

    def test_graph_round_trip_and_reference_validation(self) -> None:
        analysis = self.analyzer.analyze("Sign and date the form.")
        self.assertEqual(analysis_from_json(analysis_to_json(analysis)), analysis)
        coordination = next(item for item in analysis.relations if item.type == "PREDICATE_AND")
        invalid = replace(
            analysis,
            relations=tuple(
                replace(item, arguments=("prop_001", "entity_002"))
                if item.id == coordination.id else item
                for item in analysis.relations
            ),
        )
        with self.assertRaisesRegex(ReferenceValidationError, "must be a proposition"):
            validate_analysis(invalid)

    def test_duplicate_coordination_members_are_rejected(self) -> None:
        analysis = self.analyzer.analyze("Sign and date the form.")
        invalid = replace(
            analysis,
            relations=tuple(
                SemanticItem(
                    item.id, item.type, ("prop_001", "prop_001"),
                    item.interpretation_status, item.confidence, item.span, item.derived_from,
                ) if item.type == "PREDICATE_AND" else item
                for item in analysis.relations
            ),
        )
        with self.assertRaisesRegex(ReferenceValidationError, "distinct proposition members"):
            validate_analysis(invalid)


if __name__ == "__main__":
    unittest.main()
