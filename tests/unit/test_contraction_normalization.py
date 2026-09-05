import unittest

from nenologi import (
    AlignmentStatus, ControlledEnglishAnalyzer, DeterministicComparator,
    DeterministicPropositionAligner, LogicalRelation, UnsupportedConstructionError,
    analysis_from_json, analysis_to_json,
)


class ContractionNormalizationV03Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()

    @staticmethod
    def semantic_projection(analysis):
        return (
            [(item.type, item.label) for item in analysis.entities],
            [(item.predicate, item.arguments) for item in analysis.propositions],
            [(item.operator, item.scope) for item in analysis.quantifiers],
            [(item.operator, item.scope) for item in analysis.modality],
            [(item.operator, item.scope) for item in analysis.negation],
            [item.display for item in analysis.logical_representation],
        )

    def test_gold_contraction_and_both_apostrophes_match_expanded_semantics(self) -> None:
        expanded = self.analyzer.analyze("The valve is not open.")
        for text in ("The valve isn't open.", "The valve isn’t open."):
            with self.subTest(text=text):
                contracted = self.analyzer.analyze(text)
                self.assertEqual(self.semantic_projection(contracted), self.semantic_projection(expanded))
                self.assertEqual(contracted.negation[0].operator, "NOT")
                self.assertEqual(contracted.negation[0].scope, ("prop_001",))
                self.assertEqual(analysis_from_json(analysis_to_json(contracted)), contracted)

    def test_direct_plural_variant_has_identical_operator_topology(self) -> None:
        expanded = self.analyzer.analyze("The valves are not open.")
        for text in ("The valves aren't open.", "The valves aren’t open."):
            with self.subTest(text=text):
                self.assertEqual(self.semantic_projection(self.analyzer.analyze(text)), self.semantic_projection(expanded))

    def test_gold_pair_aligns_exactly_and_compares_equivalent(self) -> None:
        source = self.analyzer.analyze("The valve is not open.")
        target = self.analyzer.analyze("The valve isn't open.")
        alignment = DeterministicPropositionAligner().align(source, target)
        self.assertEqual(len(alignment.alignments), 1)
        self.assertIs(alignment.alignments[0].status, AlignmentStatus.EXACT)
        comparison = DeterministicComparator().compare(source, target)
        self.assertEqual(comparison.differences, ())
        self.assertIs(comparison.logical_relation, LogicalRelation.EQUIVALENT)

    def test_ambiguous_possessive_unknown_informal_and_multiple_forms_are_rejected(self) -> None:
        cases = (
            "He'd open the valve.",
            "She's open.",
            "The company's policy is open.",
            "The valve won't open.",
            "The valve ain't open.",
            "The valve gonna open.",
            "The valve isn't isn't open.",
            "The valve isn'ty open.",
        )
        for text in cases:
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)

    def test_non_contracted_and_previous_grammar_remain_deterministic(self) -> None:
        cases = (
            "The valve is not open.",
            "All employees must register.",
            "All employees must not register.",
            "Not all employees must register.",
            "The company acquired the firm.",
            "The firm was acquired by the company.",
        )
        for text in cases:
            with self.subTest(text=text):
                first = self.analyzer.analyze(text)
                second = self.analyzer.analyze(text)
                self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
