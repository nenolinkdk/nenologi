import unittest
from dataclasses import replace

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine,
    Document, EXACT_EXPLICIT_RULE, InterpretationStatus, NOT_ESTABLISHED_RULE,
    analysis_from_json, analysis_to_json,
)


class ExactExplicitInferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.engine = DeterministicInferenceEngine()

    def infer(self, premise: str, conclusion: str):
        return self.engine.infer(
            self.analyzer.analyze(premise), self.analyzer.analyze(conclusion),
        )

    def assert_not_established(self, premise: str, conclusion: str) -> None:
        result = self.infer(premise, conclusion)
        self.assertEqual(result.interpretation_status, InterpretationStatus.UNSUPPORTED)
        self.assertEqual(result.rule, NOT_ESTABLISHED_RULE)
        self.assertEqual(result.derived_from, ())
        self.assertEqual(
            self.engine.explain(result),
            "The conclusion is not established by the supported exact inference rules.",
        )

    def test_entailment_001_is_exactly_explicit(self) -> None:
        result = self.infer("The door is open.", "The door is open.")
        self.assertEqual(result.interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertEqual(result.rule, EXACT_EXPLICIT_RULE)
        self.assertEqual(result.confidence.value, 1.0)

    def test_raw_text_and_analysis_local_document_identity_are_not_authoritative(self) -> None:
        premise = self.analyzer.analyze("The door is open.")
        conclusion = replace(
            premise,
            document=Document("candidate_document", "en", "THE   DOOR IS OPEN."),
        )
        self.assertEqual(
            self.engine.infer(premise, conclusion).interpretation_status,
            InterpretationStatus.EXPLICIT,
        )

    def test_predicate_and_ordered_entities_must_match(self) -> None:
        self.assert_not_established(
            "Alice approved the request.", "Alice approved the invoice.",
        )
        self.assert_not_established(
            "Alice approved the request.", "Bob approved the request.",
        )

    def test_quantifier_modality_and_negation_must_match(self) -> None:
        self.assert_not_established("All employees must register.", "Some employees must register.")
        self.assert_not_established("All employees must register.", "All employees may register.")
        self.assert_not_established("Employees must register.", "Employees must not register.")

    def test_numeric_temporal_and_spatial_semantics_must_match(self) -> None:
        normalized_numeric = self.infer(
            "The age must be at least 18 years.", "The age must be >= 18 year.",
        )
        self.assertEqual(normalized_numeric.interpretation_status, InterpretationStatus.EXPLICIT)
        self.assert_not_established("All scores must be at least 18.", "All scores must be above 18.")
        self.assert_not_established(
            "Employees must register before Friday.", "Employees must register after Friday.",
        )
        self.assert_not_established("The key is inside the box.", "The key is beside the box.")

    def test_condition_is_a_governing_wrapper_and_no_modus_ponens_is_applied(self) -> None:
        normalized = self.infer(
            "If the light is green, employees must register.",
            "Employees must register if the light is green.",
        )
        self.assertEqual(normalized.interpretation_status, InterpretationStatus.EXPLICIT)
        self.assert_not_established(
            "If the light is green, employees must register.", "Employees must register.",
        )
        self.assert_not_established(
            "If the light is green, employees must register.", "The light is green.",
        )

    def test_scope_topology_must_match(self) -> None:
        self.assert_not_established(
            "Not all employees must register.", "All employees must not register.",
        )

    def test_evidence_explanation_serialization_and_comparator_are_deterministic(self) -> None:
        premise = self.analyzer.analyze("All employees must register before Friday.")
        conclusion = self.analyzer.analyze("All employees must register before Friday.")
        first = self.engine.infer(premise, conclusion)
        second = self.engine.infer(premise, conclusion)
        self.assertEqual(first, second)
        self.assertEqual(first.derived_from, (
            "entity_001", "prop_001", "relation_001", "quantifier_001",
            "modality_001", "temporal_001",
        ))
        self.assertEqual(
            self.engine.explain(first),
            "The conclusion is explicitly represented in the normalized premise.",
        )
        enriched = replace(premise, inferences=(first,))
        self.assertEqual(analysis_from_json(analysis_to_json(enriched)), enriched)
        self.assertEqual(DeterministicComparator().compare(premise, conclusion).differences, ())


if __name__ == "__main__":
    unittest.main()
