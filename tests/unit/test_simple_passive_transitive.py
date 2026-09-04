import unittest

from nenologi import (
    AlignmentStatus, ControlledEnglishAnalyzer, DeterministicComparator,
    DeterministicPropositionAligner, DifferenceType, LogicalRelation,
    UnsupportedConstructionError, analysis_from_json, analysis_to_json,
)


class SimplePassiveTransitiveV02Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    def test_supported_regular_and_irregular_participles_use_canonical_predicates(self) -> None:
        cases = (
            ("The firm was acquired by the company.", "ACQUIRE", "company", "firm"),
            ("The division was sold by the company.", "SELL", "company", "division"),
            ("The proposal was approved by the board.", "APPROVE", "board", "proposal"),
            ("The division was bought by the company.", "BUY", "company", "division"),
            ("The product was made by the company.", "MAKE", "company", "product"),
        )
        for text, predicate, agent, patient in cases:
            with self.subTest(text=text):
                result = self.analyzer.analyze(text)
                self.assertEqual(result.propositions[0].predicate, predicate)
                self.assertNotEqual(result.propositions[0].predicate, "BE")
                self.assertEqual([(e.type, e.label) for e in result.entities], [
                    ("ENTITY_CLASS", agent), ("OBJECT", patient),
                ])
                self.assertEqual(result.propositions[0].arguments, ("entity_001", "entity_002"))
                self.assertEqual(analysis_from_json(analysis_to_json(result)), result)

    def test_active_and_passive_share_identity_align_and_compare_equivalent(self) -> None:
        active = self.analyzer.analyze("Alice approved the request.")
        passive = self.analyzer.analyze("The request was approved by Alice.")
        self.assertEqual(active.propositions[0].predicate, passive.propositions[0].predicate)
        self.assertEqual(
            [(e.type, e.label) for e in active.entities],
            [(e.type, e.label) for e in passive.entities],
        )
        alignment = DeterministicPropositionAligner().align(active, passive)
        self.assertEqual(len(alignment.alignments), 1)
        self.assertIs(alignment.alignments[0].status, AlignmentStatus.EXACT)
        comparison = self.comparator.compare(active, passive)
        self.assertEqual(comparison.differences, ())
        self.assertIs(comparison.logical_relation, LogicalRelation.EQUIVALENT)

    def test_passive_argument_changes_use_existing_entity_relation_change(self) -> None:
        patient = self.comparator.compare(
            self.analyzer.analyze("The firm was acquired by the company."),
            self.analyzer.analyze("The subsidiary was acquired by the company."),
        )
        self.assertEqual([d.difference_type for d in patient.differences], [DifferenceType.ENTITY_RELATION_CHANGE])
        self.assertEqual((patient.differences[0].source_value, patient.differences[0].target_value),
                         ("OBJECT:FIRM", "OBJECT:SUBSIDIARY"))
        agent = self.comparator.compare(
            self.analyzer.analyze("The firm was acquired by the company."),
            self.analyzer.analyze("The firm was acquired by the board."),
        )
        self.assertEqual((agent.differences[0].source_value, agent.differences[0].target_value),
                         ("SUBJECT:COMPANY", "SUBJECT:BOARD"))

    def test_copular_behavior_remains_distinct(self) -> None:
        copular = self.analyzer.analyze("The proposal is approved.")
        self.assertEqual(copular.propositions[0].arguments, ("entity_001",))
        self.assertEqual(len(copular.entities), 1)
        self.assertEqual(copular.relations, ())

    def test_neighboring_passives_are_explicitly_rejected(self) -> None:
        cases = (
            "The firm was acquired.",
            "The firm has been acquired by the company.",
            "The firm had been acquired by the company.",
            "The firm was being acquired by the company.",
            "The firm must be acquired by the company.",
            "The firm will be acquired by the company.",
            "The firm was believed to be profitable by the company.",
            "The firm was invented by the company.",
            "The firm was acquired by.",
            "The firms were acquired by the company.",
        )
        for text in cases:
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)

    def test_output_is_deterministic(self) -> None:
        text = "The request was approved by Alice."
        self.assertEqual(analysis_to_json(self.analyzer.analyze(text)), analysis_to_json(self.analyzer.analyze(text)))


if __name__ == "__main__":
    unittest.main()
