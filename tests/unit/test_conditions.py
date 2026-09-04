import unittest

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DifferenceType,
    LogicalRelation, NumericOperator, UnsupportedConstructionError,
    analysis_from_json, analysis_to_json,
)


class ConditionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    def compare(self, source: str, target: str):
        return self.comparator.compare(self.analyzer.analyze(source), self.analyzer.analyze(target))

    def test_simple_if_has_normalized_roles_ids_formula_and_round_trip(self) -> None:
        text = "If the light is green, you may enter."
        result = self.analyzer.analyze(text)
        condition = result.conditions[0]
        self.assertEqual(condition.id, "condition_001")
        self.assertEqual(condition.antecedent, ("antecedent_prop_001",))
        self.assertEqual(condition.consequent, ("consequent_prop_001",))
        self.assertEqual(result.propositions[0].predicate, "GREEN")
        self.assertEqual(result.propositions[1].predicate, "ENTER")
        self.assertEqual(result.modality[0].scope, ("consequent_prop_001",))
        self.assertEqual(result.modality[0].operator, "MAY")
        self.assertEqual(result.logical_representation[0].display, "(Green(Light)) → (May(Enter(You)))")
        self.assertEqual(analysis_from_json(analysis_to_json(result)), result)
        self.assertEqual(self.analyzer.analyze(text), result)

    def test_condition_removed_and_added_are_single_condition_findings(self) -> None:
        conditional = "If the light is green, you may enter."
        plain = "You may enter."
        removed = self.compare(conditional, plain)
        self.assertEqual([item.difference_type for item in removed.differences], [DifferenceType.CONDITION_CHANGE])
        self.assertEqual((removed.differences[0].source_value, removed.differences[0].target_value), ("IF_GREEN", "NONE"))
        self.assertIs(removed.logical_relation, LogicalRelation.UNDETERMINED)
        added = self.compare(plain, conditional)
        self.assertEqual([item.difference_type for item in added.differences], [DifferenceType.CONDITION_CHANGE])
        self.assertEqual((added.differences[0].source_value, added.differences[0].target_value), ("NONE", "IF_GREEN"))

    def test_changed_and_unchanged_property_antecedent(self) -> None:
        changed = self.compare(
            "If the light is green, employees must register.",
            "If the light is red, employees must register.",
        )
        self.assertEqual([item.difference_type for item in changed.differences], [DifferenceType.CONDITION_CHANGE])
        self.assertEqual((changed.differences[0].source_value, changed.differences[0].target_value), ("IF_GREEN", "IF_RED"))
        unchanged = self.compare(
            " IF the light is green, employees must register ",
            "If the light is green, employees must register.",
        )
        self.assertEqual(unchanged.differences, ())

    def test_numeric_antecedent_reuses_normalization_without_double_counting(self) -> None:
        source = "If the temperature is at least 30 °C, the system must stop."
        equivalent = "If the temperature is >= 30.0 °C, the system must stop."
        first = self.analyzer.analyze(source)
        constraint = first.numeric_constraints[0]
        self.assertIs(constraint.operator, NumericOperator.GREATER_THAN_OR_EQUAL)
        self.assertEqual(constraint.scope, ("antecedent_prop_001",))
        self.assertEqual(constraint.unit, "°C")
        self.assertIn("Temperature(x) ≥ 30 °C", first.logical_representation[0].display)
        self.assertEqual(self.compare(source, equivalent).differences, ())
        changed = self.compare(
            "If the temperature is above 30°C, the system must stop.", source,
        )
        self.assertEqual([item.difference_type for item in changed.differences], [DifferenceType.NUMERIC_THRESHOLD_CHANGE])
        self.assertEqual((changed.differences[0].source_value, changed.differences[0].target_value), ("> 30", ">= 30"))

    def test_consequent_modality_and_stable_order(self) -> None:
        changed = self.compare(
            "The system must stop.",
            "If the temperature is above 30 °C, the system may stop.",
        )
        self.assertEqual(
            [item.difference_type for item in changed.differences],
            [DifferenceType.MODALITY_CHANGE, DifferenceType.CONDITION_CHANGE],
        )
        self.assertEqual([item.id for item in changed.differences], ["difference_001", "difference_002"])

    def test_unsupported_condition_forms_fail_explicitly(self) -> None:
        cases = (
            "If the light is green, if employees register, the system stops.",
            "If the light is green and the door is open, employees may enter.",
            "If the light is green employees may enter.",
            "If users may not enter, the system must stop.",
            "Employees may enter unless the light is red.",
        )
        for text in cases:
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)


if __name__ == "__main__":
    unittest.main()
