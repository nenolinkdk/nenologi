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
```

Plain-language output uses fixed templates, such as “The sentence states that every employee is required to register.”

A runnable example is available at [`examples/controlled_english.py`](../../examples/controlled_english.py).

## Explicitly unsupported

- More than one sentence
- Questions and exclamations
- Subject/predicate coordination, nested/repeated coordination, and subordination
- Relative clauses and conditions
- Passive voice and complex tense/aspect
- Multiword noun phrases beyond a determiner plus one noun
- Ranges, fractions, scientific notation, signed values, arithmetic, approximation, locale decimals, and unit conversion
- Idioms, metaphor, broad synonymy, and unknown action verbs
- Languages other than English

## Gold-standard compatibility

Both sides of these existing comparison cases are individually analyzable (automatic difference detection is not yet implemented):

- `modality_001` through `modality_003`
- `quantifier_001` through `quantifier_003`
- `negation_001` and `negation_002`
- `contradiction_001`

The deterministic comparator additionally supports both conjunction cases (`conjunction_001` and `conjunction_002`), all four numeric change cases (`numeric_001` through `numeric_004`), and numeric equivalence case `equivalence_003`.

Other cases remain intentionally outside this grammar. Gold expected results are unchanged.
