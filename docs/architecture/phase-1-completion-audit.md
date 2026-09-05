# Phase 1 Completion Audit

This document records the reproducible completion baseline for Nenologi Core Phase 1 and tracks the current 42-case pipeline. The first Phase 2 parser extension raises the suite to 109 automated tests without changing semantic, alignment, comparison, or inference behavior.

Run the authoritative per-case audit with:

```powershell
$env:PYTHONPATH = "src"
python tests/validation/audit_gold_coverage.py --json
```

## Decision

**PHASE 1 COMPLETE.** The MVP requires a parser-independent normalized model, controlled English analysis, deterministic comparison, inspectable output, explicit unsupported behavior, and automated tests without GUI or provider dependencies. It does not require all gold cases or inference to be implemented. Parser breadth and inference remain Phase 2 work.

## Capability inventory

| Capability | Status | Exact controlled subset |
| --- | --- | --- |
| Quantification | SUPPORTED | One `ALL`, `SOME`, or `NONE` operator on an aligned proposition. |
| Modality | SUPPORTED | One `MUST`, `MAY`, or `SHOULD`; listed deterministic transitions. |
| Negation | SUPPORTED | Explicit controlled `NOT` add/remove and fixed modal-internal reading. |
| Conjunction | LIMITED | One flat two-object `AND`/`OR`; no predicate coordination or commutative reordering. |
| Numeric thresholds | LIMITED | One exact decimal threshold and controlled units; no ranges, conversion, or entailment. |
| Conditions | LIMITED | One prefix `IF`, one simple antecedent and consequent; no suffix IF/UNLESS/nesting. |
| Temporal relations | LIMITED | One proposition-final weekday/clock `BEFORE`, `AFTER`, `ON`, or `UNTIL`. |
| Scope | LIMITED | Explicit acyclic single-target chains and dedicated `Not all ...`; no general resolver. |
| Entity/relation comparison | LIMITED | One positional subject, object, or predicate change with stable argument roles. |
| Proposition alignment | LIMITED | Unique one-to-one normalized signatures plus comparator-only single-position counterpart. |
| Addition/omission | LIMITED | Safely unmatched normalized propositions; ambiguity and condition antecedents excluded. |
| Logical relation | LIMITED | Exact structural equivalence and one narrow pure-negation contradiction; otherwise `UNDETERMINED`. |

## Full gold pipeline matrix

`S/A/AL/C/I` mean parser, normalized analysis, alignment, comparator, and inference. `OK`, `NO`, `NR`, `NA`, `AV`, `INC`, `AL`, `UN`, and `AMB` mean supported, unsupported, not reached, not applicable, available, incomplete, aligned, unaligned, and ambiguous. The JSON command above provides the unabbreviated machine-readable matrix and exact runtime detail.

| Case | Category | S | A | AL | C | I | Final status | Blocking reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| modality_001 | modality | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| modality_002 | modality | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| modality_003 | modality | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| conjunction_001 | conjunction | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| conjunction_002 | conjunction | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| quantifier_001 | quantification | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| quantifier_002 | quantification | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| quantifier_003 | quantification | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| negation_001 | negation | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| negation_002 | negation | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| temporal_001 | temporal | NO | NR | NR | NR | NA | PARSER_UNSUPPORTED | UNSUPPORTED_EVENT_TEMPORAL_ANCHOR |
| temporal_002 | temporal | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| temporal_003 | temporal | NO | NR | NR | NR | NA | PARSER_UNSUPPORTED | UNSUPPORTED_NESTED_TEMPORAL_PHRASE |
| condition_001 | condition | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| condition_002 | condition | NO | NR | NR | NR | NA | PARSER_UNSUPPORTED | UNSUPPORTED_SUFFIX_IF |
| condition_003 | condition | NO | NR | NR | NR | NA | PARSER_UNSUPPORTED | UNSUPPORTED_UNLESS |
| numeric_001 | numeric | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| numeric_002 | numeric | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| numeric_003 | numeric | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| numeric_004 | numeric | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| entity_relation_001 | entity | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| entity_relation_002 | entity | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| entity_relation_003 | entity | NO | NR | NR | NR | NA | PARSER_UNSUPPORTED | UNSUPPORTED_SPATIAL_RELATION |
| addition_001 | addition | OK | AV | UN | NO | NA | COMPARATOR_UNSUPPORTED | UNSUPPORTED_COORDINATED_PREDICATE_REPRESENTATION |
| omission_001 | omission | NO | NR | NR | NR | NA | PARSER_UNSUPPORTED | UNSUPPORTED_SUFFIX_IF |
| contradiction_001 | contradiction | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| scope_001 | scope | NO | NR | NR | NR | NA | PARSER_UNSUPPORTED | UNSUPPORTED_EMBEDDED_VERB |
| scope_002 | scope | NO | NR | NR | NR | NA | PARSER_UNSUPPORTED | UNSUPPORTED_EMBEDDED_VERB |
| addition_002 | addition | NO | NR | NR | NR | NA | PARSER_UNSUPPORTED | UNSUPPORTED_MULTI_SENTENCE |
| omission_002 | omission | NO | NR | NR | NR | NA | PARSER_UNSUPPORTED | UNSUPPORTED_COORDINATED_PREDICATES |
| equivalence_001 | equivalence | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| equivalence_002 | equivalence | YES | YES | YES | EXACT | NA | END_TO_END_EXACT | NONE |
| equivalence_003 | equivalence | OK | AV | AL | OK | NA | END_TO_END_EXACT | NONE |
| equivalence_004 | equivalence | YES | YES | YES | EXACT | NA | END_TO_END_EXACT | NONE |
| equivalence_005 | equivalence | OK | AV | UN | NO | NA | COMPARATOR_UNSUPPORTED | UNSUPPORTED_SYMMETRIC_CONJUNCTION_ALIGNMENT |
| entailment_001 | entailment | OK | AV | NA | NA | NO | INFERENCE_NOT_IMPLEMENTED | INFERENCE_REQUIRED |
| entailment_002 | entailment | NO | INC | NA | NA | NO | INFERENCE_NOT_IMPLEMENTED | INFERENCE_REQUIRED |
| entailment_003 | entailment | NO | INC | NA | NA | NO | INFERENCE_NOT_IMPLEMENTED | INFERENCE_REQUIRED |
| entailment_004 | entailment | NO | INC | NA | NA | NO | INFERENCE_NOT_IMPLEMENTED | INFERENCE_REQUIRED |
| entailment_005 | entailment | OK | AV | NA | NA | NO | INFERENCE_NOT_IMPLEMENTED | INFERENCE_REQUIRED |
| entailment_006 | entailment | NO | INC | NA | NA | NO | INFERENCE_NOT_IMPLEMENTED | INFERENCE_REQUIRED |
| entailment_007 | entailment | NO | INC | NA | NA | NO | INFERENCE_NOT_IMPLEMENTED | INFERENCE_REQUIRED |

Phase 1 exit baseline was 19 exact and 14 parser-unsupported. Current totals are **23 END_TO_END_EXACT, 0 ANALYZABLE_BUT_NOT_EXACT, 10 PARSER_UNSUPPORTED, 2 COMPARATOR_UNSUPPORTED, 7 INFERENCE_NOT_IMPLEMENTED.**

## Comparator-unsupported investigations

### `addition_001`

- Source normalizes to `REGISTER(addressee, your_name)` with one action relation.
- Target normalizes to one proposition, `REGISTER(addressee, your_name, show_identification)`, plus an `AND(your_name, show_identification)` object relation.
- Alignment: no pair; both `prop_001` values are safely unmatched.
- Blocker: the parser did not create a second `SHOW(identification)` proposition. Addition/Omission v0.1 cannot infer proposition splitting from an object conjunction, so emitting `ADDITION` would require a new coordinated-predicate representation, not stronger matching. The gold expectation remains unchanged.

### `equivalence_005`

- Source normalizes to `SUBMIT(addressee, form_a, form_b)` and `AND(form_a, form_b)`.
- Target normalizes to `SUBMIT(addressee, form_b, form_a)` and `AND(form_b, form_a)`.
- Alignment: no pair; two positional core arguments differ, beyond the single-position counterpart rule.
- Blocker: commutative normalization for symmetric conjunction is absent. This is an alignment/normalized-representation limitation, not addition/omission; treating both sides as safe add/omit would be false. The comparator therefore retains its explicit unsupported result.

## Parser blockers

| Construction | Cases | Domain/comparator readiness | Risk | Exact gold likely unlocked |
| --- | --- | --- | --- | ---: |
| Passive transitive | equivalence_002 | Implemented in Simple Passive Transitive v0.2 | COMPLETE | 1 |
| Suffix IF | condition_002, omission_001 | Condition model/comparator exist; omission_001 taxonomy conflicts with condition precedence | MEDIUM | 1 |
| Embedded verbs | scope_001, scope_002 | Scope chains exist; embedded propositions/alignment do not | HIGH | 2 |
| Event temporal anchor | temporal_001 | Temporal type exists; event-anchor proposition does not | HIGH | 1 |
| Nested temporal phrase | temporal_003 | Flat temporal type exists; nested relation does not | MEDIUM | 1 |
| UNLESS | condition_003 | IF exists; exception/inversion semantics do not | HIGH | 1 |
| Spatial copular relation | entity_relation_003 | Generic relation storage exists; controlled normalization/comparison is partial | MEDIUM | 1 |
| Multi-sentence | addition_002 | Domain alignment/addition exists; document sentence parsing does not | MEDIUM | 1 |
| Coordinated predicates | omission_002 | Multi-proposition comparison exists; predicate coordination parsing does not | HIGH | 1 |
| Contraction | equivalence_004 | Implemented in Contraction Normalization v0.3 | COMPLETE | 1 |

## Inference cases

| Case | Structures available today | Reasoning required | Parser first? | Risk |
| --- | --- | --- | --- | --- |
| entailment_001 | Both `OPEN(door)` analyses | Exact explicit-claim recognition | No | LOW |
| entailment_002 | Neither multi-sentence rule/membership statement nor candidate parses | Universal instantiation plus membership | Yes | HIGH |
| entailment_003 | Neither observation sequence nor future candidate parses | Defeasible prediction, not entailment | Yes | HIGH |
| entailment_004 | Neither residence nor fluency proposition parses | Open-world non-entailment/unsupported judgment | Yes | HIGH |
| entailment_005 | `OFF(switch)` and `ON(switch)` parse | Lexical opposition contradiction | No, but lexical relation data is absent | MEDIUM |
| entailment_006 | Pronoun-bearing statement/candidate do not parse | Coreference ambiguity with competing readings | Yes | HIGH |
| entailment_007 | Metaphor and theft candidate do not parse | Non-literal safety classification | Yes | HIGH |

Only entailment_001 is representationally sufficient today. Entailment_005 needs an explicit lexical-opposition resource not present in the semantic model; the other five require parser/representation work before reasoning.

## Addition/omission and alignment audit

Addition/Omission v0.1 is implemented independently of gold parser coverage. Safe unmatched propositions yield symmetric `MEDIUM`, confidence-`1.0` findings with structured payloads. Duplicate candidates remain ambiguous and yield no finding. Condition-owned antecedents are suppressed when `CONDITION_CHANGE` explains wrapper addition/removal. The single-core-position counterpart rule runs before unmatched classification, and canonical ordering places `ADDITION` then `OMISSION` after specialized dimensions.

Alignment signatures contain structural role, predicate, and ordered typed/case-folded entity labels. Quantifier, modality, negation, numeric, temporal, condition wrapper, scope, spans, displays, and raw text are excluded. Mutual uniqueness enforces one-to-one matching; ambiguity and safe-unmatched sets are explicit. Stronger alignment is needed for commutative conjunction and future coreference/split-merge work, but not for simple past normalization, contraction expansion, or exact explicit inference.

Gold coverage did not rise after Addition/Omission because no existing gold input currently reaches a correct multi-proposition normalized analysis: one case is multi-sentence parser-unsupported, one is predicate-coordination parser-unsupported, one suffix condition is parser-unsupported, and `addition_001` is represented as one object-conjoined proposition.

## Comparator and normalized-model completeness

| Difference type | Completeness | Main boundary |
| --- | --- | --- |
| QUANTIFIER_CHANGE | COMPLETE_FOR_CONTROLLED_SUBSET | Listed single-operator transitions only |
| MODALITY_CHANGE | COMPLETE_FOR_CONTROLLED_SUBSET | Listed single-operator transitions only |
| NEGATION_CHANGE | COMPLETE_FOR_CONTROLLED_SUBSET | Explicit polarity only |
| CONJUNCTION_CHANGE | PARTIAL | Flat two-object AND/OR; no commutative normalization |
| NUMERIC_THRESHOLD_CHANGE | COMPLETE_FOR_CONTROLLED_SUBSET | One exact threshold; no reasoning/conversion |
| CONDITION_CHANGE | PARTIAL | One prefix IF; antecedent structure narrowly aligned |
| TEMPORAL_CHANGE | PARTIAL | One flat weekday/clock relation |
| SCOPE_CHANGE | PARTIAL | Explicit controlled chains only |
| ENTITY_RELATION_CHANGE | PARTIAL | One positional core change |
| ADDITION | COMPLETE_FOR_CONTROLLED_SUBSET | Safe normalized unmatched target propositions |
| OMISSION | COMPLETE_FOR_CONTROLLED_SUBSET | Safe normalized unmatched source propositions |

| Dimension | Domain/schema | Parser | Comparator | Renderer | Exact gold |
| --- | --- | --- | --- | --- | ---: |
| Quantifier | Supported | Controlled | Supported | Supported | 3 |
| Modality | Supported | Controlled | Supported | Supported | 3 |
| Negation | Supported | Controlled | Supported | Supported | 2 |
| Conjunction | Generic relation | Flat objects | Partial | Supported | 2 |
| Numeric | Supported | Controlled | Supported | Supported | 4 |
| Condition | Supported | Prefix IF | Partial | Supported | 1 |
| Temporal | Supported | Weekday/clock | Partial | Supported | 1 |
| Scope | Operator references | One dedicated contrast | Partial | Supported | 0 |
| Entity/relation | Supported | Present-tense controlled forms | Partial | Supported | 0 |
| Alignment | Dedicated result API | Parser-independent | Integrated | Not applicable | Indirect |
| Addition/omission | Structured Difference payload | No multi-sentence/predicate coordination | Supported for safe unmatched | Explanation supported | 0 |
| Logical relation | Comparison enum | Not applicable | Partial | Serialized | 3 including equivalence/contradiction |

## Quality baseline and exit criteria

The current baseline passes 120 unit/validation tests, gold validation (30 change, 5 equivalence, 7 inference), all schema/reference tests, analysis/comparison JSON round-trips, Unicode formulas, Markdown links, forbidden-dependency scan, parser-independent comparator fixtures, deterministic alignment, and complete canonical `DifferenceType` ordering.

| Exit criterion | Result | Evidence |
| --- | --- | --- |
| Parser-independent normalized model | PASS | Manual Analysis fixtures and public APIs |
| Deterministic comparator | PASS | All implemented findings and stable order/IDs |
| Explicit uncertainty/status | PASS | Typed interpretation statuses and unsupported errors |
| Separate severity/confidence | PASS | Independent typed fields and regression tests |
| Explicit logical relation | PASS | Separate comparison-level enum |
| Deterministic proposition alignment | PASS | Mutual uniqueness, one-to-one, ambiguity sets |
| Controlled semantic parsing | PASS | Deliberately bounded English grammar |
| Schema/serialization stability | PASS | Reference validation and round-trips |
| Reproducible gold corpus | PASS | 42-case validator and JSON pipeline audit |
| No LLM/provider dependency | PASS | Dependency scan and zero runtime dependencies |
| Deterministic explanations | PASS | Exact rule-generated prose |
| Unsupported-language behavior | PASS | Typed rejection; multilingual parsing remains explicit out of scope |

## Phase 2 options and recommendation

| Direction | Value | Dependency | Risk | Expected gold impact | Architectural benefit |
| --- | --- | --- | --- | --- | --- |
| Controlled parser expansion | High | Existing normalized structures | Low–High by family | Immediate | Converts implemented domain capability into end-to-end coverage |
| Limited deterministic inference | High but narrow | Stable parsed representations/rule contracts | Medium–High | Up to 2 initially | Opens inference layer |
| Broader proposition alignment | Medium | New normalization evidence | High | 1 current case | Enables later coreference/split-merge work |
| Additional semantic categories | Low now | New schema/taxonomy | High | None identified | Breadth without current corpus demand |
| UI/application work | Product value | Stable core API | Medium | None | Exercises client boundary, not semantic coverage |

Simple Past Transitive Clauses v0.1 unlocked `entity_relation_001` and `entity_relation_002`. Simple Passive Transitive Clauses v0.2 unlocked `equivalence_002`, and Contraction Normalization v0.3 unlocked `equivalence_004` without contraction-specific semantics. The next recommended Phase 2 milestone is narrowly controlled spatial copular relations for `entity_relation_003`.
