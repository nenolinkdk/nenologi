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

## Explicitly unsupported

- More than one sentence
- Suffix `IF`, `UNLESS`, `ELSE`, nested/chained conditions, multiple antecedents, antecedent coordination, and `MAY NOT` inside a condition
- Questions and exclamations
- Subject/predicate coordination, nested/repeated coordination, and subordination
- Relative clauses and conditions
- Passive voice and complex tense/aspect
- Multiword noun phrases beyond a determiner plus one noun
- Ranges, fractions, scientific notation, signed values, arithmetic, approximation, locale decimals, and unit conversion
- Multiple temporal phrases, event-clause references, durations, relative dates, `before or on`, `after or on`, `since`, `during`, `when`, `by`, and `within`
- Idioms, metaphor, broad synonymy, and unknown action verbs
- Languages other than English

## Gold-standard compatibility

Both sides of these existing comparison cases are analyzable and compared exactly:

- `modality_001` through `modality_003`
- `quantifier_001` through `quantifier_003`
- `negation_001` and `negation_002`
- `contradiction_001`
- `entity_relation_001` and `entity_relation_002`

The deterministic comparator additionally supports both conjunction cases (`conjunction_001` and `conjunction_002`), all four numeric change cases (`numeric_001` through `numeric_004`), numeric equivalence case `equivalence_003`, prefix-IF removal case `condition_001`, and weekday case `temporal_002`.

Other cases remain intentionally outside this grammar. Gold expected results are unchanged; use the [machine-readable audit](phase-1-completion-audit.md) for current status.
