# Contraction Normalization v0.3

## Supported surface forms

Contraction normalization is a closed preprocessing step immediately before the existing Controlled English parser. It supports exactly:

| ASCII | Typographic | Canonical expansion |
| --- | --- | --- |
| `isn't` | `isn’t` | `is not` |
| `aren't` | `aren’t` | `are not` |

Matching is case-insensitive and applies only to complete tokens. At most one supported contraction is accepted per clause. Ordinary non-contracted input passes through the same token path unchanged.

The tokenizer emits the canonical `is`/`are` and `not` tokens while retaining source-local spans over the original contraction. The existing copular parsing, negation operator, scope, logical rendering, aligner, comparator, serialization, and schema then run unchanged. No contraction state enters the authoritative semantic model, and no contraction-specific DifferenceType exists.

## Gold target

`equivalence_004` compares `The valve is not open.` with `The valve isn't open.` The blocker was the ASCII `isn't`; its canonical expansion is `is not`, which was already supported. Both sides normalize to the same `OPEN(valve)` proposition and `NOT → prop_001` operator topology. Deterministic alignment is exact, comparison emits no findings, and the logical relation is `EQUIVALENT`.

The 42-case audit moves from 22 to 23 `END_TO_END_EXACT` and from 11 to 10 `PARSER_UNSUPPORTED`. The remaining totals stay at 0 analyzable-but-inexact, 2 comparator-unsupported, and 7 inference-not-implemented. No other gold case is unlocked.

## Safety and ambiguity policy

ASCII `'` and typographic `’` are recognized only in the four listed tokens; there is no broad Unicode punctuation conversion. Unknown, informal, or ambiguous forms—including `'d`, general `'s`, `won't`, and `ain't`—are rejected. Possessives such as `company's` and `manager’s` are rejected rather than expanded or parsed as possession. Substring replacement is never used, so contraction-like text inside a larger token is not rewritten.

General contraction dictionaries, productive morphology, possessive parsing, multiple contractions, embedded clauses, and contextual resolution of ambiguous forms remain outside v0.3.

A runnable demonstration is available at [`examples/contraction_normalization.py`](../../examples/contraction_normalization.py).
