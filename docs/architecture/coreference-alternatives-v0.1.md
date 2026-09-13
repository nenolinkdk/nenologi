# Controlled Coreference Alternatives v0.1

This representation-first milestone targets `entailment_006`:

```text
Source: Alex told Sam that they had won.
Query:  Alex had won.
Gold:   AMBIGUOUS
```

Both texts now parse. The deterministic inference engine remains conservative and returns `UNSUPPORTED / NOT_ESTABLISHED`; the audit therefore remains `INFERENCE_NOT_IMPLEMENTED / COREFERENCE_AMBIGUITY`, but parser and representation readiness are complete.

## Controlled grammar

Only these forms are added:

```text
ProperName told ProperName that (they | repeated ProperName) had won
ProperName had won
```

The repeated proper name must exactly match the speaker or recipient. Only plural-form `they` is supported as an unresolved reference. No general complement-clause, discourse, pronoun, tense, or speech-act grammar is introduced.

## Authoritative ambiguity representation

The two named mentions become `INDIVIDUAL` entities in document order. Ambiguous `they` becomes one `UNRESOLVED_REFERENCE` entity with `AMBIGUOUS` status. Two ordered `REFERENCE_ALTERNATIVE` semantic items connect that reference first to the speaker and then to the recipient. Existing `Ambiguity.reading_ids` points to those alternative items.

The embedded proposition is `WON(reference_001)`, not simultaneous `WON(Alex)` and `WON(Sam)` assertions. The outer `TELL(Alex, Sam)` proposition is connected to it through a `CONTENT_RELATION`. Thus structured IDs—not the explanatory prose or display formula—are authoritative and survive JSON round-trip validation.

Candidate filtering uses only this controlled sentence's two explicit participant roles. Ordering follows mention/entity order. There is no nearest-noun, subject, recency, gender, animacy, plausibility, world-knowledge, statistical, or semantic ranking.

## Identity and inference policy

A named query for either candidate does not exactly match the unresolved reference and is not established. Ambiguity is not contradiction, and alternatives are alternative readings rather than existential or conjunctive facts. The neutral display `Unresolved(They -> {Alex, Sam})` avoids selecting one reading.

An exact repeated name is not ambiguous: `Alex told Sam that Alex had won.` contains explicit embedded `WON(Alex)`. Reported content is nevertheless not promoted to a standalone fact, so it does not establish `Alex had won.` A direct source `Alex had won.` still matches that query through `EXACT_EXPLICIT`. A minimal inference guard excludes propositions linked as embedded content from direct-fact evidence; no coreference inference rule is introduced. Evaluating and returning `AMBIGUOUS` when only some admissible interpretations support a query is deferred to a dedicated resolution layer.

The comparator and aligner are unchanged. Analyses containing ambiguity/sets remain conservatively unsupported for comparison; no new difference type is added. Schemas and serialization formats are unchanged because existing `Entity`, `SemanticItem`, `Ambiguity`, proposition, and relation structures suffice.

## Audit and limitations

The 42-case totals remain 30 exact, 0 analyzable-but-inexact, 7 parser-unsupported, 2 comparator-unsupported, and 3 inference-not-implemented. Internally, `entailment_006` moves from parser `UNSUPPORTED` / analysis `INCOMPLETE` to parser `SUPPORTED` / analysis `AVAILABLE`; only `COREFERENCE_AMBIGUITY` remains.

Unsupported scope includes other pronouns, possessives, other embedded predicates, omitted `that`, more participants, multiple clauses or sentences, fuzzy name matching, and all heuristic or probabilistic resolution.

The next recommended deterministic safety milestone is controlled non-literal representation for `entailment_007`, preserving `CANNOT_BE_SAFELY_FORMALIZED` without forcing metaphor into a literal theft claim.
