import unittest
from dataclasses import replace

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine, InterpretationStatus,
    NOT_ESTABLISHED_RULE, UnsupportedConstructionError, analysis_from_json,
    analysis_to_json,
)


class RuleMembershipRepresentationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.engine = DeterministicInferenceEngine()

    def test_entailment_002_representation_supports_universal_instantiation(self) -> None:
        text = "All marked boxes are inspected. Box A is marked."
        source = self.analyzer.analyze(text)
        query = self.analyzer.analyze("Box A is inspected.")
        self.assertEqual(len(source.structure.sentences), 2)
        self.assertEqual(
            [(item.predicate, item.arguments) for item in source.propositions],
            [
                ("BOX", ("rule_variable_001",)),
                ("MARKED", ("rule_variable_001",)),
                ("INSPECTED", ("rule_variable_001",)),
                ("BOX", ("member_entity_002",)),
                ("MARKED", ("member_entity_002",)),
            ],
        )
        result = self.engine.infer(source, query)
        self.assertEqual(result.interpretation_status, InterpretationStatus.ENTAILED)
        self.assertEqual(result.rule, "UNIVERSAL_INSTANTIATION")

    def test_named_and_determiner_membership_use_one_predicate_view(self) -> None:
        for text, label, predicate in (
            ("Alice is a doctor.", "alice", "DOCTOR"),
            ("The device is a sensor.", "device", "SENSOR"),
        ):
            with self.subTest(text=text):
                result = self.analyzer.analyze(text)
                self.assertEqual([(item.type, item.label) for item in result.entities], [("INDIVIDUAL", label)])
                self.assertEqual([(item.predicate, item.arguments) for item in result.propositions], [(predicate, ("member_entity_001",))])
                self.assertEqual(result.sets, ())
                self.assertEqual(result.logical_representation[0].expression["operator"], "CLASS_MEMBERSHIP")

    def test_typed_name_preserves_domain_and_membership_classes(self) -> None:
        result = self.analyzer.analyze("Box A is marked.")
        self.assertEqual(result.entities[0].label, "box_a")
        self.assertEqual([item.predicate for item in result.propositions], ["BOX", "MARKED"])
        self.assertEqual(result.logical_representation[0].display, "BOX(BoxA) ∧ MARKED(BoxA)")

    def test_universal_rule_is_directional_and_scopes_all_over_condition(self) -> None:
        result = self.analyzer.analyze("All doctors are professionals.")
        condition = result.conditions[0]
        self.assertEqual(condition.antecedent, ("rule_001_antecedent_001",))
        self.assertEqual(condition.consequent, ("rule_001_consequent_001",))
        self.assertEqual(result.quantifiers[0].operator, "ALL")
        self.assertEqual(result.quantifiers[0].scope, (condition.id,))
        self.assertEqual([item.predicate for item in result.propositions], ["DOCTOR", "PROFESSIONAL"])

    def test_bound_variable_and_formula_are_deterministic(self) -> None:
        text = "All marked boxes are inspected."
        first = self.analyzer.analyze(text)
        second = self.analyzer.analyze(text)
        self.assertEqual(first, second)
        self.assertEqual((first.entities[0].id, first.entities[0].type, first.entities[0].label), ("rule_variable_001", "BOUND_VARIABLE", "x"))
        self.assertEqual(first.logical_representation[0].display, "∀x ((BOX(x) ∧ MARKED(x)) → INSPECTED(x))")
        self.assertEqual(first.logical_representation[0].expression["binder"], "rule_variable_001")
        alpha_renamed = replace(
            first, entities=(replace(first.entities[0], label="y"),),
        )
        self.assertEqual(
            self.engine.infer(first, alpha_renamed).interpretation_status,
            InterpretationStatus.EXPLICIT,
        )

    def test_exact_explicit_membership_still_works(self) -> None:
        premise = self.analyzer.analyze("Alice is a doctor.")
        query = self.analyzer.analyze("Alice is a doctor.")
        result = self.engine.infer(premise, query)
        self.assertEqual(result.interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertEqual(result.rule, "EXACT_EXPLICIT")

    def test_no_converse_or_existential_import(self) -> None:
        converse_source = self.analyzer.analyze("All doctors are professionals. Alice is a professional.")
        converse_query = self.analyzer.analyze("Alice is a doctor.")
        self.assertEqual(
            self.engine.infer(converse_source, converse_query).interpretation_status,
            InterpretationStatus.UNSUPPORTED,
        )
        universal = self.analyzer.analyze("All doctors are professionals.")
        existential = self.analyzer.analyze("Some doctors are professionals.")
        self.assertEqual(
            self.engine.infer(universal, existential).interpretation_status,
            InterpretationStatus.UNSUPPORTED,
        )

    def test_no_rule_chaining_or_negative_rule_expansion(self) -> None:
        with self.assertRaises(UnsupportedConstructionError):
            self.analyzer.analyze(
                "All doctors are professionals. All professionals are workers. Alice is a doctor."
            )
        with self.assertRaises(UnsupportedConstructionError):
            self.analyzer.analyze("No doctors are professionals. Alice is a doctor.")

    def test_serialization_round_trip_preserves_ids_references_and_unicode(self) -> None:
        source = self.analyzer.analyze("All doctors are professionals. Alice is a doctor.")
        rendered = analysis_to_json(source)
        self.assertIn("∀x", rendered)
        self.assertIn("→", rendered)
        self.assertEqual(analysis_from_json(rendered), source)
        self.assertEqual(DeterministicComparator().compare(source, source).differences, ())

    def test_neighboring_grammar_stays_narrow_and_prior_forms_regress(self) -> None:
        with self.assertRaises(UnsupportedConstructionError):
            self.analyzer.analyze("All highly skilled doctors are professionals.")
        with self.assertRaises(UnsupportedConstructionError):
            self.analyzer.analyze("Alice, the doctor, is a professional.")
        cases = (
            "Employees must register.",
            "The board approved the proposal.",
            "The proposal was approved by the board.",
            "If the light is green, employees must register.",
            "Employees must register if the light is green.",
            "Employees must register before Friday.",
            "The key is inside the box.",
        )
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(self.analyzer.analyze(text), self.analyzer.analyze(text))
        opposition = self.engine.infer(
            self.analyzer.analyze("The switch is off."),
            self.analyzer.analyze("The switch is on."),
        )
        self.assertEqual(opposition.interpretation_status, InterpretationStatus.CONTRADICTED)


if __name__ == "__main__":
    unittest.main()
