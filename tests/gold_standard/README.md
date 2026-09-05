# Gold-standard regression cases

The v0.1 corpus contains short synthetic fixtures safe for public redistribution:

- `comparison/cases.json` — material semantic/logical changes
- `equivalence/cases.json` — wording changes with no expected material difference
- `entailment/cases.json` — candidate inference classification

All collections conform to `schemas/test-case-v0.1.schema.json`. IDs are unique across the complete corpus, not merely within one file.

## Add a case

1. Choose the appropriate collection and a lowercase unique ID such as `modality_004`.
2. Keep the example synthetic, short, and controlled; isolate one variable when possible.
3. Use stable enum identifiers from the v0.1 schema.
4. For a change case, set `material_difference` to `true` and provide one or more expected differences. For equivalence, use `false` and an empty `differences` list.
   Use optional `logical_relation` only when the controlled expectation is independently `EQUIVALENT`, `CONTRADICTORY`, or `UNDETERMINED`; never substitute it for the difference that caused the relation.
5. For inference, classify the candidate independently as `EXPLICIT`, `ENTAILED`, `PROBABLE`, `AMBIGUOUS`, `UNSUPPORTED`, `CONTRADICTED`, or `CANNOT_BE_SAFELY_FORMALIZED`.
6. Run validation and review the expected result manually. Do not change gold output only to accommodate an implementation failure.

## Validate

From the repository root, using Python 3:

```text
python tests/validation/validate_gold_standard.py
python -m unittest discover -s tests/validation -p "test_*.py"
```

For the complete per-case pipeline matrix, including concrete blocker codes, run `python tests/validation/audit_gold_coverage.py --json`. The human-readable baseline is the [Phase 1 completion audit](../../docs/architecture/phase-1-completion-audit.md).

Current coverage is 27 exact, 0 analyzable-but-inexact, 7 parser-unsupported, 2 comparator-unsupported, and 6 inference-not-implemented. `entailment_001` is recognized by exact normalized semantic identity. `omission_001` records a reviewed gold correction: removing a governing IF wrapper from an aligned proposition is `CONDITION_CHANGE`, not proposition `OMISSION`.

The validator uses only the Python standard library. It verifies that all schema JSON parses, required case fields exist, IDs are globally unique, enum values and language tags are valid, required difference/status coverage exists, and equivalence cases cannot masquerade as change cases.
