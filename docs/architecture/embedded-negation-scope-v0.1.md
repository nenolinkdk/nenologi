# Controlled Embedded Negation Scope v0.1

This bounded Phase 2 milestone makes `scope_001` and `scope_002` exact:

```text
Maria did not promise to leave.
Maria promised not to leave.

The rule does not require employees to leave.
The rule requires employees not to leave.
```

The expected findings are respectively `NOT(PROMISE(LEAVE)) → PROMISE(NOT(LEAVE))` and `NOT(REQUIRE(LEAVE)) → REQUIRE(NOT(LEAVE))`, each as one high-severity `SCOPE_CHANGE` with logical relation `UNDETERMINED`.

## Controlled grammar and semantic graph

Only the four exact surface families above are registered. Both members of each pair normalize to one authoritative `LEAVE` proposition. `PROMISE` or `REQUIRE` is an existing `Operator` wrapper, and `NOT` is an existing negation operator. Their `scope` references encode the distinction:

```text
outer: NOT -> PROMISE/REQUIRE -> LEAVE proposition
inner: PROMISE/REQUIRE -> NOT -> LEAVE proposition
```

The base proposition is not duplicated. `OPERATOR_SOURCE` records the explicit wrapper source (`Maria` or `rule`) and points to the wrapper operator; the required action uses the explicit `employees` entity. This relation asserts no additional inference.

The `modality` collection carries the controlled embedded wrapper because the v0.1 model exposes generic `Operator` values there. This does not classify promise or require as deontic modality and does not add modal logic. It reuses the existing serialized operator-chain contract without a schema change.

## Comparison and duplicate policy

The proposition aligner matches `LEAVE` independently of its wrappers. Existing operator values are identical on both sides, but their scope-edge signatures differ. The comparator renders the controlled nested values and emits exactly one `SCOPE_CHANGE`; it suppresses redundant `NEGATION_CHANGE` and `MODALITY_CHANGE` because neither operator is added, removed, or renamed.

Real operator changes retain their established taxonomy: `ALL → SOME` is `QUANTIFIER_CHANGE`, `MUST → MAY` is `MODALITY_CHANGE`, and adding/removing `NOT` remains `NEGATION_CHANGE`. No logical consequence is inferred from scope movement.

## Rendering, validation, and inference

Formulas visibly distinguish `¬Promise(Leave(Maria))` from `Promise(¬Leave(Maria))` and the corresponding `Require` pair. Formula text is derived presentation; operator references are authoritative.

JSON round-trips preserve IDs, operator values, scope targets, spans, status, confidence, and order. Existing reference validation rejects unknown targets, self-reference, and longer cycles. Operator chains are never sorted because ordering is semantic.

Exact-explicit inference includes the complete normalized graph: identical scope is explicit, while a matching base predicate under different scope is not. Universal instantiation, condition, temporal, numeric, coordination, independent-document, coreference, and non-literal behavior are unchanged.

## Audit impact and limitations

The 42-case audit moves from 34 to 36 exact cases and from 5 to 3 parser-unsupported cases. It remains at 0 analyzable-but-inexact, 0 comparator-unsupported, and 3 inference-not-implemented. Only `scope_001` and `scope_002` change classification; no gold expectation, schema, or difference taxonomy changes.

There is no general embedded-clause or scope resolver. Other subjects, wrapper verbs, complements, actions, negation placements, quantifier raising, inverse readings, ambiguous alternatives, probabilistic ranking, fuzzy matching, embeddings, or LLM/API interpretation remain unsupported.

A runnable inspection is available at [`examples/embedded_negation_scope.py`](../../examples/embedded_negation_scope.py).
