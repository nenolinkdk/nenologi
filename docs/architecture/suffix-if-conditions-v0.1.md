# Controlled Suffix-IF Conditions v0.1

## Gold target and blocker

`condition_002` compares `Submit the report.` with `Submit the report if the test passes.` The target uses suffix `IF`; its normalized antecedent is `PASS(test)` and its consequent is `SUBMIT(addressee, report)`. Previously the parser rejected the standalone `if` marker before it could build a `Condition`.

The consequent already parsed independently. The antecedent required the single closed finite mapping `passes → PASS`; this intransitive action uses the existing entity, proposition, and `ACTION_RELATION` structures. The unchanged condition comparator then emits high-severity `CONDITION_CHANGE`, `NONE → IF_TEST_PASSES`, with logical relation `UNDETERMINED`.

## Grammar and normalized order

The parser accepts one declarative suffix form, with or without the already optional final period:

```text
CONSEQUENT + IF + ANTECEDENT
```

`IF` must be a standalone, case-insensitive token. Suffix form does not accept a comma. Exactly one `IF` marker is required, and both clauses are recursively handled by the existing controlled parser. The same existing restrictions on antecedents and consequents apply; v0.1 adds no general subordinate-clause grammar.

Surface order is consequent then antecedent, but semantic storage is always antecedent then consequent. IDs retain the established normalized prefixes: `antecedent_*`, `consequent_*`, and `condition_001`. Thus `If A, B.` and `B if A.` have equivalent propositions, operators, condition references, logical expression, alignment, and comparison results. Raw document text and source spans naturally retain their distinct surfaces.

## Comparison behavior

There are no suffix-specific aligner or comparator rules and no clause-order DifferenceType. Existing `CONDITION_CHANGE`, nested consequent comparison, operator scope, and numeric anti-duplication are reused. A numeric-only antecedent change emits `NUMERIC_THRESHOLD_CHANGE` without redundant `CONDITION_CHANGE`.

The full audit also makes `omission_001` analyzable because it uses the same supported suffix grammar. The later [Condition/Omission Taxonomy Resolution v0.1](condition-omission-taxonomy-v0.1.md) confirms condition precedence as canonical and corrects that case's older `OMISSION` expectation to `CONDITION_CHANGE`.

## Explicit limitations

Multiple or nested `IF`, comma-bearing suffix form, embedded complement/interrogative `IF`, conditional questions, `UNLESS`, `ELSE`, arbitrary punctuation, multiple conditions, embedded clauses, and general subordination remain unsupported. Temporal and spatial clauses compose only where the existing inner-clause and antecedent restrictions already allow them.

This parser milestone moved gold coverage from 24 to 25 `END_TO_END_EXACT`; the subsequent taxonomy resolution moves it to 26 exact and 0 analyzable-but-inexact. Seven cases remain parser-unsupported, 2 comparator-unsupported, and 7 inference-not-implemented.

A runnable demonstration is in [`examples/suffix_if_conditions.py`](../../examples/suffix_if_conditions.py).
