import unittest
from dataclasses import replace

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine,
    DifferenceType, InterpretationStatus, LogicalRelation, ReferenceValidationError,
    UnsupportedConstructionError, analysis_from_json, analysis_to_json, validate_analysis,
)


PROMISE_OUTER = "Maria did not promise to leave."
PROMISE_INNER = "Maria promised not to leave."
REQUIRE_OUTER = "The rule does not require employees to leave."
REQUIRE_INNER = "The rule requires employees not to leave."


class EmbeddedNegationScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.comparator = DeterministicComparator()
        self.engine = DeterministicInferenceEngine()

    def assert_scope_gold(self, source_text: str, target_text: str, wrapper: str) -> None:
        result = self.comparator.compare(
            self.analyzer.analyze(source_text), self.analyzer.analyze(target_text),
        )
        self.assertEqual(len(result.differences), 1)
        finding = result.differences[0]
        self.assertIs(finding.difference_type, DifferenceType.SCOPE_CHANGE)
        self.assertEqual(finding.source_value, f"NOT({wrapper}(LEAVE))")
        self.assertEqual(finding.target_value, f"{wrapper}(NOT(LEAVE))")
        self.assertEqual(finding.severity.value, "HIGH")
        self.assertEqual(finding.confidence.value, 1.0)
        self.assertIs(result.logical_relation, LogicalRelation.UNDETERMINED)

    def test_scope_001_is_exact(self) -> None:
        self.assert_scope_gold(PROMISE_OUTER, PROMISE_INNER, "PROMISE")

    def test_scope_002_is_exact(self) -> None:
        self.assert_scope_gold(REQUIRE_OUTER, REQUIRE_INNER, "REQUIRE")

    def test_outer_and_inner_operator_chains_are_explicit(self) -> None:
        outer = self.analyzer.analyze(PROMISE_OUTER)
        inner = self.analyzer.analyze(PROMISE_INNER)
        self.assertEqual([(x.id, x.operator, x.scope) for x in (*outer.modality, *outer.negation)], [
            ("embedded_001", "PROMISE", ("prop_001",)),
            ("negation_001", "NOT", ("embedded_001",)),
        ])
        self.assertEqual([(x.id, x.operator, x.scope) for x in (*inner.modality, *inner.negation)], [
            ("embedded_001", "PROMISE", ("negation_001",)),
            ("negation_001", "NOT", ("prop_001",)),
        ])
        self.assertEqual(outer.propositions[0].predicate, inner.propositions[0].predicate)

    def test_wrapper_source_and_required_action_are_not_duplicated(self) -> None:
        analysis = self.analyzer.analyze(REQUIRE_OUTER)
        self.assertEqual([(item.predicate, item.arguments) for item in analysis.propositions], [
            ("LEAVE", ("entity_002",)),
        ])
        self.assertEqual([(item.type, item.arguments) for item in analysis.relations], [
            ("OPERATOR_SOURCE", ("entity_001", "embedded_001")),
        ])

    def test_formula_round_trip_identity_and_determinism(self) -> None:
        outer = self.analyzer.analyze(PROMISE_OUTER)
        inner = self.analyzer.analyze(PROMISE_INNER)
        self.assertEqual(outer.logical_representation[0].display, "¬Promise(Leave(Maria))")
        self.assertEqual(inner.logical_representation[0].display, "Promise(¬Leave(Maria))")
        self.assertEqual(analysis_from_json(analysis_to_json(outer)), outer)
        self.assertEqual(outer, self.analyzer.analyze(PROMISE_OUTER))
        self.assertEqual(self.comparator.compare(outer, outer).differences, ())

    def test_scope_change_does_not_duplicate_negation_or_modality(self) -> None:
        result = self.comparator.compare(
            self.analyzer.analyze(REQUIRE_OUTER), self.analyzer.analyze(REQUIRE_INNER),
        )
        self.assertEqual([item.difference_type for item in result.differences], [DifferenceType.SCOPE_CHANGE])

    def test_existing_operator_change_taxonomy_is_preserved(self) -> None:
        cases = (
            ("All employees must register.", "Some employees must register.", DifferenceType.QUANTIFIER_CHANGE),
            ("All employees must register.", "All employees may register.", DifferenceType.MODALITY_CHANGE),
            ("All employees must register.", "All employees must not register.", DifferenceType.NEGATION_CHANGE),
        )
        for source, target, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(
                    [item.difference_type for item in self.comparator.compare(
                        self.analyzer.analyze(source), self.analyzer.analyze(target),
                    ).differences],
                    [expected],
                )

    def test_cycle_and_dangling_scope_are_rejected(self) -> None:
        analysis = self.analyzer.analyze(PROMISE_OUTER)
        cycle = replace(
            analysis,
            modality=(replace(analysis.modality[0], scope=("negation_001",)),),
        )
        with self.assertRaisesRegex(ReferenceValidationError, "cyclic operator scope"):
            validate_analysis(cycle)
        dangling = replace(
            analysis,
            negation=(replace(analysis.negation[0], scope=("missing_001",)),),
        )
        with self.assertRaisesRegex(ReferenceValidationError, "unknown ID"):
            validate_analysis(dangling)

    def test_exact_explicit_requires_the_same_scope_graph(self) -> None:
        exact = self.engine.infer(
            self.analyzer.analyze(PROMISE_OUTER), self.analyzer.analyze(PROMISE_OUTER),
        )
        changed = self.engine.infer(
            self.analyzer.analyze(PROMISE_OUTER), self.analyzer.analyze(PROMISE_INNER),
        )
        self.assertIs(exact.interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertIs(changed.interpretation_status, InterpretationStatus.UNSUPPORTED)

    def test_neighboring_scope_grammar_remains_unsupported(self) -> None:
        cases = (
            "Maria may not promise to leave.",
            "The rule does not require managers to leave.",
            "Maria did not promise to stay.",
        )
        for text in cases:
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)

    def test_major_semantic_regressions_remain_stable(self) -> None:
        rule = self.analyzer.analyze("All marked boxes are inspected. Box A is marked.")
        inferred = self.engine.infer(rule, self.analyzer.analyze("Box A is inspected."))
        self.assertEqual(inferred.rule, "UNIVERSAL_INSTANTIATION")
        self.assertEqual(
            self.comparator.compare(
                self.analyzer.analyze("The score must be more than 18."),
                self.analyzer.analyze("The score must be at least 18."),
            ).differences[0].difference_type,
            DifferenceType.NUMERIC_THRESHOLD_CHANGE,
        )
        self.assertEqual(len(self.analyzer.analyze("Alex told Sam that they had won.").ambiguities), 1)
        self.assertEqual(self.analyzer.analyze("Time is a thief.").propositions, ())
        self.assertEqual(len(self.analyzer.analyze("Sign and date the form.").propositions), 2)
        self.assertEqual(len(self.analyzer.analyze("The window is closed. The door is locked.").propositions), 2)


if __name__ == "__main__":
    unittest.main()
