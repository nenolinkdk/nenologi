import unittest

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DifferenceType,
    UnsupportedConstructionError, analysis_from_json, analysis_to_json,
)


class SimplePastTransitiveV01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    def test_regular_forms_normalize_to_canonical_predicates_and_entities(self) -> None:
        cases = (
            ("The board approved the proposal.", "APPROVE", "board", "proposal"),
            ("The scientist discovered the method.", "DISCOVER", "scientist", "method"),
            ("The company acquired the firm.", "ACQUIRE", "company", "firm"),
            ("The office opened the file.", "OPEN", "office", "file"),
            ("The employee registered the visitor.", "REGISTER", "employee", "visitor"),
        )
        for text, predicate, subject, object_label in cases:
            with self.subTest(text=text):
                result = self.analyzer.analyze(text)
                self.assertEqual(result.propositions[0].predicate, predicate)
                self.assertEqual(result.entities[0].label, subject)
                self.assertEqual(result.entities[1].label, object_label)
                self.assertEqual(analysis_from_json(analysis_to_json(result)), result)

    def test_explicit_irregular_forms(self) -> None:
        cases = (
            ("The company sold the division.", "SELL"),
            ("The company bought the division.", "BUY"),
            ("The company made the product.", "MAKE"),
        )
        for text, predicate in cases:
            with self.subTest(text=text):
                self.assertEqual(self.analyzer.analyze(text).propositions[0].predicate, predicate)

    def test_present_and_past_share_core_identity(self) -> None:
        present = self.analyzer.analyze("Companies acquire the firm.")
        past = self.analyzer.analyze("Companies acquired the firm.")
        self.assertEqual(present.propositions[0].predicate, past.propositions[0].predicate)
        self.assertEqual(
            [(item.type, item.label) for item in present.entities],
            [(item.type, item.label) for item in past.entities],
        )
        self.assertEqual(self.comparator.compare(present, past).differences, ())

    def test_past_subject_and_object_changes_use_existing_comparator(self) -> None:
        object_change = self.comparator.compare(
            self.analyzer.analyze("Alice approved the request."),
            self.analyzer.analyze("Alice approved the invoice."),
        )
        self.assertEqual([item.difference_type for item in object_change.differences], [DifferenceType.ENTITY_RELATION_CHANGE])
        self.assertEqual((object_change.differences[0].source_value, object_change.differences[0].target_value), ("OBJECT:REQUEST", "OBJECT:INVOICE"))
        subject_change = self.comparator.compare(
            self.analyzer.analyze("Alice approved the request."),
            self.analyzer.analyze("Bob approved the request."),
        )
        self.assertEqual((subject_change.differences[0].source_value, subject_change.differences[0].target_value), ("SUBJECT:ALICE", "SUBJECT:BOB"))

    def test_neighboring_past_constructions_remain_explicitly_unsupported(self) -> None:
        cases = (
            "The company has acquired the firm.",
            "The company had acquired the firm.",
            "The company was acquiring the firm.",
            "The company did not acquire the firm.",
            "The company walked the route.",
        )
        for text in cases:
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)


if __name__ == "__main__":
    unittest.main()
