# Addition/Omission v0.1

`ADDITION` and `OMISSION` are proposition-level semantic findings. A source proposition safely unmatched in the target is an `OMISSION`; a target proposition safely unmatched in the source is an `ADDITION`. They do not describe added or removed words.

## Alignment authority and ambiguity

`DeterministicComparator` consumes `DeterministicPropositionAligner` output and does not repeat matching. `AlignmentResult` now distinguishes all unaligned IDs from `ambiguous_source_ids` and `ambiguous_target_ids`; its `safely_unmatched_*` properties exclude ambiguity. Only safely unmatched propositions can produce findings. Duplicate candidates are not resolved by position and produce no low-confidence finding.

Alignment remains unique and one-to-one. Multi-proposition ordering is irrelevant because matching uses normalized signatures and deterministic IDs, not proposition or sentence indices.

## Rules and precedence

Aligned proposition pairs run through existing semantic rules first. Quantifier, modality, negation, conjunction, numeric, condition, temporal, scope, and entity/relation changes therefore retain their specialized `DifferenceType` and are not double-counted as add/omit.

Condition-owned antecedents are excluded when a condition wrapper is added or removed because `CONDITION_CHANGE` already accounts for that semantic structure. Operators, temporal references, numeric constraints, and scope edges are never independent additions or omissions in v0.1.

The comparator-only `SINGLE_CORE_POSITION_CHANGE` alignment rule runs before unmatched classification, preserving existing `ENTITY_RELATION_CHANGE` behavior without broadening structural matching.

Each safe addition or omission has `MEDIUM` severity and deterministic confidence `1.0`. The payload records side, proposition ID, normalized predicate, and typed core entity IDs/labels, with resolvable `Difference.references`. Severity does not assert domain importance. Logical relation is `UNDETERMINED`; absence is not contradiction.

## Capability boundary

| Status | Capability |
| --- | --- |
| **SUPPORTED** | Safe proposition-level addition/omission, symmetry, reordering, multiple normalized propositions, structured payloads, canonical ordering. |
| **LIMITED** | Only unique exact or existing comparator-approved structural counterparts; multi-proposition examples currently use constructed `Analysis` objects. |
| **UNSUPPORTED** | Ambiguous duplicate resolution, fuzzy/lexical matching, synonyms, coreference, split/merge, one-to-many, many-to-one, discourse inference, entailment, importance ranking, and contradiction from absence. |

The Controlled English parser still accepts one sentence, so current gold multi-sentence and coordination forms remain parser-unsupported. Broader parser coverage must not weaken alignment evidence requirements.
