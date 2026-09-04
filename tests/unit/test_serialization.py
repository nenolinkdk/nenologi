import json
import unittest

from nenologi import (
    Ambiguity, Comparison, ComparisonMode, Confidence, Difference,
    DifferenceType, Inference, InterpretationStatus, Severity,
    analysis_from_dict, analysis_from_json, analysis_to_dict, analysis_to_json,
    comparison_from_json, comparison_to_dict, comparison_to_json, validate_comparison,
)
from tests.unit.support import employee_analysis


class SerializationTests(unittest.TestCase):
    def test_minimal_analysis_dictionary_matches_schema_shape(self) -> None:
        data = analysis_to_dict(employee_analysis())
        self.assertEqual(data["schema_version"], "0.1")
        self.assertEqual(data["quantifiers"][0]["operator"], "ALL")
        self.assertEqual(data["modality"][0]["operator"], "MUST")
        self.assertEqual(data["propositions"][0]["predicate"], "REGISTER")

    def test_analysis_json_round_trip_and_unicode_formula(self) -> None:
        original = employee_analysis()
        encoded = analysis_to_json(original)
        self.assertIn("∀x", encoded)
        self.assertNotIn("\\u2200", encoded)
        self.assertEqual(analysis_from_json(encoded), original)

    def test_enum_round_trip(self) -> None:
        data = analysis_to_dict(employee_analysis())
        restored = analysis_from_dict(data)
        self.assertIs(restored.entities[0].interpretation_status, InterpretationStatus.EXPLICIT)

    def test_comparison_json_round_trip(self) -> None:
        source = employee_analysis("MUST")
        target = employee_analysis("MAY")
        comparison = Comparison(
            ComparisonMode.SOURCE_TRANSLATION, source, target,
            (Difference("difference_001", DifferenceType.MODALITY_CHANGE, "MUST", "MAY", Severity.HIGH,
                        Confidence(1.0), "Obligation becomes permission.",
                        ("source.modality_001", "target.modality_001")),),
        )
        self.assertEqual(validate_comparison(comparison), comparison)
        self.assertEqual(validate_comparison(comparison_to_dict(comparison)), comparison)
        self.assertEqual(comparison_from_json(comparison_to_json(comparison)), comparison)

    def test_multilingual_document_metadata_round_trip(self) -> None:
        source = employee_analysis(language="fr")
        target = employee_analysis("MAY", language="da")
        comparison = Comparison(ComparisonMode.SOURCE_TRANSLATION, source, target)
        data = json.loads(comparison_to_json(comparison))
        self.assertEqual(data["source_analysis"]["document"]["language"], "fr")
        self.assertEqual(data["target_analysis"]["document"]["language"], "da")

    def test_optional_ambiguity_and_inference_round_trip(self) -> None:
        base = employee_analysis()
        changed = base.__class__(
            document=base.document, profile=base.profile, structure=base.structure,
            entities=base.entities,
            propositions=base.propositions + (base.propositions[0].__class__("prop_002", "REGISTER", ("entity_001",), InterpretationStatus.PROBABLE, Confidence(0.4)),),
            quantifiers=base.quantifiers, modality=base.modality,
            logical_representation=base.logical_representation,
            inferences=(Inference("inference_001", "Employees register.", InterpretationStatus.ENTAILED, Confidence(0.9), ("prop_001",), "identity"),),
            ambiguities=(Ambiguity("ambiguity_001", "Two readings", ("prop_001", "prop_002"), Confidence(0.5)),),
            confidence=base.confidence,
            plain_language_interpretation=base.plain_language_interpretation,
        )
        self.assertEqual(analysis_from_json(analysis_to_json(changed)), changed)


if __name__ == "__main__":
    unittest.main()
