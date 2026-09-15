# Controlled Event-anchored Temporal Relations v0.1

This bounded Phase 2 milestone makes `temporal_001` exact:

- `Inspect the cable before starting the machine.`
- `Inspect the cable after starting the machine.`

The confirmed blocker was an event proposition used as a temporal anchor. BEFORE/AFTER parsing already existed for canonical weekday and clock references, but the previous path could not construct or validate a second proposition as the anchor.

## Grammar and representation

Only `Inspect the cable (before|after) starting the machine` is registered. `INSPECT(addressee, cable)` and `START(addressee, machine)` are ordinary explicit propositions; no Event type or event ontology is introduced. The existing `TemporalRelation` governs the inspect proposition and stores the start proposition ID as its structured `temporal_reference`.

Direction is literal and ordered: `BEFORE(prop_001, prop_002)` and `AFTER(prop_001, prop_002)`. No inverse-surface grammar, temporal equivalence rule, tense chronology, sentence-order chronology, transitivity, contradiction, or entailment is inferred.

## Comparison and alignment

The two propositions align independently by their exact normalized signatures. Multi-proposition comparison then compares the temporal relation only after confirming that its anchor propositions align. The gold transition emits one high-severity `TEMPORAL_CHANGE`, confidence 1.0, from `BEFORE` to `AFTER`, with logical relation `UNDETERMINED`. It does not also emit `ENTITY_RELATION_CHANGE`, `ADDITION`, or `OMISSION`.

## Provenance, formula, and validation

The propositions retain document-relative spans for `Inspect` and `starting`; the temporal relation and marker node retain the explicit `before` or `after` span. The derived formula is `Before(Inspect(Addressee, Cable), Start(Addressee, Machine))` or its AFTER counterpart.

JSON serialization preserves both propositions, the temporal relation, its relation type, and both endpoint IDs. Reference validation requires a `prop_*` temporal anchor to exist and rejects self-anchors. IDs and ordering are deterministic.

## Safety, boundary, and gold impact

Both propositions remain explicit because the controlled sentence explicitly states them, but the temporal relation creates no new inference. Observation/future references such as `LAST_5_EVENINGS` remain canonical literals and acquire no predictive meaning. Conditions, scope, coordination, coreference alternatives, and non-literal safety are unchanged.

`temporal_003` remains parser-unsupported: nested `UNTIL AFTER NOON` references are a separate milestone. General temporal clauses, inverse forms, WHILE/WHEN/SINCE/DURING, implicit chronology, event coordination, fuzzy matching, embeddings, and AI interpretation remain unsupported.

The 42-case audit moves from 37 to 38 exact and from 2 to 1 parser-unsupported, with 0 analyzable-but-inexact, 0 comparator-unsupported, and 3 inference-not-implemented. Only `temporal_001` changes classification; no gold expectation or difference taxonomy changes.
