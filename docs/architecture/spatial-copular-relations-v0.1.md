# Controlled Spatial Copular Relations v0.1

## Gold target and previous blocker

`entity_relation_003` compares `The key is inside the box.` with `The key is beside the box.` The previous parser treated a copula as requiring one opaque complement, so neither three-token spatial complement parsed. The expected result is one high-severity `ENTITY_RELATION_CHANGE`, `INSIDE` to `BESIDE`, with logical relation `UNDETERMINED`.

The existing entity and proposition schemas are sufficient. No spatial-specific entity class or new DifferenceType is required.

## Controlled grammar and normalization

The supported standalone form is:

```text
[THE] SUBJECT + IS/ARE + INSIDE/BESIDE + THE + REFERENCE_ENTITY
```

The subject is the existing one-word controlled subject. The reference is determiner-led and contains one or two controlled words. The exact supported predicate set is `INSIDE` and `BESIDE`.

`BE` is syntactic in this complete pattern. The parser emits the authoritative binary proposition `SPATIAL_PREDICATE(subject, reference)` plus a `SPATIAL_RELATION` semantic item over the same ordered entity IDs. It does not emit `BE`, `BE_INSIDE`, or an opaque `inside the box` property.

Ordinary one-word copular properties remain unary propositions: `The book is red.` stays `RED(book)`. Spatial recognition requires the complete controlled pattern and one of the two closed predicates.

## Comparison and inference policy

Existing normalized proposition signatures and the generic single-core-position counterpart rule align a changed subject, reference entity, or predicate. The existing comparator emits `ENTITY_RELATION_CHANGE`; predicate findings use the canonical predicate values directly. There is no `SPATIAL_CHANGE`.

Different explicit relations do not imply logical contradiction. `INSIDE(key, box)` versus `BESIDE(key, box)` is conservatively `UNDETERMINED`. No containment, topology, geometry, synonymy, opposition, transitivity, or commonsense spatial inference is implemented.

Temporal relations are recognized before ordinary clause parsing, so `Pay the invoice on Monday.` remains temporal. Spatial v0.1 does not include `ON`. Passive `BY` continues through the dedicated passive grammar and is never spatial.

## Explicit limitations

Unknown and compound prepositions, `ON`, `UNDER`, `ABOVE`, distances, coordinates, `between`, `next to`, `on top of`, nested locations, spatial negation, spatial modality, conditions, multiple spatial relations, embedded clauses, and general prepositional parsing remain unsupported.

The 42-case audit moves from 23 to 24 `END_TO_END_EXACT` and from 10 to 9 `PARSER_UNSUPPORTED`; 0 cases are analyzable-but-inexact, 2 remain comparator-unsupported, and 7 require inference. No other gold case is unlocked.

A runnable demonstration is in [`examples/spatial_copular_relations.py`](../../examples/spatial_copular_relations.py).
