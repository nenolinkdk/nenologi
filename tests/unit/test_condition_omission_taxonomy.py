import unittest

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator, DifferenceType, LogicalRelation

from .test_addition_omission import REGISTER, SUBMIT, make


class ConditionOmissionTaxonomyV01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    def compare(self, source: str, target: str):
        return self.comparator.compare(self.analyzer.analyze(source), self.analyzer.analyze(target))

    def test_exact_omission_001_is_one_condition_change(self) -> None:
        result = self.compare("Open the valve if the pressure is low.", "Open the valve.")
        self.assertEqual([d.difference_type for d in result.differences], [DifferenceType.CONDITION_CHANGE])
        self.assertEqual((result.differences[0].source_value, result.differences[0].target_value),
                         ("IF_LOW", "NONE"))
        self.assertIs(result.logical_relation, LogicalRelation.UNDETERMINED)

    def test_conditionalization_is_symmetric_and_never_duplicates_add_or_omit(self) -> None:
        conditional = "Open the valve if the pressure is low."
        unconditional = "Open the valve."
        for source, target, before, after in (
            (unconditional, conditional, "NONE", "IF_LOW"),
            (conditional, unconditional, "IF_LOW", "NONE"),
        ):
            with self.subTest(source=source):
                result = self.compare(source, target)
                self.assertEqual(len(result.differences), 1)
                self.assertIs(result.differences[0].difference_type, DifferenceType.CONDITION_CHANGE)
                self.assertEqual((result.differences[0].source_value, result.differences[0].target_value),
                                 (before, after))

    def test_real_unmatched_propositions_remain_addition_and_omission(self) -> None:
        one = make((("register", REGISTER),))
        two = make((("register", REGISTER), ("submit", SUBMIT)))
        self.assertEqual([d.difference_type for d in self.comparator.compare(one, two).differences],
                         [DifferenceType.ADDITION])
        self.assertEqual([d.difference_type for d in self.comparator.compare(two, one).differences],
                         [DifferenceType.OMISSION])

    def test_antecedent_and_consequent_changes_keep_specialized_taxonomy(self) -> None:
        antecedent = self.compare(
            "Open the valve if the pressure is low.",
            "Open the valve if the pressure is high.",
        )
        self.assertEqual([d.difference_type for d in antecedent.differences], [DifferenceType.CONDITION_CHANGE])
        consequent = self.compare(
            "You may enter if the light is green.",
            "You may stop if the light is green.",
        )
        self.assertEqual([d.difference_type for d in consequent.differences], [DifferenceType.ENTITY_RELATION_CHANGE])

    def test_numeric_anti_duplication_and_repeated_comparison_are_stable(self) -> None:
        source = self.analyzer.analyze("The system must stop if the temperature is above 30 °C.")
        target = self.analyzer.analyze("The system must stop if the temperature is at least 30 °C.")
        first = self.comparator.compare(source, target)
        second = self.comparator.compare(source, target)
        self.assertEqual(first, second)
        self.assertEqual([d.difference_type for d in first.differences], [DifferenceType.NUMERIC_THRESHOLD_CHANGE])


if __name__ == "__main__":
    unittest.main()
