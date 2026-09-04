import unittest
from dataclasses import replace

from nenologi import (
    ComparisonMode, Confidence, ControlledEnglishAnalyzer, DeterministicComparator,
    DifferenceType, InterpretationStatus, SemanticItem, UnsupportedComparisonError,
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

    def test_incompatible_predicates_and_entities_are_explicitly_rejected(self) -> None:
        for source, target in (
            ("All employees must register.", "All employees must vote."),
            ("All employees must register.", "All visitors must register."),
        ):
            with self.subTest(source=source, target=target), self.assertRaises(UnsupportedComparisonError):
                self.compare(source, target)

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


if __name__ == "__main__":
    unittest.main()
