import unittest

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DifferenceType,
    LogicalRelation, TemporalRelationType, UnsupportedConstructionError,
    analysis_from_json, analysis_to_json,
)


class TemporalRelationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()

    def compare(self, source: str, target: str):
        return self.comparator.compare(self.analyzer.analyze(source), self.analyzer.analyze(target))

    def test_relations_reference_normalization_formula_and_round_trip(self) -> None:
        for surface, normalized in (
            ("before", TemporalRelationType.BEFORE), ("after", TemporalRelationType.AFTER),
            ("on", TemporalRelationType.ON), ("until", TemporalRelationType.UNTIL),
        ):
            with self.subTest(surface=surface):
                result = self.analyzer.analyze(f"Employees must register {surface} fRiDaY.")
                temporal = result.temporal_relations[0]
                self.assertEqual(temporal.id, "temporal_001")
                self.assertEqual(temporal.proposition, "prop_001")
                self.assertIs(temporal.relation, normalized)
                self.assertEqual(temporal.temporal_reference, "Friday")
                self.assertIn("Friday", result.logical_representation[0].display)
                self.assertEqual(analysis_from_json(analysis_to_json(result)), result)

    def test_relation_transitions_and_reference_change(self) -> None:
        cases = (
            ("before Friday", "after Friday", "BEFORE", "AFTER"),
            ("after Friday", "before Friday", "AFTER", "BEFORE"),
            ("before Friday", "on Friday", "BEFORE", "ON"),
            ("before Friday", "before Monday", "BEFORE Friday", "BEFORE Monday"),
        )
        for source_phrase, target_phrase, before, after in cases:
            with self.subTest(source=source_phrase, target=target_phrase):
                result = self.compare(
                    f"Employees must register {source_phrase}.",
                    f"Employees must register {target_phrase}.",
                )
                self.assertEqual([item.difference_type for item in result.differences], [DifferenceType.TEMPORAL_CHANGE])
                self.assertEqual((result.differences[0].source_value, result.differences[0].target_value), (before, after))
                self.assertIs(result.logical_relation, LogicalRelation.UNDETERMINED)

    def test_added_removed_and_equivalent_temporal_relation(self) -> None:
        temporal = "Employees must register before Friday."
        plain = "Employees must register."
        removed = self.compare(temporal, plain)
        self.assertEqual([item.difference_type for item in removed.differences], [DifferenceType.TEMPORAL_CHANGE])
        self.assertEqual((removed.differences[0].source_value, removed.differences[0].target_value), ("BEFORE Friday", "NONE"))
        added = self.compare(plain, temporal)
        self.assertEqual([item.difference_type for item in added.differences], [DifferenceType.TEMPORAL_CHANGE])
        equivalent = self.compare("EMPLOYEES MUST REGISTER BEFORE FRIDAY", "Employees must register before Friday.")
        self.assertEqual(equivalent.differences, ())

    def test_modality_quantifier_and_temporal_finding_order(self) -> None:
        modality = self.compare(
            "Employees must register before Friday.", "Employees may register after Friday.",
        )
        self.assertEqual(
            [item.difference_type for item in modality.differences],
            [DifferenceType.MODALITY_CHANGE, DifferenceType.TEMPORAL_CHANGE],
        )
        quantified = self.compare(
            "All employees must register before Friday.", "Some employees must register after Friday.",
        )
        self.assertEqual(
            [item.difference_type for item in quantified.differences],
            [DifferenceType.QUANTIFIER_CHANGE, DifferenceType.TEMPORAL_CHANGE],
        )
        self.assertEqual([item.id for item in quantified.differences], ["difference_001", "difference_002"])

    def test_clock_time_is_temporal_not_numeric(self) -> None:
        source = self.analyzer.analyze("The system must stop before 18:00.")
        self.assertEqual(source.temporal_relations[0].temporal_reference, "18:00")
        self.assertEqual(source.numeric_constraints, ())
        result = self.compare("The system must stop before 18:00.", "The system must stop after 18:00.")
        self.assertEqual([item.difference_type for item in result.differences], [DifferenceType.TEMPORAL_CHANGE])
        self.assertIn("Before(Must(Stop(System)), 18:00)", result.source_analysis.logical_representation[0].display)

    def test_temporal_relation_in_condition_consequent(self) -> None:
        source = self.analyzer.analyze("If the light is green, the system must stop before Friday.")
        temporal = source.temporal_relations[0]
        self.assertEqual(temporal.proposition, "consequent_prop_001")
        self.assertIn("→ (Before(Must(Stop(System)), Friday))", source.logical_representation[0].display)
        result = self.compare(
            "If the light is green, the system must stop before Friday.",
            "If the light is green, the system must stop after Friday.",
        )
        self.assertEqual([item.difference_type for item in result.differences], [DifferenceType.TEMPORAL_CHANGE])

    def test_unsupported_temporal_forms_fail_explicitly(self) -> None:
        cases = (
            "Employees must register before Friday after Monday.",
            "Employees must register for three days.",
            "Employees must register on tomorrow.",
            "Employees must register before.",
            "Employees must register by Friday.",
            "Employees must register before or on Friday.",
        )
        for text in cases:
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)


if __name__ == "__main__":
    unittest.main()
