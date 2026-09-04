# Proposition Alignment v0.1

Proposition alignment identifies normalized propositions that are structural counterparts for comparison. **Alignment does not mean semantic equivalence.**

## Deterministic representation and API

`DeterministicPropositionAligner.align(source, target)` returns an `AlignmentResult` containing one-to-one `PropositionAlignment` records plus sorted source and target proposition IDs that remain unaligned. Each match records an exact `1.0` confidence, status, and rule ID; there are no probabilistic or fuzzy scores.

The normalized proposition signature contains:

- structural role: `ANTECEDENT` or `ASSERTED` (main propositions and condition consequents);
- normalized predicate identity;
- ordered core arguments as normalized entity type and case-folded label.

It excludes quantification, modality, negation, temporal relations, numeric thresholds, condition wrapping, scope topology, spans, display text, and raw document text. Consequently these surrounding dimensions do not block alignment of the underlying proposition.

## Conservative matching

Exact normalized signatures have first precedence. A candidate is accepted only when it is unique from both source and target directions. Duplicate or equally valid candidates remain unaligned; list order never breaks a tie. Each proposition participates in at most one result, and unaligned IDs remain available for future addition/omission handling.

The public default does not align a changed subject, object, or predicate. The comparator explicitly enables the narrower `SINGLE_CORE_POSITION_CHANGE` rule to preserve its existing controlled `ENTITY_RELATION_CHANGE` behavior. That rule requires the same structural role, argument count, and argument types, with exactly one changed predicate or positional entity label. Multiple changes remain unaligned.

Condition antecedents align by their structured `Condition.antecedent` role, including across numeric-threshold changes. Consequents align as asserted propositions, including across modality changes and when a condition wrapper is added or removed.

## Boundaries

| Status | Capability |
| --- | --- |
| **SUPPORTED** | Exact normalized signatures, unique one-to-one matching, conditions, deterministic unaligned sets, parser-independent manual analyses. |
| **LIMITED** | Comparator-only single-position structural counterpart matching for existing entity/relation changes. |
| **UNSUPPORTED** | Addition/omission findings, fuzzy matching, synonyms, embeddings, coreference, splitting/merging, one-to-many, many-to-one, discourse resolution, and multilingual parsing. |

Safe unmatched propositions now feed [Addition/Omission v0.1](addition-omission-v0.1.md). Ambiguous unaligned propositions remain explicitly excluded from those findings.
