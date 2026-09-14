# Controlled Non-literal Representation v0.1

This safety-first milestone targets `entailment_007`:

```text
Source: Time is a thief.
Query:  Time commits theft.
Gold:   CANNOT_BE_SAFELY_FORMALIZED
```

Previously, the source reached the class-membership parser and incorrectly became authoritative `THIEF(time)`, while the query was rejected. Both now parse, but no literal meaning is inferred from the source. Deterministic inference returns `UNSUPPORTED / NOT_ESTABLISHED`; the audit remains `INFERENCE_NOT_IMPLEMENTED / METAPHOR_NON_LITERAL_FORMALIZATION` while parser and representation readiness become complete.

## Closed controlled grammar

Only two exact construction families are added:

```text
Time is a thief
Time commits theft
```

The first belongs to a one-entry, inspectable controlled non-literal pattern. This is not a detector, ontology, plausibility model, or general figurative-language lexicon. The second is an ordinary literal query represented as `COMMIT_THEFT(time)`.

## Surface and semantic representation

The source retains the safe `time` entity, sentence and phrase spans, and a `NON_LITERAL_EXPRESSION` semantic marker. Entity, marker, and logical-expression status are `CANNOT_BE_SAFELY_FORMALIZED` with confidence 1.0 in the deterministic pattern classification. Confidence does not claim knowledge of the unknown figurative meaning.

The source has no authoritative proposition: neither `THIEF(time)` nor `COMMIT_THEFT(time)` is asserted. The neutral structured logical operator is `UNRESOLVED_NON_LITERAL`, and its display is explicitly non-literal rather than a literal formula. Raw text and explanatory prose are not authoritative semantics.

## Inference safety

Because unsafe content is not a proposition, it cannot participate in exact explicit matching, lexical opposition, or universal instantiation. The literal query is therefore neither explicit, entailed, nor contradicted. No metaphor meaning, paraphrase, mapping, or inference rule is added.

Ordinary literal input remains unaffected: identical `Time commits theft.` analyses return `EXPLICIT / EXACT_EXPLICIT`. Comparator and aligner code are unchanged; no metaphor-specific difference type exists. Schemas and serialization are unchanged because existing statuses and semantic items are sufficient.

## Audit and limitations

The 42-case totals remain 30 exact, 0 analyzable-but-inexact, 7 parser-unsupported, 2 comparator-unsupported, and 3 inference-not-implemented. Internally, `entailment_007` moves from incomplete parsing to parser `SUPPORTED` / analysis `AVAILABLE`; safe formalization remains unavailable and the blocker remains `METAPHOR_NON_LITERAL_FORMALIZATION`.

All other metaphors, figurative predicates, subjects, and paraphrases remain unsupported. There is no animacy or commonsense ontology, lexical similarity, embedding, LLM/API, external NLP, statistical classification, or probabilistic interpretation.

This completes representation readiness for all three remaining inference cases. Future Phase 2 work should define explicit policy layers—non-literal interpretation, coreference alternative evaluation, or defeasible prediction—without weakening deterministic core guarantees. The recommended next step is a Phase 2 representation-readiness audit before choosing one such policy milestone.
