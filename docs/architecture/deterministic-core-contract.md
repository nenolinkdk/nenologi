# Deterministic Core Contract — Phase 2 Freeze v1

This document freezes the first stable deterministic-core contracts under the recommended baseline `phase-2-deterministic-core-v1`. Frozen means later phases preserve these contracts unless a documented, versioned architectural change justifies migration. It does not prohibit compatible extension.

## Authority and data flow

Normalized semantic objects are authoritative. Raw text and spans provide provenance; structural nodes describe surface organization. Formulas, plain-language interpretations, explanations, and findings are deterministic derived views. Comparator and inference logic consume `Analysis`, not parser internals or raw strings.

## Representation inventory

| Structure | Semantic authority and references | Invariants, validation, serialization, rendering |
| --- | --- | --- |
| Entity | typed normalized label and stable ID | Proposition arguments resolve to entity IDs; spans are provenance; JSON preserves identity. |
| Proposition/predicate | predicate plus ordered typed entity arguments | Explicit status/confidence; arguments resolve; identity excludes incidental spans and temporal IDs; rendered as predicate atoms. |
| Operator | operator plus exactly one scoped semantic reference | Scope resolves to operator/proposition/condition; chains are acyclic; quantifier, modality, and negation formulas derive from topology. |
| NumericConstraint | exact `Decimal`, typed operator, optional canonical unit, proposition scope | No float authority, conversion, ranges, or arithmetic; scope resolves; comparison uses normalized values. |
| Condition | antecedent and consequent proposition references | Both sides non-empty and resolving; consequent is not duplicated or promoted unconditionally; IF/UNLESS formulas are derived. |
| TemporalRelation | governed proposition, typed relation, canonical or structured reference | Governed proposition resolves; proposition anchors and temporal-reference nodes resolve; self/cyclic anchors are rejected. |
| SemanticItem relation/set | typed relation with ordered ID arguments | Arguments and derivations resolve; used for action/spatial relations, coordination, temporal-reference nodes, rules, membership, and alternatives. |
| Ambiguity/reference alternatives | ambiguity references ordered alternative IDs | Alternatives remain explicit and unresolved; all reading IDs resolve; no ranking occurs. |
| Universal rule/membership | normalized rule and same-entity membership facts | Unary exact antecedents and consequent only; serialized graph is authoritative; formula is derived. |
| Non-literal marker | explicit non-literal semantic item without fabricated literal proposition | Safe representation survives JSON; interpretation is deferred. |

## Comparator contract

Propositions align by mutually unique normalized signatures: semantic role, predicate, and typed entity arguments. A single structural counterpart may differ in one declared core position. No fuzzy, embedding, synonym, or LLM alignment is permitted. Ambiguity remains unaligned.

Canonical finding order is:

1. `QUANTIFIER_CHANGE`
2. `MODALITY_CHANGE`
3. `NEGATION_CHANGE`
4. `CONJUNCTION_CHANGE`
5. `NUMERIC_THRESHOLD_CHANGE`
6. `CONDITION_CHANGE`
7. `TEMPORAL_CHANGE`
8. `SCOPE_CHANGE`
9. `ENTITY_RELATION_CHANGE`
10. `ADDITION`
11. `OMISSION`

There is no contradiction difference type. `LogicalRelation` is separately `EQUIVALENT`, `CONTRADICTORY`, or `UNDETERMINED`. No semantic difference implies contradiction by default. Exact aligned polarity reversal can establish contradiction; no findings plus complete unambiguous alignment establishes equivalence; otherwise the relation is undetermined.

Only safely unmatched propositions produce addition/omission. A changed governing condition, temporal relation, scope topology, or conjunction must produce its canonical finding without false addition/omission or subordinate duplicates.

## Condition, temporal, and scope contracts

Conditions reference ordinary antecedent and consequent propositions. Antecedent polarity is structural; controlled UNLESS is IF with explicit antecedent negation. Numeric antecedents remain numeric constraints. Conditional consequents are not unconditional evidence.

Temporal meaning comes only from explicit registered structures. Canonical literals, observation/future references, aligned proposition anchors, and nested temporal-reference graphs remain distinct. There is no temporal arithmetic, contradiction, entailment, transitivity, prediction, tense chronology, or discourse chronology.

Scope is operator topology. Quantifier, modality, and negation chains must resolve and be acyclic. Embedded PROMISE/REQUIRE contrasts compare as one `SCOPE_CHANGE`, without redundant `NEGATION_CHANGE`.

## Inference safety contract

Priority is fixed as `EXACT_EXPLICIT`, `LEXICAL_OPPOSITION`, `UNIVERSAL_INSTANTIATION`, `NOT_ESTABLISHED`. `NOT_ESTABLISHED` means unsupported by the closed rules, not false or contradicted. There is no chaining, converse, contraposition, existential import, derived-fact reuse, prediction, ambiguity ranking, metaphor interpretation, or temporal inference.

## Serialization, validation, and determinism

`Analysis → JSON → Analysis` preserves semantic identity, IDs, reference edges, exact decimals, ordering, statuses, confidence, and spans. Every reference must resolve to an allowed target type. Operator and temporal-reference graphs are acyclic; temporal proposition anchors cannot self-reference; alternative IDs resolve.

Repeated identical inputs must yield identical semantic graphs, formulas, JSON, alignments, findings, evidence, explanations, and ordering. Public output must not depend on random state, Python hash iteration, filesystem enumeration, network state, external APIs, or system date.

## Versioning rule

Compatible controlled grammar and policy layers may consume these contracts. Any incompatible representation, taxonomy, logical-relation, alignment, inference-priority, serialization, or validation change requires a documented new contract version and migration rationale.
