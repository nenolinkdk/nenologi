import unittest

from nenologi import (
    Analysis, Confidence, DomainValidationError, Entity, InterpretationStatus,
    Proposition, ReferenceValidationError, SchemaValidationError,
    analysis_to_dict, validate_analysis, validate_comparison,
)
from tests.unit.support import employee_analysis


class ValidationTests(unittest.TestCase):
    def test_serialized_model_validates(self) -> None:
        model = employee_analysis()
        self.assertEqual(validate_analysis(analysis_to_dict(model)), model)

    def test_invalid_required_field_is_schema_error(self) -> None:
        data = analysis_to_dict(employee_analysis())
        del data["document"]
        with self.assertRaises(SchemaValidationError):
            validate_analysis(data)

    def test_invalid_enum_is_schema_error(self) -> None:
        data = analysis_to_dict(employee_analysis())
        data["entities"][0]["interpretation_status"] = "CERTAIN"
        with self.assertRaises(SchemaValidationError):
            validate_analysis(data)

    def test_invalid_domain_value_is_distinct(self) -> None:
        with self.assertRaises(DomainValidationError):
            Confidence(2.0)

    def test_invalid_cross_reference_is_reference_error(self) -> None:
        base = employee_analysis()
        bad = Analysis(
            document=base.document, profile=base.profile, structure=base.structure,
            entities=base.entities,
            propositions=(Proposition("prop_001", "REGISTER", ("entity_999",), InterpretationStatus.EXPLICIT, Confidence(1.0)),),
            quantifiers=base.quantifiers, modality=base.modality,
            logical_representation=base.logical_representation, confidence=base.confidence,
            plain_language_interpretation=base.plain_language_interpretation,
        )
        with self.assertRaisesRegex(ReferenceValidationError, "entity_999"):
            validate_analysis(bad)

    def test_duplicate_semantic_id_is_reference_error(self) -> None:
        base = employee_analysis()
        duplicate = Entity("prop_001", "SET", "duplicate", InterpretationStatus.EXPLICIT, Confidence(1.0))
        bad = Analysis(
            document=base.document, profile=base.profile, structure=base.structure,
            entities=base.entities + (duplicate,), propositions=base.propositions,
            quantifiers=base.quantifiers, modality=base.modality,
            logical_representation=base.logical_representation, confidence=base.confidence,
            plain_language_interpretation=base.plain_language_interpretation,
        )
        with self.assertRaisesRegex(ReferenceValidationError, "duplicate analysis ID"):
            validate_analysis(bad)


if __name__ == "__main__":
    unittest.main()
