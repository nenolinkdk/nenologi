# Condition/Omission Taxonomy Resolution v0.1

## Case audit

`omission_001` compares:

```text
source: Open the valve if the pressure is low.
target: Open the valve.
```

The source contains `LOW(pressure)`, `OPEN(addressee, valve)`, and a `Condition` referencing the first proposition as antecedent and the second as consequent. The target contains the same normalized `OPEN(addressee, valve)` proposition without a condition. Alignment pairs those `OPEN` propositions exactly; only the source antecedent remains unaligned and is condition-owned.

Before this resolution, the comparator emitted one high-severity `CONDITION_CHANGE`, `IF_LOW → NONE`, with logical relation `UNDETERMINED`. The older gold expectation requested high-severity `OMISSION`, `IF_PRESSURE_LOW → null`, making the now-parsable case `ANALYZABLE_BUT_NOT_EXACT`.

## Taxonomy decision

The comparator behavior is canonical and the old gold expectation was wrong.

A `Condition` is an explicit wrapper/restriction referencing an existing consequent proposition; it does not replace that proposition with a separate conditional-proposition identity. Therefore:

```text
P        ↔ P IF A  => CONDITION_CHANGE
P IF A   ↔ P       => CONDITION_CHANGE
```

This describes the changed applicability of aligned semantic content. `ADDITION` and `OMISSION` remain reserved for safely unmatched propositions. A condition-owned antecedent is excluded from unmatched-proposition findings when the wrapper change already explains its presence or absence.

The rule is symmetric, general, and independent of prefix/suffix surface order. It is also consistent with the MVP specification, Conditions v0.1, semantic-core consolidation, deterministic comparison, and Addition/Omission v0.1 contracts that predate parser support for this gold case.

## Precedence and anti-duplication

For aligned propositions, specialized semantic dimensions run before unmatched classification. Condition wrapper addition/removal emits exactly one `CONDITION_CHANGE`; it never also emits `ADDITION` or `OMISSION`. A changed antecedent remains `CONDITION_CHANGE`. A nested consequent difference uses its specific dimension, such as `MODALITY_CHANGE` or `ENTITY_RELATION_CHANGE`. A numeric-only antecedent change remains `NUMERIC_THRESHOLD_CHANGE` without a redundant condition finding.

Truly unmatched propositions still yield `ADDITION` or `OMISSION`. Thus the taxonomy distinguishes applicability changes, proposition presence changes, antecedent changes, and nested proposition changes without overlap.

Logical relation is evaluated separately. Condition addition or removal is conservatively `UNDETERMINED`; this milestone adds no implication, entailment, or contradiction reasoning.

## Gold correction and impact

The `omission_001` expected finding is corrected from `OMISSION(IF_PRESSURE_LOW → null)` to `CONDITION_CHANGE(IF_LOW → NONE)`. Its historical ID and category remain unchanged for corpus continuity, while its description now identifies removal of a governing condition.

The 42-case audit moves from 25 to 26 `END_TO_END_EXACT` and from 1 to 0 `ANALYZABLE_BUT_NOT_EXACT`. Parser coverage remains unchanged: 7 parser-unsupported, 2 comparator-unsupported, and 7 inference-not-implemented cases remain. No parser, comparator, aligner, schema, or DifferenceType implementation changes are required.
