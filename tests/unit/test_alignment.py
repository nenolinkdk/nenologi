import unittest
from dataclasses import replace

from nenologi import (
    AlignmentStatus, Analysis, Condition, Confidence, ControlledEnglishAnalyzer,
    DeterministicComparator, DeterministicPropositionAligner, Document, Entity,
    InterpretationStatus, LocalizedText, Proposition, UnsupportedComparisonError,
)


CONFIDENCE = Confidence(1.0, "Manual normalized fixture")
STATUS = InterpretationStatus.EXPLICIT


def analysis_with(specifications, *, antecedent=None, consequent=None) -> Analysis:
    entities = []
    propositions = []
    for prop_id, predicate, arguments in specifications:
        refs = []
        for position, (entity_type, label) in enumerate(arguments, 1):
            entity_id = f"{prop_id}_entity_{position:03d}"
            entities.append(Entity(entity_id, entity_type, label, STATUS, CONFIDENCE))
            refs.append(entity_id)
        propositions.append(Proposition(prop_id, predicate, tuple(refs), STATUS, CONFIDENCE))
    conditions = ()
    if antecedent and consequent:
        conditions = (Condition("condition_001", (antecedent,), (consequent,), STATUS, CONFIDENCE),)
    return Analysis(
        document=Document("doc_001", "en", "Normalized fixture"), profile="general",
        entities=tuple(entities), propositions=tuple(propositions), conditions=conditions,
        confidence=CONFIDENCE,
        plain_language_interpretation=LocalizedText("en", "Normalized fixture."),
    )


class PropositionAlignmentV01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.aligner = DeterministicPropositionAligner()

    def assert_single_exact(self, source_text, target_text) -> None:
        result = self.aligner.align(self.analyzer.analyze(source_text), self.analyzer.analyze(target_text))
        self.assertEqual(len(result.alignments), 1)
        self.assertIs(result.alignments[0].status, AlignmentStatus.EXACT)
        self.assertEqual(result.unaligned_source_ids, ())
        self.assertEqual(result.unaligned_target_ids, ())

    def test_identity_and_operator_changes_do_not_block_alignment(self) -> None:
        pairs = (
            ("All employees must register.", "All employees must register."),
            ("All employees must register.", "Some employees must register."),
            ("All employees must register.", "All employees may register."),
            ("All employees must register.", "All employees must not register."),
            ("Employees must register before Friday.", "Employees must register after Friday."),
            ("The score must be more than 18.", "The score must be at least 18."),
            ("Not all employees must register.", "All employees must not register."),
        )
        for source, target in pairs:
            with self.subTest(source=source, target=target):
                self.assert_single_exact(source, target)

    def test_clearly_different_core_identity_is_unaligned_by_default(self) -> None:
        pairs = (
            ("Employees must register.", "Employees must report."),
            ("Employees must register.", "Managers must register."),
            ("Employees must submit the report.", "Employees must submit the form."),
            ("Employees must register.", "Managers must submit the report."),
        )
        for source, target in pairs:
            with self.subTest(source=source, target=target):
                result = self.aligner.align(self.analyzer.analyze(source), self.analyzer.analyze(target))
                self.assertEqual(result.alignments, ())
                self.assertEqual(len(result.unaligned_source_ids), 1)
                self.assertEqual(len(result.unaligned_target_ids), 1)

    def test_conditions_align_antecedent_and_consequent_across_operator_changes(self) -> None:
        numeric = self.aligner.align(
            self.analyzer.analyze("If the temperature is above 30 °C, the system must stop."),
            self.analyzer.analyze("If the temperature is at least 30 °C, the system must stop."),
        )
        self.assertEqual(len(numeric.alignments), 2)
        modality = self.aligner.align(
            self.analyzer.analyze("If the light is green, the system must stop."),
            self.analyzer.analyze("If the light is green, the system may stop."),
        )
        self.assertEqual(len(modality.alignments), 2)

    def test_unique_multi_proposition_alignment_and_one_to_one_invariant(self) -> None:
        source = analysis_with((
            ("source_register", "REGISTER", (("ENTITY_CLASS", "employee"),)),
            ("source_submit", "SUBMIT", (("ENTITY_CLASS", "manager"), ("OBJECT", "report"))),
        ))
        target = analysis_with((("target_register", "REGISTER", (("ENTITY_CLASS", "employee"),)),))
        result = self.aligner.align(source, target)
        self.assertEqual(
            [(item.source_proposition_id, item.target_proposition_id) for item in result.alignments],
            [("source_register", "target_register")],
        )
        self.assertEqual(result.unaligned_source_ids, ("source_submit",))
        self.assertEqual(result.unaligned_target_ids, ())
        self.assertEqual(len({item.source_proposition_id for item in result.alignments}), len(result.alignments))
        self.assertEqual(len({item.target_proposition_id for item in result.alignments}), len(result.alignments))

    def test_duplicate_candidates_are_not_guessed(self) -> None:
        duplicate = (("source_001", "REGISTER", (("ENTITY_CLASS", "employee"),)),
                     ("source_002", "REGISTER", (("ENTITY_CLASS", "employee"),)))
        target = (("target_001", "REGISTER", (("ENTITY_CLASS", "employee"),)),)
        result = self.aligner.align(analysis_with(duplicate), analysis_with(target))
        self.assertEqual(result.alignments, ())
        self.assertEqual(result.unaligned_source_ids, ("source_001", "source_002"))
        self.assertEqual(result.unaligned_target_ids, ("target_001",))

    def test_repeated_runs_are_deterministic_and_parser_independent(self) -> None:
        source = analysis_with((("source_001", "REGISTER", (("ENTITY_CLASS", "employee"),)),))
        target = analysis_with((("target_001", "REGISTER", (("ENTITY_CLASS", "employee"),)),))
        first = self.aligner.align(source, target)
        self.assertEqual(first, self.aligner.align(source, target))
        self.assertEqual(first.alignments[0].rule_id, "EXACT_NORMALIZED_SIGNATURE")

    def test_structural_counterpart_is_explicit_and_preserves_comparator_entity_change(self) -> None:
        source = self.analyzer.analyze("All employees must register.")
        target = self.analyzer.analyze("All managers must register.")
        strict = self.aligner.align(source, target)
        self.assertEqual(strict.alignments, ())
        structural = self.aligner.align(source, target, allow_structural_counterparts=True)
        self.assertIs(structural.alignments[0].status, AlignmentStatus.STRUCTURAL)
        comparison = DeterministicComparator().compare(source, target)
        self.assertEqual(comparison.differences[0].difference_type.value, "ENTITY_RELATION_CHANGE")

    def test_comparator_rejects_unrelated_propositions(self) -> None:
        with self.assertRaisesRegex(UnsupportedComparisonError, "not uniquely structurally aligned"):
            DeterministicComparator().compare(
                self.analyzer.analyze("Employees must register."),
                self.analyzer.analyze("Managers must submit the report."),
            )


if __name__ == "__main__":
    unittest.main()
