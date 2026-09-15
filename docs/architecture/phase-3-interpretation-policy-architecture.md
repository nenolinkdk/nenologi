# Phase 3.0 — Interpretation and Policy Architecture

## Decision and boundary

Phase 3 consumes the frozen `phase-2-deterministic-core-v1` output without changing its representation, comparison, taxonomy, logical-relation, inference, serialization, or validation contracts. It adds an interpretation-policy layer only where deterministic Phase 2 returns `UNSUPPORTED / NOT_ESTABLISHED` and a registered policy has complete structured applicability evidence.

```text
TEXT
  -> PHASE 2 ANALYSIS
  -> NORMALIZED SEMANTICS
  -> DETERMINISTIC COMPARISON / INFERENCE
  -> PHASE 3 POLICY EVALUATION
  -> INTERPRETATION RESULT
       status | confidence | evidence | provenance | policy | explanation inputs
```

Phase 2 owns structural analysis, normalized semantics, deterministic comparison and logical inference, `DifferenceType`, `LogicalRelation`, and graph/serialization invariants. Phase 3 owns policy applicability, isolated-reading evaluation, defeasible classification, safety propagation, and auditable interpretation results. Raw source text and spans remain provenance/display material, never policy evidence in place of normalized structures.

## Four independent dimensions

1. **Semantic difference** describes a typed change between analyses through `DifferenceType`.
2. **Logical relation** describes a comparison as `EQUIVALENT`, `CONTRADICTORY`, or `UNDETERMINED`.
3. **Interpretation status** classifies how a query is supported, opposed, uncertain, or unsafe to formalize.
4. **Confidence** records confidence in a particular representation or result under an identified rule.

No dimension implies another. `PROBABLE` does not imply `EQUIVALENT` or create a difference. `AMBIGUOUS` is not a difference. A high-confidence `UNSUPPORTED` result can mean high confidence that no registered rule establishes the query. See the [Interpretation Status Contract](interpretation-status-contract.md).

## Current Phase 3 cases inspected from executable output

### `entailment_003` — recurrence prediction

- Source: “The light flickered on each of the last five evenings.”
- Query: “The light will flicker this evening.”
- Gold: `PROBABLE`; deterministic result: `UNSUPPORTED / NOT_ESTABLISHED`, confidence `1.0`, no derived evidence.
- Source: `entity_001 = ENTITY_CLASS(light)`; `prop_001 = FLICKER(entity_001)`; `temporal_001 = ON(prop_001, LAST_5_EVENINGS)`; logical display `On(Flicker(Light), Last5Evenings)`.
- Query: the same normalized entity and predicate; `temporal_001 = ON(prop_001, THIS_EVENING)`; logical display `On(Flicker(Light), ThisEvening)`.
- Operators, ambiguities, and non-literal structures: none.
- Available evidence: matching normalized predicate/entity, explicit recurrence count 5 encoded in the canonical temporal reference, recent repeated-evening frame, and future-evening target.
- Missing step: a defeasible recurrence policy, not temporal entailment. Existing representation is sufficient for this exact controlled case.

### `entailment_006` — alternative readings

- Source: “Alex told Sam that they had won.”
- Query: “Alex had won.”
- Gold: `AMBIGUOUS`; deterministic result: `UNSUPPORTED / NOT_ESTABLISHED`, confidence `1.0`, no derived evidence.
- Entities: `entity_001 = INDIVIDUAL(alex)`, `entity_002 = INDIVIDUAL(sam)`, and ambiguous `reference_001 = UNRESOLVED_REFERENCE(they)`.
- Propositions: `prop_001 = TELL(entity_001, entity_002)` and ambiguous `embedded_prop_001 = WON(reference_001)`. Query: `prop_001 = WON(entity_001)`.
- Reference graph: `content_001 = CONTENT_RELATION(prop_001, embedded_prop_001)`; `alternative_001 = REFERENCE_ALTERNATIVE(reference_001, entity_001)`; `alternative_002 = REFERENCE_ALTERNATIVE(reference_001, entity_002)`; `ambiguity_001` preserves that order.
- Operators, temporal structures, and non-literal structures: none.
- Available evidence: ambiguity ID, ordered alternative IDs, candidate entity IDs, embedded proposition and content relation, plus the normalized query.
- Missing step: evaluate the query independently in each admissible reading. Existing representation is sufficient; it must not materialize both readings as simultaneous facts.

### `entailment_007` — non-literal safety

- Source: “Time is a thief.”
- Query: “Time commits theft.”
- Gold: `CANNOT_BE_SAFELY_FORMALIZED`; deterministic result: `UNSUPPORTED / NOT_ESTABLISHED`, confidence `1.0`, no derived evidence.
- Source: `entity_001 = ENTITY_CLASS(time)` with status `CANNOT_BE_SAFELY_FORMALIZED`; no proposition; `non_literal_001 = NON_LITERAL_EXPRESSION(entity_001)` with the same status; logical operator `UNRESOLVED_NON_LITERAL` derives from both IDs.
- Query: `entity_001 = ENTITY_CLASS(time)` and explicit `prop_001 = COMMIT_THEFT(entity_001)`.
- Operators other than the logical non-literal marker, temporal structures, and ambiguities: none.
- Available evidence: the non-literal item, its entity, its status, the absence of a literal source proposition, and the literal query proposition.
- Missing step: propagate formalization safety to the query result. Existing representation is sufficient; no metaphor meaning is inferred.

## Policy interface and orchestration

The future interface is conceptually:

```python
Policy.evaluate(
    premise: Analysis,
    query: Analysis,
    deterministic_result: Inference,
) -> InterpretationResult | NotApplicable
```

`Policy` is parser-independent and accepts validated normalized objects. `InterpretationResult` is a future versioned envelope, not added in Phase 3.0. It contains status, interpretation confidence, policy ID, typed evidence references, explicit provenance, the unchanged deterministic result, optional ordered alternative evaluations, and structured explanation inputs.

Orchestration precedence is exact:

1. Return deterministic `EXPLICIT / EXACT_EXPLICIT`.
2. Return deterministic `CONTRADICTED / LEXICAL_OPPOSITION`.
3. Return deterministic `ENTAILED / UNIVERSAL_INSTANTIATION`.
4. Only for deterministic `UNSUPPORTED / NOT_ESTABLISHED`, evaluate applicable registered Phase 3 policies in registry precedence order.
5. If exactly one policy applies, return its permitted result. If none applies, retain `UNSUPPORTED / NOT_ESTABLISHED`. Multiple applying policies are a registry/configuration error, never silently tie-broken.

This ordering expresses authority, not a claim that contradiction is generally “stronger” than explicit evidence: the current deterministic engine itself produces exactly one terminal result. Phase 3 never re-runs or overrides it. A future deterministic result outside these known rule/status pairs must fail closed until explicitly versioned.

## Open-world and regression invariants

`NOT_ESTABLISHED != FALSE`. Phase 3 may refine only the conservative fallback, and only to an allowed status backed by complete policy evidence. Missing, malformed, conflicting, or out-of-scope evidence leaves the fallback unchanged. All 39 Phase 2 exact cases bypass policy evaluation and retain their analyses, findings, logical relations, deterministic evidence, confidence, and explanations.

The historical metric remains `phase-2-deterministic-core-v1: 39/42 exact`. A future full-pipeline metric is reported separately, for example `phase-3-interpretation-pipeline-v1: 42/42`; it never rewrites the Phase 2 number.

## AI boundary, provider independence, and AI-off mode

All three current cases are class A, deterministic policies:

- `entailment_003`: deterministic bounded recurrence policy over registered temporal constants.
- `entailment_006`: deterministic evaluation of an already enumerated alternative graph.
- `entailment_007`: deterministic propagation of an existing safety marker.

No current case requires a bounded heuristic or AI. Future AI is optional, provider-neutral, and subordinate. It cannot rewrite Phase 2, override deterministic results, manufacture spans/evidence, convert unsupported to entailed without validated evidence, or collapse ambiguity without traceable justification. Proposals must enter a typed validation boundary; provider/model provenance and reproducibility limits must be recorded. Source text should not be transmitted unless necessary and authorized, secrets must never enter logs, and a structured audit trail is required. With AI unavailable, deterministic Phase 2 and registered deterministic Phase 3 policies continue unchanged; AI-only proposals degrade to the conservative fallback.

## Serialization and explanation

A future Phase 3 schema version must preserve: result ID/version, status, confidence plus rationale, policy ID/version, ordered typed evidence references, provenance class, the complete deterministic result or stable reference to it, ordered alternative evaluations where applicable, and structured explanation inputs. References must resolve against the included premise/query analyses. Unknown fields, policy/status mismatches, duplicate evidence, unresolved IDs, and invalid alternative order are rejected.

Explanation text is a deterministic rendering of result fields and explanation inputs. It is never evidence or semantic authority. Localization may change wording without changing status, evidence, provenance, or confidence.

## Determinism and test contract

Deterministic policies must produce stable selection, status, confidence, evidence and evidence order, alternative order, provenance, explanation inputs, and JSON. No randomness, wall-clock time, network, provider state, filesystem enumeration, or hash iteration may affect results.

Future tests must cover registry uniqueness/order, applicability and rejection, deterministic precedence, open-world fallback, evidence resolution, provenance, confidence rules, JSON round-trip/validation, repeated-run determinism, possible-world isolation, non-literal safety, and all 39 Phase 2 regressions. Per-policy positive and negative cases are specified in the [Policy Registry](phase-3-policy-registry.md).

## Versioning and next milestone

- Frozen core: `phase-2-deterministic-core-v1`.
- Architecture baseline: `phase-3-interpretation-policy-architecture-v1`.
- Policy IDs carry independent versions, beginning with `.v1`.
- Future combined baseline: `phase-3-interpretation-pipeline-v1`.

These are recommended names; no Git tags are created. The first implementation milestone should be **Defeasible Recurrence Prediction Policy v0.1**, implemented against this contract without Phase 2 changes.

## Required decisions A–K

- **A — Yes.** Phase 3 consumes frozen Phase 2 semantics without changing its contract.
- **B — No.** `entailment_003` needs a bounded deterministic policy, not AI.
- **C — No.** `entailment_006` can evaluate the explicit alternative graph deterministically.
- **D — No.** `entailment_007` can propagate the existing safety marker.
- **E.** Phase 2 runs its frozen order (`EXACT_EXPLICIT`, `LEXICAL_OPPOSITION`, `UNIVERSAL_INSTANTIATION`, `NOT_ESTABLISHED`). Its explicit, contradicted, or entailed result returns unchanged; only `UNSUPPORTED / NOT_ESTABLISHED` enters registry evaluation; otherwise fallback remains unchanged.
- **F — Yes.** Interpretation status is independent from `LogicalRelation`.
- **G — Yes.** Confidence is independent from status.
- **H — Yes.** Each reading is evaluated in isolation; no preferred reading is selected.
- **I — Yes.** Case 007 requires safety propagation, not metaphor interpretation.
- **J — Yes.** `PROBABLE` is explicitly defeasible and never becomes `ENTAILED`.
- **K — Yes.** The three current policies can operate fully with AI disabled.
