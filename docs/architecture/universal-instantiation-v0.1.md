# Universal Instantiation v0.1

This Phase 2 milestone adds one deterministic inference rule over the normalized structures introduced by Controlled Rule and Membership Representation v0.1. It makes `entailment_002` exact without reading raw text or implementing a general first-order reasoner.

## Gold operation

The source `All marked boxes are inspected. Box A is marked.` normalizes to:

```text
∀x ((BOX(x) ∧ MARKED(x)) → INSPECTED(x))
BOX(box_a)
MARKED(box_a)
```

The query `Box A is inspected.` contains `BOX(box_a) ∧ INSPECTED(box_a)`. The deterministic substitution is `rule_variable_001 := box_a`. Every antecedent is explicitly satisfied by the same source entity, and the instantiated consequent matches the non-explicit query predicate exactly. The result is the existing status `ENTAILED` with rule `UNIVERSAL_INSTANTIATION`.

Before this milestone, parsing and representation were complete but the engine correctly returned `UNSUPPORTED`/`NOT_ESTABLISHED` because it had no rule application step.

## Supported rule shape

Only the current controlled normalized form is accepted:

- an `ALL` operator scoped directly over one `Condition`;
- one or more unary antecedent propositions;
- exactly one unary consequent proposition;
- all templates share one entity of type `BOUND_VARIABLE`;
- all rule objects and supporting facts have `EXPLICIT` status;
- the concrete entity has type `INDIVIDUAL`;
- the query is an unwrapped collection of unary membership predicates for that individual.

Predicate, entity type, normalized entity label, arity, and argument identity match exactly. All antecedents must be present for the same entity. Binary unification, partial antecedents, cross-entity joins, lexical similarity, and external knowledge are rejected.

Additional query membership predicates must already be explicit source facts or be the one instantiated consequent. This is why the query's explicit `BOX(box_a)` component is accounted for without pretending it was derived.

## Rule priority

The engine uses this deterministic order:

1. `EXACT_EXPLICIT` -> `EXPLICIT`
2. `LEXICAL_OPPOSITION` -> `CONTRADICTED`
3. `UNIVERSAL_INSTANTIATION` -> `ENTAILED`
4. `NOT_ESTABLISHED` -> `UNSUPPORTED`

If the complete query is already explicit, direct evidence wins even when a rule could also derive it. The closed lexical-opposition behavior is unchanged.

## Evidence and substitution

Successful evidence is ordered as:

1. universal quantifier ID;
2. condition/rule ID;
3. antecedent template IDs;
4. matching concrete fact IDs in antecedent order;
5. concrete entity ID;
6. consequent template ID.

For `entailment_002` this is:

```text
rule_quantifier_001
rule_001
rule_001_antecedent_001
rule_001_antecedent_002
membership_002_001
membership_002_002
member_entity_002
rule_001_consequent_001
```

Every `derived_from` value resolves inside the premise `Analysis`, preserving existing schema validation and JSON round-trip behavior. Query IDs live in another analysis namespace and are not inserted. The deterministic confidence rationale records `rule_variable_001 := box_a`; prose remains derived, not authoritative evidence.

## Explicit non-goals

There is no forward chaining or reuse of derived facts, rule chaining, converse reasoning, contraposition, existential import, modus ponens over general conditions, multi-variable unification, n-ary rules, functions, equality, disjunction, negative rules, modal rules, numeric/temporal/spatial inference, ontology, synonymy, coreference, defeasible reasoning, or LLM/API use.

The parser, comparator, aligner, renderer, domain models, JSON Schema, and `DifferenceType` taxonomy are unchanged.

## Gold impact and roadmap

The 42-case audit moves from 28 to **29 `END_TO_END_EXACT`** and from 5 to **4 `INFERENCE_NOT_IMPLEMENTED`**. All other totals remain unchanged.

| Case | Parser | Representation | Current blocker | Suggested future milestone |
| --- | --- | --- | --- | --- |
| `entailment_003` | Unsupported | Incomplete | Defeasible prediction | Observation and Prediction Semantics |
| `entailment_004` | Unsupported | Incomplete | Open-world unsupported judgment | Controlled Residence/Fluency Non-entailment |
| `entailment_006` | Unsupported | Incomplete | Embedded propositions and coreference | Controlled Coreference Readings |
| `entailment_007` | Unsupported | Incomplete | Non-literal formalization safety | Metaphor/Formalization Safety Boundary |

The recommended next milestone is **Controlled Residence/Fluency Non-entailment v0.1** for `entailment_004`: it should first make both propositions representable, then confirm the existing conservative `NOT_ESTABLISHED` result without adding world knowledge. This is lower-risk than probabilistic prediction, coreference, or metaphor interpretation.
