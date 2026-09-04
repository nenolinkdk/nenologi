# Phase 1 Semantic Core Consolidation v0.1

This milestone hardens the existing semantic core without adding a semantic category or broadening Controlled English. Structured `Analysis` and `Comparison` objects remain authoritative; formulas and prose are derived displays.

## Taxonomy and canonical order

The taxonomy is consistent across Python enums, JSON Schemas, serialization, comparator tests, and gold data. `TEMPORAL_CHANGE` is the canonical machine name. `CONTRADICTION` is not a `DifferenceType`; comparison-level `logical_relation` separately records `EQUIVALENT`, `CONTRADICTORY`, or `UNDETERMINED`.

`CANONICAL_DIFFERENCE_ORDER` defines the complete stable order, including reserved positions for taxonomy members whose behavior is not implemented:

1. `QUANTIFIER_CHANGE`
2. `MODALITY_CHANGE`
3. `NEGATION_CHANGE`
4. `CONJUNCTION_CHANGE`
5. `NUMERIC_THRESHOLD_CHANGE`
6. `CONDITION_CHANGE`
7. `TEMPORAL_CHANGE`
8. `SCOPE_CHANGE` — implemented for explicit Scope v0.1 operator chains
9. `ENTITY_RELATION_CHANGE`
10. `ADDITION` — not implemented
11. `OMISSION` — not implemented

The comparator sorts findings by this explicit constant and then assigns deterministic IDs; enum, dictionary, and traversal order are not relied upon.

## Severity and confidence

| Difference | Current deterministic severity |
| --- | --- |
| Quantifier, modality, explicit negation, conjunction | `HIGH` for supported transitions |
| Numeric threshold | `MEDIUM`; `HIGH` when entering or leaving exact equality |
| Condition | `HIGH` |
| Temporal | `MEDIUM`; `HIGH` for `BEFORE ↔ AFTER` |
| Positional entity or predicate | `HIGH` |

Severity means materiality within the controlled comparison, not safety, quality, or real-world consequence. Confidence is independent: exact normalized rules currently use `1.0` with a deterministic rationale. Neither value is derived from the other.

## Duplicate-finding rules

- Adding/removing a condition yields `CONDITION_CHANGE`, not `ADDITION`/`OMISSION`.
- Adding/removing a temporal constraint yields `TEMPORAL_CHANGE`, not `ADDITION`/`OMISSION`.
- A numeric-only change inside an aligned antecedent yields `NUMERIC_THRESHOLD_CHANGE`, not a duplicate `CONDITION_CHANGE`.
- Explicit polarity reversal yields `NEGATION_CHANGE`; `CONTRADICTORY` may coexist because it describes proposition relation rather than the changed dimension.
- Canonically equivalent structures produce no finding.

Regression tests cover all five rules and cross-dimension combinations involving quantifier/modality, modality/temporal, quantifier/numeric, condition/consequent modality, condition/antecedent numeric, condition/consequent temporal, quantifier/modality/conjunction, quantifier/temporal, and modality/entity change.

## Reproducible gold audit

Run:

```powershell
$env:PYTHONPATH = "src"
python tests/validation/audit_gold_coverage.py
```

The audit executes each comparison/equivalence case through analyzer and comparator, compares exact structured findings, and classifies inference cases separately.

| Status | Cases |
| --- | ---: |
| Total | 42 |
| `END_TO_END_EXACT` | 19 |
| `ANALYZABLE_BUT_NOT_EXACT` | 0 |
| `PARSER_UNSUPPORTED` | 14 |
| `COMPARATOR_UNSUPPORTED` | 2 |
| `INFERENCE_NOT_IMPLEMENTED` | 7 |

| Feature | Exact | Parser unsupported | Comparator unsupported | Inference not implemented |
| --- | ---: | ---: | ---: | ---: |
| Modality | 3 | 0 | 0 | 0 |
| Quantification | 3 | 0 | 0 | 0 |
| Negation | 2 | 0 | 0 | 0 |
| Conjunction | 2 | 0 | 0 | 0 |
| Numeric threshold | 4 | 0 | 0 | 0 |
| Condition | 1 | 2 | 0 | 0 |
| Temporal | 1 | 2 | 0 | 0 |
| Entity/relation | 0 | 3 | 0 | 0 |
| Contradiction relation | 1 | 0 | 0 | 0 |
| Equivalence | 2 | 2 | 1 | 0 |
| Addition | 0 | 1 | 1 | 0 |
| Omission | 0 | 2 | 0 | 0 |
| Scope | 0 | 2 | 0 | 0 |
| Entailment | 0 | 0 | 0 | 7 |

Gold expectations were not changed. The previous hand-maintained count omitted already-exact `equivalence_001`; the audit corrects the overall number from 18 to 19.

## Consolidated capability status

| Status | Capability |
| --- | --- |
| **SUPPORTED** | Controlled quantification, modality, explicit negation, flat object conjunction, exact numeric thresholds, prefix IF, proposition-final temporal relations, deterministic JSON round-trip, conservative logical relation |
| **LIMITED** | Positional entity/predicate comparison, one aligned main proposition, one condition, one temporal relation, controlled units/weekdays/clock times, fixed English explanations |
| **UNSUPPORTED** | General scope and `MAY NOT` resolution, `UNLESS`, nested conditions, complex coordination, event-based temporal anchors, ranges/interval reasoning, addition/omission, broad proposition alignment, lexical semantics, multilingual parsing, general contradiction, inference/NLI, and providers/LLMs |

A rich round-trip regression combines a numeric antecedent with condition, quantified/modal consequent, and temporal relation. It verifies exact equality plus stable IDs, scopes, and references after `Analysis → JSON → Analysis`.

## Schema, normalization, and rendering

Schema/domain enum synchronization and condition, numeric, and temporal shapes are checked by the repository validator. Explicit serialization remains symmetric, all references resolve, and no obsolete parallel representations were found. The comparator imports normalized models only and does not depend on analyzer internals.

Normalization regressions cover `Every → ALL`, `at least 18 → >= 18`, weekday casing, and separation of clock time from numeric thresholds. Numeric and temporal explanations now state canonical before/after values while avoiding domain or logical overclaims. Changed numeric, condition, temporal, and conjunction structures remain `UNDETERMINED`; only the narrow pure polarity reversal is `CONTRADICTORY`.

## Recommended next milestone

Scope v0.1 and [Proposition Alignment v0.1](proposition-alignment-v0.1.md) are now implemented. The recommended next milestone is explicit addition/omission semantics over the aligner's conservative unaligned sets; it should remain narrow and must not introduce lexical similarity, inference, or NLI.
