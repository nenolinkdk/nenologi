import unittest

from nenologi import (
    AlignmentStatus, ControlledEnglishAnalyzer, DeterministicComparator,
    DeterministicPropositionAligner, DifferenceType, LogicalRelation,
    TemporalRelationType, UnsupportedConstructionError, analysis_from_json,
    analysis_to_json,
)


class SpatialCopularRelationsV01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    def test_gold_forms_create_binary_spatial_propositions(self) -> None:
        for text, predicate in (
            ("The key is inside the box.", "INSIDE"),
            ("The key is beside the box.", "BESIDE"),
        ):
            with self.subTest(text=text):
                result = self.analyzer.analyze(text)
                self.assertEqual(result.propositions[0].predicate, predicate)
                self.assertNotEqual(result.propositions[0].predicate, "BE")
                self.assertEqual(result.propositions[0].arguments, ("entity_001", "entity_002"))
                self.assertEqual([(e.type, e.label) for e in result.entities], [
                    ("ENTITY_CLASS", "key"), ("OBJECT", "box"),
                ])
                self.assertEqual(result.relations[0].type, "SPATIAL_RELATION")
                self.assertEqual(result.logical_representation[0].display, f"{predicate.title()}(Key, Box)")
                self.assertEqual(analysis_from_json(analysis_to_json(result)), result)

    def test_reference_and_subject_changes_reuse_entity_relation_comparison(self) -> None:
        reference = self.comparator.compare(
            self.analyzer.analyze("The key is inside the box."),
            self.analyzer.analyze("The key is inside the cabinet."),
        )
        self.assertEqual([d.difference_type for d in reference.differences], [DifferenceType.ENTITY_RELATION_CHANGE])
        self.assertEqual((reference.differences[0].source_value, reference.differences[0].target_value),
                         ("OBJECT:BOX", "OBJECT:CABINET"))
        subject = self.comparator.compare(
            self.analyzer.analyze("The key is inside the box."),
            self.analyzer.analyze("The book is inside the box."),
        )
        self.assertEqual((subject.differences[0].source_value, subject.differences[0].target_value),
                         ("SUBJECT:KEY", "SUBJECT:BOOK"))
        alignment = DeterministicPropositionAligner().align(
            self.analyzer.analyze("The key is inside the box."),
            self.analyzer.analyze("The key is inside the cabinet."),
            allow_structural_counterparts=True,
        )
        self.assertIs(alignment.alignments[0].status, AlignmentStatus.STRUCTURAL)

    def test_gold_relation_change_is_high_and_does_not_infer_contradiction(self) -> None:
        result = self.comparator.compare(
            self.analyzer.analyze("The key is inside the box."),
            self.analyzer.analyze("The key is beside the box."),
        )
        self.assertEqual([d.difference_type for d in result.differences], [DifferenceType.ENTITY_RELATION_CHANGE])
        self.assertEqual((result.differences[0].source_value, result.differences[0].target_value),
                         ("INSIDE", "BESIDE"))
        self.assertEqual(result.differences[0].severity.value, "HIGH")
        self.assertIs(result.logical_relation, LogicalRelation.UNDETERMINED)

    def test_copular_temporal_and_passive_paths_remain_distinct(self) -> None:
        copular = self.analyzer.analyze("The book is red.")
        self.assertEqual(copular.propositions[0].predicate, "RED")
        self.assertEqual(copular.propositions[0].arguments, ("entity_001",))
        temporal = self.analyzer.analyze("Pay the invoice on Monday.")
        self.assertIs(temporal.temporal_relations[0].relation, TemporalRelationType.ON)
        self.assertFalse(any(item.type == "SPATIAL_RELATION" for item in temporal.relations))
        passive = self.analyzer.analyze("The firm was acquired by the company.")
        self.assertEqual(passive.propositions[0].predicate, "ACQUIRE")
        self.assertFalse(any(item.type == "SPATIAL_RELATION" for item in passive.relations))

    def test_neighboring_spatial_constructions_are_rejected(self) -> None:
        cases = (
            "The book is very near the table.",
            "The book is two metres from the table.",
            "The book is between the table and the chair.",
            "The book is next to the table.",
            "The book is inside the box on the table.",
            "The book is on top of the table.",
            "The book is not inside the box.",
            "The book may be inside the box.",
            "The book is under the table.",
        )
        for text in cases:
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)

    def test_previous_grammar_and_repeated_parse_are_deterministic(self) -> None:
        cases = (
            "All employees must register.",
            "The company acquired the firm.",
            "The firm was acquired by the company.",
            "The valve isn't open.",
            "The key is inside the box.",
        )
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(self.analyzer.analyze(text), self.analyzer.analyze(text))


if __name__ == "__main__":
    unittest.main()
