# Phase 3 Policy Registry — Architecture v1

The registry is an ordered, versioned, auditable catalogue. Registration validates unique IDs, declared output statuses, deterministic classification, evidence schema, and precedence. Phase 3.1 implements only `DEFEASIBLE_RECURRENCE_PREDICTION.v1`; the other entries remain specifications.

| Registry order | Stable policy ID | Status | Purpose | Class | Allowed result | Fixed v0.x confidence rule |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `NON_LITERAL_SAFETY_PROPAGATION.v1` | specified, not registered | Refuse unsafe literalization when an applicable source marker exists. | deterministic | `CANNOT_BE_SAFELY_FORMALIZED` | `1.0` when exact marker/query guards pass. |
| 2 | `ALTERNATIVE_READING_EVALUATION.v1` | specified, not registered | Evaluate a query across complete isolated reference readings. | deterministic | `AMBIGUOUS` | `1.0` when the alternative graph is complete and reading outcomes differ. |
| 3 | `DEFEASIBLE_RECURRENCE_PREDICTION.v1` | implemented and registered | Classify a narrowly registered repeated-past/future recurrence as probable. | deterministic bounded policy | `PROBABLE` | `1.0` when exact guards pass: certainty of the policy classification, not probability of the event. |

The order resolves only mutually exclusive applicability families. If more than one policy still applies, evaluation fails closed as a registry error. All policies require an incoming `UNSUPPORTED / NOT_ESTABLISHED`; deterministic terminal results bypass the registry.

## `DEFEASIBLE_RECURRENCE_PREDICTION.v1`

Purpose: support `entailment_003` without claiming entailment.

Applicability requires all of:

- exactly aligned normalized predicate, arity, entity types, and entity labels;
- an explicit source proposition governed by `ON ... LAST_N_EVENINGS`, where the registered reference supplies an explicit recurrence count and `N >= 2`;
- an explicit query proposition governed by `ON ... THIS_EVENING`;
- compatible registered temporal granularity (`evening` to `this evening`) and the same controlled event family;
- incoming `NOT_ESTABLISHED`; no deterministic contradiction or other terminal result;
- no unresolved ambiguity, non-literal marker, condition, modality, negation, or conflicting temporal evidence affecting the proposition.

Evidence: source/query proposition IDs, their entity IDs, source/query temporal relation IDs, deterministic inference ID/result, and policy ID. Explanation inputs include normalized predicate/entity, recurrence count, source frame, target frame, and “defeasible, not entailed.”

Reject one observation, absent/unknown recurrence count, different predicate/entity/arity, incompatible temporal granularity, non-future target, unsupported temporal constants, conditions or modal changes, ambiguity/non-literal structures, explicit contradiction, and any need for world knowledge. Rejection preserves `UNSUPPORTED / NOT_ESTABLISHED`.

Positive tests: exact case 003; word/digit normalization if both produce the same canonical reference; repeated runs and JSON round-trip. Negative tests: count one, different entity, different predicate, non-future query, morning/evening mismatch, conditional or negated occurrence, explicit contradiction precedence, missing temporal evidence, and unrelated residence/fluency input.

The implemented v0.1 boundary is documented in [Defeasible Recurrence Prediction Policy v0.1](defeasible-recurrence-prediction-v0.1.md).

## `ALTERNATIVE_READING_EVALUATION.v1`

Purpose: classify `entailment_006` without resolving the pronoun.

Applicability requires a validated ambiguity whose ordered `reading_ids` resolve to a complete set of `REFERENCE_ALTERNATIVE` items for one unresolved reference used by the relevant embedded proposition. The query must align after substituting at least one candidate. Each reading is cloned/evaluated in isolation using deterministic rules allowed for embedded-content evaluation; no reading can affect another.

Exact decision rule:

- if at least one admissible reading supports the normalized query and at least one admissible reading does not support it, return `AMBIGUOUS`;
- record every reading and its local outcome in source order;
- do not promote all candidate substitutions to facts, select a preferred reading, or rank candidates;
- if the graph is incomplete/invalid or no reading aligns, the policy is not applicable;
- unanimous results require a separately specified future rule and remain fallback in v1 rather than being promoted silently.

Evidence: ambiguity ID, unresolved reference ID, ordered alternative IDs, candidate entity IDs, embedded proposition ID, content relation ID, query proposition ID, deterministic gate, and per-reading outcome/evidence. No nearest-name, grammatical-subject, recency, gender, world-knowledge, statistical, or LLM preference is allowed.

Positive tests: case 006 yields one supporting and one non-supporting reading and returns `AMBIGUOUS`; reversed mention order preserves declared alternative order. Negative tests: no ambiguity, dangling/incomplete alternatives, query matching no reading, repeated resolved name, multiple unresolved references beyond v1, deterministic terminal precedence, and proof that no simultaneous `WON(Alex) AND WON(Sam)` graph is created.

## `NON_LITERAL_SAFETY_PROPAGATION.v1`

Purpose: classify case 007 safely without metaphor interpretation.

Applicability requires a validated `NON_LITERAL_EXPRESSION` (or versioned equivalent) with status `CANNOT_BE_SAFELY_FORMALIZED`, a resolving `UNRESOLVED_NON_LITERAL` logical expression, no asserted literal source proposition for that expression, and a literal query whose subject/entity is the marked entity and whose assertion would require literalizing the marked expression. The incoming result must be `NOT_ESTABLISHED`.

Evidence: non-literal semantic item ID, marked entity ID, logical-expression ID, query proposition/entity IDs, deterministic gate, and policy ID. The policy propagates the safety status only; it derives no `THIEF`, `COMMIT_THEFT`, synonym, opposition, or metaphorical proposition.

Reject absent/unknown markers, ordinary literal source propositions, unrelated query entities, parser failure with no safe marker, malformed references, or any request that requires guessing a metaphor meaning. Such cases retain the fallback.

Positive tests: case 007; round-trip retains the marker and produces identical evidence. Negative tests: literal “Time commits theft.” remains exact when repeated, unrelated queries remain unsupported, unsupported metaphors without a marker do not acquire the status, malformed markers fail validation, deterministic results take precedence, and no literal proposition is manufactured.

## Registry-wide tests and audit

Tests must verify unique stable IDs, deterministic order, one-policy-only selection, allowed status enforcement, evidence resolution/order, explicit provenance, fixed confidence rationale, explanation derivation, schema round-trip, repeatability, safe failure on unknown versions, AI-off execution, and unchanged results for all 39 Phase 2 exact cases. The registry must expose its policy ID/version and deterministic/heuristic/AI classification in serialized output.
