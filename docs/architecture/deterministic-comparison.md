# Deterministic semantic comparison v0.1

`DeterministicComparator` compares two already normalized `Analysis` objects. It never reads or compares raw document strings and has no dependency on `ControlledEnglishAnalyzer` internals.

This behavior is frozen by the [Deterministic Core Contract — Phase 2 Freeze v1](deterministic-core-contract.md); incompatible later changes require a versioned contract.

Scope v0.1 compares category-level topology among aligned quantifier, modality, and negation references. A topology change among operator dimensions present on both sides emits one structured `SCOPE_CHANGE`; operator identity changes remain separate findings, and scope movement of an existing negation is not duplicated as `NEGATION_CHANGE`. See [Scope v0.1](scope-v0.1.md).

Before applying difference rules, the comparator now requires an explicit unique match from the [Proposition Alignment v0.1](proposition-alignment-v0.1.md) service. It enables only the documented single-core-position structural rule needed to preserve existing `ENTITY_RELATION_CHANGE` behavior.

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

v0.1 compares one aligned `EXPLICIT` main proposition on each side. For a supported condition, that main proposition is the consequent; otherwise the analysis contains exactly one proposition. Argument count and entity types/roles must correspond positionally. One entity label or the predicate may change, but not both and not multiple entities. Operators may form one controlled, acyclic scope chain ending at the aligned proposition. Otherwise `UnsupportedComparisonError` is raised; the engine does not guess an alignment or report false equivalence.

The controlled analyzer now normalizes simple plural entity labels to singular forms so `Every employee` and `All employees` align. This is a deliberately small normalization, not general morphology or entity resolution.

## Rule tables

Finite operator transitions are explicit data in `comparison/rules.py`; structural numeric, condition, and entity rules are explicit comparator branches:

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
| Condition | prefix IF added, removed, or antecedent identity changed | `HIGH` |
| Temporal relation | relation/reference added, removed, or changed | `MEDIUM`; `BEFORE ↔ AFTER` is `HIGH` |

These severities indicate a material controlled semantic change, not legal, safety, or real-world impact. Every supported exact comparison uses confidence `1.0` with a deterministic rationale. Confidence remains independent of severity.

An unlisted transition raises `UnsupportedComparisonError`. It is not silently treated as equivalent.

## Finding order and equivalence

Findings are emitted in fixed dimension order:

1. `QUANTIFIER_CHANGE`
2. `MODALITY_CHANGE`
3. `NEGATION_CHANGE`
4. `CONJUNCTION_CHANGE`
5. `NUMERIC_THRESHOLD_CHANGE`
6. `CONDITION_CHANGE`
7. `TEMPORAL_CHANGE`
8. `ENTITY_RELATION_CHANGE`

IDs (`difference_001`, and so on) follow that order. All dimensions are checked, so one comparison may produce multiple findings. Equivalent normalized analyses use `differences = []`; no artificial no-change difference type or severity is introduced.

Negative quantification (`NONE` plus its structural `NOT_EXISTS`) is handled solely as quantification. The comparator ignores `NOT_EXISTS` for explicit polarity comparison, preventing a duplicate negation finding.

## Contradiction taxonomy correction

`CONTRADICTION` was removed from the v0.1 `DifferenceType` enum because it described a logical relation rather than what changed. The correction is additive at the comparison level: `Comparison.logical_relation` now carries `EQUIVALENT`, `CONTRADICTORY`, or `UNDETERMINED`.

Gold case `contradiction_001` now expects `NEGATION_CHANGE` (`AFFIRMED → NEGATED`) and `logical_relation: CONTRADICTORY`. This is a specification correction, not an accommodation to implementation: the same normalized polarity pattern must have the same difference classification regardless of whether the noun is “switch”, “valve”, or “alarm”. General contradiction reasoning remains deferred.

## Controlled conjunction and entity comparison

Conjunction is read from one normalized `AND` or `OR` semantic relation joining exactly two proposition objects. Adding/removing conjunction, repeated coordination, and nested coordination are unsupported. `AND ↔ OR` uses explicit transition rules.

Predicate-level `PREDICATE_AND` instead references distinct authoritative propositions. Exact alignment may therefore retain one member and classify one safely unmatched member as addition or omission. Flat object conjunction members are ordered by normalized semantic identity, making reversed `AND` surfaces equivalent while preserving source spans. See [Coordinated Predicate Graphs v0.1](coordinated-predicate-graphs-v0.1.md).

Entity comparison uses positional roles in one proposition. Index zero is reported as `SUBJECT:<LABEL>`; later positions as `OBJECT:<LABEL>`. Predicate changes report the canonical source and target predicate values directly. This is controlled structural correspondence, not entity resolution, synonymy, or lexical similarity.

Gold-standard comparator coverage increased from 8 to 11 cases: the previous modality, quantifier, and negation cases; both conjunction cases; and the corrected contradiction-relation case. The three existing entity/relation gold cases remain unsupported because they require past-tense normalization or spatial-relation grammar beyond this controlled extension.

## Numeric thresholds

Exactly one normalized numeric constraint may be scoped to the aligned proposition. Operator, exact decimal value, and optional normalized unit are compared. Equivalent surfaces such as `at least 18` and `>= 18.0` produce no finding. A changed component produces `NUMERIC_THRESHOLD_CHANGE`; the explanation identifies whether operator, value, or unit changed without inferring safety or domain consequences. Units are compared literally and never converted. For compatibility with the committed gold contract, finding values use canonical symbolic strings such as `>= 18`; their references point to the complete structured constraints in the two nested analyses, which remain authoritative.

Numeric differences do not by themselves establish contradiction or entailment, so their logical relation is `UNDETERMINED`. Interval algebra is outside v0.1. Gold coverage is now 16 exact cases: the previous 11, four numeric changes, and one numeric equivalence.

## Conditions

A condition aligns its consequent with the other main proposition and holds explicit references to one antecedent and one consequent. Adding or removing that governing IF relation produces one `CONDITION_CHANGE`; it does not also produce `ADDITION` or `OMISSION`. If both conditions align and only a normalized numeric threshold inside the antecedent changes, the comparator emits the more specific `NUMERIC_THRESHOLD_CHANGE`, not a redundant condition finding. A distinct antecedent predicate/entity produces `CONDITION_CHANGE`; multiple independent nested changes may produce their corresponding distinct findings.

Condition comparison establishes neither contradiction nor conditional entailment, so changed conditions use `UNDETERMINED`. Prefix `condition_001`, suffix `condition_002`, deconditionalization case `omission_001`, and controlled UNLESS case `condition_003` are exact. Antecedent polarity participates in condition identity, so UNLESS versus positive IF produces one `CONDITION_CHANGE` without a redundant negation finding. See [Controlled UNLESS Conditions v0.1](unless-conditions-v0.1.md).

## Temporal relations

Exactly one structured temporal relation may govern an aligned proposition. It contains a typed `BEFORE`, `AFTER`, `ON`, or `UNTIL` relation and either a canonical literal reference, an aligned proposition reference, or the registered structured noon-reference graph. Comparator values retain the relation and resolve structured references before comparison. Those cases produce the existing v0.1 taxonomy value `TEMPORAL_CHANGE`; they do not additionally produce `ADDITION` or `OMISSION`.

Temporal relations can govern a condition consequent because the `Condition` continues to reference that proposition rather than duplicating temporal content. Clock references such as `18:00` never enter `NumericConstraint`. Changed temporal relations use logical relation `UNDETERMINED`; no calendar, interval, or entailment reasoning is performed.

Temporal v0.1 activated weekday case `temporal_002`; [Controlled Event-anchored Temporal Relations v0.1](event-anchored-temporal-relations-v0.1.md) activates `temporal_001`; and [Controlled Nested Temporal References v0.1](nested-temporal-references-v0.1.md) activates `temporal_003` through a resolved reference graph. The public task terminology “temporal relation change” maps to the committed machine identifier `TEMPORAL_CHANGE`.

## Unsupported comparisons

- Ambiguous multiple propositions or non-`EXPLICIT` aligned propositions
- Different argument counts/types, more than one changed entity, or simultaneous entity and predicate changes
- Multiple operators of one dimension on an aligned proposition
- Any modality or quantifier transition absent from the rule tables
- General contradiction, coordination, alignment, temporal, conditional, interval, or scope reasoning
- Fuzzy alignment, ambiguous addition/omission, proposition split/merge, and domain-specific importance ranking
- Adding/removing a numeric constraint, multiple numeric constraints, ranges, conversions, or numeric entailment
- Multiple, nested, general `UNLESS`, `ELSE`, biconditional, chained, counterfactual, or causally interpreted conditions outside the registered prefix, suffix, and exact UNLESS forms
- Multiple/nested temporal phrases, event anchors, durations, relative dates, time zones, calendar arithmetic, recurrence, tense/aspect, or temporal entailment
- `MAY NOT` scope resolution

The two controlled embedded-negation families are an explicit exception to general scope parsing. When identical `PROMISE`/`REQUIRE`, `NOT`, and `LEAVE` ingredients have different operator edges, the comparator emits one high-severity `SCOPE_CHANGE` using canonical nested values. See [Controlled Embedded Negation Scope v0.1](embedded-negation-scope-v0.1.md).

A runnable end-to-end example is available at [`examples/semantic_comparison.py`](../../examples/semantic_comparison.py).
