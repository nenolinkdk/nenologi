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
[ALL | EVERY | SOME | NO] SUBJECT [MUST | MAY | SHOULD] [NOT] VERB [OBJECT]
[THE | A | AN] SUBJECT (IS | ARE) [NOT] COMPLEMENT
```

The quantifier and article are optional. Subjects and objects contain one noun; an object may have `the`, `a`, or `an`. The controlled action vocabulary is `access`, `approve`, `enter`, `open`, `register`, `restart`, `submit`, `vote`, and `wear`. A small copular form supports one complement, primarily to connect existing controlled gold cases.

Supported semantic features are:

- `ALL` and normalized `EVERY -> ALL`
- `SOME`
- `NO -> NONE` plus `NOT_EXISTS`
- `MUST`, `MAY`, and `SHOULD`
- `NOT` immediately after a modal, or after `is`/`are`
- Intransitive actions and a single simple object
- A proposition, optional action relation, entities, operators, source spans, and structural phrase nodes

Within this controlled grammar, `MAY NOT` is compositionally represented as `May(¬P)`. Ordinary English can also use “may not” as prohibition; inputs requiring that alternate reading need a future ambiguity-aware grammar.

## Normalization and preservation

Recognition is case-insensitive; runs of whitespace are insignificant; one final period is optional. `EVERY` normalizes to `ALL`, and `NO` to `NONE`. A small deterministic singularizer is used only for display text. No synonym expansion, tense conversion, or world-knowledge inference occurs.

`document.text` always preserves the caller's exact input. Token spans refer to that original string. Equivalent normalized inputs produce the same positional ID sequence and semantic identifiers, although original text and spans may differ.

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
```

Plain-language output uses fixed templates, such as “The sentence states that every employee is required to register.”

A runnable example is available at [`examples/controlled_english.py`](../../examples/controlled_english.py).

## Explicitly unsupported

- More than one sentence
- Questions and exclamations
- Coordination and subordination
- Relative clauses and conditions
- Passive voice and complex tense/aspect
- Multiword noun phrases beyond a determiner plus one noun
- Idioms, metaphor, broad synonymy, and unknown action verbs
- Languages other than English

## Gold-standard compatibility

Both sides of these existing comparison cases are individually analyzable (automatic difference detection is not yet implemented):

- `modality_001` through `modality_003`
- `quantifier_001` through `quantifier_003`
- `negation_001` and `negation_002`
- `contradiction_001`

Other cases remain intentionally outside this grammar. Gold expected results are unchanged.
