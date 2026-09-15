# Controlled Nested Temporal References v0.1

This bounded Phase 2 milestone makes `temporal_003` exact:

- `Wait until noon.`
- `Wait until after noon.`

The confirmed blocker was not the `UNTIL` relation itself. The parser already supported flat UNTIL references, but it could neither parse `WAIT` nor represent the target's relative `AFTER(NOON)` reference without flattening the two temporal levels.

## Grammar and semantic graph

Only `Wait until [after] noon` is registered. The ordinary proposition is `WAIT(addressee)`. An existing `TemporalRelation` represents the outer edge:

```text
prop_001 WAIT(addressee)
  -> temporal_001 UNTIL
       -> temporal_reference_001
            -> TEMPORAL_POINT(entity_002 NOON)
            or TEMPORAL_AFTER(entity_002 NOON)
```

The reference node is an existing `SemanticItem`; `NOON` is an `Entity` of type `TEMPORAL_POINT`. This reuses the current analysis collections, ID system, serialization, and reference mechanics. No model class, schema field, parallel temporal subsystem, date library, or opaque compound string is introduced.

## Identity, validation, and comparison

The WAIT proposition has the same normalized identity in both documents, so existing alignment is unchanged. The comparator resolves the reference graph and produces one medium-severity `TEMPORAL_CHANGE`, confidence 1.0, from `UNTIL_NOON` to `UNTIL_AFTER_NOON`. It emits no addition, omission, entity/relation, condition, or scope duplicate. Logical relation remains `UNDETERMINED`.

Temporal-reference IDs are deterministic. The outer reference must resolve to a registered temporal-reference node, every inner argument must resolve through ordinary reference validation, and direct or indirect temporal-reference cycles are rejected. JSON round-trip preserves the full graph.

## Formula and provenance

Derived formulas are `Until(Wait(Addressee), Noon)` and `Until(Wait(Addressee), After(Noon))`. `Wait`, `until`, `noon`, and the compound `after noon` reference retain exact document-relative spans. No span is fabricated for an unlexicalized relation.

## Boundaries and gold impact

No temporal inference, contradiction, transitivity, arithmetic, tense chronology, discourse chronology, prediction, ambiguity ranking, or metaphor interpretation is added. Weekday, clock, ON, UNTIL, observation/future, event-anchor, condition, scope, coordination, and independent-sentence behavior remain unchanged. General recursive temporal grammar and other nested forms remain unsupported.

The audit moves from 38 to 39 exact cases and from 1 to 0 parser-unsupported cases. It remains at 0 analyzable-but-inexact, 0 comparator-unsupported, and 3 inference-not-implemented. Only `temporal_003` changes classification. This result makes the deterministic implementation ready for a separate Phase 2 Completion Audit; this milestone does not itself declare Phase 2 complete.
