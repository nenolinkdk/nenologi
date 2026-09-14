# Controlled Independent Two-sentence Propositions v0.1

This bounded Phase 2 milestone makes gold case `addition_002` exact:

```text
Source: The window is closed.
Target: The window is closed. The door is locked.
Gold:   ADDITION, DOOR_LOCKED, MEDIUM
```

## Segmentation and semantic independence

The parser accepts exactly two declarative sentences separated by one or more whitespace characters after a period. Each sentence must independently produce one ordinary, unqualified, explicit proposition under the existing single-sentence grammar. The existing rule-then-membership parser remains earlier and authoritative for its specialized two-sentence form.

The two sentence nodes preserve surface order and document-relative spans. Their propositions remain independent: adjacency creates no conjunction, discourse relation, temporal sequence, causality, shared event, subject carryover, or coreference.

## IDs, entities, and spans

Sentence, proposition, entity, relation, clause, and logical-expression IDs are deterministically rebased in surface order. Parsing the same document repeatedly produces the same `Analysis`. Proposition predicate and typed argument-label identity is unchanged from standalone parsing.

Entity occurrences are not merged, even when their normalized labels match. The v0.1 `Entity` model has one optional source span, so separate mention entities preserve traceability without claiming cross-sentence identity. Exact type/label identity remains available to proposition alignment; pronouns, aliases, synonyms, and implicit subjects are never resolved.

All spans are shifted into the original document coordinate system. Sentence 2 never restarts at offset zero.

## Alignment, comparison, and inference

The existing exact aligner matches `CLOSED(window)` across source and target and leaves `LOCKED(door)` safely target-unmatched. The comparator emits one medium-severity `ADDITION` with the committed `DOOR_LOCKED` payload and `UNDETERMINED` logical relation. Reversing the documents emits the symmetric `OMISSION`; no redundant entity, conjunction, condition, or temporal finding is introduced.

Within this bounded independent-document representation, reversing the two propositions is semantically equivalent because no sentence-order relation is asserted. Surface order and spans remain preserved structurally. This does not establish a general discourse-order equivalence policy.

Both propositions are authoritative, so the existing exact-explicit lookup can find either member without a new inference rule. Logical rendering remains two independent expressions, never `A ∧ B`.

## Safety and validation

If either sentence is unsupported or qualified beyond the bounded form, the whole document raises `UnsupportedConstructionError`; partial authoritative output is never returned. More than two sentences, punctuation ambiguity, cross-sentence reference, and implicit subject carryover remain unsupported. A non-literal sentence is not promoted to an ordinary proposition.

The combined analysis round-trips through JSON. Deterministic ID remapping preserves proposition-to-entity, relation, logical-expression, and structural references, and existing reference validation remains strict.

## Audit impact and limitations

The 42-case audit moves from 33 to 34 exact cases, from 6 to 5 parser-unsupported cases, and remains at 0 analyzable-but-inexact, 0 comparator-unsupported, and 3 inference-not-implemented. Only `addition_002` changes classification; no gold expectation or schema changes.

This is not a general sentence segmenter or discourse parser. Abbreviations, quotations, decimals at sentence boundaries, ellipses, semicolons, questions, exclamations, paragraphs, arbitrary sentence counts, discourse relations, chronology, causality, ellipsis, fuzzy entity identity, and LLM/API interpretation remain outside scope.

A runnable inspection is available at [`examples/independent_two_sentence_propositions.py`](../../examples/independent_two_sentence_propositions.py).
