# Initial gold standard

The initial v0.1 gold standard contains 30 controlled change cases, 5 semantic-equivalence cases, and 7 inference-status cases. Each case changes as little as possible, making failures diagnosable. The machine-readable files and contribution instructions are in the [gold-standard directory](../../tests/gold_standard/README.md).

```json
{
  "id": "modality_001",
  "source": "All employees must register.",
  "target": "All employees may register.",
  "expected": {
    "difference_type": "MODALITY_CHANGE",
    "source_value": "MUST",
    "target_value": "MAY",
    "severity": "HIGH"
  }
}
```

## Initial allocation

- 30 comparison cases with material changes, covering all 11 corrected v0.1 difference types plus a contradiction-relation case
- 5 controlled semantic-equivalence cases
- 7 inference cases covering all v0.1 interpretation statuses

Expected data may include multiple acceptable analyses when ambiguity is intentional. Severity is expected only for findings; confidence is independently evaluated with tolerances or categorical expectations. Cases should be small enough for human review and schema validation.

Gold updates require an explanation and review. A changed implementation must not silently rewrite expected outputs to make tests pass.

Taxonomy correction: `contradiction_001` now expects a `NEGATION_CHANGE` and separate `CONTRADICTORY` logical relation. Its text did not change. This prevents contradiction (a proposition relation) from being confused with negation change (the textual/semantic cause).

The deterministic comparator currently executes 16 exact cases. Numeric Thresholds v0.1 raised coverage from 11 to 16 by activating `numeric_001` through `numeric_004` plus `equivalence_003`; expected gold results were not changed.

Conditions v0.1 raises exact coverage from 16 to 17 by activating prefix-IF removal case `condition_001`. Suffix-IF `condition_002` and `UNLESS` case `condition_003` remain intentionally inactive; no gold expectation was changed.
