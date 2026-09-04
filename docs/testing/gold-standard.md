# Initial gold standard

The first gold standard should contain approximately 30 controlled cases: at least two per critical difference class, plus single-text interpretation, ambiguity, and safe-formalization cases. Each case should change as little as possible, making failures diagnosable.

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

- 12 comparison cases: one for each v0.1 difference type
- 7 additional critical minimal pairs: MUST/MAY, AND/OR, ALL/SOME, BEFORE/AFTER, `>`/`>=`, negation, and condition changes
- 4 single-text structural/semantic cases
- 3 scope or reference ambiguity cases
- 2 bounded-entailment cases
- 2 `cannot_be_safely_formalized` or unsupported cases

Expected data may include multiple acceptable analyses when ambiguity is intentional. Severity is expected only for findings; confidence is independently evaluated with tolerances or categorical expectations. Cases should be small enough for human review and schema validation.

Gold updates require an explanation and review. A changed implementation must not silently rewrite expected outputs to make tests pass.
