import unittest
from decimal import Decimal

from nenologi import (
    Ambiguity, Condition, Confidence, DifferenceType, DomainValidationError, Inference,
    InterpretationStatus, NumericConstraint, NumericOperator, Severity,
)


class DomainModelTests(unittest.TestCase):
    def test_confidence_accepts_boundaries(self) -> None:
        self.assertEqual(Confidence(0.0).value, 0.0)
        self.assertEqual(Confidence(1.0).value, 1.0)

    def test_confidence_rejects_out_of_range_and_non_finite_values(self) -> None:
        for value in (-0.01, 1.01, float("nan"), float("inf"), True):
            with self.subTest(value=value), self.assertRaises(DomainValidationError):
                Confidence(value)

    def test_stable_enum_values(self) -> None:
        self.assertEqual(InterpretationStatus("ENTAILED"), InterpretationStatus.ENTAILED)
        self.assertEqual(Severity("CRITICAL"), Severity.CRITICAL)
        self.assertEqual(DifferenceType("SCOPE_CHANGE"), DifferenceType.SCOPE_CHANGE)

    def test_optional_inference_fields(self) -> None:
        inference = Inference("inference_001", "Box A is inspected.", InterpretationStatus.ENTAILED, Confidence(0.9))
        self.assertEqual(inference.derived_from, ())
        self.assertIsNone(inference.rule)

    def test_ambiguity_requires_two_readings(self) -> None:
        with self.assertRaises(DomainValidationError):
            Ambiguity("ambiguity_001", "Two readings are possible.", ("prop_001",), Confidence(0.5))

    def test_numeric_constraint_uses_exact_decimal_and_rejects_float(self) -> None:
        constraint = NumericConstraint(
            "numeric_001", NumericOperator.EQUAL, "18.50", ("prop_001",),
            InterpretationStatus.EXPLICIT, Confidence(1.0),
        )
        self.assertEqual(constraint.value, Decimal("18.5"))
        self.assertEqual(
            NumericConstraint(
                "numeric_002", NumericOperator.EQUAL, "0.0", ("prop_001",),
                InterpretationStatus.EXPLICIT, Confidence(1.0),
            ).value,
            Decimal("0"),
        )
        with self.assertRaises(DomainValidationError):
            NumericConstraint(
                "numeric_001", NumericOperator.EQUAL, 18.5, ("prop_001",),
                InterpretationStatus.EXPLICIT, Confidence(1.0),
            )

    def test_condition_requires_both_proposition_roles(self) -> None:
        with self.assertRaises(DomainValidationError):
            Condition("condition_001", (), ("prop_001",), InterpretationStatus.EXPLICIT, Confidence(1.0))


if __name__ == "__main__":
    unittest.main()
