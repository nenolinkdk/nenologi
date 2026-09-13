# Controlled Residence/Fluency Non-entailment v0.1

This milestone closes gold case `entailment_004` without adding world knowledge. The source `Peter lived in Paris for five years.` and the query `Peter speaks fluent French.` are both explicitly represented, but the inference result is `UNSUPPORTED` with rule `NOT_ESTABLISHED`.

## Controlled grammar

The analyzer accepts exactly these new proposition families:

```text
ProperName (lives | lived) in ProperName [for (integer | zero..ten) (year | years)]
ProperName speaks [fluent] ProperName
```

A final period is optional for this single-sentence fragment. Proper names use the existing narrow capitalized-name convention. Broader prepositional phrases, coordination, adverbs, modal forms, synonyms, coreference, and multi-sentence discourse are outside this milestone.

## Normalized semantics

Residence is the ordered binary proposition `LIVES_IN(person, location)`. Both `lives` and `lived` normalize to that predicate; v0.1 does not assign tense semantics. A supplied duration is preserved separately as a `DURATION` entity and relation attached to the residence proposition, for example `During(LivesIn(Peter, Paris), 5 year)`.

Language use is represented independently as either `SPEAKS(person, language)` or `SPEAKS_FLUENTLY(person, language)`. The argument order is semantic and is never reversed. Entities are typed `INDIVIDUAL`, `LOCATION`, `LANGUAGE`, and, when present, `DURATION`.

## Conservative inference boundary

The deterministic inference engine is unchanged. Exact normalized statements can still be `EXPLICIT`, lexical oppositions can still be `CONTRADICTED`, and supported class rules can still yield `ENTAILED`. Any unmatched residence/language pair falls through to `NOT_ESTABLISHED`.

In particular, Nenologi does not encode mappings such as Paris-to-French or France-to-French, does not infer fluency from residence duration, does not infer residence from language use, and does not infer facts about another person. This is open-world non-entailment: `UNSUPPORTED` does not mean the query is false.

## Validation and audit impact

Tests cover the exact gold case, deterministic predicates and IDs, entity typing, duration structure, argument order, same- and different-person cases, exact positive controls, serialization/reference validation, comparator behavior, existing inference rules, and rejection of broader syntax.

The 42-case audit moves from 29 to 30 `END_TO_END_EXACT` cases and from 4 to 3 `INFERENCE_NOT_IMPLEMENTED` cases. It remains at 0 `ANALYZABLE_BUT_NOT_EXACT`, 7 `PARSER_UNSUPPORTED`, and 2 `COMPARATOR_UNSUPPORTED`.

The next recommended representation-first milestone is controlled observation and future-event representation for `entailment_003`. Probabilistic prediction should remain outside deterministic inference until its policy is explicitly specified.
