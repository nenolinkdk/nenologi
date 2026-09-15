# Phase 2 Representation-readiness Audit

## Decision

**Decision B — Phase 2 continues through two specific small milestones.** The current deterministic core is stable and all seven inference cases are parseable. Two deterministic parser cases remain; there are no comparator blockers. The three non-exact inference cases require policy rather than broader deterministic entailment.

**Controlled UNLESS Conditions v0.1 is complete.** It represents the exact registered UNLESS antecedent through an explicit negation operator and condition graph. The audit is now 37 exact, 0 analyzable-but-inexact, 2 parser-unsupported, 0 comparator-unsupported, and 3 inference-not-implemented.

The next recommended milestone is **Controlled Event-anchored Temporal Relations v0.1** for `temporal_001`.

## Verified baseline

Post-milestone verification was performed against the complete Controlled UNLESS Conditions v0.1 working tree.

- Tests: 261 passed.
- Gold corpus: 42 cases.
- Audit: 37 `END_TO_END_EXACT`, 0 `ANALYZABLE_BUT_NOT_EXACT`, 2 `PARSER_UNSUPPORTED`, 0 `COMPARATOR_UNSUPPORTED`, 3 `INFERENCE_NOT_IMPLEMENTED`.
- Gold validation: 30 change, 5 equivalence, and 7 inference cases passed schema validation.

The existing audit command remains the machine-readable status source:

```text
python tests/validation/audit_gold_coverage.py --json
```

A static JSON copy is intentionally not committed because it would duplicate executable status and become stale.

## Classification vocabulary

- **A — COMPLETE:** current end-to-end result exactly matches gold.
- **B — PHASE 2 DETERMINISTIC CORE:** bounded representation, parsing, alignment, canonicalization, or comparison work remains.
- **C — PHASE 3 POLICY / INTERPRETATION:** representation exists, but the expected result requires uncertainty, alternative-reading evaluation, or a safety policy.
- **D — LATER AI-ASSISTED INTERPRETATION:** optional assistance for open-ended language interpretation; never a deterministic-core dependency.
- **E — OUT OF SCOPE / OPTIONAL:** no committed gold or core need justifies implementation.

## Complete 42-case inventory

`P/R` means parser/representation; `C/I` means comparator or inference. Text is abbreviated only in this overview; exact blocker texts appear below.

| Case | Category | Source → target/query summary | P/R | C/I | Audit | Blocker | Phase | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| modality_001 | modality | must → may register | ready | exact | END_TO_END_EXACT | none | A | Typed modality change matches gold. |
| modality_002 | modality | must → should wear badges | ready | exact | END_TO_END_EXACT | none | A | Typed modality change matches gold. |
| modality_003 | modality | may → must vote | ready | exact | END_TO_END_EXACT | none | A | Typed modality change matches gold. |
| conjunction_001 | conjunction | form A and B → A or B | ready | exact | END_TO_END_EXACT | none | A | Flat object conjunction is compared. |
| conjunction_002 | conjunction | tea or coffee → tea and coffee | ready | exact | END_TO_END_EXACT | none | A | Flat object conjunction is compared. |
| quantifier_001 | quantification | all → some labelled boxes | ready | exact | END_TO_END_EXACT | none | A | Quantifiers normalize and compare. |
| quantifier_002 | quantification | some → all locked doors | ready | exact | END_TO_END_EXACT | none | A | Quantifiers normalize and compare. |
| quantifier_003 | quantification | no → some lit lamps | ready | exact | END_TO_END_EXACT | none | A | `NO` normalization and negation scope are exact. |
| negation_001 | negation | valve not open → open | ready | exact | END_TO_END_EXACT | none | A | Polarity change matches gold. |
| negation_002 | negation | alarm active → not active | ready | exact | END_TO_END_EXACT | none | A | Polarity change matches gold. |
| temporal_001 | temporal | inspect before → after starting | blocked | not reached | PARSER_UNSUPPORTED | event temporal anchor | B | Requires two event propositions and directed temporal linking. |
| temporal_002 | temporal | before Monday → on Monday | ready | exact | END_TO_END_EXACT | none | A | Flat weekday relation is complete. |
| temporal_003 | temporal | until noon → until after noon | blocked | not reached | PARSER_UNSUPPORTED | nested temporal phrase | B | Requires canonical noon and nested temporal reference. |
| condition_001 | condition | if green may enter → may enter | ready | exact | END_TO_END_EXACT | none | A | Condition removal is exact. |
| condition_002 | condition | submit → submit if test passes | ready | exact | END_TO_END_EXACT | none | A | Suffix condition addition is exact. |
| condition_003 | condition | unless locked → if locked | ready | exact | END_TO_END_EXACT | none | A | Exact UNLESS antecedent negation and condition comparison. |
| numeric_001 | numeric | > 10 → >= 10 | ready | exact | END_TO_END_EXACT | none | A | Exact threshold semantics. |
| numeric_002 | numeric | < 5 → <= 5 degrees | ready | exact | END_TO_END_EXACT | none | A | Exact threshold semantics. |
| numeric_003 | numeric | >= 3 → > 3 copies | ready | exact | END_TO_END_EXACT | none | A | Number words and thresholds normalize. |
| numeric_004 | numeric | = 2 → >= 2 files | ready | exact | END_TO_END_EXACT | none | A | Exact threshold semantics. |
| entity_relation_001 | entity/relation | Alice → Bob approved request | ready | exact | END_TO_END_EXACT | none | A | Subject role change is exact. |
| entity_relation_002 | entity/relation | request → invoice | ready | exact | END_TO_END_EXACT | none | A | Object role change is exact. |
| entity_relation_003 | spatial | inside → beside box | ready | exact | END_TO_END_EXACT | none | A | Ordered spatial relation is exact. |
| addition_001 | addition | register name → plus show ID | ready | exact | END_TO_END_EXACT | none | A | `REGISTER` aligns and unmatched `SHOW` is one high-severity addition. |
| omission_001 | omission | conditional open → open | ready | exact | END_TO_END_EXACT | none | A | Gold correctly resolves as condition change. |
| contradiction_001 | contradiction | switch on → not on | ready | exact | END_TO_END_EXACT | none | A | Negation finding plus contradictory relation. |
| scope_001 | scope | not promise leave → promise not leave | ready | exact | END_TO_END_EXACT | none | A | Explicit `NOT`/`PROMISE` operator topology. |
| scope_002 | scope | not require leave → require not leave | ready | exact | END_TO_END_EXACT | none | A | Explicit `NOT`/`REQUIRE` operator topology. |
| addition_002 | addition | closed window → plus locked door | ready | exact | END_TO_END_EXACT | none | A | Two independent propositions; unmatched `LOCKED(door)` is one addition. |
| omission_002 | omission | sign and date form → sign form | ready | exact | END_TO_END_EXACT | none | A | Shared-argument `SIGN`/`DATE` propositions yield one omission. |
| equivalence_001 | equivalence | every → all | ready | exact | END_TO_END_EXACT | none | A | Quantifier normalization is exact. |
| equivalence_002 | equivalence | active → passive approval | ready | exact | END_TO_END_EXACT | none | A | Voice normalizes to semantic roles. |
| equivalence_003 | equivalence | at least 3 → 3 or more | ready | exact | END_TO_END_EXACT | none | A | Threshold normalization is exact. |
| equivalence_004 | equivalence | not → contraction | ready | exact | END_TO_END_EXACT | none | A | Controlled contraction normalization is exact. |
| equivalence_005 | equivalence | A and B → B and A | ready | exact | END_TO_END_EXACT | none | A | Flat commutative members use canonical semantic ordering. |
| entailment_001 | inference | door open → same | ready | EXACT_EXPLICIT | END_TO_END_EXACT | none | A | Complete normalized identity. |
| entailment_002 | inference | universal rule + fact → inspected | ready | UNIVERSAL_INSTANTIATION | END_TO_END_EXACT | none | A | Closed unary rule instantiation. |
| entailment_003 | inference | repeated flicker → future flicker | ready | NOT_ESTABLISHED | INFERENCE_NOT_IMPLEMENTED | defeasible prediction | C | Gold `PROBABLE` requires uncertainty policy. |
| entailment_004 | inference | residence → fluent language | ready | NOT_ESTABLISHED | END_TO_END_EXACT | none | A | Correct open-world non-entailment. |
| entailment_005 | inference | switch off → on | ready | LEXICAL_OPPOSITION | END_TO_END_EXACT | none | A | Closed opposition gives contradiction. |
| entailment_006 | inference | ambiguous they won → Alex won | ready | NOT_ESTABLISHED | INFERENCE_NOT_IMPLEMENTED | alternative evaluation | C | Gold `AMBIGUOUS` requires evaluation across readings. |
| entailment_007 | inference | Time is a thief → commits theft | ready, unsafe literalization blocked | NOT_ESTABLISHED | INFERENCE_NOT_IMPLEMENTED | non-literal policy | C | Gold safety status requires policy propagation, not metaphor guessing. |

## Remaining parser blockers

| Case | Exact source | Exact target | Unsupported construction | Needed semantics / model fit | Downstream effect | Risk | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_001 | `Inspect the cable before starting the machine.` | `Inspect the cable after starting the machine.` | Event clause as temporal anchor | Two event propositions plus a directed relation between them. `SemanticItem` can link proposition IDs; `TemporalRelation.temporal_reference` alone is insufficiently typed for an event. | Unlocks temporal comparison. | Medium: event identity and gerund surface scope. | PHASE_2_DETERMINISTIC; dedicated event-anchor milestone. |
| temporal_003 | `Wait until noon.` | `Wait until after noon.` | `wait`, `noon`, and nested `until after` | A `WAIT` proposition, canonical `NOON`, and nested relation/reference. Existing structures can encode a conservative composite reference, though a typed nested relation may be cleaner. | Unlocks temporal comparison. | Medium: avoid general temporal-expression parsing. | PHASE_2_DETERMINISTIC; bounded nested-temporal milestone. |
None of the two requires uncertainty, AI, embeddings, world knowledge, or fuzzy matching. They require bounded graph construction in addition to grammar.

## Resolved comparator blockers

Coordinated Predicate Graphs v0.1 resolves both previously recorded comparator blockers below. They are retained here as historical root-cause evidence; current execution is exact.

### `addition_001` — coordinated predicate representation

- Source: `Register your name.`
- Target: `Register your name and show identification.`
- Both parse, but the target is currently one `REGISTER(addressee, your_name, show_identification)` proposition. `show identification` is incorrectly represented as a third object under an `AND` relation.
- Source structure: entities `addressee`, `your_name`; proposition `REGISTER(entity_001, entity_002)`.
- Target structure: adds entity label `show_identification`; proposition `REGISTER(entity_001, entity_002, entity_003)`; conjunction joins the two object arguments.
- Alignment: no pair; both `prop_001` values are unaligned. Comparator raises `main propositions are not uniquely structurally aligned`; no findings are emitted.
- Gold expects one `ADDITION`, target value `SHOW_IDENTIFICATION`, severity `HIGH`.
- Root cause is representation first, then exact alignment/addition logic. Correct structure is separate `REGISTER` and `SHOW` propositions, with shared addressee and their own objects.
- Recommendation: deterministic Phase 2. No fuzzy alignment is needed; align `REGISTER` exactly and report unaligned `SHOW` as addition.

### `equivalence_005` — commutative conjunction canonicalization

- Source: `Submit form A and form B.`
- Target: `Submit form B and form A.`
- Both parse as one `SUBMIT` proposition with two ordered object entities and an `AND` relation. Surface order changes the entity-to-argument positions.
- Alignment: no pair; each `prop_001` is unaligned. Comparator raises the same unique-alignment error; no findings are emitted.
- Gold expects no differences.
- Root cause is canonicalization/alignment, not fuzzy similarity. `AND` is commutative, so members should be ordered by normalized semantic identity for comparison while preserving source spans separately. `OR` can use the same deterministic member-set treatment for flat coordination.
- Recommendation: deterministic Phase 2, combined with coordinated predicate graphs because both touch coordination boundaries.

## Remaining inference blockers

| Case | Parser / representation | Current result | Gold | Missing capability | Deterministic core? | Uncertainty / alternatives / non-literal | AI boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| entailment_003 | Supported; `FLICKER(light)` has `LAST_5_EVENINGS` versus `THIS_EVENING` | `UNSUPPORTED / NOT_ESTABLISHED` | `PROBABLE` | Defeasible prediction and calibrated support policy | No; Phase 3 | Uncertainty required; no alternatives or metaphor | AI undesirable as a hidden rule; optional only behind an explicit provider/policy boundary. |
| entailment_006 | Supported; unresolved `they` retains ordered Alex/Sam alternatives and embedded `WON(reference)` | `UNSUPPORTED / NOT_ESTABLISHED` | `AMBIGUOUS` | Evaluate the query over admissible readings without selecting one | No; Phase 3 | Alternatives required; probability and metaphor are not | AI unnecessary for this controlled case and undesirable for candidate selection; optional later for candidate extraction only. |
| entailment_007 | Supported; source has `NON_LITERAL_EXPRESSION`, safety status, and no literal proposition | `UNSUPPORTED / NOT_ESTABLISHED` | `CANNOT_BE_SAFELY_FORMALIZED` | Policy for propagating analysis-level unsafe-formalization status to an inference answer | No; Phase 3 | Non-literal safety required; no meaning interpretation is required | AI unnecessary for safe refusal; optional later for proposed interpretations that remain non-authoritative. |

All three are representation-ready. None should be converted into deterministic entailment. A Phase 3 policy layer may return the gold status while preserving evidence, alternatives, and safety provenance.

## Representation-readiness matrix

`Y` means implemented for the controlled subset, `—` means not applicable, and `P` means partial or deliberately bounded.

| Dimension | Represented | Compared | Inferred | Serialized | Rendered | Gold | Limitations | Phase status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entity | Y | Y | P | Y | Y | broad | Controlled labels/types only | A |
| Relation | Y | Y | P | Y | Y | broad | Closed relation shapes | A |
| Predicate | Y | Y | P | Y | Y | broad | Closed grammar/lexicon | A |
| Quantification | Y | Y | universal subset | Y | Y | 3+ | No nested generalized quantifiers | A |
| Modality | Y | Y | exact only | Y | Y | 3 | No modal logic | A |
| Negation | Y | Y | opposition/exact | Y | Y | 3+ | Controlled scope only | A |
| Conjunction | Y | Y | exact members | Y | Y | 6 | Two registered predicate forms; flat two-object forms | A |
| Numeric constraints | Y | Y | exact only | Y | Y | 5 | No unit conversion/arithmetic | A |
| Conditions | Y | Y | exact only | Y | Y | 3 exact | Registered prefix, suffix, and exact UNLESS forms only | A |
| Temporality | P | P | exact only | Y | Y | 2+ | Flat weekday/clock and two relative references; event/nested forms remain | B |
| Scope | Y | Y | exact only | Y | Y | 3 controlled | Registered operator chains only | A |
| Spatial relation | Y | Y | exact only | Y | Y | 1 | `INSIDE`/`BESIDE` only | A |
| Voice normalization | Y | Y | exact only | Y | Y | 1 | One singular passive family | A |
| Tense handling | P | normalized where declared | exact only | Y | Y | several | No generic tense semantics | A for intended boundary |
| Proposition alignment | Y | Y | — | Y | Y | broad | Exact structural alignment; no fuzzy matching | A |
| Addition/omission | Y | Y | — | Y | Y | 5 exact | Controlled predicate and two-sentence forms only | A |
| Universal rules | Y | — | Y | Y | Y | 1 | Unary, single-step, closed form | A |
| Membership | Y | — | Y | Y | Y | 1 | Controlled class facts only | A |
| Universal instantiation | represented | — | Y | Y | Y | entailment_002 | No binary rules, chaining, converse, or contraposition | A |
| Lexical opposition | represented | — | Y | Y | Y | entailment_005 | Closed `OFF`/`ON` registry | A |
| Embedded propositions | Y | comparator conservative | no promotion | Y | Y | entailment_006 | One `TELL ... HAD WON` family | A representation; policy C |
| Coreference alternatives | Y | conservative | not evaluated | Y | Y | entailment_006 | Two controlled participants and `they` only | C policy |
| Non-literal marking | Y | conservative | not propagated | Y | safe display | entailment_007 | One registered construction; no interpretation | C policy |
| Open-world non-entailment | Y | — | Y | Y | Y | entailment_004 | Absence of proof remains unsupported, not false | A |
| Prediction/probability | evidence represented | — | no | Y | Y | entailment_003 | No calibration, persistence, trend, or forecast | C policy |

## Deterministic-core boundary

Nenologi's deterministic core converts only declared controlled language into normalized, validated semantic graphs; compares explicit graph structure and conservative logical relations; recognizes exact explicit evidence; applies narrowly registered unary universal instantiation and lexical opposition; and otherwise returns open-world `NOT_ESTABLISHED`. It may preserve ambiguity and unsafe-formalization markers, but it must not silently select a reading or a figurative meaning.

Probabilistic prediction, confidence propagation from evidence, evaluation or resolution of alternative readings, metaphor interpretation, commonsense/world knowledge, ontology inference, fuzzy semantic relations, embeddings, and LLM judgments belong outside deterministic core. Policy layers must be explicit consumers of the normalized graph, and AI assistance—if later introduced—must remain optional, attributable, and non-authoritative.

## Phase 2 exit criteria

Phase 2 exits when all of the following are measurable and true:

1. The two cases listed as deterministic parser blockers are either exact or explicitly removed from the intended Phase 2 corpus by a reviewed scope decision.
2. `addition_001` and `equivalence_005` compare exactly, with coordinated predicates represented separately and flat conjunction members canonicalized without fuzzy matching.
3. Audit totals contain 0 `ANALYZABLE_BUT_NOT_EXACT`, 0 intended `PARSER_UNSUPPORTED`, and 0 intended `COMPARATOR_UNSUPPORTED` cases.
4. `entailment_003`, `_006`, and `_007` remain fully parseable and represented, with their Phase 3 blockers named and no hidden policy inference.
5. Every analysis/comparison round-trips through JSON with reference and schema validation.
6. The complete unit/validation suite, gold audit, Unicode/formula checks, Markdown-link checks, and forbidden-dependency scan pass.
7. No deterministic rule depends on probability, world knowledge, fuzzy matching, embeddings, external NLP, an LLM, or system date.
8. Documentation and executable audit agree on totals, per-case readiness, core boundaries, and deferrals.

## Remaining Phase 2 milestones

In priority order:

1. **Controlled Event-anchored Temporal Relations v0.1** — `temporal_001`; expected +1 exact.
2. **Controlled Nested Temporal References v0.1** — `temporal_003`; expected +1 exact.

If all land without corpus changes, the expected deterministic audit becomes 39 exact, 0 analyzable-but-inexact, 0 parser-unsupported, 0 comparator-unsupported, and 3 policy-layer inference cases. This forecast is a planning target, not a forced test result.

## Explicit deferrals

- Phase 3 policy/interpretation: probable prediction (`entailment_003`), alternative-reading evaluation (`entailment_006`), and safe non-literal status propagation (`entailment_007`).
- Later optional AI assistance: open-ended candidate extraction, metaphor interpretation proposals, and fuzzy language mapping, always outside authoritative deterministic semantics.
- Out of scope/optional: commonsense and world-knowledge entailment, general English parsing, ontology reasoning, statistical resolution, GUI, PDF, and Trawedit integration for this core milestone.

The audit was updated after Controlled UNLESS Conditions v0.1; no gold expectation changed.
