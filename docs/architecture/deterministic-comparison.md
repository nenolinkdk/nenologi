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

## Difference and logical relation

`differences` answer **what changed**: an operator, entity, or predicate. `logical_relation` separately describes the supported relation between the resulting propositions:

- `EQUIVALENT` — no supported structural/semantic difference was found after safe alignment
- `CONTRADICTORY` — the only change is explicit polarity over the otherwise identical proposition
- `UNDETERMINED` — the narrow comparator does not establish either relation

A polarity reversal therefore yields one `NEGATION_CHANGE` and `CONTRADICTORY`; it does not emit a duplicate contradiction difference.

## Alignment boundary

v0.1 compares exactly one `EXPLICIT` proposition on each side. Argument count and entity types/roles must correspond positionally. One entity label or the predicate may change, but not both and not multiple entities. Operator scope must be exactly that proposition. Otherwise `UnsupportedComparisonError` is raised; the engine does not guess an alignment or report false equivalence.

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
| Conjunction | `AND → OR` | `HIGH` |
| Conjunction | `OR → AND` | `HIGH` |
| One positional subject/object label | changed | `HIGH` |
| Predicate identity | changed | `HIGH` |
| Numeric threshold | operator/value/unit changed | `MEDIUM`, or `HIGH` when exact equality is entered/left |

These severities indicate a material controlled semantic change, not legal, safety, or real-world impact. Every supported exact comparison uses confidence `1.0` with a deterministic rationale. Confidence remains independent of severity.

An unlisted transition raises `UnsupportedComparisonError`. It is not silently treated as equivalent.

## Finding order and equivalence

Findings are emitted in fixed dimension order:

1. `QUANTIFIER_CHANGE`
2. `MODALITY_CHANGE`
3. `NEGATION_CHANGE`
4. `CONJUNCTION_CHANGE`
5. `NUMERIC_THRESHOLD_CHANGE`
6. `ENTITY_RELATION_CHANGE`

IDs (`difference_001`, and so on) follow that order. All dimensions are checked, so one comparison may produce multiple findings. Equivalent normalized analyses use `differences = []`; no artificial no-change difference type or severity is introduced.

Negative quantification (`NONE` plus its structural `NOT_EXISTS`) is handled solely as quantification. The comparator ignores `NOT_EXISTS` for explicit polarity comparison, preventing a duplicate negation finding.

## Contradiction taxonomy correction

`CONTRADICTION` was removed from the v0.1 `DifferenceType` enum because it described a logical relation rather than what changed. The correction is additive at the comparison level: `Comparison.logical_relation` now carries `EQUIVALENT`, `CONTRADICTORY`, or `UNDETERMINED`.

Gold case `contradiction_001` now expects `NEGATION_CHANGE` (`AFFIRMED → NEGATED`) and `logical_relation: CONTRADICTORY`. This is a specification correction, not an accommodation to implementation: the same normalized polarity pattern must have the same difference classification regardless of whether the noun is “switch”, “valve”, or “alarm”. General contradiction reasoning remains deferred.

## Controlled conjunction and entity comparison

Conjunction is read from one normalized `AND` or `OR` semantic relation joining exactly two proposition objects. Adding/removing conjunction, repeated coordination, and nested coordination are unsupported. `AND ↔ OR` uses explicit transition rules.

Entity comparison uses positional roles in one proposition. Index zero is reported as `SUBJECT:<LABEL>`; later positions as `OBJECT:<LABEL>`. Predicate changes use `PREDICATE:<VALUE>`. This is controlled structural correspondence, not entity resolution, synonymy, or lexical similarity.

Gold-standard comparator coverage increased from 8 to 11 cases: the previous modality, quantifier, and negation cases; both conjunction cases; and the corrected contradiction-relation case. The three existing entity/relation gold cases remain unsupported because they require past-tense normalization or spatial-relation grammar beyond this controlled extension.

## Numeric thresholds

Exactly one normalized numeric constraint may be scoped to the aligned proposition. Operator, exact decimal value, and optional normalized unit are compared. Equivalent surfaces such as `at least 18` and `>= 18.0` produce no finding. A changed component produces `NUMERIC_THRESHOLD_CHANGE`; the explanation identifies whether operator, value, or unit changed without inferring safety or domain consequences. Units are compared literally and never converted. For compatibility with the committed gold contract, finding values use canonical symbolic strings such as `>= 18`; their references point to the complete structured constraints in the two nested analyses, which remain authoritative.

Numeric differences do not by themselves establish contradiction or entailment, so their logical relation is `UNDETERMINED`. Interval algebra is outside v0.1. Gold coverage is now 16 exact cases: the previous 11, four numeric changes, and one numeric equivalence.

## Unsupported comparisons

- Multiple propositions or non-`EXPLICIT` aligned propositions
- Different argument counts/types, more than one changed entity, or simultaneous entity and predicate changes
- Multiple/scoped-to-other-proposition operators
- Any modality or quantifier transition absent from the rule tables
- General contradiction/coordination/alignment, temporal, conditional, interval, scope, or addition/omission logic
- Adding/removing a numeric constraint, multiple numeric constraints, ranges, conversions, or numeric entailment
- `MAY NOT` scope resolution

A runnable end-to-end example is available at [`examples/semantic_comparison.py`](../../examples/semantic_comparison.py).
