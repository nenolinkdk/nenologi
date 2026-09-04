# Multilayer analysis

Nenologi separates three analytical layers. Later layers may reference earlier ones, but they must not erase the evidence from which an interpretation was derived.

## 1. Structural layer

The structural layer records document, sentence, clause, and discourse organization. It covers coordination and subordination, textual sequence, and discourse relations such as contrast, exception, cause, and consequence. It should retain spans or other traceable references to the source text.

## 2. Semantic layer

The semantic layer represents entities, predicates, properties, semantic roles, relations, negation, quantification, modality, temporality, conditions, scope, and references. It distinguishes what is directly expressed from what is resolved or inferred. Uncertain reference resolution and alternate scope readings must remain visible.

## 3. Logical and inference layer

The logical layer normalizes supported readings using propositional or predicate logic where appropriate, plus set relations and constraints. It enables entailment, contradiction, comparison, and bounded inference. A logical expression is an explicit model produced by Nenologi—not the hidden state of an AI model and not necessarily the only defensible interpretation.

## Information flow

```text
source spans
  -> structural nodes and discourse links
  -> entities, propositions, operators, and references
  -> candidate normalized readings
  -> comparisons and justified inferences
  -> plain-language interpretations with provenance
```

Each generated item should be traceable to source spans, upstream representation identifiers, or an explicitly named rule. Unsupported common-sense assumptions must not silently become facts.

## Uncertainty and impact

Interpretation state and confidence apply to analyses. Severity applies to findings. For example, a possible omitted negation can have low confidence and high severity. This separation prevents uncertainty from being confused with harmlessness.
