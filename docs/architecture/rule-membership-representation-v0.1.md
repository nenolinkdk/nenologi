# Controlled Rule and Membership Representation v0.1

This representation-first Phase 2 milestone supplies normalized structures required for future universal instantiation. It deliberately adds no inference rule.

## `entailment_002`

The gold source is the two-sentence text `All marked boxes are inspected. Box A is marked.`; the query is `Box A is inspected.`.

Previously, the source was rejected because the analyzer supported neither multiple sentences nor the rule/membership noun-phrase forms. The query was also outside the prior typed-name grammar. The audit therefore reported parser `UNSUPPORTED`, representation `INCOMPLETE`, and inference blocker `UNIVERSAL_INSTANTIATION_AND_MULTI_SENTENCE`.

The new source analysis contains:

```text
universal rule: ∀x ((BOX(x) ∧ MARKED(x)) → INSPECTED(x))
membership:     BOX(box_a) ∧ MARKED(box_a)
```

The query contains `BOX(box_a) ∧ INSPECTED(box_a)`. The engine still returns `UNSUPPORTED` with `NOT_ESTABLISHED`, because `UNIVERSAL_INSTANTIATION` is intentionally absent.

## Authoritative semantic representation

Nenologi uses the predicate view for controlled class membership: `CLASS(individual)`. Membership is stored as ordinary `Proposition` values over an `INDIVIDUAL` entity. `Analysis.sets` remains empty so the same fact is not duplicated as both predicate and set membership.

A universal class rule reuses existing normalized structures:

- one `BOUND_VARIABLE` entity with a deterministic structural ID;
- antecedent and consequent class `Proposition` values sharing that entity;
- one directed `Condition` from antecedent proposition IDs to consequent proposition IDs;
- one `ALL` `Operator` scoped over that condition.

The quantifier-to-condition reference is the only reference-validation extension. No Python domain field or JSON Schema shape changed.

For `All marked boxes are inspected`, both `BOX(x)` and `MARKED(x)` are antecedents. This preserves the head class rather than collapsing `marked boxes` into an opaque string. Rule direction is explicit in `Condition.antecedent` and `.consequent`.

## Controlled grammar

Membership accepts only:

```text
ProperName IS A|AN class
THE individual IS A|AN class
Type Initial IS class
```

Examples are `Alice is a doctor.`, `The device is a sensor.`, and the gold-required `Box A is marked.`. The typed-name form emits both `BOX(box_a)` and `MARKED(box_a)`.

Universal rules accept:

```text
ALL [modifier] class-plural ARE consequent
ALL class-plural ARE consequent-plural
```

This admits the gold rule and `All doctors are professionals.` while preserving the existing interpretation of simple property sentences such as `All doors are open.`. Arbitrary noun phrases, multiple modifiers, relative clauses, modalized or negative rules, and synonym normalization remain unsupported.

## Controlled multi-sentence boundary

At most two period-terminated declarative class-logic sentences are accepted, and a two-sentence document must be ordered `RULE. MEMBERSHIP.`. There is no general sentence tokenizer or discourse parser. Abbreviations, quotations, semicolons, questions, exclamations, three-sentence rule chains, and mixed arbitrary sentences remain unsupported.

The combined `Analysis` contains two deterministic sentence nodes and one shared semantic object graph. No cross-sentence inference occurs during parsing.

## Binder and rendering policy

The binder is the entity `rule_variable_001` (or the corresponding sentence-position ID), type `BOUND_VARIABLE`. Antecedent and consequent propositions reference that same entity, making variable correspondence structural. The stable display name `x` is not match authority; analysis-local IDs are canonicalized by semantic comparison/inference signatures.

`LogicalExpression.expression` records `UNIVERSAL_CLASS_RULE` or `CLASS_MEMBERSHIP` plus structured references. Displays such as `∀x ((BOX(x) ∧ MARKED(x)) → INSPECTED(x))` are deterministic derived output only.

## Inference and comparison boundary

`DeterministicInferenceEngine` was not given universal instantiation, forward chaining, converse reasoning, contraposition, or existential import. An explicitly repeated membership fact remains eligible for `EXACT_EXPLICIT`; a rule plus matching membership does not derive its consequent.

The comparator receives the normalized model unchanged. Identical rule analyses compare identically, but no `RULE_CHANGE` or other `DifferenceType` was added. Broader rule comparison remains future work.

## Gold impact

The overall audit totals remain **28 `END_TO_END_EXACT`, 0 `ANALYZABLE_BUT_NOT_EXACT`, 7 `PARSER_UNSUPPORTED`, 2 `COMPARATOR_UNSUPPORTED`, and 5 `INFERENCE_NOT_IMPLEMENTED`**. `entailment_002` stays in the inference-not-implemented category, but its internal pipeline moves from parser `UNSUPPORTED`/analysis `INCOMPLETE` to parser `SUPPORTED`/analysis `AVAILABLE`. Its sole blocker is now `UNIVERSAL_INSTANTIATION`.

| Case | Parser | Representation | Inference | Missing capability |
| --- | --- | --- | --- | --- |
| `entailment_002` | Supported | Rule and membership available | Not established | Universal instantiation |
| `entailment_003` | Unsupported | Incomplete | Not implemented | Defeasible prediction |
| `entailment_004` | Unsupported | Incomplete | Not implemented | Open-world unsupported judgment |
| `entailment_006` | Unsupported | Incomplete | Not implemented | Embedded propositions and coreference |
| `entailment_007` | Unsupported | Incomplete | Not implemented | Non-literal safety classification |

The recommended next milestone is **Universal Instantiation v0.1**, operating only on these normalized rule and membership structures—not on raw text.
