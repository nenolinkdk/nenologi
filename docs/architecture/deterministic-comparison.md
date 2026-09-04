# Deterministic semantic comparison v0.1

`DeterministicComparator` compares two already normalized `Analysis` objects. It never reads or compares raw document strings and has no dependency on `ControlledEnglishAnalyzer` internals.

```python
from nenologi import ControlledEnglishAnalyzer, DeterministicComparator

analyzer = ControlledEnglishAnalyzer()
source = analyzer.analyze("All employees must register.")
target = analyzer.analyze("Some employees may register.")
comparison = DeterministicComparator().compare(source, target)
```

The parser-neutral `Comparator` protocol exposes `compare(source, target, *, mode=...) -> Comparison`. Future analyzers can produce the same domain model, and future comparator strategies can implement the same boundary.

## Alignment boundary

v0.1 compares exactly one `EXPLICIT` proposition on each side. Predicates, argument count, argument roles, entity types, and normalized entity labels must match exactly. Operator scope must be exactly that proposition. Otherwise `UnsupportedComparisonError` is raised; the engine does not guess an alignment or report false equivalence.

The controlled analyzer now normalizes simple plural entity labels to singular forms so `Every employee` and `All employees` align. This is a deliberately small normalization, not general morphology or entity resolution.

## Rule tables

All supported transitions are explicit data in `comparison/rules.py`:

| Dimension | Transition | Severity |
| --- | --- | --- |
| Modality | `MUST → MAY` | `HIGH` |
| Modality | `MUST → SHOULD` | `HIGH` |
| Modality | `MAY → MUST` | `HIGH` |
| Quantifier | `ALL → SOME` | `HIGH` |
| Quantifier | `SOME → ALL` | `HIGH` |
| Quantifier | `NONE → SOME` | `HIGH` |
| Explicit polarity | affirmed → negated | `HIGH` |
| Explicit polarity | negated → affirmed | `HIGH` |

These severities indicate a material controlled semantic change, not legal, safety, or real-world impact. Every supported exact comparison uses confidence `1.0` with a deterministic rationale. Confidence remains independent of severity.

An unlisted transition raises `UnsupportedComparisonError`. It is not silently treated as equivalent.

## Finding order and equivalence

Findings are emitted in fixed dimension order:

1. `QUANTIFIER_CHANGE`
2. `MODALITY_CHANGE`
3. `NEGATION_CHANGE`

IDs (`difference_001`, and so on) follow that order. All dimensions are checked, so one comparison may produce multiple findings. Equivalent normalized analyses use `differences = []`; no artificial no-change difference type or severity is introduced.

Negative quantification (`NONE` plus its structural `NOT_EXISTS`) is handled solely as quantification. The comparator ignores `NOT_EXISTS` for explicit polarity comparison, preventing a duplicate negation finding.

## Contradiction taxonomy limitation

`contradiction_001` is individually analyzable but not counted as comparator-compatible. Its normalized pattern—an affirmed copular proposition versus the same explicitly negated proposition—is structurally identical to `negation_001` and `negation_002`, yet its gold expectation is `CONTRADICTION` rather than `NEGATION_CHANGE`.

Without an additional taxonomy rule or representation signal, classifying only the switch example as contradiction would be a lexical special case. v0.1 therefore consistently emits `NEGATION_CHANGE` for this polarity pattern, emits no duplicate contradiction finding, and leaves general contradiction classification for a later design decision. Gold data is unchanged.

## Unsupported comparisons

- Multiple propositions or non-`EXPLICIT` aligned propositions
- Different predicates, entity roles, types, or normalized labels
- Multiple/scoped-to-other-proposition operators
- Any modality or quantifier transition absent from the rule tables
- General contradiction, coordination, temporal, conditional, numeric, scope, addition/omission, or entity alignment logic
- `MAY NOT` scope resolution

A runnable end-to-end example is available at [`examples/semantic_comparison.py`](../../examples/semantic_comparison.py).
