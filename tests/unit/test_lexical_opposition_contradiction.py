import unittest
from dataclasses import replace

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine,
    InterpretationStatus, LEXICAL_OPPOSITION_PAIRS, LEXICAL_OPPOSITION_RULE,
    NOT_ESTABLISHED_RULE, Proposition, analysis_from_json, analysis_to_json,
    are_lexical_opposites,
)


class LexicalOppositionContradictionTests(unittest.TestCase):
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

    @staticmethod
    def with_predicate(analysis, predicate: str):
        return replace(
            analysis,
            propositions=tuple(replace(item, predicate=predicate) for item in analysis.propositions),
            logical_representation=(),
        )

    def test_entailment_005_and_reverse_direction_are_contradicted(self) -> None:
        for premise, query in (
            ("The switch is off.", "The switch is on."),
            ("The switch is on.", "The switch is off."),
        ):
            with self.subTest(premise=premise):
                result = self.infer(premise, query)
                self.assertEqual(result.interpretation_status, InterpretationStatus.CONTRADICTED)
                self.assertEqual(result.rule, LEXICAL_OPPOSITION_RULE)

    def test_registry_is_closed_explicit_and_symmetric(self) -> None:
        self.assertEqual(LEXICAL_OPPOSITION_PAIRS, (("OFF", "ON"),))
        self.assertTrue(are_lexical_opposites("OFF", "ON"))
        self.assertTrue(are_lexical_opposites("ON", "OFF"))
        self.assertFalse(are_lexical_opposites("OPEN", "CLOSED"))
        self.assertFalse(are_lexical_opposites("POSSIBLE", "IMPOSSIBLE"))

    def test_exact_has_priority_and_unrelated_predicate_is_not_established(self) -> None:
        exact = self.infer("The switch is off.", "The switch is off.")
        self.assertEqual(exact.interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertEqual(exact.rule, "EXACT_EXPLICIT")
        self.assert_not_established("The switch is off.", "The switch is ready.")

    def test_entity_identity_is_required(self) -> None:
        self.assert_not_established("The switch is off.", "The light is on.")

    def test_binary_arity_order_and_arguments_are_required(self) -> None:
        base = self.analyzer.analyze("Alice approved the request.")
        source_prop = replace(base.propositions[0], predicate="OFF")
        source = replace(base, propositions=(source_prop,), logical_representation=())
        opposite_prop = replace(base.propositions[0], predicate="ON")
        exact_target = replace(base, propositions=(opposite_prop,), logical_representation=())
        self.assertEqual(
            self.engine.infer(source, exact_target).interpretation_status,
            InterpretationStatus.CONTRADICTED,
        )
        reversed_target = replace(
            exact_target,
            propositions=(replace(opposite_prop, arguments=tuple(reversed(opposite_prop.arguments))),),
        )
        self.assertEqual(
            self.engine.infer(source, reversed_target).interpretation_status,
            InterpretationStatus.UNSUPPORTED,
        )
        unary_target = replace(
            exact_target,
            propositions=(replace(opposite_prop, arguments=opposite_prop.arguments[:1]),),
        )
        self.assertEqual(
            self.engine.infer(source, unary_target).interpretation_status,
            InterpretationStatus.UNSUPPORTED,
        )

    def test_modality_quantification_condition_and_scope_block_opposition(self) -> None:
        pairs = (
            ("Employees may register.", "Employees register."),
            ("All employees must register.", "Some employees must register."),
            ("Not all employees must register.", "All employees must not register."),
        )
        for source_text, target_text in pairs:
            source = self.with_predicate(self.analyzer.analyze(source_text), "OFF")
            target = self.with_predicate(self.analyzer.analyze(target_text), "ON")
            self.assertEqual(
                self.engine.infer(source, target).interpretation_status,
                InterpretationStatus.UNSUPPORTED,
            )
        self.assert_not_established(
            "If the light is green, the switch is off.", "The switch is on.",
        )

    def test_temporal_numeric_and_spatial_differences_block_opposition(self) -> None:
        self.assert_not_established(
            "The switch is off before Friday.", "The switch is on after Friday.",
        )
        source = self.analyzer.analyze("All scores must be at least 18.")
        target = self.analyzer.analyze("All scores must be at least 21.")
        source = replace(
            source, propositions=(replace(source.propositions[0], predicate="OFF"),),
            logical_representation=(),
        )
        target = replace(
            target, propositions=(replace(target.propositions[0], predicate="ON"),),
            logical_representation=(),
        )
        self.assertEqual(
            self.engine.infer(source, target).interpretation_status,
            InterpretationStatus.UNSUPPORTED,
        )
        self.assert_not_established("The key is inside the box.", "The key is beside the box.")

    def test_evidence_rule_explanation_repeat_and_round_trip_are_deterministic(self) -> None:
        premise = self.analyzer.analyze("The switch is off.")
        conclusion = self.analyzer.analyze("The switch is on.")
        first = self.engine.infer(premise, conclusion)
        self.assertEqual(first, self.engine.infer(premise, conclusion))
        self.assertEqual(first.derived_from, ("entity_001", "prop_001"))
        self.assertEqual(first.rule, LEXICAL_OPPOSITION_RULE)
        self.assertEqual(
            self.engine.explain(first),
            "The conclusion conflicts with an explicitly represented predicate whose "
            "opposition is declared in the controlled lexical rule set.",
        )
        enriched = replace(premise, inferences=(first,))
        self.assertEqual(analysis_from_json(analysis_to_json(enriched)), enriched)

    def test_simultaneous_support_and_opposition_preserves_explicit_priority(self) -> None:
        base = self.analyzer.analyze("The switch is off.")
        opposed = Proposition(
            "prop_002", "ON", base.propositions[0].arguments,
            InterpretationStatus.EXPLICIT, base.propositions[0].confidence,
        )
        inconsistent = replace(
            base, propositions=(*base.propositions, opposed), logical_representation=(),
        )
        result = self.engine.infer(inconsistent, base)
        self.assertEqual(result.interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertEqual(result.rule, "EXACT_EXPLICIT")
        self.assertEqual(result.derived_from, ("entity_001", "prop_001"))

    def test_parser_and_comparator_regression(self) -> None:
        source = self.analyzer.analyze("The switch is off.")
        target = self.analyzer.analyze("The switch is on.")
        self.assertEqual(source.propositions[0].predicate, "OFF")
        self.assertEqual(target.propositions[0].predicate, "ON")
        comparison = DeterministicComparator().compare(source, target)
        self.assertEqual(len(comparison.differences), 1)
        self.assertEqual(comparison.differences[0].difference_type.value, "ENTITY_RELATION_CHANGE")


if __name__ == "__main__":
    unittest.main()
