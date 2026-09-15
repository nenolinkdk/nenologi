# Controlled English Analyzer v0.1

`ControlledEnglishAnalyzer` is the first real Nenologi analysis path:

```text
text -> controlled parser -> Analysis -> validation
     -> structured semantics + derived formula + fixed interpretation
```

It is a proof of the core architecture, not a general English parser. Unsupported constructions raise `UnsupportedConstructionError`; the analyzer never guesses or returns silent partial semantics.

## Parser-neutral interface

The public `Analyzer` protocol defines:

```python
analyze(text, *, language="en", profile="general") -> Analysis
```

Consumers can depend on this interface rather than parser internals. Future rule-based, language-specific, LLM-backed, or hybrid analyzers may implement it, but none is implemented or selected here. Models remain parser-independent.

## Grammar

One optional-final-period declarative sentence is accepted:

```text
[ALL | EVERY | SOME | NO] SUBJECT [MUST | MAY | SHOULD] [NOT] VERB [OBJECT [AND | OR] OBJECT]
[THE | A | AN] SUBJECT (IS | ARE) [NOT] COMPLEMENT
VERB OBJECT [AND | OR] OBJECT
[ALL | EVERY | SOME | NO] SUBJECT ([MUST | MAY | SHOULD] BE | IS | ARE) NUMERIC_CONSTRAINT
VERB NUMERIC_CONSTRAINT [UNIT]
IF SIMPLE_ANTECEDENT, CONSEQUENT
PROPOSITION [BEFORE | AFTER | ON | UNTIL] TEMPORAL_REFERENCE
PROPER_NAME IS A|AN CLASS
ALL [MODIFIER] CLASS_PLURAL ARE CLASS
UNIVERSAL_RULE. MEMBERSHIP.
PROPER_NAME (LIVES | LIVED) IN PROPER_NAME [FOR NUMBER YEAR(S)]
PROPER_NAME SPEAKS [FLUENT] PROPER_NAME
THE SUBJECT FLICKERED ON EACH OF THE LAST NUMBER EVENINGS
THE SUBJECT WILL FLICKER THIS EVENING
PROPER_NAME TOLD PROPER_NAME THAT (THEY | REPEATED_PROPER_NAME) HAD WON
PROPER_NAME HAD WON
TIME IS A THIEF
TIME COMMITS THEFT
```

The quantifier and article are optional. Subjects contain one noun. An object contains one or two controlled words and may have `the`, `a`, or `an`. Exactly two object phrases may be joined by one `AND` or `OR`. The imperative form exists only for this same controlled object grammar. The controlled action vocabulary is `access`, `approve`, `choose`, `enter`, `open`, `receive`, `register`, `report`, `restart`, `submit`, `vote`, and `wear`. A small copular form supports one complement.

Supported semantic features are:

- `ALL` and normalized `EVERY -> ALL`
- `SOME`
- `NO -> NONE` plus `NOT_EXISTS`
- `MUST`, `MAY`, and `SHOULD`
- `NOT` immediately after a modal, or after `is`/`are`
- Intransitive actions and a single simple object
- One flat `AND`/`OR` coordination between two simple objects
- One numeric threshold using `more than`, `greater than`, `at least`, `less than`, `below`, `at most`, or `exactly`; the symbolic forms `>`, `>=`, `<`, `<=`, and `=` are equivalent
- Integer values, simple dot decimals, and the number words zero through ten; `VALUE or more` is the one additional equivalence form used by the committed gold standard
- A proposition, optional action relation, entities, operators, source spans, and structural phrase nodes
- One prefix `IF` condition whose antecedent is one simple copular property or numeric threshold and whose consequent is one otherwise supported controlled proposition
- One proposition-final temporal phrase using `before`, `after`, `on`, or `until` with a weekday or 24-hour `HH:MM` clock time
- Predicate-view class membership and universal class rules over one structural bound variable
- One controlled two-sentence `RULE. MEMBERSHIP.` document; no general sentence or discourse parsing
- One controlled residence proposition with an optional year duration, or one controlled language-speaking proposition
- One repeated flicker observation or one future-evening flicker proposition with a canonical relative temporal reference
- One controlled `TELL` clause with ambiguous `they` or an exact repeated participant name, plus one named `WON` claim
- One registered non-literal `Time is a thief` form and its independently literal theft query

Within this controlled grammar, `MAY NOT` is compositionally represented as `May(¬P)`. Ordinary English can also use “may not” as prohibition; inputs requiring that alternate reading need a future ambiguity-aware grammar.

## Normalization and preservation

Recognition is case-insensitive; runs of whitespace are insignificant; one final period is optional. `EVERY` normalizes to `ALL`, and `NO` to `NONE`. A small deterministic singularizer normalizes the simple controlled entity label and supports display text, allowing `employee` and `employees` to align. No broad morphology, synonym expansion, tense conversion, or world-knowledge inference occurs.

`document.text` always preserves the caller's exact input. Token spans refer to that original string. Equivalent normalized inputs produce the same positional ID sequence and semantic identifiers, although original text and spans may differ.

Numeric values use exact `Decimal` semantics and serialize as canonical decimal strings. The controlled units are `year(s)`, `kg`, `%`, `°C`, `degree(s)`, `copy/copies`, and `file(s)`; inflected forms normalize to singular machine values. Units are not converted. `g` is intentionally unsupported, so `10 kg` cannot be equated with `10000 g`.

## Deterministic IDs

IDs are role-and-position based: `doc_001`, `sentence_001`, `entity_001`, `prop_001`, `quantifier_001`, `modality_001`, `negation_001`, `relation_001`, and `logic_001`. No random values or process-global counters are used.

## Derived output

The structured `Analysis` is authoritative. Formula strings are deterministic display values, for example:

```text
All employees must register.
∀x (Employee(x) → Must(Register(x)))

Some employees must register.
∃x (Employee(x) ∧ Must(Register(x)))

No visitors may enter.
¬∃x (Visitor(x) ∧ May(Enter(x)))

All patients must receive treatment A and treatment B.
∀x (Patient(x) → Must((Receive(x, TreatmentA) ∧ Receive(x, TreatmentB))))

The score must be at least 18.
Must(Score(x) ≥ 18)

If the temperature is above 30 °C, the system must stop.
(Temperature(x) > 30 °C) → (Must(Stop(System)))

Employees must register before Friday.
Before(Must(Register(Employee)), Friday)
```

Plain-language output uses fixed templates, such as “The sentence states that every employee is required to register.”

A runnable example is available at [`examples/controlled_english.py`](../../examples/controlled_english.py).

## Scope v0.1

Exactly one fronted form is supported: `Not all SUBJECT [MODAL] PREDICATE`. It normalizes as explicit `NOT > ALL > [MODAL] > proposition` references. Ordinary controlled modal negation normalizes as `[QUANTIFIER] > MODAL > NOT > proposition`. Other fronted quantifier/negation combinations are rejected rather than guessed.

`MAY NOT` retains the fixed controlled reading `MAY > NOT > proposition`; this is not general natural-language disambiguation. See [Scope v0.1](scope-v0.1.md).

## Simple past transitive v0.1

The parser accepts the explicit affirmative active forms documented in [Simple Past Transitive Clauses v0.1](simple-past-transitive-v0.1.md). Each requires a determiner-led object and maps through a closed verb lexicon to the existing canonical predicate. Tense is not represented as a semantic operator or comparison dimension.

## Simple passive transitive v0.2

The parser accepts the singular controlled `PATIENT + WAS + PAST_PARTICIPLE + BY + AGENT` form documented in [Simple Passive Transitive Clauses v0.2](simple-passive-transitive-v0.2.md). It reorders surface roles into the same agent/patient semantics as active clauses. Auxiliary `WAS`, surface voice, and tense add no semantic operator or difference type.

## Contraction normalization v0.3

Immediately before controlled parsing, the tokenizer expands the closed forms `isn't`/`isn’t` to `is not` and `aren't`/`aren’t` to `are not`. At most one is accepted per clause. The existing negation and scope logic receives canonical tokens; no contraction metadata or semantic rule is added. See [Contraction Normalization v0.3](contraction-normalization-v0.3.md).

## Controlled spatial copular relations v0.1

The complete form `[THE] SUBJECT + IS/ARE + INSIDE/BESIDE + THE + REFERENCE_ENTITY` becomes a binary spatial proposition with ordered subject/reference arguments. `BE` is syntactic. Other copular complements remain unary properties, and temporal phrases retain their separate representation. See [Controlled Spatial Copular Relations v0.1](spatial-copular-relations-v0.1.md).

## Controlled suffix-IF conditions v0.1

One standalone `CONSEQUENT + IF + ANTECEDENT` form normalizes to the existing antecedent-first `Condition`, exactly like prefix `If A, B`. Both inner clauses reuse the current parser; the gold-required finite form `passes` maps explicitly to `PASS`. See [Controlled Suffix-IF Conditions v0.1](suffix-if-conditions-v0.1.md).

## Controlled rule and membership representation v0.1

The parser accepts the narrow class-membership, universal-rule, and two-sentence forms documented in [Controlled Rule and Membership Representation v0.1](rule-membership-representation-v0.1.md). Membership uses class propositions; a rule uses shared `BOUND_VARIABLE` arguments, a directed `Condition`, and `ALL` scoped over that condition. No universal instantiation occurs.

## Controlled residence and language propositions v0.1

The parser accepts the narrow `ProperName lives/lived in ProperName [for N years]` and `ProperName speaks [fluent] ProperName` forms documented in [Controlled Residence/Fluency Non-entailment v0.1](residence-fluency-non-entailment-v0.1.md). They normalize to distinct ordered binary predicates. Residence duration is preserved structurally, but no tense, geography, nationality, or country-language inference is added.

## Controlled observation and future representation v0.1

The exact repeated-evening observation and future-evening forms documented in [Controlled Observation and Future Representation v0.1](observation-future-representation-v0.1.md) normalize to `FLICKER(subject)` plus an `ON` temporal relation. Canonical references `LAST_N_EVENINGS` and `THIS_EVENING` preserve semantic identity without date resolution. `will` is treated as temporal syntax in this fragment, not as a general modality operator, and no prediction rule is added.

## Controlled coreference alternatives v0.1

The narrow speech/content forms documented in [Controlled Coreference Alternatives v0.1](coreference-alternatives-v0.1.md) represent `they` as one unresolved reference with two ordered participant alternatives. The embedded `WON(reference)` proposition is connected to `TELL(speaker, recipient)` by a content relation. Alternatives are not materialized as simultaneous facts, and no heuristic resolution or general complement-clause grammar is added.

## Controlled non-literal representation v0.1

The exact registered form `Time is a thief` is intercepted before ordinary class-membership parsing and represented as a `NON_LITERAL_EXPRESSION` with `CANNOT_BE_SAFELY_FORMALIZED` status and no proposition. `Time commits theft` remains an independent literal `COMMIT_THEFT(time)` proposition. See [Controlled Non-literal Representation v0.1](non-literal-representation-v0.1.md). No general metaphor detection or interpretation is added.

## Coordinated predicate graphs v0.1

The exact `Register ... and show ...` and `Sign and date ...` forms produce two authoritative propositions linked by `PREDICATE_AND`, with shared entity references where the surface construction shares participants. Flat two-object `AND`/`OR` remains one proposition and uses canonical semantic member ordering. See [Coordinated Predicate Graphs v0.1](coordinated-predicate-graphs-v0.1.md).

## Controlled independent two-sentence propositions v0.1

Exactly two period-terminated declarative sentences may be combined when each independently yields one ordinary, unqualified, explicit proposition. IDs are rebased deterministically and spans remain document-relative. No conjunction, discourse relation, temporality, coreference, or subject carryover is inferred. Unsupported members reject the whole document. See [Controlled Independent Two-sentence Propositions v0.1](independent-two-sentence-propositions-v0.1.md).

## Controlled embedded negation scope v0.1

The four exact `Maria ... promise ... leave` and `The rule ... require employees ... leave` forms documented in [Controlled Embedded Negation Scope v0.1](embedded-negation-scope-v0.1.md) normalize to one `LEAVE` proposition plus `PROMISE`/`REQUIRE` and `NOT` operator chains. Scope references, rather than surface text, distinguish outer from embedded negation. No general embedded-clause or scope resolution is added.

## Controlled UNLESS conditions v0.1

The exact `You may enter unless the door is locked` form normalizes to the existing `Condition` graph with `NOT` scoped to the `LOCKED` antecedent and `MAY` scoped to the `ENTER` consequent. The negation span retains the lexical `unless` trigger. See [Controlled UNLESS Conditions v0.1](unless-conditions-v0.1.md). No general UNLESS or conditional logic is added.

## Controlled event-anchored temporal relations v0.1

The exact `Inspect the cable (before|after) starting the machine` family produces ordinary `INSPECT` and `START` propositions plus one existing `TemporalRelation` whose endpoints are proposition IDs. The explicit marker carries relation provenance. See [Controlled Event-anchored Temporal Relations v0.1](event-anchored-temporal-relations-v0.1.md). No general event or temporal parser is added.

## Controlled nested temporal references v0.1

The exact `Wait until [after] noon` family represents `WAIT` plus an outer `UNTIL` relation whose reference is a structured `TEMPORAL_POINT(NOON)` or `TEMPORAL_AFTER(NOON)` semantic node. See [Controlled Nested Temporal References v0.1](nested-temporal-references-v0.1.md). No recursive or general temporal grammar is added.

## Explicitly unsupported

- More than two sentences; two-sentence documents outside the controlled independent-proposition or `RULE. MEMBERSHIP.` forms
- `UNLESS` outside the single registered form, `ELSE`, nested/chained/multiple conditions, comma-bearing suffix `IF`, multiple antecedents, antecedent coordination, and `MAY NOT` inside a condition
- Event-anchored temporal clauses outside the single registered inspect/start family; inverse, nested, coordinated, or implicit event chronology
- Nested temporal references outside the single registered `UNTIL [AFTER] NOON` family
- Questions and exclamations
- Predicate coordination outside the two registered forms, nested/repeated coordination, and subordination
- Relative clauses and complement clauses outside the controlled scope forms and single `TELL ... THAT ... HAD WON` form
- Passive constructions outside the single explicit v0.2 form, including `WERE`, agentless, perfect, progressive, modal, future, infinitival, and embedded passives
- Contractions other than the four explicit v0.3 spellings, multiple contractions, possessive apostrophes, and ambiguous apostrophe forms
- Spatial predicates other than `INSIDE` and `BESIDE`, compound/nested locations, distances, and spatial negation or modality
- Multiword noun phrases beyond a determiner plus one noun
- Ranges, fractions, scientific notation, signed values, arithmetic, approximation, locale decimals, and unit conversion
- Multiple temporal phrases, event-clause references, durations outside the single controlled residence form, relative dates outside the two controlled evening references, `before or on`, `after or on`, `since`, `during`, `when`, `by`, and `within`
- Idioms, metaphors outside the one registered non-literal form, broad synonymy, and unknown action verbs
- Languages other than English

## Gold-standard compatibility

Both sides of these existing comparison cases are analyzable and compared exactly:

- `modality_001` through `modality_003`
- `quantifier_001` through `quantifier_003`
- `negation_001` and `negation_002`
- `contradiction_001`
- `entity_relation_001` and `entity_relation_002`

The deterministic comparator additionally supports both conjunction cases (`conjunction_001` and `conjunction_002`), coordinated addition/omission cases `addition_001` and `omission_002`, all four numeric change cases (`numeric_001` through `numeric_004`), all three entity/relation cases, and equivalence cases `equivalence_002` through `equivalence_005`, plus prefix-IF removal case `condition_001` and weekday case `temporal_002`.

All gold inference cases are analyzable. Prediction, coreference-alternative evaluation, and non-literal policy remain explicit Phase 3 blockers; residence/fluency is exactly and conservatively `UNSUPPORTED`. The controlled parser boundary is frozen by the [Deterministic Core Contract](deterministic-core-contract.md). Gold expected results are unchanged; use the [Phase 2 Completion Audit](phase-2-completion-audit.md) for current status.
