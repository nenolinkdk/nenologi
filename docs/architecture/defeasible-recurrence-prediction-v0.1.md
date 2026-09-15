# Defeasible Recurrence Prediction Policy v0.1

## Result

Phase 3.1 implements `DEFEASIBLE_RECURRENCE_PREDICTION.v1` as the first parser-independent interpretation policy. It makes `entailment_003` return `PROBABLE` through `Phase3InterpretationEngine`; the frozen `DeterministicInferenceEngine` still returns `UNSUPPORTED / NOT_ESTABLISHED` for the same inputs.

`PROBABLE` is defeasible interpretation, never logical entailment. The result carries confidence `1.0` because all deterministic policy guards matched exactly. That value is confidence in the classification under this policy version, not a numerical probability that the event will occur.

## Applicability

The policy consumes validated normalized analyses and the Phase 2 inference. It applies only when:

- Phase 2 returned `UNSUPPORTED / NOT_ESTABLISHED`;
- premise and query each contain exactly one explicit proposition and one explicit `ON` temporal relation governing it;
- predicates match exactly;
- argument arity matches and every paired entity has exactly the same normalized type and label;
- the premise reference is exactly `LAST_N_EVENINGS`, with an explicit integer `N >= 2`;
- the query reference is exactly `THIS_EVENING`;
- neither analysis contains quantifiers, modality, negation, numeric constraints, conditions, relations, sets, or ambiguities.

The minimum of two observations is the smallest bounded recurrence rule. It is an applicability threshold, not a statistical sample-size claim. The implementation performs no string matching against source text, synonyms, calendar arithmetic, timezone reasoning, recurrence calculation, trend analysis, world knowledge, or probability estimation.

## Result envelope

The new reusable immutable `InterpretationResult` stores the existing `InterpretationStatus`, `Confidence`, policy ID, ordered `EvidenceReference` values, explicit `InterpretationProvenance`, the complete underlying Phase 2 `Inference`, structured explanation inputs, and schema version. JSON serialization round-trips every field deterministically.

Evidence order for this policy is observed proposition, observed entity arguments, recurrence temporal relation, future proposition, future entity arguments, future temporal relation, and deterministic inference gate. References are typed by premise/query/deterministic side and object kind and are resolved before a matched result is returned. The policy ID itself remains the result's explicit registry reference.

Provenance is `PHASE3_DETERMINISTIC_POLICY`. Explanation text is rendered from predicate, entity labels, recurrence count, source frame, and query frame; it is neither authority nor evidence.

## Precedence and fallback

`Phase3InterpretationEngine` first runs the unchanged deterministic engine. `EXACT_EXPLICIT`, `LEXICAL_OPPOSITION`, and `UNIVERSAL_INSTANTIATION` results return unchanged and bypass every policy. Only `NOT_ESTABLISHED` enters the ordered registry. A no-match remains `UNSUPPORTED`, and multiple matches fail closed.

One observation, a different predicate or entity, a wrong temporal frame, extra semantic structure, or any deterministic terminal result prevents `PROBABLE`. Phase 3.2 alternative-reading evaluation and Phase 3.3 non-literal safety propagation remain unimplemented.

## Metrics and dependencies

- Frozen Phase 2: 39/42 exact, with 3 inference policies not implemented.
- Full interpretation pipeline after Phase 3.1: 40/42 exact, with `entailment_006` and `entailment_007` remaining.
- Runtime dependencies: unchanged and empty. The policy is offline and uses no AI, network, NLP service, embedding, fuzzy matching, or random behavior.

Run `tests/validation/audit_gold_coverage.py` for the historical Phase 2 metric and add `--full-pipeline` for the Phase 3-aware metric.
