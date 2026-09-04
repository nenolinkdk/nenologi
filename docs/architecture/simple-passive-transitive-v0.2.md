# Simple Passive Transitive Clauses v0.2

## Controlled grammar

This milestone accepts exactly one affirmative singular passive clause:

```text
THE PATIENT [PATIENT_WORD] WAS PAST_PARTICIPLE BY [THE] AGENT
```

The patient is determiner-led and contains one or two controlled words. The agent is one controlled word and may have a determiner. `WAS` is the only supported agreement form; plural `WERE` is deliberately deferred rather than accepted without a general number model. The participle must occur in the closed Simple Past Transitive v0.1 lexicon.

## Semantic normalization

Surface voice is not authoritative. The passive surface subject becomes the semantic patient/object, while the `BY` phrase becomes the semantic agent/source-side subject:

```text
The company acquired the firm.       -> ACQUIRE(company, firm)
The firm was acquired by the company. -> ACQUIRE(company, firm)
```

Both forms therefore produce the same proposition signature and align through the unchanged deterministic aligner. The unchanged comparator reports no difference and `EQUIVALENT`. A changed agent or patient continues to use the existing `ENTITY_RELATION_CHANGE` rule.

`WAS` is a syntactic auxiliary in this complete pattern. It emits neither a `BE` proposition nor a tense operator. Voice and tense are not semantic comparison dimensions: there is no `VOICE_CHANGE`, `PASSIVE_CHANGE`, or `TENSE_CHANGE`. Ordinary copular parsing remains separate because passive recognition requires `WAS`, a recognized participle, `BY`, and an agent.

## Lexicon and BY policy

The implementation reuses `_PAST_ACTIONS`; identical active-past and passive-participle spellings map to one canonical predicate. Regular controlled forms include `acquired`, `approved`, `discovered`, `opened`, and `registered`; the existing explicit irregular forms are `sold`, `bought`, and `made`. There is no general participle morphology or expanded irregular dictionary.

`BY` has only the passive-agent role inside the complete grammar above. It does not introduce general prepositional-phrase parsing.

## Gold target and impact

`equivalence_002` is `Alice approved the request.` versus `The request was approved by Alice.` Before v0.2, its target stopped at `UNSUPPORTED_PASSIVE_VOICE`; all lexical forms already existed. Both sides now normalize to `APPROVE(alice, request)` and the existing pipeline returns `EQUIVALENT` with no findings.

The reproducible 42-case audit moves from 21 to 22 `END_TO_END_EXACT` and from 12 to 11 `PARSER_UNSUPPORTED`; the other totals remain 0 analyzable-but-inexact, 2 comparator-unsupported, and 7 inference-not-implemented.

## Explicit limitations

Agentless, perfect, past-perfect, progressive, modal, future, infinitival, embedded, plural/`WERE`, unknown-participle, malformed-agent, and arbitrary-preposition passives are rejected. Multi-sentence parsing, general agreement, tense inference, fuzzy alignment, synonyms, and passive-specific comparator rules remain outside v0.2.

A runnable demonstration is in [`examples/simple_passive_transitive.py`](../../examples/simple_passive_transitive.py).
