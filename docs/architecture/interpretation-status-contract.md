# Interpretation Status Contract — Phase 3.0

The existing `InterpretationStatus` enum already contains every required value. Phase 3.0 introduces no duplicate enum and no model or schema change. This document defines how the same vocabulary applies to a future query-level `InterpretationResult`.

## Status vocabulary

| Status | Exact meaning and query relationship | Origin and required evidence | Confidence and override | Precedence effect |
| --- | --- | --- | --- | --- |
| `EXPLICIT` | The query is explicitly present under exact normalized semantic identity. | Deterministic Phase 2; matching normalized object IDs and `EXACT_EXPLICIT`. | Normally `1.0` for the controlled rule; cannot be downgraded or overridden. | Terminal before policy evaluation. |
| `CONTRADICTED` | The query conflicts with evidence under a declared deterministic contradiction rule. It is not merely absent. | Deterministic Phase 2; normalized opposing proposition and rule evidence. | Fixed auditable confidence for that rule; Phase 3 cannot override it. | Terminal before policy evaluation. |
| `ENTAILED` | The query follows under a declared sound deterministic rule but is not directly stated. | Deterministic Phase 2; rule, premises, substitutions, and `UNIVERSAL_INSTANTIATION`. | Rule-specific fixed confidence; cannot be replaced by a weaker policy result. | Terminal before policy evaluation. |
| `PROBABLE` | Structured evidence supports a defeasible expectation, but the query is not logically entailed. | Policy-derived; registered policy, matching evidence and all applicability checks. | Fixed per policy version and rationale; can be superseded only by a newly available deterministic terminal result on re-evaluation, never within one result. | Allowed only after `NOT_ESTABLISHED`. |
| `AMBIGUOUS` | Admissible isolated readings yield materially different query outcomes and no reading is selected. | Policy-derived; ambiguity ID, complete ordered alternatives, and an outcome for each reading. | Confidence concerns correct applicability/evaluation, not probability of a reading; deterministic evidence later resolving the ambiguity may supersede it on re-analysis. | Allowed only after `NOT_ESTABLISHED`. |
| `CANNOT_BE_SAFELY_FORMALIZED` | A represented safety marker establishes that the source must not be converted into the literal proposition required by the query. | Usually deterministic policy propagation; non-literal item/status and query relation. | Confidence concerns marker recognition and propagation, not metaphor meaning; only a new validated analysis may replace it. | Allowed only after `NOT_ESTABLISHED`. |
| `UNSUPPORTED` | No registered deterministic rule or applicable Phase 3 policy establishes, contradicts, probabilistically supports, disambiguates, or safely blocks formalization of the query. | `NOT_ESTABLISHED` plus evidence that policy evaluation found no applicable policy; no invented negative evidence. | `1.0` may mean certainty about rule non-applicability, not certainty that the query is false. | Conservative fallback. |

`InterpretationStatus` is independent of `LogicalRelation` and `DifferenceType`. Those apply to comparison results; a query interpretation may coexist with `UNDETERMINED` comparison and does not create or rewrite differences. `PROBABLE`, `AMBIGUOUS`, and `CANNOT_BE_SAFELY_FORMALIZED` are interpretation outcomes, not logical relations.

## Confidence contract

The existing `Confidence(value, rationale)` is sufficient for Phase 3 v0.x if each location documents what it measures. No field is added in this specification milestone.

- **Representation confidence** belongs to Phase 2 semantic objects and measures confidence that a controlled construction was represented as declared.
- **Policy applicability confidence** is conceptually the certainty that all policy guards matched. Deterministic v0.x policies require exact guards; applicability is therefore auditable rather than probabilistically scored.
- **Interpretation confidence** belongs to the future result and measures confidence in the policy result under that policy version.

These values must not be multiplied or treated as calibrated real-world probability. A deterministic policy uses a fixed documented value and rationale. For `PROBABLE`, confidence is not the probability that the predicted event occurs. For `AMBIGUOUS`, it is not a ranking of readings. For non-literal safety, it is not confidence in a figurative interpretation.

## Evidence contract

The smallest reusable future evidence item is:

```text
EvidenceRef {
  role: stable controlled role,
  analysis_side: PREMISE | QUERY | DETERMINISTIC_RESULT,
  object_kind: ENTITY | PROPOSITION | OPERATOR | TEMPORAL_RELATION |
               SEMANTIC_ITEM | AMBIGUITY | ALTERNATIVE | INFERENCE,
  object_id: stable ID,
  reading_id: optional alternative ID
}
```

Evidence is an ordered, duplicate-free tuple. Every ID must resolve against the embedded or referenced normalized inputs; `reading_id` is required for reading-local evidence and forbidden otherwise. The result separately stores `policy_id`; prose is never the only evidence. Where the deterministic result has no `derived_from` IDs, the result itself remains referenced as the policy gate and the policy adds its own normalized evidence.

## Provenance contract

Provenance is explicit and separate from evidence and confidence:

```text
EXACT_EXPLICIT
LEXICAL_OPPOSITION
UNIVERSAL_INSTANTIATION
PHASE3_DETERMINISTIC_POLICY
BOUNDED_HEURISTIC
AI_ASSISTED_INTERPRETATION
NOT_ESTABLISHED
```

A policy result records both the provenance class and stable policy ID/version. Future heuristic or AI results additionally record algorithm/model/provider version as appropriate. Explanation text cannot serve as provenance.

## `PROBABLE` downstream contract

Consumers must present `PROBABLE` as defeasible support, keep it distinct from explicit and entailed facts, preserve the policy/evidence/confidence, avoid using it as a premise for deterministic inference unless a future version explicitly authorizes that operation, and leave `LogicalRelation` and `DifferenceType` unchanged.

## `AMBIGUOUS` downstream contract

Consumers preserve all ordered admissible reading outcomes. Alternatives are mutually exclusive evaluation worlds, not simultaneous assertions. A query supported in one valid reading and unsupported in another is `AMBIGUOUS`; the engine does not pick, merge, or rank them.

## Non-literal safety contract

`CANNOT_BE_SAFELY_FORMALIZED` is a deliberate refusal to assert a literal formalization. It means neither false nor contradicted, is not a parser failure, and does not call the source meaningless. A registered non-literal marker may be propagated without interpreting the metaphor. No literal proposition may be synthesized from that marker.
