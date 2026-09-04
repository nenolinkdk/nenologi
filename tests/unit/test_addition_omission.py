import unittest
from dataclasses import replace

from nenologi import (
    DeterministicComparator, DeterministicPropositionAligner, DifferenceType,
    InterpretationStatus, LogicalRelation, Operator, comparison_from_json, comparison_to_json,
)

from .test_alignment import CONFIDENCE, analysis_with


REGISTER = ("REGISTER", (("ENTITY_CLASS", "employee"),))
SUBMIT = ("SUBMIT", (("ENTITY_CLASS", "manager"), ("OBJECT", "report")))
APPROVE = ("APPROVE", (("ENTITY_CLASS", "manager"), ("OBJECT", "request")))


def make(specs):
    return analysis_with(tuple((identifier, predicate, arguments) for identifier, (predicate, arguments) in specs))


def with_register_operators(analysis, quantifier, modality):
    status = InterpretationStatus.EXPLICIT
    return replace(
        analysis,
        quantifiers=(Operator("quantifier_001", quantifier, ("register",), status, CONFIDENCE),),
        modality=(Operator("modality_001", modality, ("register",), status, CONFIDENCE),),
    )


class AdditionOmissionV01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.comparator = DeterministicComparator()

    def test_safe_omission_addition_and_symmetry(self) -> None:
        larger = make((("register", REGISTER), ("submit", SUBMIT)))
        smaller = make((("register", REGISTER),))
        omission = self.comparator.compare(larger, smaller)
        addition = self.comparator.compare(smaller, larger)
        self.assertEqual([item.difference_type for item in omission.differences], [DifferenceType.OMISSION])
        self.assertEqual([item.difference_type for item in addition.differences], [DifferenceType.ADDITION])
        self.assertEqual(omission.differences[0].source_value["predicate"], "SUBMIT")
        self.assertIsNone(omission.differences[0].target_value)
        self.assertIsNone(addition.differences[0].source_value)
        self.assertEqual(addition.differences[0].target_value["predicate"], "SUBMIT")
        self.assertIs(omission.logical_relation, LogicalRelation.UNDETERMINED)
        self.assertIs(addition.logical_relation, LogicalRelation.UNDETERMINED)

    def test_multiple_alignment_reordering_and_single_unmatched(self) -> None:
        source = make((("register", REGISTER), ("submit", SUBMIT), ("approve", APPROVE)))
        reordered = make((("target_approve", APPROVE), ("target_register", REGISTER)))
        result = self.comparator.compare(source, reordered)
        self.assertEqual([item.difference_type for item in result.differences], [DifferenceType.OMISSION])
        self.assertEqual(result.differences[0].source_value["proposition_id"], "submit")
        reverse = self.comparator.compare(reordered, source)
        self.assertEqual([item.difference_type for item in reverse.differences], [DifferenceType.ADDITION])
        same_reordered = make((("other_submit", SUBMIT), ("other_register", REGISTER), ("other_approve", APPROVE)))
        self.assertEqual(self.comparator.compare(source, same_reordered).differences, ())

    def test_ambiguous_duplicates_create_no_invented_findings(self) -> None:
        single = make((("target_register", REGISTER),))
        duplicate_source = make((("source_a", REGISTER), ("source_b", REGISTER)))
        result = self.comparator.compare(duplicate_source, single)
        self.assertEqual(result.differences, ())
        self.assertIs(result.logical_relation, LogicalRelation.UNDETERMINED)
        reverse = self.comparator.compare(single, duplicate_source)
        self.assertEqual(reverse.differences, ())
        self.assertIs(reverse.logical_relation, LogicalRelation.UNDETERMINED)
        alignment = DeterministicPropositionAligner().align(duplicate_source, single)
        self.assertEqual(alignment.safely_unmatched_source_ids, ())
        self.assertEqual(alignment.ambiguous_source_ids, ("source_a", "source_b"))

    def test_semantic_change_plus_independent_addition_is_canonical(self) -> None:
        source = with_register_operators(make((("register", REGISTER),)), "ALL", "MUST")
        target = with_register_operators(make((("register", REGISTER), ("submit", SUBMIT))), "SOME", "MAY")
        result = self.comparator.compare(source, target)
        self.assertEqual(
            [item.difference_type for item in result.differences],
            [DifferenceType.QUANTIFIER_CHANGE, DifferenceType.MODALITY_CHANGE, DifferenceType.ADDITION],
        )
        self.assertEqual([item.id for item in result.differences], ["difference_001", "difference_002", "difference_003"])
        self.assertEqual(result, self.comparator.compare(source, target))

    def test_semantic_change_plus_independent_omission_is_canonical(self) -> None:
        source = with_register_operators(make((("register", REGISTER), ("submit", SUBMIT))), "ALL", "MUST")
        target = with_register_operators(make((("register", REGISTER),)), "SOME", "MAY")
        result = self.comparator.compare(source, target)
        self.assertEqual(
            [item.difference_type for item in result.differences],
            [DifferenceType.QUANTIFIER_CHANGE, DifferenceType.MODALITY_CHANGE, DifferenceType.OMISSION],
        )

    def test_payload_references_and_conservative_policy(self) -> None:
        source = make((("register", REGISTER), ("submit", SUBMIT)))
        target = make((("register", REGISTER),))
        finding = self.comparator.compare(source, target).differences[0]
        self.assertEqual(finding.severity.value, "MEDIUM")
        self.assertEqual(finding.confidence.value, 1.0)
        self.assertEqual(finding.references[0], "source.submit")
        self.assertEqual(finding.source_value["side"], "source")
        self.assertEqual(finding.source_value["arguments"][1]["label"], "report")
        comparison = self.comparator.compare(source, target)
        self.assertEqual(comparison_from_json(comparison_to_json(comparison)), comparison)


if __name__ == "__main__":
    unittest.main()
