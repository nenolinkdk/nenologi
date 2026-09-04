import unittest

from nenologi import (
    Ambiguity, Confidence, DifferenceType, DomainValidationError, Inference,
    InterpretationStatus, Severity,
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


if __name__ == "__main__":
    unittest.main()
