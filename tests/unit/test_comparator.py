import unittest
from dataclasses import replace

from nenologi import (
    ComparisonMode, Confidence, ControlledEnglishAnalyzer, DeterministicComparator,
    DifferenceType, InterpretationStatus, LogicalRelation, SemanticItem, UnsupportedComparisonError,
    comparison_from_json, comparison_to_json,
)


class DeterministicComparatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    def compare(self, source: str, target: str):
        return self.comparator.compare(self.analyzer.analyze(source), self.analyzer.analyze(target))

    def assert_transition(self, source: str, target: str, difference_type: DifferenceType, before: str, after: str) -> None:
        result = self.compare(source, target)
        self.assertEqual(len(result.differences), 1)
        finding = result.differences[0]
        self.assertIs(finding.difference_type, difference_type)
        self.assertEqual((finding.source_value, finding.target_value), (before, after))
        self.assertEqual(finding.confidence.value, 1.0)

    def test_modality_transitions(self) -> None:
        cases = (
            ("All employees must register.", "All employees may register.", "MUST", "MAY"),
            ("All employees must register.", "All employees should register.", "MUST", "SHOULD"),
            ("All employees may register.", "All employees must register.", "MAY", "MUST"),
        )
        for source, target, before, after in cases:
            with self.subTest(before=before, after=after):
                self.assert_transition(source, target, DifferenceType.MODALITY_CHANGE, before, after)

    def test_quantifier_transitions(self) -> None:
        cases = (
            ("All employees must register.", "Some employees must register.", "ALL", "SOME"),
            ("Some employees must register.", "All employees must register.", "SOME", "ALL"),
            ("No employees may enter.", "Some employees may enter.", "NONE", "SOME"),
        )
        for source, target, before, after in cases:
            with self.subTest(before=before, after=after):
                self.assert_transition(source, target, DifferenceType.QUANTIFIER_CHANGE, before, after)

    def test_negation_added_and_removed(self) -> None:
        self.assert_transition(
            "All employees must register.", "All employees must not register.",
            DifferenceType.NEGATION_CHANGE, "AFFIRMED", "NEGATED",
        )
        self.assert_transition(
            "All employees must not register.", "All employees must register.",
            DifferenceType.NEGATION_CHANGE, "NEGATED", "AFFIRMED",
        )

    def test_every_and_all_are_equivalent(self) -> None:
        result = self.compare("Every employee must register.", "All employees must register.")
        self.assertEqual(result.differences, ())
        self.assertIs(result.logical_relation, LogicalRelation.EQUIVALENT)

    def test_no_normalizes_to_none_without_duplicate_negation_finding(self) -> None:
        result = self.compare("No employees may enter.", "Some employees may enter.")
        self.assertEqual([item.difference_type for item in result.differences], [DifferenceType.QUANTIFIER_CHANGE])

    def test_identical_analysis_is_equivalent(self) -> None:
        analysis = self.analyzer.analyze("All employees must register.")
        result = self.comparator.compare(analysis, analysis, mode=ComparisonMode.VERSION_COMPARISON)
        self.assertEqual(result.differences, ())

    def test_multiple_findings_and_deterministic_order(self) -> None:
        result = self.compare("All employees must register.", "Some employees may register.")
        self.assertEqual(
            [item.difference_type for item in result.differences],
            [DifferenceType.QUANTIFIER_CHANGE, DifferenceType.MODALITY_CHANGE],
        )
        self.assertEqual([item.id for item in result.differences], ["difference_001", "difference_002"])

    def test_comparison_serialization_round_trip(self) -> None:
        result = self.compare("All employees must register.", "Some employees may register.")
        self.assertEqual(comparison_from_json(comparison_to_json(result)), result)

    def test_subject_object_and_predicate_changes(self) -> None:
        cases = (
            ("All employees must register.", "All managers must register.", "SUBJECT:EMPLOYEE", "SUBJECT:MANAGER", "affected entity"),
            ("All employees must submit the report.", "All employees must submit the form.", "OBJECT:REPORT", "OBJECT:FORM", "object"),
            ("All employees must register.", "All employees must report.", "PREDICATE:REGISTER", "PREDICATE:REPORT", "action"),
        )
        for source, target, before, after, explanation in cases:
            with self.subTest(before=before, after=after):
                result = self.compare(source, target)
                self.assertEqual(len(result.differences), 1)
                finding = result.differences[0]
                self.assertIs(finding.difference_type, DifferenceType.ENTITY_RELATION_CHANGE)
                self.assertEqual((finding.source_value, finding.target_value), (before, after))
                self.assertIn(explanation, finding.explanation)

    def test_multiple_entity_and_predicate_changes_are_rejected(self) -> None:
        with self.assertRaises(UnsupportedComparisonError):
            self.compare("All employees must register.", "All managers must report.")

    def test_unsupported_transition_is_not_silently_equivalent(self) -> None:
        with self.assertRaisesRegex(UnsupportedComparisonError, "modality transition"):
            self.compare("All employees should register.", "All employees may register.")

    def test_unsupported_semantic_dimension_is_not_silently_equivalent(self) -> None:
        source = self.analyzer.analyze("All employees must register.")
        target = replace(source, conditions=(SemanticItem(
            "condition_001", "IF", ("prop_001",), InterpretationStatus.EXPLICIT,
            Confidence(1.0), derived_from=("prop_001",),
        ),))
        with self.assertRaisesRegex(UnsupportedComparisonError, "conditions"):
            self.comparator.compare(source, target)

    def test_raw_text_to_comparison_integration(self) -> None:
        source = self.analyzer.analyze("All employees must register.")
        target = self.analyzer.analyze("Some employees may register.")
        result = self.comparator.compare(source, target)
        self.assertEqual(result.source_analysis.logical_representation[0].display, "∀x (Employee(x) → Must(Register(x)))")
        self.assertEqual(result.target_analysis.logical_representation[0].display, "∃x (Employee(x) ∧ May(Register(x)))")
        self.assertIn("quantified scope", result.differences[0].explanation)
        self.assertIn("weakens", result.differences[1].explanation)

    def test_conjunction_transitions_equivalence_and_formula(self) -> None:
        source = "All patients must receive treatment A and treatment B."
        target = "All patients must receive treatment A or treatment B."
        result = self.compare(source, target)
        self.assertEqual(result.differences[0].difference_type, DifferenceType.CONJUNCTION_CHANGE)
        self.assertEqual((result.differences[0].source_value, result.differences[0].target_value), ("AND", "OR"))
        self.assertIn("∧", result.source_analysis.logical_representation[0].display)
        self.assertEqual(comparison_from_json(comparison_to_json(result)), result)
        reverse = self.compare(target, source)
        self.assertEqual((reverse.differences[0].source_value, reverse.differences[0].target_value), ("OR", "AND"))
        equivalent = self.compare(
            "ALL PATIENTS MUST RECEIVE TREATMENT A AND TREATMENT B",
            "  All patients must receive treatment A and treatment B.  ",
        )
        self.assertEqual(equivalent.differences, ())

    def test_quantifier_modality_and_conjunction_order(self) -> None:
        result = self.compare(
            "All patients must receive treatment A and treatment B.",
            "Some patients may receive treatment A or treatment B.",
        )
        self.assertEqual(
            [finding.difference_type for finding in result.differences],
            [DifferenceType.QUANTIFIER_CHANGE, DifferenceType.MODALITY_CHANGE, DifferenceType.CONJUNCTION_CHANGE],
        )
        self.assertIs(result.logical_relation, LogicalRelation.UNDETERMINED)

    def test_negation_is_one_difference_with_separate_logical_relation(self) -> None:
        result = self.compare("The switch is on.", "The switch is not on.")
        self.assertEqual([finding.difference_type for finding in result.differences], [DifferenceType.NEGATION_CHANGE])
        self.assertIs(result.logical_relation, LogicalRelation.CONTRADICTORY)


if __name__ == "__main__":
    unittest.main()
