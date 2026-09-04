import unittest

from nenologi import (
    Analysis, Comparison, ComparisonMode, Confidence, ControlledEnglishAnalyzer, DomainValidationError, Entity, InterpretationStatus,
    Proposition, ReferenceValidationError, SchemaValidationError,
    analysis_to_dict, comparison_to_dict, validate_analysis, validate_comparison,
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

    def test_invalid_logical_relation_is_schema_error(self) -> None:
        analysis = employee_analysis()
        data = comparison_to_dict(Comparison(ComparisonMode.VERSION_COMPARISON, analysis, analysis))
        data["logical_relation"] = "SIMILAR"
        with self.assertRaises(SchemaValidationError):
            validate_comparison(data)

    def test_invalid_numeric_operator_is_schema_error(self) -> None:
        data = analysis_to_dict(employee_analysis())
        data["numeric_constraints"] = [{
            "id": "numeric_001", "operator": "APPROXIMATELY", "value": "18",
            "scope": ["prop_001"], "interpretation_status": "EXPLICIT",
            "confidence": {"value": 1.0},
        }]
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

    def test_condition_requires_known_proposition_references(self) -> None:
        data = analysis_to_dict(ControlledEnglishAnalyzer().analyze("If the light is green, employees may enter."))
        data["conditions"][0]["antecedent"] = ["prop_999"]
        with self.assertRaisesRegex(ReferenceValidationError, "prop_999"):
            validate_analysis(data)

    def test_temporal_relation_requires_known_proposition_reference(self) -> None:
        data = analysis_to_dict(ControlledEnglishAnalyzer().analyze("Employees must register before Friday."))
        data["temporal_relations"][0]["proposition"] = "prop_999"
        with self.assertRaisesRegex(ReferenceValidationError, "prop_999"):
            validate_analysis(data)

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
