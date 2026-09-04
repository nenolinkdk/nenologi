# Difference taxonomy

Initial semantic/logical difference classes:

- Negation change
- Conjunction/disjunction change
- Quantifier change
- Modality change
- Condition change
- Temporal change
- Scope change
- Entity/relation change
- Addition
- Omission
- Numerical/threshold change

Example:

```text
MODALITY_CHANGE
source: MUST
target: MAY
severity: HIGH
```

Severity and confidence are separate dimensions.

Contradiction is a logical relation between propositions, not a structural/semantic difference class. A negation change may cause a contradictory relation without creating a second textual-change finding. See [Deterministic semantic comparison](../architecture/deterministic-comparison.md).
