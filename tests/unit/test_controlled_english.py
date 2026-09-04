import unittest
from decimal import Decimal

from nenologi import (
    ControlledEnglishAnalyzer, NumericOperator, UnsupportedConstructionError,
    analysis_from_json, analysis_to_dict, analysis_to_json, validate_analysis,
)


class ControlledEnglishAnalyzerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()

    def test_all_and_every_normalize_to_all(self) -> None:
        all_result = self.analyzer.analyze("All employees must register.")
        every_result = self.analyzer.analyze("Every employee must register.")
        self.assertEqual(all_result.quantifiers[0].operator, "ALL")
        self.assertEqual(every_result.quantifiers[0].operator, "ALL")
        self.assertEqual(all_result.logical_representation[0].display, every_result.logical_representation[0].display)

    def test_some_quantifier_and_expected_formula(self) -> None:
        result = self.analyzer.analyze("Some employees must register.")
        self.assertEqual(result.quantifiers[0].operator, "SOME")
        self.assertEqual(result.logical_representation[0].display, "∃x (Employee(x) ∧ Must(Register(x)))")

    def test_no_is_none_quantifier_and_negative_quantification(self) -> None:
        result = self.analyzer.analyze("No visitors may enter.")
        self.assertEqual(result.quantifiers[0].operator, "NONE")
        self.assertEqual(result.negation[0].operator, "NOT_EXISTS")
        self.assertEqual(result.logical_representation[0].display, "¬∃x (Visitor(x) ∧ May(Enter(x)))")
        self.assertEqual(result.plain_language_interpretation.text, "The sentence states that no visitor is permitted or able to enter.")

    def test_modalities_and_absent_modality(self) -> None:
        for word, normalized in (("must", "MUST"), ("may", "MAY"), ("should", "SHOULD")):
            with self.subTest(word=word):
                self.assertEqual(self.analyzer.analyze(f"Employees {word} register.").modality[0].operator, normalized)
        result = self.analyzer.analyze("All employees register.")
        self.assertEqual(result.modality, ())
        self.assertEqual(result.logical_representation[0].display, "∀x (Employee(x) → Register(x))")

    def test_explicit_not_after_must_and_may(self) -> None:
        must_not = self.analyzer.analyze("All operators must not restart the server.")
        may_not = self.analyzer.analyze("Some users may not access the system.")
        self.assertEqual(must_not.negation[0].operator, "NOT")
        self.assertIn("Must(¬Restart(x, Server))", must_not.logical_representation[0].display)
        self.assertIn("May(¬Access(x, System))", may_not.logical_representation[0].display)

    def test_transitive_predicate_object_and_relation(self) -> None:
        result = self.analyzer.analyze("All employees must submit reports.")
        self.assertEqual(result.propositions[0].predicate, "SUBMIT")
        self.assertEqual(result.propositions[0].arguments, ("entity_001", "entity_002"))
        self.assertEqual(result.entities[1].label, "report")
        self.assertEqual(result.relations[0].type, "ACTION_RELATION")
        self.assertIn("object_phrase", {node.kind for node in result.structure.clauses})

    def test_controlled_and_or_objects_and_serialization(self) -> None:
        for word, normalized, symbol in (("and", "AND", "∧"), ("or", "OR", "∨")):
            with self.subTest(word=word):
                result = self.analyzer.analyze(f"All patients must receive treatment A {word} treatment B.")
                conjunction = next(item for item in result.relations if item.type in {"AND", "OR"})
                self.assertEqual(conjunction.type, normalized)
                self.assertEqual(conjunction.arguments, ("entity_002", "entity_003"))
                self.assertIn(symbol, result.logical_representation[0].display)
                self.assertEqual(analysis_from_json(analysis_to_json(result)), result)

    def test_numeric_words_and_symbols_normalize_to_exact_constraints(self) -> None:
        forms = (
            ("more than 18", NumericOperator.GREATER_THAN), ("> 18", NumericOperator.GREATER_THAN),
            ("at least 18", NumericOperator.GREATER_THAN_OR_EQUAL), (">= 18", NumericOperator.GREATER_THAN_OR_EQUAL),
            ("less than 18", NumericOperator.LESS_THAN), ("< 18", NumericOperator.LESS_THAN),
            ("at most 18", NumericOperator.LESS_THAN_OR_EQUAL), ("<= 18", NumericOperator.LESS_THAN_OR_EQUAL),
            ("exactly 18", NumericOperator.EQUAL), ("= 18", NumericOperator.EQUAL),
        )
        for surface, operator in forms:
            with self.subTest(surface=surface):
                result = self.analyzer.analyze(f"The score must be {surface}.")
                constraint = result.numeric_constraints[0]
                self.assertIs(constraint.operator, operator)
                self.assertEqual(constraint.value, Decimal("18"))
                self.assertEqual(constraint.scope, ("prop_001",))

    def test_numeric_decimal_unit_formula_and_serialization(self) -> None:
        result = self.analyzer.analyze("The weight must be less than 18.50 kg.")
        constraint = result.numeric_constraints[0]
        self.assertEqual(constraint.value, Decimal("18.5"))
        self.assertEqual(constraint.unit, "kg")
        self.assertEqual(result.logical_representation[0].display, "Must(Weight(x) < 18.5 kg)")
        self.assertEqual(analysis_from_json(analysis_to_json(result)), result)

    def test_numeric_quantity_after_action_and_or_more_equivalence_form(self) -> None:
        first = self.analyzer.analyze("Bring at least three copies.")
        second = self.analyzer.analyze("Bring three or more copies.")
        self.assertEqual(first.numeric_constraints[0].operator, second.numeric_constraints[0].operator)
        self.assertEqual(first.numeric_constraints[0].value, Decimal("3"))
        self.assertEqual(first.numeric_constraints[0].unit, "copy")
        direct = self.analyzer.analyze("The score is at least 18.")
        self.assertEqual(direct.logical_representation[0].display, "Score(x) ≥ 18")

    def test_unsupported_numeric_constructions_are_rejected(self) -> None:
        unsupported = (
            "The score must be between 10 and 20.", "The score must be at least 1/2.",
            "The score must be about 18.", "The score must be at least 1e3.",
            "The weight must be at least 10000 g.",
        )
        for text in unsupported:
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)

    def test_structure_includes_required_controlled_parts(self) -> None:
        result = self.analyzer.analyze("All operators must not restart the server.")
        self.assertEqual(len(result.structure.sentences), 1)
        self.assertEqual(
            {node.kind for node in result.structure.clauses},
            {"subject_phrase", "predicate_phrase", "modal", "negation_marker", "object_phrase"},
        )

    def test_normalization_preserves_text_but_stabilizes_semantics_and_ids(self) -> None:
        first = self.analyzer.analyze("  ALL   EMPLOYEES MUST REGISTER  ")
        second = self.analyzer.analyze("All employees must register.")
        self.assertEqual(first.document.text, "  ALL   EMPLOYEES MUST REGISTER  ")
        self.assertEqual((first.propositions[0].id, first.propositions[0].predicate, first.propositions[0].arguments),
                         (second.propositions[0].id, second.propositions[0].predicate, second.propositions[0].arguments))
        self.assertEqual((first.quantifiers[0].id, first.quantifiers[0].operator, first.quantifiers[0].scope),
                         (second.quantifiers[0].id, second.quantifiers[0].operator, second.quantifiers[0].scope))
        self.assertEqual((first.modality[0].id, first.modality[0].operator, first.modality[0].scope),
                         (second.modality[0].id, second.modality[0].operator, second.modality[0].scope))
        self.assertEqual([item.id for item in first.all_identified_objects()], [item.id for item in second.all_identified_objects()])

    def test_analysis_serializes_validates_and_round_trips(self) -> None:
        result = self.analyzer.analyze("Some users may access the system.")
        serialized = analysis_to_dict(result)
        self.assertEqual(validate_analysis(serialized), result)
        self.assertEqual(analysis_from_json(analysis_to_json(result)), result)

    def test_plain_language_interpretation_is_deterministic(self) -> None:
        result = self.analyzer.analyze("All employees must register.")
        self.assertEqual(result.plain_language_interpretation.text, "The sentence states that every employee is required to register.")
        result = self.analyzer.analyze("Some users may access the system.")
        self.assertEqual(result.plain_language_interpretation.text, "The sentence states that at least some users are permitted or able to access the system.")
        result = self.analyzer.analyze("No visitors may enter the room.")
        self.assertEqual(result.plain_language_interpretation.text, "The sentence states that no visitor is permitted or able to enter the room.")

    def test_copular_subset_supports_gold_quantifier_and_negation_forms(self) -> None:
        result = self.analyzer.analyze("No lamps are lit.")
        self.assertEqual(result.propositions[0].predicate, "LIT")
        self.assertEqual(result.plain_language_interpretation.text, "The sentence states that no lamp is lit.")

    def test_unsupported_constructions_are_rejected(self) -> None:
        unsupported = (
            "All employees who work remotely must register.",
            "Employees must register and vote.",
            "Submit form A and form B and form C.",
            "Must employees register?",
            "Employees registered yesterday.",
        )
        for text in unsupported:
            with self.subTest(text=text), self.assertRaises(UnsupportedConstructionError):
                self.analyzer.analyze(text)

    def test_non_english_language_is_explicitly_rejected(self) -> None:
        with self.assertRaises(UnsupportedConstructionError):
            self.analyzer.analyze("Tous employés doivent enregistrer.", language="fr")


if __name__ == "__main__":
    unittest.main()
