# Coordinated Predicate Graphs v0.1

This bounded Phase 2 milestone makes `addition_001`, `omission_002`, and `equivalence_005` exact without changing their gold expectations.

## Controlled forms

Two predicate-coordination forms are registered:

```text
Register your name and show identification.
Sign and date the form.
```

Each coordinated action is an authoritative `Proposition`. A `PREDICATE_AND` semantic item references the two proposition IDs; it never treats the second predicate as an object. Shared participants reuse entity IDs: `REGISTER` and `SHOW` share the addressee, while `SIGN` and `DATE` share both addressee and form. Surface-order proposition IDs and spans remain stable, but coordination members and the displayed conjunction use normalized semantic ordering.

The pre-existing flat object form remains one proposition:

```text
Submit form A and form B.
```

Its `AND`/`OR` relation still joins object entities. Commutative members are canonicalized by typed normalized entity identity, so reversing the two objects under `AND` is equivalent. Predicate-level and object-level coordination therefore remain structurally distinct.

## Comparison and inference

Unique proposition signatures align independently. An unmatched member of a controlled predicate graph produces the committed high-severity string payload (`SHOW_IDENTIFICATION` or `DATE_FORM`) and no redundant conjunction finding. Ordinary unmatched normalized propositions retain the existing structured, medium-severity payload.

An authoritative coordinated member is available to exact-explicit inference. This is conjunction elimination over propositions already asserted by the graph, not a new probabilistic or world-knowledge rule. Coordination itself does not establish broader entailment, split/merge alignment, importance, or contradiction.

## Validation, audit, and limits

`PREDICATE_AND` requires at least two distinct proposition references. Unknown, entity, and duplicate members fail reference validation. JSON round-trips preserve the graph.

The reproducible 42-case audit is now 33 exact, 0 analyzable-but-inexact, 6 parser-unsupported, 0 comparator-unsupported, and 3 inference-not-implemented. No schema, gold expectation, or difference taxonomy changed.

This is not general coordination parsing. Repeated, nested, mixed, elliptical, clausal, and more-than-two-member coordination remain unsupported, as do fuzzy alignment, LLM judgment, and policy inference.

A runnable inspection is available at [`examples/coordinated_predicate_graphs.py`](../../examples/coordinated_predicate_graphs.py).
