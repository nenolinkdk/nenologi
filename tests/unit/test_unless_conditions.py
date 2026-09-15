import unittest
from dataclasses import replace

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine,
    DifferenceType, InterpretationStatus, LogicalRelation, ReferenceValidationError,
    UnsupportedConstructionError, analysis_from_json, analysis_to_json, validate_analysis,
)


UNLESS = "You may enter unless the door is locked."
IF = "You may enter if the door is locked."


class UnlessConditionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()
        self.engine = DeterministicInferenceEngine()

    def test_condition_003_is_exact(self) -> None:
        result = self.comparator.compare(
            self.analyzer.analyze(UNLESS), self.analyzer.analyze(IF),
        )
        self.assertEqual(len(result.differences), 1)
        finding = result.differences[0]
        self.assertIs(finding.difference_type, DifferenceType.CONDITION_CHANGE)
        self.assertEqual((finding.source_value, finding.target_value), ("UNLESS_LOCKED", "IF_LOCKED"))
        self.assertEqual(finding.severity.value, "HIGH")
        self.assertEqual(finding.confidence.value, 1.0)
        self.assertIs(result.logical_relation, LogicalRelation.UNDETERMINED)

    def test_unless_is_if_with_structurally_negated_antecedent(self) -> None:
        analysis = self.analyzer.analyze(UNLESS)
        self.assertEqual([(item.id, item.predicate) for item in analysis.propositions], [
            ("antecedent_prop_001", "LOCKED"),
            ("consequent_prop_001", "ENTER"),
        ])
        self.assertEqual(analysis.conditions[0].antecedent, ("antecedent_prop_001",))
        self.assertEqual(analysis.conditions[0].consequent, ("consequent_prop_001",))
        self.assertEqual(
            [(item.id, item.operator, item.scope) for item in analysis.negation],
            [("antecedent_negation_001", "NOT", ("antecedent_prop_001",))],
        )
        self.assertEqual(analysis.modality[0].scope, ("consequent_prop_001",))

    def test_formula_provenance_ids_and_round_trip_are_deterministic(self) -> None:
        analysis = self.analyzer.analyze(UNLESS)
        self.assertEqual(analysis.logical_representation[0].display, "(¬Locked(Door)) → (May(Enter(You)))")
        negation = analysis.negation[0]
        self.assertEqual((negation.span.start, negation.span.end), (14, 20))
        self.assertEqual(UNLESS[negation.span.start:negation.span.end].lower(), "unless")
        self.assertEqual(analysis, self.analyzer.analyze(UNLESS))
        self.assertEqual(analysis_from_json(analysis_to_json(analysis)), analysis)

    def test_no_redundant_negation_addition_or_omission(self) -> None:
        result = self.comparator.compare(
            self.analyzer.analyze(UNLESS), self.analyzer.analyze(IF),
        )
        self.assertEqual([item.difference_type for item in result.differences], [DifferenceType.CONDITION_CHANGE])

    def test_prefix_suffix_and_numeric_conditions_are_unchanged(self) -> None:
        prefix = self.analyzer.analyze("If the light is green, you may enter.")
        suffix = self.analyzer.analyze("You may enter if the light is green.")
        self.assertEqual(self.comparator.compare(prefix, suffix).differences, ())
        numeric = self.comparator.compare(
            self.analyzer.analyze("If the temperature is above 30°C, the system must stop."),
            self.analyzer.analyze("If the temperature is at least 30°C, the system must stop."),
        )
        self.assertEqual([item.difference_type for item in numeric.differences], [DifferenceType.NUMERIC_THRESHOLD_CHANGE])

    def test_consequent_does_not_become_unconditionally_explicit(self) -> None:
        result = self.engine.infer(
            self.analyzer.analyze(UNLESS), self.analyzer.analyze("You may enter."),
        )
        self.assertIs(result.interpretation_status, InterpretationStatus.UNSUPPORTED)

    def test_reference_validation_remains_strict(self) -> None:
        analysis = self.analyzer.analyze(UNLESS)
        invalid_condition = replace(
            analysis.conditions[0], antecedent=("prop_999",),
        )
        with self.assertRaisesRegex(ReferenceValidationError, "prop_999"):
            validate_analysis(replace(analysis, conditions=(invalid_condition,)))
        invalid_negation = replace(
            analysis.negation[0], scope=("prop_999",),
        )
        with self.assertRaisesRegex(ReferenceValidationError, "prop_999"):
            validate_analysis(replace(analysis, negation=(invalid_negation,)))

    def test_neighboring_unless_forms_are_rejected(self) -> None:
        cases = (
            "Unless the door is locked, you may enter.",
            "You may enter unless the door is open.",
            "You must enter unless the door is locked.",
            "You may enter unless the door is locked unless the alarm is active.",
        )
        for text in cases:
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)

    def test_positive_if_is_not_equivalent_to_unless(self) -> None:
        result = self.comparator.compare(
            self.analyzer.analyze(UNLESS), self.analyzer.analyze(IF),
        )
        self.assertIsNot(result.logical_relation, LogicalRelation.EQUIVALENT)
        with self.assertRaises(UnsupportedConstructionError):
            self.analyzer.analyze("If the door is not locked, you may enter.")

    def test_scope_temporal_and_other_milestones_regress(self) -> None:
        scope = self.comparator.compare(
            self.analyzer.analyze("Maria did not promise to leave."),
            self.analyzer.analyze("Maria promised not to leave."),
        )
        self.assertEqual(scope.differences[0].difference_type, DifferenceType.SCOPE_CHANGE)
        temporal = self.comparator.compare(
            self.analyzer.analyze("Employees must register before Friday."),
            self.analyzer.analyze("Employees must register after Friday."),
        )
        self.assertEqual(temporal.differences[0].difference_type, DifferenceType.TEMPORAL_CHANGE)
        self.assertEqual(len(self.analyzer.analyze("Sign and date the form.").propositions), 2)
        self.assertEqual(len(self.analyzer.analyze("The window is closed. The door is locked.").propositions), 2)

    def test_inference_and_safety_regressions(self) -> None:
        rule = self.analyzer.analyze("All marked boxes are inspected. Box A is marked.")
        inferred = self.engine.infer(rule, self.analyzer.analyze("Box A is inspected."))
        self.assertEqual(inferred.rule, "UNIVERSAL_INSTANTIATION")
        self.assertEqual(len(self.analyzer.analyze("Alex told Sam that they had won.").ambiguities), 1)
        self.assertEqual(self.analyzer.analyze("Time is a thief.").propositions, ())


if __name__ == "__main__":
    unittest.main()
