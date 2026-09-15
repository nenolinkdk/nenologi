# Controlled UNLESS Conditions v0.1

This bounded Phase 2 milestone makes `condition_003` exact:

```text
Source: You may enter unless the door is locked.
Target: You may enter if the door is locked.
Gold:   CONDITION_CHANGE, UNLESS_LOCKED -> IF_LOCKED, HIGH
```

## Grammar and normalization

Only the exact suffix form `You may enter unless the door is locked` is registered. For this controlled exception reading, `Q unless P` is normalized as `IF NOT(P), THEN Q`. This is justified for the fixed case: permission to enter applies when the door is not locked. It is not a claim that every natural-language use of “unless” has this equivalence.

The existing `Condition` continues to reference the ordinary `LOCKED(door)` antecedent proposition and `ENTER(you)` consequent proposition. A `NOT` operator scopes the antecedent proposition. The consequent retains its existing `MAY` operator. No opaque UNLESS predicate, new condition model, or new difference type is introduced.

## Comparison and duplicate policy

The comparator treats antecedent polarity as part of normalized condition identity. Its controlled display value is `UNLESS_LOCKED` for this negated antecedent and `IF_LOCKED` for the positive target. Because applicability changed while the aligned consequent remains, the result is one high-severity `CONDITION_CHANGE`, confidence 1.0, with logical relation `UNDETERMINED`.

Antecedent negation is consumed by condition comparison for this pair. It does not also produce `NEGATION_CHANGE`, `ADDITION`, or `OMISSION`. Existing prefix IF, suffix IF, numeric antecedent, consequent modality, and condition-removal behavior remain unchanged.

No direct IF-equivalence case is activated: `If the door is not locked, you may enter` is not part of the existing controlled antecedent grammar. Adding it solely to demonstrate paraphrase equivalence would broaden this milestone unnecessarily.

## Rendering, provenance, and safety

The derived display is `(¬Locked(Door)) → (May(Enter(You)))`. The semantic negation is normalized from the lexical trigger `unless`; its span therefore covers the real `unless` token. No fabricated NOT-token span is recorded. Condition, clause, entity, proposition, modality, and original document spans remain document-relative.

JSON round-trips preserve all IDs, references, spans, confidence, and status. Existing validation checks antecedent/consequent references and negation scope targets. Repeated parsing is deterministic.

The consequent remains governed by a condition and cannot be promoted to unconditional exact-explicit evidence. No inference rule, universal rule, default reasoning, counterfactual reasoning, or probability is added. Universal instantiation, scope, temporal, coreference, and non-literal safety remain unchanged.

## Audit impact and limitations

The 42-case audit moves from 36 to 37 exact cases and from 3 to 2 parser-unsupported cases. It remains at 0 analyzable-but-inexact, 0 comparator-unsupported, and 3 inference-not-implemented. Only `condition_003` changes classification; no gold expectation, schema, or taxonomy changes.

Prefix UNLESS, other subjects/predicates, postposed variants beyond the registered sentence, multiple/nested/mixed conditions, exceptive uses, counterfactuals, discourse interpretation, fuzzy matching, embeddings, and LLM/API interpretation remain unsupported.

A runnable inspection is available at [`examples/unless_conditions.py`](../../examples/unless_conditions.py).
