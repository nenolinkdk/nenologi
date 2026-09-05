import unittest
from dataclasses import replace

from nenologi import (
    CANONICAL_DIFFERENCE_ORDER, ControlledEnglishAnalyzer, DeterministicComparator,
    DifferenceType, LogicalRelation, Operator, analysis_from_json, analysis_to_json,
)
from tests.unit.support import employee_analysis
from tests.validation.audit_gold_coverage import ImplementationStatus, audit_gold_coverage


class SemanticConsolidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    def compare(self, source: str, target: str):
        return self.comparator.compare(self.analyzer.analyze(source), self.analyzer.analyze(target))

    def test_canonical_order_covers_the_complete_difference_taxonomy(self) -> None:
        self.assertEqual(set(CANONICAL_DIFFERENCE_ORDER), set(DifferenceType))
        self.assertEqual(
            CANONICAL_DIFFERENCE_ORDER,
            (
                DifferenceType.QUANTIFIER_CHANGE, DifferenceType.MODALITY_CHANGE,
                DifferenceType.NEGATION_CHANGE, DifferenceType.CONJUNCTION_CHANGE,
                DifferenceType.NUMERIC_THRESHOLD_CHANGE, DifferenceType.CONDITION_CHANGE,
                DifferenceType.TEMPORAL_CHANGE, DifferenceType.SCOPE_CHANGE,
                DifferenceType.ENTITY_RELATION_CHANGE, DifferenceType.ADDITION,
                DifferenceType.OMISSION,
            ),
        )
        self.assertNotIn("CONTRADICTION", {item.value for item in DifferenceType})

    def test_cross_dimension_regression_matrix(self) -> None:
        cases = (
            (
                "All employees must register.", "Some employees may register.",
                [DifferenceType.QUANTIFIER_CHANGE, DifferenceType.MODALITY_CHANGE],
            ),
            (
                "Employees must register before Friday.", "Employees may register after Friday.",
                [DifferenceType.MODALITY_CHANGE, DifferenceType.TEMPORAL_CHANGE],
            ),
            (
                "All scores must be at least 18.", "Some scores must be more than 21.",
                [DifferenceType.QUANTIFIER_CHANGE, DifferenceType.NUMERIC_THRESHOLD_CHANGE],
            ),
            (
                "If the light is green, employees must register.",
                "If the light is green, employees may register.",
                [DifferenceType.MODALITY_CHANGE],
            ),
            (
                "If the temperature is above 30°C, the system must stop.",
                "If the temperature is at least 30°C, the system must stop.",
                [DifferenceType.NUMERIC_THRESHOLD_CHANGE],
            ),
            (
                "If the light is green, the system must stop before Friday.",
                "If the light is green, the system must stop after Friday.",
                [DifferenceType.TEMPORAL_CHANGE],
            ),
            (
                "All patients must receive treatment A and treatment B.",
                "Some patients may receive treatment A or treatment B.",
                [DifferenceType.QUANTIFIER_CHANGE, DifferenceType.MODALITY_CHANGE, DifferenceType.CONJUNCTION_CHANGE],
            ),
            (
                "All employees must register before Friday.",
                "Some employees must register after Friday.",
                [DifferenceType.QUANTIFIER_CHANGE, DifferenceType.TEMPORAL_CHANGE],
            ),
            (
                "All employees must submit the report.",
                "All employees may submit the form.",
                [DifferenceType.MODALITY_CHANGE, DifferenceType.ENTITY_RELATION_CHANGE],
            ),
        )
        for source, target, expected in cases:
            with self.subTest(source=source, target=target):
                result = self.compare(source, target)
                self.assertEqual([item.difference_type for item in result.differences], expected)
                self.assertEqual(
                    [item.id for item in result.differences],
                    [f"difference_{index:03d}" for index in range(1, len(expected) + 1)],
                )

    def test_known_changes_are_not_double_counted(self) -> None:
        cases = (
            (
                "If the light is green, employees must register.", "Employees must register.",
                [DifferenceType.CONDITION_CHANGE],
            ),
            (
                "Employees must register before Friday.", "Employees must register.",
                [DifferenceType.TEMPORAL_CHANGE],
            ),
            (
                "If the temperature is above 30°C, the system must stop.",
                "If the temperature is at least 30°C, the system must stop.",
                [DifferenceType.NUMERIC_THRESHOLD_CHANGE],
            ),
        )
        for source, target, expected in cases:
            with self.subTest(source=source):
                self.assertEqual([item.difference_type for item in self.compare(source, target).differences], expected)
        polarity = self.compare("The switch is on.", "The switch is not on.")
        self.assertEqual([item.difference_type for item in polarity.differences], [DifferenceType.NEGATION_CHANGE])
        self.assertIs(polarity.logical_relation, LogicalRelation.CONTRADICTORY)

    def test_rich_analysis_round_trip_preserves_ids_and_references(self) -> None:
        text = "If the temperature is at least 30°C, all systems must stop before Friday."
        analysis = self.analyzer.analyze(text)
        restored = analysis_from_json(analysis_to_json(analysis))
        self.assertEqual(restored, analysis)
        self.assertEqual([item.id for item in restored.all_identified_objects()], [item.id for item in analysis.all_identified_objects()])
        condition = restored.conditions[0]
        self.assertEqual(condition.antecedent, ("antecedent_prop_001",))
        self.assertEqual(condition.consequent, ("consequent_prop_001",))
        self.assertEqual(restored.numeric_constraints[0].scope, condition.antecedent)
        self.assertEqual(restored.quantifiers[0].scope, condition.consequent)
        self.assertEqual(restored.modality[0].scope, condition.consequent)
        self.assertEqual(restored.temporal_relations[0].proposition, condition.consequent[0])

    def test_normalized_equivalence_and_conservative_logical_relations(self) -> None:
        equivalent_pairs = (
            ("Every employee must register.", "All employees must register."),
            ("The score must be at least 18.", "The score must be >= 18.0."),
            ("Employees must register before fRiDaY.", "EMPLOYEES MUST REGISTER BEFORE FRIDAY"),
        )
        for source, target in equivalent_pairs:
            with self.subTest(source=source):
                result = self.compare(source, target)
                self.assertEqual(result.differences, ())
                self.assertIs(result.logical_relation, LogicalRelation.EQUIVALENT)
        self.assertEqual(self.analyzer.analyze("The system must stop before 18:00.").numeric_constraints, ())
        changed_pairs = (
            ("The score must be more than 18.", "The score must be at least 18."),
            ("Employees must register before Friday.", "Employees must register after Friday."),
            ("All patients must receive treatment A and treatment B.", "All patients must receive treatment A or treatment B."),
        )
        for source, target in changed_pairs:
            with self.subTest(source=source):
                self.assertIs(self.compare(source, target).logical_relation, LogicalRelation.UNDETERMINED)

    def test_explanations_are_deterministic_and_separate_severity_from_confidence(self) -> None:
        pairs = (
            ("All employees must register.", "Some employees must register."),
            ("All employees must register.", "All employees may register."),
            ("The switch is on.", "The switch is not on."),
            ("All patients must receive treatment A and treatment B.", "All patients must receive treatment A or treatment B."),
            ("The score must be more than 18.", "The score must be at least 18."),
            ("If the light is green, employees must register.", "Employees must register."),
            ("Employees must register before Friday.", "Employees must register after Friday."),
            ("All employees must submit the report.", "All employees must submit the form."),
        )
        findings = [self.compare(source, target).differences[0] for source, target in pairs]
        self.assertEqual(
            {finding.difference_type for finding in findings},
            {
                DifferenceType.QUANTIFIER_CHANGE, DifferenceType.MODALITY_CHANGE,
                DifferenceType.NEGATION_CHANGE, DifferenceType.CONJUNCTION_CHANGE,
                DifferenceType.NUMERIC_THRESHOLD_CHANGE, DifferenceType.CONDITION_CHANGE,
                DifferenceType.TEMPORAL_CHANGE, DifferenceType.ENTITY_RELATION_CHANGE,
            },
        )
        numeric = next(item for item in findings if item.difference_type is DifferenceType.NUMERIC_THRESHOLD_CHANGE)
        temporal = next(item for item in findings if item.difference_type is DifferenceType.TEMPORAL_CHANGE)
        self.assertIn("from > 18 to >= 18", numeric.explanation)
        self.assertIn("from BEFORE to AFTER", temporal.explanation)
        self.assertEqual(numeric.severity.value, "MEDIUM")
        for finding in findings:
            self.assertEqual(finding.confidence.value, 1.0)
            self.assertIn(finding.severity.value, {"MEDIUM", "HIGH"})
            self.assertTrue(finding.explanation)

    def test_reproducible_gold_audit_breakdown(self) -> None:
        audit = audit_gold_coverage()
        self.assertEqual(sum(audit.totals.values()), 42)
        self.assertEqual(audit.totals[ImplementationStatus.END_TO_END_EXACT], 23)
        self.assertEqual(audit.totals[ImplementationStatus.ANALYZABLE_BUT_NOT_EXACT], 0)
        self.assertEqual(audit.totals[ImplementationStatus.PARSER_UNSUPPORTED], 10)
        self.assertEqual(audit.totals[ImplementationStatus.COMPARATOR_UNSUPPORTED], 2)
        self.assertEqual(audit.totals[ImplementationStatus.INFERENCE_NOT_IMPLEMENTED], 7)
        self.assertEqual(len(audit.cases), 42)
        self.assertEqual(len({item["case_id"] for item in audit.cases}), 42)
        self.assertFalse(any(
            str(item["blocking_reason"]).startswith("UNCLASSIFIED_") for item in audit.cases
        ))
        for item in audit.cases:
            self.assertIn("parser", item)
            self.assertIn("analysis", item)
            self.assertIn("alignment", item)
            self.assertIn("comparator", item)
            self.assertIn("inference", item)
            self.assertIn("final_status", item)

    def test_comparator_accepts_normalized_models_without_parser_dependency(self) -> None:
        source = employee_analysis("MUST")
        original = source.modality[0]
        target = replace(
            source,
            modality=(Operator(
                original.id, "MAY", original.scope, original.interpretation_status,
                original.confidence, original.span,
            ),),
        )
        result = self.comparator.compare(source, target)
        self.assertEqual([item.difference_type for item in result.differences], [DifferenceType.MODALITY_CHANGE])


if __name__ == "__main__":
    unittest.main()
