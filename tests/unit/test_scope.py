import unittest
from dataclasses import replace

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DifferenceType,
    LogicalExpression, LogicalRelation, Operator, UnsupportedConstructionError,
    analysis_from_json, analysis_to_json,
)

from .support import employee_analysis


class ScopeV01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    def test_controlled_not_all_contrast_has_explicit_scope_and_formula(self) -> None:
        outer_not = self.analyzer.analyze("Not all employees must register.")
        inner_not = self.analyzer.analyze("All employees must not register.")
        self.assertEqual(outer_not.negation[0].scope, ("quantifier_001",))
        self.assertEqual(outer_not.quantifiers[0].scope, ("modality_001",))
        self.assertEqual(inner_not.quantifiers[0].scope, ("modality_001",))
        self.assertEqual(inner_not.modality[0].scope, ("negation_001",))
        self.assertEqual(outer_not.logical_representation[0].display, "¬∀x (Employee(x) → Must(Register(x)))")
        self.assertEqual(inner_not.logical_representation[0].display, "∀x (Employee(x) → Must(¬Register(x)))")
        result = self.comparator.compare(outer_not, inner_not)
        self.assertEqual([item.difference_type for item in result.differences], [DifferenceType.SCOPE_CHANGE])
        self.assertIs(result.logical_relation, LogicalRelation.UNDETERMINED)
        self.assertIn("No logical consequence", result.differences[0].explanation)

    def test_identical_scope_has_no_difference(self) -> None:
        analysis = self.analyzer.analyze("Not all employees must register.")
        self.assertEqual(self.comparator.compare(analysis, analysis).differences, ())

    def test_domain_scope_comparison_is_parser_independent_and_not_duplicated(self) -> None:
        base = employee_analysis()
        confidence = base.confidence
        not_all = replace(
            base,
            quantifiers=(replace(base.quantifiers[0], scope=("modality_001",)),),
            modality=(replace(base.modality[0], scope=("prop_001",)),),
            negation=(Operator("negation_001", "NOT", ("quantifier_001",), base.quantifiers[0].interpretation_status, confidence),),
        )
        all_not = replace(
            base,
            quantifiers=(replace(base.quantifiers[0], scope=("modality_001",)),),
            modality=(replace(base.modality[0], scope=("negation_001",)),),
            negation=(Operator("negation_001", "NOT", ("prop_001",), base.quantifiers[0].interpretation_status, confidence),),
        )
        result = self.comparator.compare(not_all, all_not)
        self.assertEqual([item.difference_type for item in result.differences], [DifferenceType.SCOPE_CHANGE])
        changed_quantifier = replace(all_not, quantifiers=(replace(all_not.quantifiers[0], operator="SOME"),))
        combined = self.comparator.compare(not_all, changed_quantifier)
        self.assertEqual(
            [item.difference_type for item in combined.differences],
            [DifferenceType.QUANTIFIER_CHANGE, DifferenceType.SCOPE_CHANGE],
        )

    def test_modality_negation_scope_and_round_trip(self) -> None:
        base = employee_analysis()
        confidence = base.confidence
        status = base.quantifiers[0].interpretation_status
        not_must = replace(
            base,
            modality=(replace(base.modality[0], scope=("prop_001",)),),
            negation=(Operator("negation_001", "NOT", ("modality_001",), status, confidence),),
            logical_representation=(LogicalExpression(
                "logic_001", {"operator": "NOT", "arguments": ["modality_001"]}, status, confidence,
                "¬Must(Register(x))", ("prop_001", "modality_001", "negation_001"),
            ),),
        )
        must_not = replace(
            not_must,
            modality=(replace(base.modality[0], scope=("negation_001",)),),
            negation=(replace(not_must.negation[0], scope=("prop_001",)),),
        )
        restored = analysis_from_json(analysis_to_json(not_must))
        self.assertEqual(restored, not_must)
        self.assertEqual(
            [item.difference_type for item in self.comparator.compare(not_must, must_not).differences],
            [DifferenceType.SCOPE_CHANGE],
        )

    def test_actual_negation_add_remove_remains_negation_change(self) -> None:
        affirmed = self.analyzer.analyze("All employees must register.")
        negated = self.analyzer.analyze("All employees must not register.")
        self.assertEqual(
            [item.difference_type for item in self.comparator.compare(affirmed, negated).differences],
            [DifferenceType.NEGATION_CHANGE],
        )

    def test_unsupported_scope_is_rejected(self) -> None:
        for text in ("Not some employees must register.", "All employees may possibly not register."):
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)


if __name__ == "__main__":
    unittest.main()
