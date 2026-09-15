import unittest
from dataclasses import replace

from nenologi import (
    DEFEASIBLE_RECURRENCE_PREDICTION_POLICY, ControlledEnglishAnalyzer,
    DeterministicInferenceEngine, DomainValidationError, EvidenceObjectKind,
    EvidenceSide, InterpretationProvenance, InterpretationResult, InterpretationStatus,
    Phase3InterpretationEngine, interpretation_result_from_json,
    interpretation_result_to_json, validate_interpretation_evidence,
)
from tests.validation.audit_gold_coverage import ImplementationStatus, audit_gold_coverage


class DefeasibleRecurrencePredictionV01Tests(unittest.TestCase):
    source_text = "The light flickered on each of the last five evenings."
    query_text = "The light will flicker this evening."

    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.deterministic = DeterministicInferenceEngine()
        self.engine = Phase3InterpretationEngine()
        self.source = self.analyzer.analyze(self.source_text)
        self.query = self.analyzer.analyze(self.query_text)

    def test_entailment_003_is_probable_but_not_entailed(self) -> None:
        phase_2 = self.deterministic.infer(self.source, self.query)
        phase_3 = self.engine.evaluate(self.source, self.query)
        self.assertEqual((phase_2.interpretation_status.value, phase_2.rule), (
            "UNSUPPORTED", "NOT_ESTABLISHED",
        ))
        self.assertIs(phase_3.interpretation_status, InterpretationStatus.PROBABLE)
        self.assertIsNot(phase_3.interpretation_status, InterpretationStatus.ENTAILED)
        self.assertEqual(phase_3.deterministic_result, phase_2)
        self.assertEqual(phase_3.policy_id, DEFEASIBLE_RECURRENCE_PREDICTION_POLICY)

    def test_confidence_and_provenance_are_classification_metadata(self) -> None:
        result = self.engine.evaluate(self.source, self.query)
        self.assertEqual(result.confidence.value, 1.0)
        self.assertIn("not event probability", result.confidence.rationale)
        self.assertIs(
            result.provenance, InterpretationProvenance.PHASE3_DETERMINISTIC_POLICY,
        )
        self.assertNotIn("AI", result.provenance.value)

    def test_evidence_is_typed_ordered_and_resolves(self) -> None:
        result = self.engine.evaluate(self.source, self.query)
        validate_interpretation_evidence(result, self.source, self.query)
        self.assertEqual(
            [(item.role, item.analysis_side, item.object_kind) for item in result.evidence],
            [
                ("observed_proposition", EvidenceSide.PREMISE, EvidenceObjectKind.PROPOSITION),
                ("observed_entity", EvidenceSide.PREMISE, EvidenceObjectKind.ENTITY),
                ("recurrence_temporal", EvidenceSide.PREMISE, EvidenceObjectKind.TEMPORAL_RELATION),
                ("future_proposition", EvidenceSide.QUERY, EvidenceObjectKind.PROPOSITION),
                ("future_entity", EvidenceSide.QUERY, EvidenceObjectKind.ENTITY),
                ("future_temporal", EvidenceSide.QUERY, EvidenceObjectKind.TEMPORAL_RELATION),
                ("deterministic_gate", EvidenceSide.DETERMINISTIC_RESULT, EvidenceObjectKind.INFERENCE),
            ],
        )

    def test_serialization_and_repeated_evaluation_are_deterministic(self) -> None:
        first = self.engine.evaluate(self.source, self.query)
        second = self.engine.evaluate(self.source, self.query)
        self.assertEqual(first, second)
        payload = interpretation_result_to_json(first)
        self.assertEqual(interpretation_result_from_json(payload), first)
        self.assertEqual(interpretation_result_to_json(second), payload)

    def test_explanation_is_derived_and_marks_prediction_as_defeasible(self) -> None:
        result = self.engine.evaluate(self.source, self.query)
        explanation = self.engine.explain(result)
        self.assertIn("last 5 evenings", explanation)
        self.assertIn("probable", explanation)
        self.assertIn("does not logically entail", explanation)
        self.assertTrue(result.explanation_inputs)

    def test_one_observation_rejects_policy(self) -> None:
        one = replace(
            self.source,
            temporal_relations=(replace(
                self.source.temporal_relations[0], temporal_reference="LAST_1_EVENINGS",
            ),),
        )
        self.assertFallback(one, self.query)

    def test_different_predicate_rejects_policy(self) -> None:
        different = replace(
            self.query,
            propositions=(replace(self.query.propositions[0], predicate="GLOW"),),
        )
        self.assertFallback(self.source, different)

    def test_different_entity_rejects_policy(self) -> None:
        different = replace(
            self.query,
            entities=(replace(self.query.entities[0], label="lamp"),),
        )
        self.assertFallback(self.source, different)

    def test_wrong_temporal_frame_rejects_policy(self) -> None:
        incompatible = replace(
            self.query,
            temporal_relations=(replace(
                self.query.temporal_relations[0], temporal_reference="MONDAY",
            ),),
        )
        self.assertFallback(self.source, incompatible)

    def test_phase_2_terminal_results_bypass_policy(self) -> None:
        cases = (
            ("The door is open.", "The door is open.", InterpretationStatus.EXPLICIT),
            ("The switch is off.", "The switch is on.", InterpretationStatus.CONTRADICTED),
            (
                "All marked boxes are inspected. Box A is marked.",
                "Box A is inspected.", InterpretationStatus.ENTAILED,
            ),
        )
        for source, query, expected in cases:
            with self.subTest(expected=expected):
                result = self.engine.evaluate(
                    self.analyzer.analyze(source), self.analyzer.analyze(query),
                )
                self.assertIs(result.interpretation_status, expected)
                self.assertIsNone(result.policy_id)
                self.assertEqual(result.interpretation_status,
                                 result.deterministic_result.interpretation_status)

    def test_registry_is_minimal_stable_and_rejects_duplicate_ids(self) -> None:
        self.assertEqual(self.engine.policy_ids, (
            DEFEASIBLE_RECURRENCE_PREDICTION_POLICY,
        ))
        policy = self.engine._policies[0]
        with self.assertRaisesRegex(DomainValidationError, "unique"):
            Phase3InterpretationEngine((policy, policy))

    def test_policy_envelope_requires_policy_id_and_structured_evidence(self) -> None:
        deterministic = self.deterministic.infer(self.source, self.query)
        with self.assertRaisesRegex(DomainValidationError, "policy_id and evidence"):
            InterpretationResult(
                id="interpretation_001",
                interpretation_status=InterpretationStatus.PROBABLE,
                confidence=deterministic.confidence,
                provenance=InterpretationProvenance.PHASE3_DETERMINISTIC_POLICY,
                deterministic_result=deterministic,
            )

    def test_phase_2_and_full_pipeline_metrics_remain_separate(self) -> None:
        phase_2 = audit_gold_coverage()
        full = audit_gold_coverage(full_pipeline=True)
        self.assertEqual(phase_2.totals[ImplementationStatus.END_TO_END_EXACT], 39)
        self.assertEqual(phase_2.totals[ImplementationStatus.INFERENCE_NOT_IMPLEMENTED], 3)
        self.assertEqual(full.totals[ImplementationStatus.END_TO_END_EXACT], 40)
        self.assertEqual(full.totals[ImplementationStatus.INFERENCE_NOT_IMPLEMENTED], 2)
        self.assertIs(
            full.case_status["entailment_003"], ImplementationStatus.END_TO_END_EXACT,
        )
        for case_id in ("entailment_006", "entailment_007"):
            self.assertIs(
                full.case_status[case_id], ImplementationStatus.INFERENCE_NOT_IMPLEMENTED,
            )

    def assertFallback(self, source, query) -> None:
        result = self.engine.evaluate(source, query)
        self.assertIs(result.interpretation_status, InterpretationStatus.UNSUPPORTED)
        self.assertEqual(result.deterministic_result.rule, "NOT_ESTABLISHED")
        self.assertIsNone(result.policy_id)


if __name__ == "__main__":
    unittest.main()
