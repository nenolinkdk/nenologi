# Simple Past Transitive Clauses v0.1

This Phase 2 parser milestone recognizes a deliberately bounded set of affirmative active English simple-past clauses and maps them to the existing proposition/entity model. Tense is not a semantic comparison dimension.

## Controlled grammar

```text
[THE] SUBJECT CONTROLLED_PAST_VERB (THE | A | AN) OBJECT
```

Subject and object remain the existing one- or two-word controlled noun phrases. A past form must have a determiner-led object; this prevents an adverb such as `yesterday` from being guessed as an object. Quantifier, modal, negated, coordinated, embedded, and multi-sentence past forms are outside this subset.

Normalization uses an explicit lexicon, never general suffix stripping:

| Regular controlled form | Canonical predicate |
| --- | --- |
| acquired | `ACQUIRE` |
| approved | `APPROVE` |
| discovered | `DISCOVER` |
| opened | `OPEN` |
| registered | `REGISTER` |

| Explicit irregular form | Canonical predicate |
| --- | --- |
| bought | `BUY` |
| made | `MAKE` |
| sold | `SELL` |

The base predicates are also accepted by the existing controlled present/imperative path. Present and past inputs with the same normalized entities therefore share proposition identity and produce no tense-only difference. Original text and source spans remain preserved, but no tense operator, `TENSE_CHANGE`, aspect, event time, or temporal inference is introduced.

## Boundaries and result

| Status | Capability |
| --- | --- |
| **SUPPORTED** | One affirmative active controlled past verb with one determiner-led object. |
| **LIMITED** | Only the eight listed past forms; no productive morphology. |
| **UNSUPPORTED** | Passive voice, `did not`, present/past perfect, progressive aspect, unknown verbs, adverbial/intransitive past, coordination, relative/embedded clauses, and multi-sentence input. |

The parser alone unlocks `entity_relation_001` and `entity_relation_002`; both now normalize to `APPROVE(subject, object)` and the unchanged comparator emits the expected `ENTITY_RELATION_CHANGE`. Gold coverage moves from 19 exact / 14 parser-unsupported to 21 exact / 12 parser-unsupported. `equivalence_002` remains blocked by passive voice.
