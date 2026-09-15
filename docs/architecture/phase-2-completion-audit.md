# Phase 2 Completion Audit and Deterministic Core Freeze v1

## Decision

**FREEZE PHASE 2.** The executable audit reports 39 end-to-end exact cases, no parser or comparator blockers, and three representation-ready interpretation-policy cases. The decision is architectural: normalized structures are authoritative, comparisons and inference are deterministic and conservative, graph invariants are validated, and the remaining results require probability, alternative-reading evaluation, or non-literal policy rather than representation repair.

The frozen internal baseline name is **`phase-2-deterministic-core-v1`**. This is a recommendation only; no Git tag was created. The normative contracts are in [Deterministic Core Contract](deterministic-core-contract.md).

## Independent verification

- Gold corpus: 42 cases: 30 change, 5 equivalence, 7 inference.
- Actual audit: 39 `END_TO_END_EXACT`, 0 `ANALYZABLE_BUT_NOT_EXACT`, 0 `PARSER_UNSUPPORTED`, 0 `COMPARATOR_UNSUPPORTED`, 3 `INFERENCE_NOT_IMPLEMENTED`.
- Test suite: 283 passed, 0 failed, 0 skipped, 0 xfailed.
- Runtime dependencies declared by `pyproject.toml`: none; Python >=3.11 and setuptools are the only runtime/build requirements.
- Forbidden dependency scan: no LLM, NLP service, embedding, vector, fuzzy-semantic, or network client dependency.

## Authoritative 42-case completion table

`C/I` is comparator or inference. For comparison cases, the actual logical relation is shown after the finding; where gold omits a logical relation, exactness is determined by its declared findings.

| ID | Category | Source / statement | Target / query | Expected | Actual | Parser | C/I | Audit | Semantic feature | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| modality_001 | modality | All employees must register. | All employees may register. | `MODALITY_CHANGE MUST→MAY HIGH` | same; `UNDETERMINED` | supported | supported | exact | modality scope | none |
| modality_002 | modality | Visitors must wear badges. | Visitors should wear badges. | `MODALITY_CHANGE MUST→SHOULD HIGH` | same; `UNDETERMINED` | supported | supported | exact | modality scope | none |
| modality_003 | modality | Members may vote. | Members must vote. | `MODALITY_CHANGE MAY→MUST HIGH` | same; `UNDETERMINED` | supported | supported | exact | modality scope | none |
| conjunction_001 | conjunction | Submit form A and form B. | Submit form A or form B. | `CONJUNCTION_CHANGE AND→OR HIGH` | same; `UNDETERMINED` | supported | supported | exact | flat object conjunction | none |
| conjunction_002 | conjunction | Choose tea or coffee. | Choose tea and coffee. | `CONJUNCTION_CHANGE OR→AND HIGH` | same; `UNDETERMINED` | supported | supported | exact | flat object conjunction | none |
| quantifier_001 | quantification | All boxes are labelled. | Some boxes are labelled. | `QUANTIFIER_CHANGE ALL→SOME HIGH` | same; `UNDETERMINED` | supported | supported | exact | quantifier scope | none |
| quantifier_002 | quantification | Some doors are locked. | All doors are locked. | `QUANTIFIER_CHANGE SOME→ALL HIGH` | same; `UNDETERMINED` | supported | supported | exact | quantifier scope | none |
| quantifier_003 | quantification | No lamps are lit. | Some lamps are lit. | `QUANTIFIER_CHANGE NONE→SOME HIGH` | same; `UNDETERMINED` | supported | supported | exact | empty-set quantification | none |
| negation_001 | negation | The valve is not open. | The valve is open. | `NEGATION_CHANGE NEGATED→AFFIRMED HIGH` | same; `CONTRADICTORY` | supported | supported | exact | proposition polarity | none |
| negation_002 | negation | The alarm is active. | The alarm is not active. | `NEGATION_CHANGE AFFIRMED→NEGATED HIGH` | same; `CONTRADICTORY` | supported | supported | exact | proposition polarity | none |
| temporal_001 | temporal | Inspect the cable before starting the machine. | Inspect the cable after starting the machine. | `TEMPORAL_CHANGE BEFORE→AFTER HIGH` | same; `UNDETERMINED` | supported | supported | exact | proposition event anchor | none |
| temporal_002 | temporal | Pay the invoice before Monday. | Pay the invoice on Monday. | `TEMPORAL_CHANGE BEFORE→ON MEDIUM` | same; `UNDETERMINED` | supported | supported | exact | weekday reference | none |
| temporal_003 | temporal | Wait until noon. | Wait until after noon. | `TEMPORAL_CHANGE UNTIL_NOON→UNTIL_AFTER_NOON MEDIUM` | same; `UNDETERMINED` | supported | supported | exact | nested temporal reference | none |
| condition_001 | condition | If the light is green, you may enter. | You may enter. | `CONDITION_CHANGE IF_GREEN→NONE HIGH` | same; `UNDETERMINED` | supported | supported | exact | prefix IF removal | none |
| condition_002 | condition | Submit the report. | Submit the report if the test passes. | `CONDITION_CHANGE NONE→IF_TEST_PASSES HIGH` | same; `UNDETERMINED` | supported | supported | exact | suffix IF addition | none |
| condition_003 | condition | You may enter unless the door is locked. | You may enter if the door is locked. | `CONDITION_CHANGE UNLESS_LOCKED→IF_LOCKED HIGH` | same; `UNDETERMINED` | supported | supported | exact | antecedent polarity | none |
| numeric_001 | numeric | The score must be greater than 10. | The score must be at least 10. | `NUMERIC_THRESHOLD_CHANGE >10→>=10 MEDIUM` | same; `UNDETERMINED` | supported | supported | exact | exact decimal threshold | none |
| numeric_002 | numeric | The temperature must be below 5 degrees. | The temperature must be at most 5 degrees. | `NUMERIC_THRESHOLD_CHANGE <5→<=5 MEDIUM` | same; `UNDETERMINED` | supported | supported | exact | unit threshold | none |
| numeric_003 | numeric | Bring at least three copies. | Bring more than three copies. | `NUMERIC_THRESHOLD_CHANGE >=3→>3 MEDIUM` | same; `UNDETERMINED` | supported | supported | exact | number-word threshold | none |
| numeric_004 | numeric | Select exactly two files. | Select at least two files. | `NUMERIC_THRESHOLD_CHANGE =2→>=2 HIGH` | same; `UNDETERMINED` | supported | supported | exact | exact-to-minimum threshold | none |
| entity_relation_001 | entity/relation | Alice approved the request. | Bob approved the request. | `ENTITY_RELATION_CHANGE SUBJECT:ALICE→SUBJECT:BOB HIGH` | same; `UNDETERMINED` | supported | supported | exact | subject role | none |
| entity_relation_002 | entity/relation | Alice approved the request. | Alice approved the invoice. | `ENTITY_RELATION_CHANGE OBJECT:REQUEST→OBJECT:INVOICE HIGH` | same; `UNDETERMINED` | supported | supported | exact | object role | none |
| entity_relation_003 | entity/relation | The key is inside the box. | The key is beside the box. | `ENTITY_RELATION_CHANGE INSIDE→BESIDE HIGH` | same; `UNDETERMINED` | supported | supported | exact | spatial relation | none |
| addition_001 | addition | Register your name. | Register your name and show identification. | `ADDITION null→SHOW_IDENTIFICATION HIGH` | same; `UNDETERMINED` | supported | supported | exact | coordinated predicates | none |
| omission_001 | omission | Open the valve if the pressure is low. | Open the valve. | `CONDITION_CHANGE IF_LOW→NONE HIGH` | same; `UNDETERMINED` | supported | supported | exact | governing condition | none |
| contradiction_001 | contradiction | The switch is on. | The switch is not on. | `NEGATION_CHANGE`; `CONTRADICTORY` | same | supported | supported | exact | explicit polarity conflict | none |
| scope_001 | scope | Maria did not promise to leave. | Maria promised not to leave. | `SCOPE_CHANGE NOT(PROMISE(LEAVE))→PROMISE(NOT(LEAVE)) HIGH` | same; `UNDETERMINED` | supported | supported | exact | embedded operator topology | none |
| scope_002 | scope | The rule does not require employees to leave. | The rule requires employees not to leave. | `SCOPE_CHANGE NOT(REQUIRE(LEAVE))→REQUIRE(NOT(LEAVE)) HIGH` | same; `UNDETERMINED` | supported | supported | exact | embedded operator topology | none |
| addition_002 | addition | The window is closed. | The window is closed. The door is locked. | `ADDITION null→DOOR_LOCKED MEDIUM` | same; `UNDETERMINED` | supported | supported | exact | independent propositions | none |
| omission_002 | omission | Sign and date the form. | Sign the form. | `OMISSION DATE_FORM→null HIGH` | same; `UNDETERMINED` | supported | supported | exact | coordinated predicates | none |
| equivalence_001 | equivalence | Every employee must register. | All employees must register. | no differences | no differences; `EQUIVALENT` | supported | supported | exact | quantifier normalization | none |
| equivalence_002 | equivalence | Alice approved the request. | The request was approved by Alice. | no differences | no differences; `EQUIVALENT` | supported | supported | exact | voice normalization | none |
| equivalence_003 | equivalence | Bring at least three copies. | Bring three or more copies. | no differences | no differences; `EQUIVALENT` | supported | supported | exact | threshold normalization | none |
| equivalence_004 | equivalence | The valve is not open. | The valve isn't open. | no differences | no differences; `EQUIVALENT` | supported | supported | exact | contraction normalization | none |
| equivalence_005 | equivalence | Submit form A and form B. | Submit form B and form A. | no differences | no differences; `EQUIVALENT` | supported | supported | exact | commutative AND | none |
| entailment_001 | inference | The door is open. | The door is open. | `EXPLICIT` | `EXPLICIT / EXACT_EXPLICIT` | supported | exact explicit | exact | normalized identity | none |
| entailment_002 | inference | All marked boxes are inspected. Box A is marked. | Box A is inspected. | `ENTAILED` | `ENTAILED / UNIVERSAL_INSTANTIATION` | supported | universal instantiation | exact | rule + membership | none |
| entailment_003 | inference | The light flickered on each of the last five evenings. | The light will flicker this evening. | `PROBABLE` | `UNSUPPORTED / NOT_ESTABLISHED` | supported | policy absent | deferred | observation/future temporal evidence | defeasible prediction |
| entailment_004 | inference | Peter lived in Paris for five years. | Peter speaks fluent French. | `UNSUPPORTED` | `UNSUPPORTED / NOT_ESTABLISHED` | supported | not established | exact | open-world non-entailment | none |
| entailment_005 | inference | The switch is off. | The switch is on. | `CONTRADICTED` | `CONTRADICTED / LEXICAL_OPPOSITION` | supported | lexical opposition | exact | closed OFF/ON registry | none |
| entailment_006 | inference | Alex told Sam that they had won. | Alex had won. | `AMBIGUOUS` | `UNSUPPORTED / NOT_ESTABLISHED` | supported | policy absent | deferred | unresolved reference alternatives | alternative-reading evaluation |
| entailment_007 | inference | Time is a thief. | Time commits theft. | `CANNOT_BE_SAFELY_FORMALIZED` | `UNSUPPORTED / NOT_ESTABLISHED` | supported | policy absent | deferred | non-literal safety marker | non-literal policy |

## Exactness and architecture findings

All 39 exact cases traverse their intended parser and comparator/inference pipeline. Comparison uses normalized objects and never document strings. Alignment uses role, predicate, and typed normalized entity arguments; IDs and spans are not semantic identity. Exact inference compares semantic signatures, and tests independently vary raw document text. Controlled gold-specific grammar exists, but no rule returns a gold answer from a case ID or raw sentence equality. Ordering is canonicalized and repeatedly tested. No ignored unsupported fragment was found.

The authoritative data flow is `input → structural analysis → normalized semantic graph → deterministic comparison/inference → derived formula/explanation/finding`. Formulas, explanations, and surface text are not semantic authority. No violation was found.

## Remaining Phase 3 cases

- `entailment_003` is representation-ready: `FLICKER(light)` is linked to `ON LAST_5_EVENINGS`, while the query is linked to `ON THIS_EVENING`. Producing `PROBABLE` requires an explicit defeasible prediction and calibration policy.
- `entailment_006` is representation-ready: `TELL(Alex,Sam)` embeds `WON(reference_001)`; ordered `REFERENCE_ALTERNATIVE` nodes connect the unresolved reference to Alex and Sam. Producing `AMBIGUOUS` requires evaluating the query across admissible readings without choosing one.
- `entailment_007` is representation-ready: the source stores `UNRESOLVED_NON_LITERAL` and no literal theft proposition. Producing `CANNOT_BE_SAFELY_FORMALIZED` requires policy propagation, not metaphor interpretation.

These are policy boundaries, not Phase 2 defects. They remain `NOT_ESTABLISHED` in the deterministic engine.

## Audit conclusions

The difference order is quantifier, modality, negation, conjunction, numeric threshold, condition, temporal, scope, entity/relation, addition, omission. There is no `CONTRADICTION` difference type; `EQUIVALENT`, `CONTRADICTORY`, and `UNDETERMINED` remain separate comparison relations. Contradiction is established only by explicit polarity reversal over an otherwise aligned proposition. Equivalence requires no findings and complete unambiguous alignment. All other supported changes remain undetermined.

Alignment is mutually unique and exact/structural over normalized typed roles. Ambiguous candidates remain unmatched. Safe unmatched propositions alone produce addition/omission. Condition antecedents, temporal anchors, and coordinated proposition members are not double-counted. Scope topology suppresses redundant polarity findings.

Inference priority is `EXACT_EXPLICIT`, `LEXICAL_OPPOSITION`, `UNIVERSAL_INSTANTIATION`, then `NOT_ESTABLISHED`. The fallback means absence of proof, not falsehood or contradiction. Universal instantiation is unary, exact, same-entity, all-antecedents-required, single-step substitution with no chaining, converse, contraposition, derived-fact reuse, or existential import.

Representative operators, conditions, numeric constraints, simple/event/nested temporal relations, scope chains, ambiguity alternatives, coordinated propositions, rules/membership, and non-literal markers round-trip through JSON with stable identity. Validation rejects dangling proposition/condition/temporal/alternative references, invalid/self event anchors, direct/indirect temporal cycles, and operator cycles. Formula rendering for every major family is derived from normalized objects.

Repeated analysis and comparison produce stable IDs, graphs, findings, evidence order, formulas, and JSON. Sorted/canonical operations guard set-derived ordering; no randomness, filesystem enumeration, system date, network, or hash-dependent public ordering was found.

## Known frozen limitations

The following are intentional boundaries, not defects: controlled grammar; no broad NLP or lexical semantics; no general synonym, world-knowledge, coreference, discourse, temporal, probabilistic, defeasible, or metaphor reasoning; no fuzzy matching, embeddings, vector database, LLM interpretation, or external semantic service. Temporal support is limited to registered weekday/clock, relative-evening, event-anchor, and nested-noon families. Rules remain unary and single-step.

## Next task

Begin Phase 3 with a policy-contract design milestone. The recommended first entry point is **Defeasible Prediction Policy v0.1** for `entailment_003`, followed by alternative-reading evaluation and non-literal status propagation. No Phase 3 functionality is implemented by this audit.

That design milestone is now recorded in [Phase 3.0 — Interpretation and Policy Architecture](phase-3-interpretation-policy-architecture.md). This cross-link does not alter the frozen Phase 2 decision, contracts, or 39/42 metric.
