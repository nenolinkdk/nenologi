import unittest
from dataclasses import replace

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicInferenceEngine, InterpretationStatus,
    Proposition, UNIVERSAL_INSTANTIATION_RULE, analysis_from_json, analysis_to_json,
)


class UniversalInstantiationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ControlledEnglishAnalyzer()
        self.engine = DeterministicInferenceEngine()

    def gold_source(self):
        return self.analyzer.analyze("All marked boxes are inspected. Box A is marked.")

    def gold_query(self):
        return self.analyzer.analyze("Box A is inspected.")

    def test_entailment_002_uses_universal_instantiation(self) -> None:
        result = self.engine.infer(self.gold_source(), self.gold_query())
        self.assertEqual(result.interpretation_status, InterpretationStatus.ENTAILED)
        self.assertEqual(result.rule, UNIVERSAL_INSTANTIATION_RULE)
        self.assertNotEqual(result.interpretation_status, InterpretationStatus.EXPLICIT)

    def test_every_antecedent_is_required(self) -> None:
        source = self.gold_source()
        without_marked = replace(
            source,
            propositions=tuple(item for item in source.propositions if item.id != "membership_002_002"),
            logical_representation=source.logical_representation[:1],
        )
        result = self.engine.infer(without_marked, self.gold_query())
        self.assertEqual(result.interpretation_status, InterpretationStatus.UNSUPPORTED)

    def test_antecedents_must_hold_for_the_same_entity(self) -> None:
        source = self.gold_source()
        box_a = source.entities[1]
        box_b = replace(box_a, id="member_entity_003", label="box_b")
        split_facts = tuple(
            replace(item, arguments=(box_b.id,)) if item.id == "membership_002_002" else item
            for item in source.propositions
        )
        source = replace(
            source, entities=(*source.entities, box_b), propositions=split_facts,
            logical_representation=source.logical_representation[:1],
        )
        self.assertEqual(
            self.engine.infer(source, self.gold_query()).interpretation_status,
            InterpretationStatus.UNSUPPORTED,
        )

    def test_query_entity_and_consequent_must_match_exactly(self) -> None:
        different_entity = self.analyzer.analyze("Box B is inspected.")
        unrelated = self.analyzer.analyze("Box A is ready.")
        for query in (different_entity, unrelated):
            with self.subTest(query=query.document.text):
                self.assertEqual(
                    self.engine.infer(self.gold_source(), query).interpretation_status,
                    InterpretationStatus.UNSUPPORTED,
                )

    def test_only_unary_templates_are_supported(self) -> None:
        source = self.gold_source()
        antecedent = source.propositions[0]
        binary = replace(antecedent, arguments=(antecedent.arguments[0], antecedent.arguments[0]))
        source = replace(
            source, propositions=(binary, *source.propositions[1:]),
            logical_representation=(),
        )
        self.assertEqual(
            self.engine.infer(source, self.gold_query()).interpretation_status,
            InterpretationStatus.UNSUPPORTED,
        )

    def test_rule_requires_all_scoped_over_the_directed_condition(self) -> None:
        source = self.gold_source()
        wrong_quantifier = replace(
            source, quantifiers=(replace(source.quantifiers[0], operator="SOME"),),
        )
        no_quantifier = replace(source, quantifiers=())
        reversed_rule = replace(
            source,
            conditions=(replace(
                source.conditions[0], antecedent=source.conditions[0].consequent,
                consequent=source.conditions[0].antecedent[:1],
            ),),
        )
        for premise in (wrong_quantifier, no_quantifier, reversed_rule):
            self.assertEqual(
                self.engine.infer(premise, self.gold_query()).interpretation_status,
                InterpretationStatus.UNSUPPORTED,
            )

    def test_no_converse_contraposition_or_existential_import(self) -> None:
        converse = self.analyzer.analyze("All doctors are professionals. Alice is a professional.")
        self.assertEqual(
            self.engine.infer(converse, self.analyzer.analyze("Alice is a doctor.")).interpretation_status,
            InterpretationStatus.UNSUPPORTED,
        )
        rule = self.analyzer.analyze("All doctors are professionals.")
        for query in (
            self.analyzer.analyze("No doctors are professionals."),
            self.analyzer.analyze("Some doctors are professionals."),
        ):
            self.assertEqual(
                self.engine.infer(rule, query).interpretation_status,
                InterpretationStatus.UNSUPPORTED,
            )

    def test_explicit_support_has_priority_over_derivation(self) -> None:
        source = self.gold_source()
        explicit = Proposition(
            "membership_002_003", "INSPECTED", ("member_entity_002",),
            InterpretationStatus.EXPLICIT, source.confidence,
        )
        source = replace(
            source, propositions=(*source.propositions, explicit),
            logical_representation=source.logical_representation[:1],
        )
        result = self.engine.infer(source, self.gold_query())
        self.assertEqual(result.interpretation_status, InterpretationStatus.EXPLICIT)
        self.assertEqual(result.rule, "EXACT_EXPLICIT")

    def test_lexical_opposition_priority_and_regression_are_preserved(self) -> None:
        result = self.engine.infer(
            self.analyzer.analyze("The switch is off."),
            self.analyzer.analyze("The switch is on."),
        )
        self.assertEqual(result.interpretation_status, InterpretationStatus.CONTRADICTED)
        self.assertEqual(result.rule, "LEXICAL_OPPOSITION")

    def test_evidence_substitution_explanation_and_repetition_are_deterministic(self) -> None:
        source = self.gold_source()
        query = self.gold_query()
        first = self.engine.infer(source, query)
        self.assertEqual(first, self.engine.infer(source, query))
        self.assertEqual(first.derived_from, (
            "rule_quantifier_001", "rule_001",
            "rule_001_antecedent_001", "rule_001_antecedent_002",
            "membership_002_001", "membership_002_002", "member_entity_002",
            "rule_001_consequent_001",
        ))
        self.assertEqual(
            first.confidence.rationale,
            "Universal instantiation (rule_variable_001 := box_a)",
        )
        self.assertEqual(first, self.engine.infer(source, query))
        self.assertIn("matching membership facts", self.engine.explain(first))

    def test_inference_round_trip_uses_only_premise_references(self) -> None:
        source = self.gold_source()
        result = self.engine.infer(source, self.gold_query())
        enriched = replace(source, inferences=(result,))
        self.assertEqual(analysis_from_json(analysis_to_json(enriched)), enriched)


if __name__ == "__main__":
    unittest.main()
