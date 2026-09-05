import unittest

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicPropositionAligner,
    DifferenceType, LogicalRelation, UnsupportedConstructionError,
    analysis_from_json, analysis_to_json,
)


class SuffixIfConditionsV01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    @staticmethod
    def semantic_projection(analysis):
        return (
            [(e.id, e.type, e.label) for e in analysis.entities],
            [(p.id, p.predicate, p.arguments) for p in analysis.propositions],
            [(r.id, r.type, r.arguments, r.derived_from) for r in analysis.relations],
            [(o.id, o.operator, o.scope) for o in analysis.quantifiers],
            [(o.id, o.operator, o.scope) for o in analysis.modality],
            [(o.id, o.operator, o.scope) for o in analysis.negation],
            [(c.id, c.antecedent, c.consequent) for c in analysis.conditions],
            [(n.id, n.operator, n.value, n.scope) for n in analysis.numeric_constraints],
            analysis.logical_representation[0].expression,
            analysis.logical_representation[0].display,
        )

    def test_gold_suffix_creates_normalized_condition_and_round_trips(self) -> None:
        result = self.analyzer.analyze("Submit the report if the test passes.")
        condition = result.conditions[0]
        self.assertEqual(condition.antecedent, ("antecedent_prop_001",))
        self.assertEqual(condition.consequent, ("consequent_prop_001",))
        self.assertEqual([(p.id, p.predicate) for p in result.propositions], [
            ("antecedent_prop_001", "PASS"), ("consequent_prop_001", "SUBMIT"),
        ])
        self.assertEqual(analysis_from_json(analysis_to_json(result)), result)
        without_period = self.analyzer.analyze("Submit the report if the test passes")
        self.assertEqual(self.semantic_projection(result), self.semantic_projection(without_period))

    def test_prefix_and_suffix_are_semantically_equivalent_and_align(self) -> None:
        prefix = self.analyzer.analyze("If the light is green, you may enter.")
        suffix = self.analyzer.analyze("You may enter if the light is green.")
        self.assertEqual(self.semantic_projection(prefix), self.semantic_projection(suffix))
        alignment = DeterministicPropositionAligner().align(prefix, suffix)
        self.assertEqual(len(alignment.alignments), 2)
        comparison = self.comparator.compare(prefix, suffix)
        self.assertEqual(comparison.differences, ())
        self.assertIs(comparison.logical_relation, LogicalRelation.EQUIVALENT)

    def test_changed_suffix_antecedent_and_consequent_reuse_existing_rules(self) -> None:
        antecedent = self.comparator.compare(
            self.analyzer.analyze("You may enter if the light is green."),
            self.analyzer.analyze("You may enter if the light is red."),
        )
        self.assertEqual([d.difference_type for d in antecedent.differences], [DifferenceType.CONDITION_CHANGE])
        self.assertEqual((antecedent.differences[0].source_value, antecedent.differences[0].target_value),
                         ("IF_GREEN", "IF_RED"))
        consequent = self.comparator.compare(
            self.analyzer.analyze("You may enter if the light is green."),
            self.analyzer.analyze("You must enter if the light is green."),
        )
        self.assertEqual([d.difference_type for d in consequent.differences], [DifferenceType.MODALITY_CHANGE])

    def test_numeric_antecedent_change_has_no_duplicate_condition_finding(self) -> None:
        result = self.comparator.compare(
            self.analyzer.analyze("The system must stop if the temperature is above 30 °C."),
            self.analyzer.analyze("The system must stop if the temperature is at least 30 °C."),
        )
        self.assertEqual([d.difference_type for d in result.differences], [DifferenceType.NUMERIC_THRESHOLD_CHANGE])

    def test_modality_negation_scope_and_temporal_consequent_match_prefix(self) -> None:
        pairs = (
            ("If the light is green, all operators must not restart the server.",
             "All operators must not restart the server if the light is green."),
            ("If the light is green, the system must stop before Friday.",
             "The system must stop before Friday if the light is green."),
        )
        for prefix_text, suffix_text in pairs:
            with self.subTest(suffix=suffix_text):
                prefix = self.analyzer.analyze(prefix_text)
                suffix = self.analyzer.analyze(suffix_text)
                self.assertEqual(self.semantic_projection(prefix), self.semantic_projection(suffix))

    def test_unsupported_if_neighbors_and_previous_grammar(self) -> None:
        unsupported = (
            "Submit the report if the test passes if the light is green.",
            "If the test passes, submit the report if the light is green.",
            "The manager asked if the system was ready.",
            "Submit the report unless the test passes.",
            "What happens if the system fails?",
            "Submit the report, if the test passes.",
        )
        for text in unsupported:
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)
        regressions = (
            "All employees must register.", "The company acquired the firm.",
            "The firm was acquired by the company.", "The valve isn't open.",
            "The key is inside the box.", "Pay the invoice before Monday.",
            "The gift is open.",
        )
        for text in regressions:
            with self.subTest(text=text):
                self.assertEqual(self.analyzer.analyze(text), self.analyzer.analyze(text))


if __name__ == "__main__":
    unittest.main()
